from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.project import Project
from app.models.sites import Site

from app.schemas.sites import (
    SiteCreate,
    SiteResponse,
    SiteUpdate,
)

router = APIRouter(tags=["Sites"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post(
    "/sites",
    response_model=SiteResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_site(
    site: SiteCreate,
    db: Session = Depends(get_db),
):

    project = (
        db.query(Project)
        .filter(Project.id == site.project_id)
        .first()
    )

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found.",
        )

    new_site = Site(**site.model_dump())

    db.add(new_site)
    db.commit()
    db.refresh(new_site)

    return new_site


@router.get(
    "/sites",
    response_model=list[SiteResponse],
)
def get_sites(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):

    return (
        db.query(Site)
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get(
    "/sites/{site_id}",
    response_model=SiteResponse,
)
def get_site(
    site_id: int,
    db: Session = Depends(get_db),
):

    site = (
        db.query(Site)
        .filter(Site.id == site_id)
        .first()
    )

    if site is None:
        raise HTTPException(
            status_code=404,
            detail="Site not found.",
        )

    return site


@router.put(
    "/sites/{site_id}",
    response_model=SiteResponse,
)
def update_site(
    site_id: int,
    updated_site: SiteUpdate,
    db: Session = Depends(get_db),
):

    site = (
        db.query(Site)
        .filter(Site.id == site_id)
        .first()
    )

    if site is None:
        raise HTTPException(
            status_code=404,
            detail="Site not found.",
        )

    project = (
        db.query(Project)
        .filter(Project.id == updated_site.project_id)
        .first()
    )

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found.",
        )

    for key, value in updated_site.model_dump().items():
        setattr(site, key, value)

    db.commit()
    db.refresh(site)

    return site


@router.delete(
    "/sites/{site_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_site(
    site_id: int,
    db: Session = Depends(get_db),
):

    site = (
        db.query(Site)
        .filter(Site.id == site_id)
        .first()
    )

    if site is None:
        raise HTTPException(
            status_code=404,
            detail="Site not found.",
        )

    db.delete(site)
    db.commit()