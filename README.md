# RAG System - Sistema de Recuperación Aumentada con Generación 🤖

Sistema RAG completo que permite ingestar documentos PDF y conversar con ellos usando IA. Solo necesitas proporcionar las credenciales de Qdrant y Groq.

## 🚀 Inicio Rápido (3 Pasos)

### 1. Configura las credenciales

Edita el archivo `.env` con tus API keys:

```env
# Groq (para generación de respuestas)
GROQ_API_KEY=gsk_tu_api_key

# Qdrant (para almacenamiento de vectores)
QDRANT_URL=https://tu-cluster.qdrant.io:6333
QDRANT_API_KEY=tu_api_key_de_qdrant
```

**Obtener claves:**
- Groq: [console.groq.com](https://console.groq.com) (gratuito)
- Qdrant: [cloud.qdrant.io](https://cloud.qdrant.io) (free tier disponible)

### 2. Coloca tus documentos

```bash
mkdir -p data/pdfs
# Copia tus archivos PDF o TXT en data/pdfs/
```

### 3. Ejecuta

```bash
# Instalar dependencias
uv venv --python 3.11
.venv\Scripts\activate
uv pip install -r requirements.txt

# Iniciar interfaz de chat
chainlit run chainlit.py
```

¡Listo! El sistema creará automáticamente la colección en Qdrant la primera vez que ingieras documentos.

**Uso:**
1. Abre `http://localhost:8000` en tu navegador
2. Haz clic en "📤 Ingestar PDFs" para procesar tus documentos
3. ¡Empieza a hacer preguntas sobre el contenido!

## 📦 Tecnologías

| Componente | Tecnología |
|------------|------------|
| LLM | Groq (Llama 3) |
| Base Vectorial | Qdrant |
| Embeddings | Sentence-Transformers |
| Framework | FastAPI |
| Interfaz | Chainlit |

## 📁 Estructura

```
rag-system/
├── app/
│   ├── main.py              # API REST
│   ├── qdrant_store.py      # Gestión de Qdrant (crea colección automáticamente)
│   ├── pdf_processor.py     # Extracción de PDFs
│   ├── rag_chain.py         # Cadena RAG
│   └── embeddings.py        # Embeddings
├── chainlit.py              # Interfaz web
├── data/pdfs/               # Tus PDFs aquí
├── .env                     # Tus credenciales
└── requirements.txt
```

## 🐳 Docker

```bash
cp .env.example .env
# Edita .env con tus claves
docker-compose up --build
```

La interfaz estará en `http://localhost:8000` y la API en `http://localhost:8001/docs`.