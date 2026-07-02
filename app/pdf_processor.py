"""
Procesamiento de PDFs: extracción y fragmentación de texto.
Implementa chunking inteligente con solapamiento para mejorar recuperación RAG.
"""
import os
from pathlib import Path
from typing import List, Tuple, Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from pypdf import PdfReader
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class PDFProcessor:
    """
    Procesa archivos PDF extrayendo texto y fragmentándolo en chunks.
    
    Características:
    - Extracción de texto con pypdf
    - Chunking configurable con solapamiento
    - Preservación de metadatos del documento
    """
    
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        """
        Inicializa el procesador.
        
        Args:
            chunk_size: Tamaño máximo de cada fragmento
            chunk_overlap: Número de caracteres superpuestos entre chunks
        """
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap
        
        # Configuración del splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", ". ", ", ", " ", ""],
            length_function=len,
            is_separator_regex=False,
        )
        logger.info(
            f"📄 PDF Processor inicializado: "
            f"chunk_size={self.chunk_size}, overlap={self.chunk_overlap}"
        )
    
    def extract_text_from_pdf(self, pdf_path: Path) -> Tuple[str, dict]:
        """
        Extrae texto y metadatos de un archivo PDF.
        
        Args:
            pdf_path: Ruta al archivo PDF
            
        Returns:
            Tupla con (texto_extraído, metadatos)
            
        Raises:
            FileNotFoundError: Si el archivo no existe
            Exception: Si hay error al procesar el PDF
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {pdf_path}")
        
        logger.info(f"📖 Extrayendo texto de: {pdf_path.name}")
        
        reader = PdfReader(str(pdf_path))
        text = ""
        
        # Extraer texto de cada página
        for i, page in enumerate(reader.pages):
            try:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"
            except Exception as e:
                logger.warning(f"Error en página {i+1} de {pdf_path.name}: {e}")
        
        # Metadatos del documento
        metadata = {
            "source": str(pdf_path.absolute()),
            "filename": pdf_path.name,
            "num_pages": len(reader.pages),
            "extracted_at": str(Path().absolute()),
        }
        
        logger.info(f"✅ Extraído {len(text)} caracteres de {pdf_path.name}")
        return text, metadata
    
    def process_pdf(self, pdf_path: Path) -> List[Document]:
        """
        Procesa un PDF completo: extrae texto y fragmenta en chunks.
        
        Args:
            pdf_path: Ruta al archivo PDF
            
        Returns:
            Lista de Documents fragmentados con metadatos
        """
        text, metadata = self.extract_text_from_pdf(pdf_path)
        
        if not text.strip():
            logger.warning(f"⚠️ No se提取 texto de {pdf_path.name}")
            return []
        
        # Crear documento inicial
        doc = Document(page_content=text, metadata=metadata)
        
        # Fragmentar en chunks
        chunks = self.text_splitter.split_documents([doc])
        
        # Añadir metadatos adicionales a cada chunk
        for i, chunk in enumerate(chunks):
            chunk.metadata["chunk_id"] = i
            chunk.metadata["chunk_total"] = len(chunks)
        
        logger.info(f"📝 Generado {len(chunks)} chunks de {pdf_path.name}")
        return chunks
    
    def process_directory(self, directory: Path = None) -> List[Document]:
        """
        Procesa todos los PDFs y TXT en un directorio.
        
        Args:
            directory: Directorio a explorar (usa pdfs_dir del config si no se especifica)
            
        Returns:
            Lista con todos los chunks de todos los archivos
        """
        dir_path = Path(directory) if directory else settings.pdfs_path
        
        if not dir_path.exists():
            logger.warning(f"📁 Directorio no existe: {dir_path}")
            dir_path.mkdir(parents=True, exist_ok=True)
            return []
        
        all_chunks = []
        # Procesar PDFs y archivos TXT
        files = list(dir_path.glob("*.pdf")) + list(dir_path.glob("*.txt"))
        
        if not files:
            logger.info(f"📭 No se encontraron archivos en {dir_path}")
            return []
        
        logger.info(f"📚 Procesando {len(files)} archivos en {dir_path}")
        
        for file_path in files:
            try:
                if file_path.suffix.lower() == '.pdf':
                    chunks = self.process_pdf(file_path)
                elif file_path.suffix.lower() == '.txt':
                    chunks = self.process_txt(file_path)
                else:
                    continue
                all_chunks.extend(chunks)
            except Exception as e:
                logger.error(f"❌ Error procesando {file_path.name}: {e}")
        
        logger.info(f"✅ Total: {len(all_chunks)} chunks de {len(files)} archivos")
        return all_chunks
    
    def process_txt(self, txt_path: Path) -> List[Document]:
        """
        Procesa un archivo TXT: lee texto y fragmenta en chunks.
        
        Args:
            txt_path: Ruta al archivo TXT
            
        Returns:
            Lista de Documents fragmentados con metadatos
        """
        if not txt_path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {txt_path}")
        
        logger.info(f"📄 Procesando TXT: {txt_path.name}")
        
        # Leer archivo
        text = txt_path.read_text(encoding='utf-8')
        
        if not text.strip():
            logger.warning(f"⚠️ Archivo vacío: {txt_path.name}")
            return []
        
        # Metadatos del documento
        metadata = {
            "source": str(txt_path.absolute()),
            "filename": txt_path.name,
            "extracted_at": str(Path().absolute()),
        }
        
        # Crear documento inicial
        doc = Document(page_content=text, metadata=metadata)
        
        # Fragmentar en chunks
        chunks = self.text_splitter.split_documents([doc])
        
        # Añadir metadatos adicionales a cada chunk
        for i, chunk in enumerate(chunks):
            chunk.metadata["chunk_id"] = i
            chunk.metadata["chunk_total"] = len(chunks)
        
        logger.info(f"📝 Generado {len(chunks)} chunks de {txt_path.name}")
        return chunks


# Instancia global del procesador
pdf_processor = PDFProcessor()