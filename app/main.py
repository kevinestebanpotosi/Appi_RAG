"""
FastAPI - API REST para el Sistema RAG.
Endpoints para chat, gestión de PDFs e información del sistema.
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from pathlib import Path
import logging

# Importar módulos del sistema
from app.config import settings, get_settings
from app.pdf_processor import pdf_processor
from app.qdrant_store import qdrant_manager
from app.rag_chain import rag_chain

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# ============================================
# INICIALIZACIÓN DE LA APP
# ============================================

app = FastAPI(
    title="RAG System API",
    description="Sistema RAG con Qdrant, Groq y procesamiento de PDFs",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar orígenes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# MODELOS Pydantic
# ============================================

class ChatRequest(BaseModel):
    query: str
    k: Optional[int] = 5

class ChatResponse(BaseModel):
    answer: str
    sources_used: int
    sources: List[dict]

class IngestRequest(BaseModel):
    pdf_path: Optional[str] = None  # Path específico o None para usar directorio default

class IngestResponse(BaseModel):
    status: str
    chunks_created: int
    files_processed: List[str]

class CollectionInfoResponse(BaseModel):
    status: str
    info: dict

# ============================================
# ENDPOINTS
# ============================================

@app.get("/", tags=["Info"])
async def root():
    """Endpoint raíz con información del API."""
    return {
        "name": "RAG System API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Verifica el estado del sistema."""
    try:
        info = qdrant_manager.get_collection_info()
        return {
            "status": "healthy",
            "qdrant": "connected" if info else "disconnected",
            "collection": info,
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}


@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat_endpoint(request: ChatRequest):
    """
    Endpoint principal de chat.
    
    Recibe una pregunta, busca contexto en Qdrant y genera respuesta con Groq.
    """
    if not request.query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La consulta no puede estar vacía",
        )
    
    logger.info(f"💬 Chat request: {request.query[:50]}...")
    
    try:
        answer, docs = rag_chain.invoke(request.query)
        
        # Formatear fuentes
        sources = [
            {
                "filename": doc.metadata.get("filename", "Desconocido"),
                "chunk_id": doc.metadata.get("chunk_id", 0),
                "relevance": "high",  # Podría calculardistance
            }
            for doc in docs
        ]
        
        return ChatResponse(
            answer=answer,
            sources_used=len(docs),
            sources=sources,
        )
    except Exception as e:
        logger.error(f"❌ Error en chat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error procesando la consulta: {str(e)}",
        )


@app.post("/ingest", response_model=IngestResponse, tags=["PDFs"])
async def ingest_pdfs(request: IngestRequest, background_tasks: BackgroundTasks):
    """
    Ingiere PDFs a Qdrant.
    
    - Sin body: Procesa todos los PDFs en el directorio configurado
    - Con pdf_path: Procesa un PDF específico
    """
    logger.info(f"📤 Ingesta de PDFs iniciada")
    
    try:
        if request.pdf_path:
            # Procesar PDF específico
            pdf_path = Path(request.pdf_path)
            if not pdf_path.exists():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Archivo no encontrado: {pdf_path}",
                )
            
            chunks = pdf_processor.process_pdf(pdf_path)
            if chunks:
                qdrant_manager.add_documents(chunks)
                
                return IngestResponse(
                    status="success",
                    chunks_created=len(chunks),
                    files_processed=[pdf_path.name],
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No se pudo extraer texto del PDF",
                )
        else:
            # Procesar directorio completo
            pdfs_dir = settings.pdfs_path
            if not pdfs_dir.exists():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Directorio de PDFs no encontrado: {pdfs_dir}",
                )
            
            chunks = pdf_processor.process_directory(pdfs_dir)
            if not chunks:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"No se encontraron PDFs en {pdfs_dir}",
                )
            
            qdrant_manager.add_documents(chunks)
            
            # Obtener nombres de archivos procesados
            pdf_files = [f.name for f in pdfs_dir.glob("*.pdf")]
            
            return IngestResponse(
                status="success",
                chunks_created=len(chunks),
                files_processed=pdf_files,
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error en ingesta: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error procesando PDFs: {str(e)}",
        )


@app.delete("/ingest", tags=["PDFs"])
async def clear_vector_store():
    """
    Elimina todos los documentos de la colección.
    """
    try:
        qdrant_manager.clear_collection()
        return {"status": "success", "message": "Colección limpiada"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@app.get("/collection", response_model=CollectionInfoResponse, tags=["Admin"])
async def get_collection_info():
    """Obtiene información sobre la colección de Qdrant."""
    try:
        info = qdrant_manager.get_collection_info()
        return CollectionInfoResponse(status="success", info=info)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# ============================================
# PUNTO DE ENTRADA
# ============================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
    )