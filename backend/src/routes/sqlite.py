from fastapi import APIRouter, File, UploadFile, HTTPException, Header
import tempfile
import os
import shutil
from ..pdf.parse import load_documents, calculate_chunk_ids, split_documents
from ..pdf.store import add_to_sqlite

router = APIRouter()

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    # save uploaded file to a temporary file first, before loading it and passing it to backend for manipulation and embedding
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="File must be a PDF")
    try:
        # use temporary file for upload, in case user cuts off app halfway during upload -> corrupted file
        original_filename = file.filename
        temp_file_name = os.path.join(tempfile.gettempdir(), original_filename)
        with open(temp_file_name, "wb") as tmp:
            shutil.copyfileobj(file.file, tmp)

        print(f"{temp_file_name}")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to upload file")
    finally:
        file.file.close()

    # start loading, parsing, chunking, embedding and storing into sqlite
    try:
        add_to_sqlite(calculate_chunk_ids(split_documents(load_documents(temp_file_name))))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to upload file")
    os.remove(temp_file_name)