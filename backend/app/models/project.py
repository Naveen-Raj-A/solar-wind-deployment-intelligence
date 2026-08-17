from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String

from app.database import Base


# Project database model
class Project(Base):
    __tablename__ = "projects"

    # Unique ID for each project
    id = Column(Integer, primary_key=True, index=True)

    # Name of the solar or wind project
    project_name = Column(String, nullable=False)

    # Description of the project
    description = Column(String, nullable=False)

    # State where the project is located
    state = Column(String, nullable=False)

    # Geographical coordinates
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    # Date and time when the project was created
    created_at = Column(DateTime, default=datetime.utcnow)