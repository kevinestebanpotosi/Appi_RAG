"""
Configuración centralizada del sistema RAG.
Carga variables de entorno y valida la configuración al inicio.
"""
import os
from pathlib import Path
from functools import lru_cache
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()


class Settings(BaseSettings):
    """
    Configuración del sistema RAG con Qdrant y Groq.
    Las variables de entorno tienen prioridad sobre los valores por defecto.
    """
    
    # Groq Configuration
    groq_api_key: str = ""
    
    # Qdrant Configuration
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str = ""
    qdrant_collection_name: str = "rag_pdf_collection"
    
    # Embeddings Configuration
    embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    
    # PDF Processing Configuration
    pdfs_dir: str = "./data/pdfs"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._validate_required()
    
    def _validate_required(self):
        """Valida que las variables requeridas estén presentes."""
        if not self.groq_api_key:
            raise ValueError(
                "❌ ERROR: GROQ_API_KEY no encontrada en variables de entorno.\n"
                "   Crea un archivo .env con tu API key de Groq."
            )
    
    @property
    def pdfs_path(self) -> Path:
        """Retorna la ruta absoluta al directorio de PDFs."""
        return Path(self.pdfs_dir).expanduser().absolute()
    
    @property
    def collection_exists(self) -> bool:
        """Indica si se usará Qdrant Cloud (API key configurada)."""
        return bool(self.qdrant_api_key) and not self.qdrant_url.startswith("http://localhost")


@lru_cache()
def get_settings() -> Settings:
    """
    Instancia cached de settings.
    Usa lru_cache para evitar recargar configuración múltiples veces.
    """
    return Settings()


# Instancia global para uso en la aplicación
settings = get_settings()