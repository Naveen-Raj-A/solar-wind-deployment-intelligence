from datetime import datetime

from pydantic import BaseModel, Field


class SiteBase(BaseModel):
    project_id: int

    site_name: str = Field(..., min_length=1)

    state: str = Field(..., min_length=1)

    latitude: float = Field(..., ge=-90, le=90)

    longitude: float = Field(..., ge=-180, le=180)


class SiteCreate(SiteBase):
    pass


class SiteUpdate(SiteBase):
    pass


class SiteResponse(SiteBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True