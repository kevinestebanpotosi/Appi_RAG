# Appi RAG - Sistema de Recuperación Aumentada con Generación 🤖

Sistema completo RAG (Retrieval-Augmented Generation) que permite ingestar documentos PDF/TXT y conversar con ellos usando IA de última generación. El sistema utiliza Groq para generación de respuestas rápidas y Qdrant para almacenamiento vectorial eficiente.

## ✨ Características Principales

- **🎯 Búsqueda Semántica Avanzada**: Encuentra información relevante en tus documentos usando embeddings multilingües
- **🚀 Respuestas Ultra Rápidas**: Utiliza Groq con modelos Llama 3.3 70B para generación de respuestas en tiempo real
- **📊 Almacenamiento Vectorial Profesional**: Qdrant Cloud para manejo eficiente de vectores con búsqueda por similitud
- **💬 Interfaz Web Amigable**: Chainlit para una experiencia de chat intuitiva y atractiva
- **🔧 Configuración Automática**: Crea colecciones automáticamente en Qdrant al primer uso
- **🌐 Multilingüe**: Embeddings optimizados para español y otros idiomas
- **📄 Soporte Múltiple**: Procesa PDFs y archivos de texto plano

## 🚀 Empezando en 3 Pasos

### 1. Configurar Credenciales

Copia el archivo de ejemplo y configura tus API keys:

```bash
# Copiar plantilla de configuración
cp .env.example .env

# Editar .env con tus credenciales
```

**Credenciales necesarias:**
- **Groq API**: Gratuita en [console.groq.com](https://console.groq.com)
- **Qdrant Cloud**: Free tier disponible en [cloud.qdrant.io](https://cloud.qdrant.io)

### 2. Preparar Documentos

Coloca tus documentos en la carpeta designada:

```bash
# Crear estructura de directorios (automática al ejecutar)
mkdir -p data/pdfs

# Copiar tus archivos PDF o TXT
# Los archivos en data/pdfs/ se ignoran en Git por seguridad
```

### 3. Ejecutar la Aplicación

#### Opción A: Usando UV (Recomendado)

```bash
# Crear entorno virtual e instalar dependencias
uv venv --python 3.11
source .venv/bin/activate  # En Linux/Mac
# En Windows: .venv\Scripts\activate

# Instalar dependencias
uv pip install -r requirements.txt

# Iniciar interfaz web
chainlit run chainlit.py
```

#### Opción B: Usando Docker

```bash
# Construir y ejecutar con Docker Compose
docker-compose up --build

# La interfaz estará disponible en http://localhost:8000
```

## 🎯 Uso del Sistema

1. **Accede a la interfaz**: Abre `http://localhost:8000` en tu navegador
2. **Ingesta de documentos**: Haz clic en "📤 Ingestar PDFs" para procesar tus archivos
3. **Consulta interactiva**: Escribe preguntas sobre el contenido de tus documentos
4. **Visualiza fuentes**: Cada respuesta incluye referencias a los documentos consultados

**Flujo de trabajo típico:**
```
Subir documentos → Procesar automáticamente → Hacer preguntas → Obtener respuestas con referencias
```

## 🏗️ Arquitectura del Sistema

```
appi_rag/
├── 📁 app/                          # Código principal de la aplicación
│   ├── __init__.py
│   ├── config.py                   # Configuración Pydantic
│   ├── embeddings.py               # Gestión de embeddings (sentence-transformers)
│   ├── llm_generator.py            # Generación de respuestas con Groq
│   ├── main.py                     # API REST (FastAPI)
│   ├── pdf_processor.py           # Extracción y chunking de PDFs/TXT
│   ├── qdrant_store.py            # Gestión de Qdrant (crea colección automática)
│   ├── rag_chain.py               # Cadena RAG completa (LangChain)
│   ├── rag_client.py              # Cliente para consultas RAG
│   └── schemas.py                 # Esquemas Pydantic
├── 📁 data/pdfs/                   # Documentos del usuario (ignorados en Git)
│   └── .gitkeep                   # Mantiene la carpeta en Git
├── chainlit.py                    # Interfaz web con Chainlit
├── chainlit.md                    # Mensaje de bienvenida
├── � pyproject.toml              # Dependencias y metadatos
├── 📋 requirements.txt            # Dependencias para pip
├── .env.example                   # Plantilla de configuración
├── .env                           # Credenciales (NO SUBIR A GIT)
├── .gitignore                     # Patrones ignorados
├── 🐳 Dockerfile                  # Configuración Docker
├── 🐳 docker-compose.yml          # Orquestación Docker
└── 📖 README.md                   # Esta documentación
```

## 🔧 Componentes Técnicos

| Componente | Tecnología | Función |
|------------|------------|---------|
| **LLM** | Groq (Llama 3.3-70B) | Generación de respuestas en tiempo real |
| **Vector DB** | Qdrant Cloud | Almacenamiento y búsqueda de vectores |
| **Embeddings** | Sentence-Transformers | Conversión texto→vector (multilingüe) |
| **Framework** | LangChain | Orquestación de la cadena RAG |
| **API** | FastAPI | Backend REST |
| **UI** | Chainlit | Interfaz web conversacional |
| **PDF Processing** | PyPDF | Extracción de texto de documentos |

## ⚙️ Configuración Avanzada

### Variables de Entorno (.env)

```env
# GROQ API - Obligatorio
GROQ_API_KEY=gsk_tu_api_key_aquí

# QDRANT - Obligatorio
QDRANT_URL=https://tu_cluster.qdrant.io:6333
QDRANT_API_KEY=tu_api_key_de_qdrant_aquí

# Configuración Opcional
QDRANT_COLLECTION_NAME=rag_pdf_collection  # Nombre de colección
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
PDFS_DIR=./data/pdfs                       # Directorio de documentos
CHUNK_SIZE=1000                            # Tamaño de fragmentos
CHUNK_OVERLAP=200                          # Solapamiento entre fragmentos
```

### Personalización de Modelos

```python
# En el archivo .env puedes cambiar:
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2  # Modelo más rápido
# O
EMBEDDING_MODEL=intfloat/multilingual-e5-large          # Modelo más preciso
```

## 🐛 Solución de Problemas

### Error común: "Qdrant client version incompatible"
```bash
# El cliente Qdrant puede mostrar advertencias de compatibilidad
# Es seguro ignorar si el sistema funciona correctamente
# Para solucionar, puedes:
pip install qdrant-client==1.16.3  # Versión compatible
```

### Error: "GROQ_API_KEY not set"
```bash
# Verifica que el archivo .env exista y contenga:
GROQ_API_KEY=tu_clave_válida_aquí
# Las claves de Groq empiezan con "gsk_"
```

### Error: "No PDFs found"
```bash
# Asegúrate de que los archivos estén en la carpeta correcta:
ls data/pdfs/  # Debería mostrar tus archivos
# Los archivos pueden ser .pdf o .txt
```

## 🔐 Seguridad

- **NUNCA** subas el archivo `.env` a Git (está en `.gitignore`)
- Usa `.env.example` como plantilla para otros desarrolladores
- Las claves API deben rotarse periódicamente
- Los documentos en `data/pdfs/` se ignoran en Git por privacidad

## 🚢 Despliegue

### Opciones de Despliegue

1. **Local**: Ideal para desarrollo y pruebas
2. **Docker**: Para entornos consistentes
3. **Cloud**: Adaptable para AWS, Google Cloud, Azure

### Requisitos de Sistema

- **Python**: 3.11 o superior
- **RAM**: Mínimo 4GB (8GB recomendado)
- **Espacio**: 1GB libre para modelos y documentos
- **Red**: Conexión a internet para APIs externas

## 🤝 Contribución

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## � Agradecimientos

- [Groq](https://groq.com) por el acceso a modelos Llama de última generación
- [Qdrant](https://qdrant.tech) por la excelente base de datos vectorial
- [LangChain](https://langchain.com) por el framework de orquestación RAG
- [Chainlit](https://chainlit.io) por la interfaz de chat intuitiva

---

**Nota**: Este sistema está diseñado para uso profesional y educativo. Siempre verifica la precisión de las respuestas generadas por IA.

**✨ ¡Empieza a conversar con tus documentos hoy mismo!**