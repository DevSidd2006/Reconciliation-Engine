from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_all_mismatches():
    return {"message": "List of mismatches"}