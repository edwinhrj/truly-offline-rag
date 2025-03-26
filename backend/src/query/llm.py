from langchain.prompts import ChatPromptTemplate
from langchain.llms import HuggingFaceHub
from ..pdf.embedding import get_embedding_function
from langchain_milvus import Milvus
from config import config


PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question concisely based on the above context: {question}
"""

def query_rag(query_text: str, company: str):
    embedding_function = get_embedding_function()
    db = Milvus(
        embedding_function=embedding_function,
        collection_name=company,
        connection_args={"uri":config.MILVUS_URI},
        consistency_level="Strong",
        auto_id=False, 
        enable_dynamic_field=True,
    )

    # Search the DB.
    results = db.similarity_search_with_score(query_text, config.TOP_K)

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)

    llm = HuggingFaceHub(
        repo_id="Qwen/Qwen2.5-Coder-32B", 
        model_kwargs={"temperature": 0.7, "max_new_tokens": 256},
        huggingfacehub_api_token="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"
    )
    response_text = llm(prompt)

    sources = [doc.metadata.get("id", None) for doc, _score in results]
    formatted_response = f"Response: {response_text}\nSources: {sources}"
    print(formatted_response)
    return response_text

