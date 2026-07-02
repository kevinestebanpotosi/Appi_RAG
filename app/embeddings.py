"""
Gestión de embeddings usando sentence-transformers.
Convierte texto a vectores para almacenamiento en Qdrant.
"""
from typing import List, Optional
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.embeddings import Embeddings
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class EmbeddingManager:
    """
    Gestiona el modelo de embeddings para el sistema RAG.
    
    Utiliza modelos pre-entrenados multilingües optimizados para español.
    El modelo por defecto (MiniLM) es rápido y eficiente en recursos.
    """
    
    def __init__(self, model_name: Optional[str] = None):
        """
        Inicializa el modelo de embeddings.
        
        Args:
            model_name: Nombre del modelo HF (usa config si no se especifica)
        """
        self.model_name = model_name or settings.embedding_model
        self._model: Optional[Embeddings] = None
    
    @property
    def model(self) -> Embeddings:
        """Carga lazy del modelo de embeddings."""
        if self._model is None:
            logger.info(f"📦 Cargando modelo de embeddings: {self.model_name}")
            self._model = HuggingFaceEmbeddings(
                model_name=self.model_name,
                model_kwargs={
                    "device": "cpu",  # Usar "cuda" si tienes GPU
                    #"normalize_embeddings": True,
                },
                encode_kwargs={
                    "normalize_embeddings": True,
                    "batch_size": 32,
                },
            )
            logger.info("✅ Modelo de embeddings cargado exitosamente")
        return self._model
    
    def embed_text(self, text: str) -> List[float]:
        """
        Convierte un texto a su representación vectorial.
        
        Args:
            text: Texto a convertir
            
        Returns:
            Vector como lista de floats normalizado
        """
        return self.model.embed_query(text)
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Convierte múltiples textos a vectores de forma eficiente.
        
        Args:
            texts: Lista de textos a convertir
            
        Returns:
            Lista de vectores normalizados
        """
        return self.model.embed_documents(texts)
    
    def get_embedding_dimension(self) -> int:
        """
        Retorna la dimensión de los vectores generados.
        Útil para configurar colecciones en Qdrant.
        """
        # MiniLM-L12-v2 produce vectores de 384 dimensiones
        sample = self.embed_text("dimension test")
        return len(sample)


# Instancia global del manager
embedding_manager = EmbeddingManager()


def get_embedding_dimension() -> int:
    """Helper para obtener la dimensión de embeddings."""
    return embedding_manager.get_embedding_dimension()