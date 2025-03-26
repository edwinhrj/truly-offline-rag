from fastapi import APIRouter, Body
from ..query.llm import llm
from ..query.retrieve import retrieve_similar_sentences

router = APIRouter()

@router.post("/ask")    
async def ask(query: str = Body(..., embed=True)):

    template = """You are a helpful assistant who answers questions using only the provided context.
    If you don't know the answer, simply state that you don't know.

    {context}

    Question: {question}"""

    rows = retrieve_similar_sentences(query)
    stream = llm.create_chat_completion(
        messages = [
        {"role": "user", "content": template.format(
            context = "\n\n".join([sentence[0] for sentence in rows]),
            question = query      
        )}
        ],
        stream=True
    )

    output = ""
    for token in stream:
        delta = token["choices"][0].get("delta", {})
        content = delta.get("content", "")
        output += content
    
    return output



    