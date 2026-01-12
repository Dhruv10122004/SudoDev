from pydantic import BaseModel
from typing import Optional, List

class AgentRunRequest(BaseModel):
    instance_id: str
    problem_statement: str

class AgentRunResponse(BaseModel):
    run_id: str
    status: str

class AgentStatusResponse(BaseModel):
    run_id: str
    status: str
    message: Optional[str] = None
    logs: Optional[List[str]] = []
    current_step: Optional[int] = 0
    patch: Optional[str] = None
