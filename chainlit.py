"""
Chainlit - Interfaz de Chat Amigable
=====================================
Interfaz web conversacional para el sistema RAG.
Ejecutar con: chainlit run chainlit.py -w
"""
import chainlit as cl
from app.rag_chain import rag_chain
from app.qdrant_store import qdrant_manager
from app.pdf_processor import pdf_processor
from app.config import settings
# Removed unused import
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@cl.on_chat_start
async def start_chat():
    """Inicializa el chat cuando el usuario comienza una nueva sesión."""
    # Verificar estado del sistema
    try:
        info = qdrant_manager.get_collection_info()
        docs_count = info.get("vectors_count", 0)
        status_msg = f"Sistema listo con {docs_count} documentos ingreados."
    except Exception as e:
        status_msg = "Sistema iniciado (Qdrant no conectado)"
        logger.warning(f"Qdrant no disponible: {e}")
    
    # Mensaje de bienvenida
    welcome_msg = f"""¡Hola! 👋 Soy tu asistente RAG.

{status_msg}

**¿Qué puedo hacer?**
- 📚 Responder preguntas sobre tus documentos PDF
- 🔍 Buscar información específica en el contenido
- 📋 Extraer datos relevantes de tus archivos

**Para empezar:**
1. Coloca tus PDFs en: `{settings.pdfs_path}`
2. Haz clic en "Ingestar PDFs" abajo
3. ¡Empieza a hacer preguntas!

Escribe tu pregunta cuando estés listo. 😊"""

    await cl.Message(content=welcome_msg).send()

    # Añadir botón para ingestar PDFs
    actions = [
        cl.Action(
            name="ingest",
            value="ingest_pdfs",
            label="📤 Ingestar PDFs",
            description="Procesa los PDFs en la carpeta data/pdfs",
            payload={"action": "ingest_pdfs"}
        )
    ]
    await cl.Message(content="¿Deseas ingestar los PDFs ahora?", actions=actions).send()


@cl.action_callback("ingest")
async def on_ingest(action):
    """Procesa los PDFs cuando el usuario hace clic en el botón."""
    # Remover el botón
    await action.remove()
    
    msg = cl.Message(content="📤 Procesando PDFs...")
    await msg.send()

    try:
        chunks = pdf_processor.process_directory(settings.pdfs_path)
        if chunks:
            qdrant_manager.add_documents(chunks)
            unique_files = len(set(c.metadata.get("filename") for c in chunks))
            msg.content = f"✅ ¡Listo! Se procesaron {len(chunks)} fragmentos de {unique_files} archivos."
        else:
            msg.content = "⚠️ No se encontraron PDFs para procesar. Colócalos en la carpeta `data/pdfs`."
        await msg.update()
        
        # Preguntar si quiere seguir chatting
        await cl.Message(content="¿Tienes alguna pregunta sobre tus documentos?").send()
        
    except Exception as e:
        msg.content = f"❌ Error: {str(e)}"
        await msg.update()


@cl.on_message
async def handle_message(message: cl.Message):
    """Procesa cada mensaje del usuario y genera una respuesta."""
    user_query = message.content
    
    if not user_query.strip():
        await cl.Message(content="Por favor, escribe una pregunta.").send()
        return

    # Mostrar indicador de escritura
    msg = cl.Message(content="🔍 Buscando información relevante...")
    await msg.send()

    try:
        # Ejecutar cadena RAG
        answer, docs = rag_chain.invoke_sync(user_query)

        # Formatear fuentes
        sources = []
        seen_files = set()
        for doc in docs:
            filename = doc.metadata.get("filename", "Desconocido")
            if filename not in seen_files:
                sources.append(f"📄 {filename}")
                seen_files.add(filename)

        # Construir respuesta
        if sources:
            sources_text = "\n".join(sources)
            full_answer = f"{answer}\n\n**Fuentes consultadas:**\n{sources}"
        else:
            full_answer = answer + "\n\n⚠️ No se encontraron documentos relevantes."

        msg.content = full_answer
        await msg.update()

    except Exception as e:
        logger.error(f"Error: {e}")
        await cl.Message(content=f"❌ Error: {str(e)}").send()