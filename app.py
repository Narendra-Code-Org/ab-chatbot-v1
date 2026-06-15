import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, UploadFile, File, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from werkzeug.utils import secure_filename
import anyio

from chatbot.ingest_default import ingest_default_docs
from chatbot.ingest_uploaded import ingest_uploaded_doc
from chatbot.chain import ask_question

# Setup logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ab-chatbot")

UPLOAD_FOLDER = 'data/uploaded_pdfs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ingest default documents on startup in a worker thread
    logger.info("Starting default document ingestion...")
    try:
        await anyio.to_thread.run_sync(ingest_default_docs)
        logger.info("Default document ingestion completed successfully.")
    except Exception as e:
        logger.error(f"Error during default ingestion: {e}", exc_info=True)
    yield

app = FastAPI(
    title="Autonomous Building RAG Chatbot",
    description="A FastAPI production-ready RAG chatbot utilizing AWS Bedrock and Qdrant Cloud.",
    version="1.0.0",
    lifespan=lifespan
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

class AskRequest(BaseModel):
    question: str

@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse(request, "index.html")

@app.post("/ask")
async def ask(payload: AskRequest):
    question = payload.question.strip()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No question provided"
        )
    
    try:
        # Run synchronous blocking qa chain in worker thread to prevent event loop lag
        response = await anyio.to_thread.run_sync(ask_question, question)
        return response
    except Exception as e:
        logger.error(f"Error during ask_question: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No selected file"
        )
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Allowed file types are .pdf"
        )
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    
    try:
        # Write incoming file stream using anyio async file writing
        async with await anyio.open_file(filepath, "wb") as buffer:
            while chunk := await file.read(65536):
                await buffer.write(chunk)
                
        # Ingest uploaded PDF in worker thread
        await anyio.to_thread.run_sync(ingest_uploaded_doc, filepath)
        return {"message": f"Successfully processed {filename}"}
    except Exception as e:
        logger.error(f"Error processing file {filename}: {e}", exc_info=True)
        # Clean up files on ingestion failures
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except Exception as cleanup_err:
                logger.error(f"Failed to delete corrupted file {filepath}: {cleanup_err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(e)}"
        )

if __name__ == '__main__':
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host='0.0.0.0', port=port, reload=False)
