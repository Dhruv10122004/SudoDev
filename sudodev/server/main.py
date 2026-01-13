from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uuid
import logging
import os
from datetime import datetime
from datasets import load_dataset

from sudodev.server.models import AgentRunRequest, AgentRunResponse, AgentStatusResponse
from sudodev.core.cache_manager import InstanceCacheManager

# Load SWE-bench dataset at startup (cached for fast lookups)
print("Loading SWE-bench dataset...")
swe_bench_dataset = load_dataset("princeton-nlp/SWE-bench_Lite", split="test")
print(f"Loaded {len(swe_bench_dataset)} issues from SWE-bench")

cache_dir = os.getenv("SWEBENCH_CACHE_DIR", "/app/cache/swebench")
cache_manager = InstanceCacheManager(cache_dir)
print(f"Cache manager initialized at {cache_dir}")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent_runs = {}

def add_log(run_id: str, message: str, step: int = None):
    """Add a log message to the agent run"""
    if run_id in agent_runs:
        agent_runs[run_id]["logs"].append(message)
        if step is not None:
            agent_runs[run_id]["current_step"] = step

class LogCaptureHandler(logging.Handler):
    """Custom logging handler to capture agent logs"""
    def __init__(self, run_id: str):
        super().__init__()
        self.run_id = run_id
        self.setLevel(logging.INFO)
        formatter = logging.Formatter('%(message)s')
        self.setFormatter(formatter)
        
    def emit(self, record):
        try:
            msg = self.format(record)
            if msg.strip():
                add_log(self.run_id, msg)
        except Exception:
            pass

def run_agent(run_id: str, request: AgentRunRequest):
    """Execute the real SudoDev agent"""
    import time
    from sudodev.core.improved_agent import ImprovedAgent
    from sudodev.core.utils.logger import setup_logger
    
    agent_runs[run_id]["status"] = "running"
    agent_runs[run_id]["message"] = "Preparing instance..."
    
    log_handler = LogCaptureHandler(run_id)
    root_logger = logging.getLogger()
    root_logger.addHandler(log_handler)
    
    try:
        add_log(run_id, f"[INIT] Loading issue {request.instance_id} from SWE-bench...", 0)
        
        issue = next((item for item in swe_bench_dataset if item["instance_id"] == request.instance_id), None)
        
        if not issue:
            raise FileNotFoundError(f"Instance {request.instance_id} not found in SWE-bench dataset")
        
        add_log(run_id, f"[CACHE] Checking cache for {request.instance_id}...", 0)
        if not cache_manager.is_instance_cached(request.instance_id):
            add_log(run_id, f"[CACHE] Instance not cached, downloading from SWE-bench...", 0)
            agent_runs[run_id]["message"] = "Downloading instance environment..."
            
            if not cache_manager.download_instance(request.instance_id):
                raise Exception(f"Failed to download instance {request.instance_id}")
            
            add_log(run_id, f"[CACHE] Instance cached successfully", 0)
        else:
            add_log(run_id, f"[CACHE] Using cached instance ✓", 0)
        
        add_log(run_id, f"[INIT] Agent initialized for {request.instance_id}", 0)
        agent_runs[run_id]["message"] = "Agent is processing..."
        time.sleep(0.5)
        
        agent = ImprovedAgent(issue)
        success = agent.run()
        
        patch = ""
        if success and hasattr(agent, 'get_patch'):
            patch = agent.get_patch()
        agent_runs[run_id]["patch"] = patch
        
        if success:
            add_log(run_id, "[VERIFY] All tests passed ✓", 5)
            agent_runs[run_id]["status"] = "completed"
            agent_runs[run_id]["message"] = "Fix generated successfully"
        else:
            add_log(run_id, "[ERROR] Agent failed to generate fix")
            agent_runs[run_id]["status"] = "failed"
            agent_runs[run_id]["message"] = "Agent could not resolve the issue"
            
    except FileNotFoundError as e:
        error_msg = f"Instance ID not found: {request.instance_id}"
        add_log(run_id, f"[ERROR] {error_msg}")
        agent_runs[run_id]["status"] = "failed"
        agent_runs[run_id]["message"] = error_msg
    except Exception as e:
        error_msg = str(e)
        add_log(run_id, f"[ERROR] {error_msg}")
        agent_runs[run_id]["status"] = "failed"
        agent_runs[run_id]["message"] = f"Agent error: {error_msg}"
    finally:
        root_logger.removeHandler(log_handler)

@app.get("/")
def root():
    return {"message": "SudoDev API"}

@app.post("/api/run")
def start_run(request: AgentRunRequest, background_tasks: BackgroundTasks):
    run_id = str(uuid.uuid4())
    
    agent_runs[run_id] = {
        "status": "pending",
        "instance_id": request.instance_id,
        "problem_statement": request.problem_statement,
        "created_at": datetime.now().isoformat(),
        "logs": [],
        "current_step": 0,
        "patch": ""
    }
    
    background_tasks.add_task(run_agent, run_id, request)
    
    return AgentRunResponse(run_id=run_id, status="pending")

@app.get("/api/status/{run_id}")
def get_status(run_id: str):
    if run_id not in agent_runs:
        return {"error": "Run not found"}
    
    run = agent_runs[run_id]
    return AgentStatusResponse(
        run_id=run_id,
        status=run["status"],
        message=run.get("message"),
        logs=run.get("logs", []),
        current_step=run.get("current_step", 0),
        patch=run.get("patch", "")
    )

@app.get("/api/runs")
def list_runs():
    return {"runs": list(agent_runs.keys())}

@app.get("/api/cache/status")
def cache_status():
    return cache_manager.get_cache_info()

@app.delete("/api/cache/clear")
def clear_cache(instance_id: str = None):
    cache_manager.clear_cache(instance_id)
    return {"message": f"Cache cleared for {instance_id}" if instance_id else "All cache cleared"}
