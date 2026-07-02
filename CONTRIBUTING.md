# Guía de Contribución - Appi RAG

¡Gracias por tu interés en contribuir a Appi RAG! Esta guía te ayudará a entender cómo contribuir efectivamente al proyecto.

## 🎯 Cómo Contribuir

### 1. Reportar Errores (Bugs)

**Antes de reportar:**
- [ ] Verifica que el error no esté ya reportado en [Issues](https://github.com/tu-usuario/appi-rag/issues)
- [ ] Revisa la [Guía de Uso](USAGE.md) y [Preguntas Frecuentes](README.md#preguntas-frecuentes)
- [ ] Prueba con la última versión del código

**Template para reportar bugs:**
```markdown
## Descripción del Error

Descripción clara y concisa del problema.

## Pasos para Reproducir

1. Ir a '...'
2. Hacer clic en '....'
3. Desplazarse hasta '....'
4. Ver error

## Comportamiento Esperado

Descripción clara de lo que esperabas que sucediera.

## Capturas de Pantalla

Si aplica, añade capturas de pantalla.

## Contexto Adicional

- Sistema Operativo: [ej. Windows 11, Ubuntu 22.04]
- Versión de Python: [ej. 3.11.0]
- Versión del proyecto: [ej. 1.0.0]
- Configuración relevante de .env

## Logs de Error

```
Pega aquí los logs de error relevantes
```
```

### 2. Solicitar Funcionalidades (Feature Requests)

**Template para solicitar features:**
```markdown
## ¿Tu solicitud está relacionada con un problema?

Una descripción clara y concisa del problema.

## Solución Deseada

Una descripción clara de lo que quieres que suceda.

## Alternativas Consideradas

Una descripción de las soluciones alternativas que consideraste.

## Contexto Adicional

Cualquier contexto adicional sobre la solicitud.
```

### 3. Contribuir con Código

#### Proceso de Desarrollo

1. **Fork** el repositorio
2. **Clone** tu fork:
   ```bash
   git clone https://github.com/tu-usuario/appi-rag.git
   cd appi-rag
   ```

3. **Configurar entorno de desarrollo:**
   ```bash
   # Crear entorno virtual
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # .venv\Scripts\activate   # Windows
   
   # Instalar dependencias
   pip install -r requirements.txt
   
   # Instalar dependencias de desarrollo
   pip install black flake8 pytest pre-commit
   ```

4. **Crear una rama para tu feature:**
   ```bash
   git checkout -b feature/nueva-funcionalidad
   ```

5. **Desarrollar tu feature:**
   - Sigue las convenciones de código existentes
   - Añade tests para tu código
   - Actualiza documentación cuando sea necesario

6. **Ejecutar pruebas:**
   ```bash
   # Formatear código
   black .
   
   # Verificar estilo
   flake8
   
   # Ejecutar tests
   pytest
   ```

7. **Commit de cambios:**
   ```bash
   git add .
   git commit -m "feat: añade nueva funcionalidad"
   # Usa commit messages convencionales
   ```

8. **Push a tu fork:**
   ```bash
   git push origin feature/nueva-funcionalidad
   ```

9. **Abrir Pull Request**

#### Convenciones de Código

**Estructura de Commits:**
- `feat:` Nueva funcionalidad
- `fix:` Corrección de bug
- `docs:` Cambios en documentación
- `style:` Cambios de formato (sin afectar funcionalidad)
- `refactor:` Refactorización de código
- `test:` Añadir o modificar tests
- `chore:` Cambios en tareas de mantenimiento

**Estilo de Código:**
- Sigue PEP 8 para Python
- Usa type hints
- Documenta funciones y clases con docstrings
- Máximo 88 caracteres por línea (configuración Black)

**Ejemplo de docstring:**
```python
def procesar_documento(ruta: str) -> List[Document]:
    """
    Procesa un documento PDF o TXT y lo divide en chunks.
    
    Args:
        ruta: Ruta al archivo a procesar
        
    Returns:
        Lista de objetos Document con metadata
        
    Raises:
        FileNotFoundError: Si el archivo no existe
        ValueError: Si el formato no es soportado
    """
```

### 4. Mejorar Documentación

La documentación es crucial. Puedes contribuir:
- Corrigiendo errores en README.md, USAGE.md
- Añadiendo ejemplos de uso
- Traduciendo a otros idiomas
- Creando tutoriales

## 🧪 Pruebas

### Estructura de Tests

```
tests/
├── unit/           # Pruebas unitarias
│   ├── test_embeddings.py
│   ├── test_pdf_processor.py
│   └── test_config.py
├── integration/    # Pruebas de integración
│   ├── test_rag_chain.py
│   └── test_qdrant_integration.py
└── e2e/           # Pruebas end-to-end
    └── test_chat_flow.py
```

### Escribiendo Tests

```python
import pytest
from app.pdf_processor import PDFProcessor

class TestPDFProcessor:
    def test_chunk_creation(self):
        """Test que verifica la creación correcta de chunks."""
        processor = PDFProcessor(chunk_size=500, chunk_overlap=100)
        # ... código de test
        
    def test_empty_pdf(self):
        """Test para PDF vacío."""
        with pytest.raises(ValueError):
            processor.process_pdf("vacio.pdf")
```

## 🔧 Configuración de Desarrollo

### Pre-commit Hooks

Configura pre-commit para asegurar calidad de código:

```bash
# Instalar pre-commit
pip install pre-commit

# Configurar hooks
pre-commit install

# Ejecutar en todos los archivos
pre-commit run --all-files
```

Configuración `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.1.0
    hooks:
      - id: black
        language_version: python3.11
        
  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
```

### Variables de Entorno para Desarrollo

Crea `.env.dev` para desarrollo:

```env
# Modo desarrollo
DEBUG=true
LOG_LEVEL=DEBUG

# APIs de prueba (opcional)
GROQ_API_KEY=test_key
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=

# Configuración de desarrollo
CHUNK_SIZE=500
CHUNK_OVERLAP=100
```

## 📁 Estructura del Proyecto

```
appi-rag/
├── app/                    # Código principal
│   ├── __init__.py
│   ├── config.py          # Configuración
│   ├── embeddings.py      # Embeddings
│   ├── llm_generator.py   # Generación LLM
│   ├── main.py            # API FastAPI
│   ├── pdf_processor.py   # Procesamiento PDF
│   ├── qdrant_store.py    # Almacenamiento Qdrant
│   ├── rag_chain.py       # Cadena RAG
│   ├── rag_client.py      # Cliente RAG
│   └── schemas.py         # Esquemas Pydantic
├── tests/                 # Pruebas
│   ├── __init__.py
│   ├── conftest.py       # Configuración pytest
│   ├── unit/             # Pruebas unitarias
│   ├── integration/      # Pruebas integración
│   └── e2e/              # Pruebas end-to-end
├── data/                  # Datos (ignorado en Git)
│   └── pdfs/
├── docs/                  # Documentación
│   ├── api/              # Documentación API
│   ├── guides/           # Guías
│   └── architecture/     # Arquitectura
└── scripts/              # Scripts de utilidad
    ├── setup_dev.py
    ├── run_tests.py
    └── clean_cache.py
```

## 🚀 Flujo de Trabajo de Desarrollo

### 1. Iniciar Nuevo Feature

```bash
# Sincronizar con upstream
git fetch upstream
git checkout main
git merge upstream/main

# Crear rama
git checkout -b feature/nombre-feature
```

### 2. Desarrollo Local

```bash
# Instalar en modo desarrollo
pip install -e .

# Ejecutar tests
pytest tests/unit/

# Verificar estilo
flake8 app/

# Formatear código
black app/
```

### 3. Pre-parar Pull Request

```bash
# Actualizar con main
git fetch upstream
git merge upstream/main

# Resolver conflictos si los hay
# Ejecutar todas las pruebas
pytest tests/

# Verificar cobertura
pytest --cov=app tests/

# Commit final
git commit -m "feat: descripción completa"
```

### 4. Crear Pull Request

1. Push a tu fork
2. Ir a GitHub
3. Crear Pull Request
4. Llenar template de PR
5. Esperar revisión

**Template de Pull Request:**
```markdown
## Descripción de Cambios

Descripción clara de qué hace este PR.

## Tipo de Cambio

- [ ] Bug fix
- [ ] Nueva funcionalidad
- [ ] Breaking change
- [ ] Actualización de documentación
- [ ] Refactorización

## Checklist

- [ ] Mi código sigue las convenciones del proyecto
- [ ] He realizado self-review de mi código
- [ ] He comentado mi código donde sea necesario
- [ ] He actualizado la documentación
- [ ] He añadido tests que prueban mi fix/feature
- [ ] Todos los tests pasan localmente

## Pruebas Realizadas

- [ ] Pruebas unitarias
- [ ] Pruebas de integración
- [ ] Pruebas end-to-end
- [ ] Pruebas manuales

## Capturas de Pantalla

Si aplica, añade capturas.

## Contexto Adicional

Cualquier información adicional.
```

## 📊 Mantenimiento del Código

### Cobertura de Código

```bash
# Generar reporte de cobertura
pytest --cov=app --cov-report=html tests/

# Ver en navegador
open htmlcov/index.html
```

### Dependencias

```bash
# Actualizar dependencias
pip list --outdated

# Actualizar requirements.txt
pip freeze > requirements.txt

# Verificar vulnerabilidades
pip-audit
```

### Documentación

```bash
# Generar documentación automática
pdoc app --html --output-dir docs/api

# Servir documentación local
python -m http.server --directory docs/api 8000
```

## 🏆 Buenas Prácticas

### Para Nuevos Contribuidores

1. **Empieza pequeño**: Correcciones de typos, mejoras en docs
2. **Pregunta**: No dudes en preguntar en issues o discussions
3. **Sigue convenciones**: Observa el código existente
4. **Sé paciente**: Las revisiones pueden tomar tiempo

### Para Mantenedores

1. **Revisión constructiva**: Enfócate en el código, no en la persona
2. **Explica el porqué**: Cuando pidas cambios, explica la razón
3. **Reconoce contribuciones**: Agradece el esfuerzo de los contribuidores
4. **Mantén el proyecto accesible**: Documentación clara, issues bien organizados

## 🤝 Código de Conducta

Este proyecto sigue el [Código de Conducta de Contributor Covenant](CODE_OF_CONDUCT.md). Al participar, se espera que mantengas este código.

## 📝 Licencia

Al contribuir, aceptas que tus contribuciones serán licenciadas bajo la [Licencia MIT](LICENSE).

## 🙏 Agradecimientos

Gracias por considerar contribuir a Appi RAG. Tu tiempo y esfuerzo son muy valorados y ayudan a hacer este proyecto mejor para todos.

---

**¿Listo para contribuir?** 🚀

1. Revisa los [issues abiertos](https://github.com/tu-usuario/appi-rag/issues)
2. Únete a la [discusión](https://github.com/tu-usuario/appi-rag/discussions)
3. ¡Empieza a codificar!

Si tienes preguntas, no dudes en preguntar. ¡Feliz codificación!