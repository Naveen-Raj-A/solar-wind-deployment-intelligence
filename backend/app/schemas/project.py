from datetime import datetime

from pydantic import BaseModel, Field


# ------------------------------------------------------------------
# Base Schema
# ------------------------------------------------------------------

class ProjectBase(BaseModel):
    project_name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1)
    state: str = Field(..., min_length=1, max_length=100)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


# ------------------------------------------------------------------
# Create Schema
# ------------------------------------------------------------------

class ProjectCreate(ProjectBase):
    pass


# ------------------------------------------------------------------
# Update Schema
# ------------------------------------------------------------------

class ProjectUpdate(ProjectBase):
    pass


# ------------------------------------------------------------------
# Response Schema
# ------------------------------------------------------------------

class ProjectResponse(ProjectBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True