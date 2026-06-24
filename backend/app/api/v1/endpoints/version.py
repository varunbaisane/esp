from fastapi import APIRouter

router = APIRouter()

@router.get("/version")
def get_version():
    return {
        "name": "Engineering Support Escalation Platform",
        "version": "1.0.0"
    }
