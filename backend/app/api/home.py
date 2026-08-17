from fastapi import APIRouter


# Create router for home-related endpoints
router = APIRouter()


# Root endpoint
@router.get("/")
def root():
    return {
        "message": "Welcome to the Solar & Wind Deployment Intelligence Platform"
    }