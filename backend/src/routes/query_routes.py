from fastapi import APIRouter

router = APIRouter()

@router.post("/ask")
async def upload_pdf():
    pass