from pydantic import BaseModel, Field, model_validator
from typing import Optional, List, Literal

class AgentRunRequest(BaseModel):
    instance_id: Optional[str] = None # for swe bench mode
    github_url: Optional[str] = None  # for github mode
    issue_description: Optional[str] = None
    branch: Optional[str] = "main"

    problem_statement: Optional[str] = None
    mode: Literal["swebench", "github"] = Field(default="swebench")

    @model_validator(mode='after')
    def validate_mode_fields(self):
        """Validate that required fields are present for each mode"""
        if self.mode == "swebench":
            if not self.instance_id:
                raise ValueError("instance_id is required for swebench mode")
        elif self.mode == "github":
            if not self.github_url:
                raise ValueError("github_url is required for github mode")
            if not self.issue_description:
                raise ValueError("issue_description is required for github mode")
        
        return self

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
