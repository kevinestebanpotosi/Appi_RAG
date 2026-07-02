"""
Gestión de la base de datos vectorial Qdrant.
Implementa operaciones CRUD para el sistema RAG.
"""
from typing import List, Optional, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.models import (
    VectorParams,
    Distance,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)
from langchain_core.documents import Document
from langchain_qdrant import QdrantVectorStore
from app.config import settings
from app.embeddings import embedding_manager
import logging

logger = logging.getLogger(__name__)


# Dimensión fija para el modelo por defecto (MiniLM-L12-v2)
# Si usas otro modelo, ajusta este valor
EMBEDDING_DIMENSIONS = {
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2": 384,
    "sentence-transformers/LaBSE": 768,
    "intfloat/multilingual-e5-large": 1024,
}

# Dimensión por defecto para cualquier modelo HuggingFace
DEFAULT_EMBEDDING_DIMENSION = 384


class QdrantStoreManager:
    """
    Gestiona la conexión y operaciones con Qdrant.
    
    Solo necesita QDRANT_URL y QDRANT_API_KEY en el .env.
    La colección se crea automáticamente si no existe.
    """
    
    def __init__(self):
        """Inicializa el cliente Qdrant."""
        # Soporta tanto Qdrant Cloud como local
        self.client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key if settings.qdrant_api_key else None,
        )
        self.collection_name = settings.qdrant_collection_name
        self._vector_store: Optional[QdrantVectorStore] = None
        self._collection_created = False
    
    def _get_embedding_dimension(self) -> int:
        """Obtiene la dimensión del modelo de embeddings."""
        model_name = settings.embedding_model
        
        # Buscar en el diccionario conocido
        if model_name in EMBEDDING_DIMENSIONS:
            return EMBEDDING_DIMENSIONS[model_name]
        
        # Si no lo conocemos, intentamos obtener la dimensión real
        # Esto requiere que el modelo esté descargado
        try:
            from app.embeddings import get_embedding_dimension
            return get_embedding_dimension()
        except Exception:
            logger.warning(
                f"⚠️ No se pudo detectar la dimensión del modelo '{model_name}'. "
                f"Usando valor por defecto: {DEFAULT_EMBEDDING_DIMENSION}"
            )
            return DEFAULT_EMBEDDING_DIMENSION
    
    def _ensure_collection_exists(self):
        """
        Crea la colección en Qdrant si no existe.
        Solo necesita URL y API key configuradas.
        """
        if self._collection_created:
            return
        
        try:
            logger.info(f"🗄️ Conectando a Qdrant: {settings.qdrant_url}")
            logger.info(f"📁 Verificando colección: {self.collection_name}")
            
            # Verificar si la colección existe
            try:
                collections = self.client.get_collections().collections
                collection_names = [c.name for c in collections]
                collection_exists = self.collection_name in collection_names
            except Exception:
                collection_exists = False
            
            if not collection_exists:
                dimension = self._get_embedding_dimension()
                logger.info(f"📐 Creando colección '{self.collection_name}' (dimensión: {dimension})")
                
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=dimension,
                        distance=Distance.COSINE,
                    ),
                )
                logger.info("✅ Colección creada exitosamente")
            else:
                logger.info(f"ℹ️ Colección '{self.collection_name}' ya existe")
            
            self._collection_created = True
            
        except Exception as e:
            logger.error(f"❌ Error conectando a Qdrant: {e}")
            raise ConnectionError(
                f"No se pudo conectar a Qdrant en {settings.qdrant_url}. "
                "Verifica QDRANT_URL y QDRANT_API_KEY en el archivo .env"
            )
    
    @property
    def vector_store(self) -> QdrantVectorStore:
        """Obtiene el vector store de LangChain."""
        if self._vector_store is None:
            # Asegurar que la colección existe antes de crear el store
            self._ensure_collection_exists()
            
            self._vector_store = QdrantVectorStore(
                client=self.client,
                collection_name=self.collection_name,
                embedding=embedding_manager.model,
                content_payload_key="page_content",
                metadata_payload_key="metadata",
            )
            logger.info("✅ Vector Store inicializado")
        return self._vector_store
    
    def add_documents(self, documents: List[Document], batch_size: int = 100):
        """
        Añade documentos a la colección.
        
        Args:
            documents: Lista de Documents de LangChain
            batch_size: Tamaño del lote para inserción
        """
        if not documents:
            logger.warning("⚠️ No hay documentos para añadir")
            return
        
        logger.info(f"📤 Añadiendo {len(documents)} chunks a Qdrant")
        
        # Asegurar que la colección existe
        self._ensure_collection_exists()
        
        self.vector_store.add_documents(documents, batch_size=batch_size)
        logger.info("✅ Documentos almacenados exitosamente")
    
    def search(
        self,
        query: str,
        k: int = 5,
        filter_source: Optional[str] = None,
    ) -> List[Document]:
        """
        Busca documentos similares a la query.
        
        Args:
            query: Texto de búsqueda
            k: Número de resultados a retornar
            filter_source: Filtrar por archivo fuente (opcional)
            
        Returns:
            Lista de Documents ordenados por similitud
        """
        logger.info(f"🔍 Buscando: '{query[:50]}...' (k={k})")
        
        # Asegurar que la colección existe
        self._ensure_collection_exists()
        
        # Construir filtro si se especifica fuente
        search_kwargs = {"k": k}
        if filter_source:
            search_kwargs["filter"] = Filter(
                must=[
                    FieldCondition(
                        key="metadata.source",
                        match=MatchValue(value=filter_source),
                    )
                ]
            )
        
        results = self.vector_store.similarity_search(query, **search_kwargs)
        logger.info(f"✅ Encontrados {len(results)} documentos relevantes")
        return results
    
    def delete_by_source(self, source: str) -> int:
        """
        Elimina todos los documentos de una fuente específica.
        
        Args:
            source: Ruta del archivo fuente
            
        Returns:
            Número de puntos eliminados
        """
        logger.info(f"🗑️ Eliminando documentos de: {source}")
        
        try:
            self._ensure_collection_exists()
            
            # Buscar puntos de esta fuente
            points = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="metadata.source",
                            match=MatchValue(value=source),
                        )
                    ]
                ),
                limit=10000,
            )
            
            if points[0]:
                point_ids = [p.id for p in points[0]]
                self.client.delete(
                    collection_name=self.collection_name,
                    points_selector=point_ids,
                )
                logger.info(f"✅ Eliminados {len(point_ids)} puntos")
                return len(point_ids)
            
        except Exception as e:
            logger.error(f"❌ Error eliminando documentos: {e}")
        return 0
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Obtiene información sobre la colección."""
        try:
            self._ensure_collection_exists()
            
            info = self.client.get_collection(self.collection_name)
            count = self.client.count(
                self.collection_name,
                exact=True,
            ).count
            return {
                "name": self.collection_name,
                "status": str(info.status),
                "vectors_count": count,
                "dimension": info.config.params.vectors.size,
                "distance": str(info.config.params.vectors.distance),
            }
        except Exception as e:
            logger.error(f"❌ Error obteniendo info: {e}")
            return {}
    
    def clear_collection(self):
        """Elimina todos los puntos de la colección."""
        try:
            self._ensure_collection_exists()
            logger.warning("⚠️ Limpiando colección completa...")
            self.client.delete_collection(self.collection_name)
            self._vector_store = None
            self._collection_created = False
            logger.info("✅ Colección eliminada")
        except Exception as e:
            logger.error(f"❌ Error limpiando colección: {e}")
    
    def recreate_collection(self):
        """
        Elimina y vuelve a crear la colección.
        Útil para empezar desde cero.
        """
        logger.info("🔄 Recreando colección...")
        self.clear_collection()
        self._ensure_collection_exists()
        logger.info("✅ Colección recreada")


# Instancia global del manager
qdrant_manager = QdrantStoreManager()