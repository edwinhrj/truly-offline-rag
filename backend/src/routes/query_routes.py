from fastapi import APIRouter, Body
from ..query.llm import llm

router = APIRouter()

@router.post("/ask")    
async def ask(question: str = Body(..., embed=True)):
    return str(llm(question))