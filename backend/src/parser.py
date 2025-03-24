from config import config
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from pymilvus import connections, utility
from langchain_community.document_loaders import PyPDFLoader

def load_documents(file_name):
    loader = PyPDFLoader(file_name)
    documents = loader.load()
    return documents

def split_documents(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=80,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter.split_documents(documents)

def calculate_chunk_ids(chunks):
    # Generate unique IDs for each chunk, e.g. "source:page:chunkIndex"
    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page")
        current_page_id = f"{source}:{page}"

        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        chunk_id = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id
        chunk.metadata["id"] = chunk_id

    return chunks

def clear_database(collection_name):

    # Connect to Milvus.
    connections.connect(host=config.MILVUS_HOST, port=config.MILVUS_PORT)
    # db.using_database(db_name)
    # Check if the collection exists, and drop it if it does.
    if utility.has_collection(collection_name):
        utility.drop_collection(collection_name)
        print(f"Collection '{collection_name}' dropped.")
    else:
        print(f"Collection '{collection_name}' does not exist.")