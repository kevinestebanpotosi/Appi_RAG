"""
Cadena RAG completa: recuperación + generación de respuestas.
Integra Qdrant con Groq (Llama 3) para respuestas contextualizadas.
"""
from typing import List, Tuple
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_groq import ChatGroq
from langchain_core.documents import Document
from app.config import settings
from app.qdrant_store import qdrant_manager
import logging

logger = logging.getLogger(__name__)


class RAGChain:
    """
    Implementa el patrón RAG completo.
    
    Flujo:
    1. User Query → Embedding
    2. Búsqueda en Qdrant (documentos similares)
    3. Context + Query → Groq (Llama 3)
    4. Respuesta generada
    """
    
    def __init__(self, model_name: str = "llama-3.3-70b-versatile", temperature: float = 0.3):
        """
        Inicializa la cadena RAG.
        
        Args:
            model_name: Modelo de Groq a usar
            temperature: Temperatura de generación (0=preciso, 1=creativo)
        """
        self.temperature = temperature
        
        # Inicializar LLM
        logger.info(f"🤖 Inicializando Groq con modelo: {model_name}")
        self.llm = ChatGroq(
            api_key=settings.groq_api_key,
            model_name=model_name,
            temperature=temperature,
            max_tokens=1024,
        )
        
        # Definir el prompt del sistema
        self.system_prompt = """Eres un asistente IA profesional y amigable.
Tu objetivo es responder preguntas basándote ÚNICAMENTE en el contexto proporcionado.

INSTRUCCIONES:
1. Usa el CONTEXTO para responder, no inventes información.
2. Si la respuesta no está en el contexto, dilo claramente y sugiere reformular la pregunta.
3. Responde siempre en Español con un tono profesional pero accesible.
4. Si el contexto incluye enlaces o referencias, inclúyelos en tu respuesta.
5. Estructura respuestas largas con listas o párrafos cortos.

CONTEXTO RELEVANTE:
{context}

PREGUNTA DEL USUARIO: {question}"""
        
        # Crear el prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", "{question}"),
        ])
        
        # Construir la cadena
        self._build_chain()
        logger.info("✅ Cadena RAG inicializada")
    
    def _build_chain(self):
        """Construye la cadena RAG con retriever + prompt + llm."""
        
        # Función para formatear documentos
        def format_docs(docs: List[Document]) -> str:
            """Convierte documentos a texto formateado."""
            if not docs:
                return "No se encontró información relevante."
            
            formatted = []
            for i, doc in enumerate(docs, 1):
                source = doc.metadata.get("filename", "Desconocido")
                formatted.append(f"[{i}] {doc.page_content}\n   (Fuente: {source})")
            
            return "\n\n".join(formatted)
        
        # Crear la cadena con LCEL (LangChain Expression Language)
        self.chain = (
            {"context": qdrant_manager.vector_store.as_retriever(k=5) | format_docs, "question": RunnablePassthrough()}
            | self.prompt
            | self.llm
            | StrOutputParser()
        )
    
    async def invoke(self, query: str) -> Tuple[str, List[Document]]:
        """
        Ejecuta la cadena RAG de forma asíncrona.
        
        Args:
            query: Pregunta del usuario
            
        Returns:
            Tupla con (respuesta_generada, documentos_usados)
        """
        logger.info(f"🎯 Procesando query: {query[:50]}...")
        
        # Obtener documentos antes de invocar la cadena
        docs = qdrant_manager.search(query, k=5)
        
        # Generar respuesta
        response = self.chain.invoke(query)
        
        logger.info(f"✅ Respuesta generada ({len(response)} caracteres)")
        return response, docs
    
    def invoke_sync(self, query: str) -> Tuple[str, List[Document]]:
        """Versión síncrona de invoke."""
        logger.info(f"🎯 Procesando query (sync): {query[:50]}...")
        docs = qdrant_manager.search(query, k=5)
        response = self.chain.invoke(query)
        return response, docs


# Instancia global de la cadena RAG
rag_chain = RAGChain()