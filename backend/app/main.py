from fastapi import FastAPI

from app.api import (
    home,
    projects,
    sites,
    predictions,
    wind,
    deployment,
)

from app.database import Base, engine
from app.models import project


# --------------------------------------------------
# CREATE DATABASE TABLES
# --------------------------------------------------

Base.metadata.create_all(bind=engine)


# --------------------------------------------------
# CREATE FASTAPI APPLICATION
# --------------------------------------------------

app = FastAPI(
    title="Solar & Wind Deployment Intelligence API"
)


# --------------------------------------------------
# REGISTER API ROUTERS
# --------------------------------------------------

app.include_router(home.router)
app.include_router(projects.router)
app.include_router(sites.router)
app.include_router(predictions.router)
app.include_router(wind.router)
app.include_router(deployment.router)


# --------------------------------------------------
# ROOT ENDPOINT
# --------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "Welcome to Solar & Wind Deployment Intelligence Platform"
    }


# --------------------------------------------------
# HEALTH CHECK ENDPOINT
# --------------------------------------------------

@app.get("/health")
def health_check():
    return {
        "status": "Running"
    }


# --------------------------------------------------
# ABOUT ENDPOINT
# --------------------------------------------------

@app.get("/about")
def about():
    return {
        "project": "Solar & Wind Deployment Intelligence Platform"
    }