from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.project import Project
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
)

router = APIRouter(tags=["Projects"])


# ------------------------------------------------------------------
# Database Dependency
# ------------------------------------------------------------------

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ------------------------------------------------------------------
# Create Project
# ------------------------------------------------------------------

@router.post(
    "/projects",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
):

    existing = (
        db.query(Project)
        .filter(Project.project_name == project.project_name)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project with this name already exists.",
        )

    new_project = Project(**project.model_dump())

    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    return new_project


# ------------------------------------------------------------------
# Get All Projects
# ------------------------------------------------------------------

@router.get(
    "/projects",
    response_model=list[ProjectResponse],
)
def get_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):

    return (
        db.query(Project)
        .offset(skip)
        .limit(limit)
        .all()
    )


# ------------------------------------------------------------------
# Get Project By ID
# ------------------------------------------------------------------

@router.get(
    "/projects/{project_id}",
    response_model=ProjectResponse,
)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
):

    project = (
        db.query(Project)
        .filter(Project.id == project_id)
        .first()
    )

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found.",
        )

    return project


# ------------------------------------------------------------------
# Update Project
# ------------------------------------------------------------------

@router.put(
    "/projects/{project_id}",
    response_model=ProjectResponse,
)
def update_project(
    project_id: int,
    updated_project: ProjectUpdate,
    db: Session = Depends(get_db),
):

    project = (
        db.query(Project)
        .filter(Project.id == project_id)
        .first()
    )

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found.",
        )

    duplicate = (
        db.query(Project)
        .filter(
            Project.project_name == updated_project.project_name,
            Project.id != project_id,
        )
        .first()
    )

    if duplicate:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project with this name already exists.",
        )

    for key, value in updated_project.model_dump().items():
        setattr(project, key, value)

    db.commit()
    db.refresh(project)

    return project


# ------------------------------------------------------------------
# Delete Project
# ------------------------------------------------------------------

@router.delete(
    "/projects/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
):

    project = (
        db.query(Project)
        .filter(Project.id == project_id)
        .first()
    )

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found.",
        )

    db.delete(project)
    db.commit()