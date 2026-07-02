# Guía de Uso Detallada - Appi RAG

## 📋 Tabla de Contenidos
- [Instalación Paso a Paso](#instalación-paso-a-paso)
- [Configuración de Credenciales](#configuración-de-credenciales)
- [Procesamiento de Documentos](#procesamiento-de-documentos)
- [Interfaz Web](#interfaz-web)
- [API REST](#api-rest)
- [Solución de Problemas](#solución-de-problemas)
- [Preguntas Frecuentes](#preguntas-frecuentes)

## 🛠️ Instalación Paso a Paso

### 1. Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/appi-rag.git
cd appi-rag
```

### 2. Configurar Entorno Virtual

**Windows:**
```bash
# Crear entorno virtual
python -m venv .venv

# Activar entorno
.venv\Scripts\activate

# Actualizar pip
python -m pip install --upgrade pip
```

**Linux/Mac:**
```bash
# Crear entorno virtual
python3 -m venv .venv

# Activar entorno
source .venv/bin/activate

# Actualizar pip
pip install --upgrade pip
```

### 3. Instalar Dependencias

```bash
# Usando pip
pip install -r requirements.txt

# O usando uv (más rápido)
uv pip install -r requirements.txt
```

### 4. Configuración Inicial

```bash
# Copiar plantilla de configuración
cp .env.example .env

# Editar el archivo .env con tus credenciales
# Usa tu editor favorito:
notepad .env  # Windows
nano .env     # Linux/Mac
# o cualquier editor de texto
```

## 🔑 Configuración de Credenciales

### Obtener Credenciales Groq

1. Visita [console.groq.com](https://console.groq.com)
2. Regístrate o inicia sesión
3. Ve a "API Keys" en el menú lateral
4. Haz clic en "Create API Key"
5. Copia la clave (comienza con `gsk_`)
6. Pégala en tu archivo `.env`:
   ```
   GROQ_API_KEY=gsk_tu_clave_aquí
   ```

### Obtener Credenciales Qdrant

1. Visita [cloud.qdrant.io](https://cloud.qdrant.io)
2. Regístrate o inicia sesión
3. Crea un nuevo cluster (usa el free tier)
4. Una vez creado, haz clic en "API Keys"
5. Genera una nueva API key
6. Copia tanto la URL como la API key
7. Pégala en tu archivo `.env`:
   ```
   QDRANT_URL=https://tu-cluster-id.qdrant.io:6333
   QDRANT_API_KEY=eyJ...tu_api_key...aqui
   ```

## 📄 Procesamiento de Documentos

### Formatos Soportados

- **PDF** (.pdf): Documentos escaneados y digitales
- **Texto** (.txt): Archivos de texto plano
- **Múltiples archivos**: Procesa varios documentos a la vez

### Preparar Documentos

```bash
# Crear carpeta de documentos (si no existe)
mkdir -p data/pdfs

# Copiar documentos
# Windows:
copy "C:\Mis Documentos\*.pdf" data\pdfs\

# Linux/Mac:
cp ~/Documentos/*.pdf data/pdfs/
```

### Estructura Recomendada

```
data/pdfs/
├── manual_usuario.pdf
├── politicas_empresa.pdf
├── contrato_servicio.txt
└── informe_anual.pdf
```

### Buenas Prácticas

1. **Calidad de documentos**: PDFs con texto extraíble (no solo imágenes)
2. **Tamaño**: Documentos menores a 50MB funcionan mejor
3. **Organización**: Agrupa documentos relacionados
4. **Nombres descriptivos**: Usa nombres claros para identificar contenido

## 💬 Interfaz Web (Chainlit)

### Iniciar la Interfaz

```bash
# Modo desarrollo (con recarga automática)
chainlit run chainlit.py -w

# Modo producción
chainlit run chainlit.py
```

### Flujo de Trabajo en la Interfaz

1. **Pantalla de bienvenida**: Información del sistema y estado
2. **Botón de ingesta**: Procesa todos los documentos en `data/pdfs/`
3. **Chat interactivo**: Escribe preguntas naturales sobre tus documentos
4. **Respuestas con fuentes**: Cada respuesta incluye referencias a documentos originales

### Características de la Interfaz

- **Indicadores visuales**: Iconos para diferentes estados
- **Progreso en tiempo real**: Ver el estado de procesamiento
- **Historial de chat**: Mantiene la conversación
- **Formato Markdown**: Respuestas bien formateadas

### Ejemplos de Preguntas

```
# Preguntas generales
"¿Qué políticas de seguridad existen?"
"Resume el contenido del manual de usuario"
"¿Cuáles son los términos del contrato?"

# Preguntas específicas
"¿En qué página habla sobre garantías?"
"Busca información sobre fechas límite"
"¿Qué se dice sobre confidencialidad?"

# Preguntas comparativas
"Compara las políticas A y B"
"¿Cuál documento es más reciente?"
```

## 🔌 API REST

### Iniciar la API

```bash
# Desde la raíz del proyecto
uvicorn app.main:app --reload --port 8001
```

### Endpoints Disponibles

#### 1. Salud del Sistema
```http
GET /health
```
```json
{
  "status": "healthy",
  "qdrant_connected": true,
  "groq_available": true,
  "documents_count": 42
}
```

#### 2. Información de Colección
```http
GET /collection/info
```
```json
{
  "collection_name": "rag_pdf_collection",
  "vectors_count": 156,
  "points_count": 156,
  "dimension": 384
}
```

#### 3. Ingestar Documentos
```http
POST /ingest
```
```json
{
  "file_path": "data/pdfs/documento.pdf"
}
```

#### 4. Consulta RAG
```http
POST /chat
```
```json
{
  "query": "¿Cuáles son las políticas de seguridad?",
  "max_results": 5
}
```
Respuesta:
```json
{
  "answer": "Las políticas de seguridad incluyen...",
  "sources": [
    {
      "filename": "politicas_empresa.pdf",
      "page": 12,
      "content": "Texto relevante extraído..."
    }
  ]
}
```

### Ejemplos con cURL

```bash
# Consultar salud del sistema
curl -X GET http://localhost:8001/health

# Hacer una pregunta
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "¿Qué documentos hablan sobre seguridad?"}'

# Ingestar un documento específico
curl -X POST http://localhost:8001/ingest \
  -H "Content-Type: application/json" \
  -d '{"file_path": "data/pdfs/importante.pdf"}'
```

## 🐛 Solución de Problemas

### Problemas Comunes y Soluciones

#### 1. Error: "ModuleNotFoundError: No module named '...'"
```bash
# Verificar que el entorno virtual esté activado
# Windows:
where python
# Debería mostrar .venv\Scripts\python.exe

# Linux/Mac:
which python
# Debería mostrar .venv/bin/python

# Reinstalar dependencias
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

#### 2. Error: "GROQ_API_KEY not set"
```bash
# Verificar que .env exista y tenga el formato correcto
cat .env  # Debería mostrar GROQ_API_KEY=gsk_...

# Verificar que python-dotenv esté instalado
pip show python-dotenv

# Cargar variables manualmente (para pruebas)
export GROQ_API_KEY="tu_clave"  # Linux/Mac
set GROQ_API_KEY="tu_clave"     # Windows cmd
$env:GROQ_API_KEY="tu_clave"    # Windows PowerShell
```

#### 3. Error: "Qdrant connection failed"
```bash
# Verificar credenciales Qdrant
echo $QDRANT_URL      # Linux/Mac
echo %QDRANT_URL%     # Windows cmd
$env:QDRANT_URL       # Windows PowerShell

# Probar conexión manualmente
curl $QDRANT_URL/collections

# Verificar versión del cliente
pip show qdrant-client

# Si hay incompatibilidad:
pip install qdrant-client==1.16.3
```

#### 4. Error: "No PDFs found to process"
```bash
# Verificar estructura de directorios
ls -la data/pdfs/     # Linux/Mac
dir data\pdfs\        # Windows

# Verificar permisos
# Los archivos deben ser legibles

# Verificar formato de archivos
# Solo .pdf y .txt son soportados
```

#### 5. Error: "Model download failed"
```bash
# Verificar conexión a internet
ping huggingface.co

# Verificar espacio en disco
# Los modelos de embeddings requieren ~500MB

# Probar con modelo más pequeño
# Editar .env:
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

### Logs y Depuración

#### Habilitar Logs Detallados
```python
# En chainlit.py o main.py, agregar:
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Ver Logs en Tiempo Real
```bash
# Para Chainlit
chainlit run chainlit.py --debug

# Para FastAPI
uvicorn app.main:app --reload --log-level debug
```

#### Archivos de Log Importantes
- `chainlit.log`: Logs de la interfaz web
- Salida de consola: Errores y advertencias
- Archivos temporales: En `data/` o `/tmp/`

## ❓ Preguntas Frecuentes

### ¿Cuántos documentos puedo procesar?
- **Recomendado**: Hasta 100 documentos medianos
- **Límite técnico**: Depende de la memoria RAM y espacio en Qdrant
- **Rendimiento óptimo**: 20-50 documentos de tamaño moderado

### ¿Qué idiomas soporta?
- **Embeddings**: Multilingüe (español, inglés, francés, alemán, etc.)
- **LLM**: Principalmente inglés, pero entiende y responde en español
- **Mejor rendimiento**: Español e inglés

### ¿Es seguro para documentos confidenciales?
- **Groq**: Procesa texto en sus servidores
- **Qdrant Cloud**: Tus datos están en sus servidores
- **Recomendación**: Usa documentos no confidenciales o despliega localmente

### ¿Cómo mejorar la precisión de las respuestas?
1. Usa documentos bien estructurados
2. Proporciona contexto específico en las preguntas
3. Ajusta `CHUNK_SIZE` y `CHUNK_OVERLAP` en `.env`
4. Usa modelos de embeddings más avanzados

### ¿Puedo usar otros modelos LLM?
- Actualmente solo Groq
- Futuras versiones podrán soportar OpenAI, Anthropic, etc.
- Requeriría modificar `rag_chain.py`

### ¿Cómo hago backup de mis datos?
1. Exporta la colección de Qdrant
2. Guarda los documentos originales
3. Exporta configuraciones del sistema

## 🚀 Mejoras de Rendimiento

### Optimización para Producción

1. **Cache de embeddings**: Reutiliza embeddings calculados
2. **Batch processing**: Procesa documentos en lotes
3. **CDN para modelos**: Descarga modelos desde mirrors locales
4. **Load balancing**: Distribuye carga entre múltiples instancias

### Configuración Avanzada

```env
# En .env para mejor rendimiento
CHUNK_SIZE=800      # Fragmentos más pequeños para precisión
CHUNK_OVERLAP=150   # Mejor contexto entre fragmentos
GROQ_MODEL=llama-3.3-70b-versatile  # Modelo de Groq
TEMPERATURE=0.2     # Respuestas más deterministas
```

## 📚 Recursos Adicionales

- [Documentación de Groq](https://console.groq.com/docs)
- [Documentación de Qdrant](https://qdrant.tech/documentation/)
- [Guía de LangChain](https://python.langchain.com/docs/)
- [Tutoriales de Chainlit](https://docs.chainlit.io)

## 🤝 Soporte

Para reportar problemas o solicitar ayuda:
1. Revisa esta guía primero
2. Consulta los logs del sistema
3. Abre un issue en el repositorio
4. Proporciona información detallada:
   - Sistema operativo
   - Versión de Python
   - Logs de error
   - Pasos para reproducir

---

**¡Listo para empezar!** 🎉

Con esta guía tienes todo lo necesario para instalar, configurar y usar Appi RAG efectivamente. Si encuentras algún problema o tienes sugerencias, no dudes en contribuir al proyecto.