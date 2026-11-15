from pydantic import BaseModel, Field, ConfigDict


class AddTaskArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str = Field(min_length=3, max_length=120)
    priority: str = Field(default="medium", pattern="^(low|medium|high)$")


class ListTasksArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: str = Field(default="all", pattern="^(all|open|done)$")


class CompleteTaskArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    task_id: int = Field(gt=0)


class SearchMemoryArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(min_length=2, max_length=200)
