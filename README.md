# Mini Asistente Q&A
## Características Principales

- **Procesamiento Local de Documentos**: Sube y procesa archivos PDF y TXT localmente
- **Integración con Gemini API**: Utiliza la API de Google Gemini para embeddings y generación de respuestas
- **Búsqueda Semántica**: Búsqueda avanzada basada en significado, no solo palabras clave
- **Chat Inteligente**: Interfaz de chat para hacer preguntas sobre el contenido de los documentos
- **Arquitectura Modular**: Diseño modular con separación clara de responsabilidades
- **Docker Ready**: Configuración completa con Docker Compose para desarrollo y producción
- **Privacidad**: Los documentos permanecen en tu sistema local

## Arquitectura del Sistema

### Frontend (Next.js + TypeScript + TailwindCSS)
- Atomic Design: Componentes organizados en átomos, moléculas y organismos
- State Management: Context API para manejo de estado global
- Diseño Modular escalable

### Backend (FastAPI + Python)
- API RESTful: Endpoints bien definidos con documentación automática
- Procesamiento de Documentos: Extracción de texto y fragmentación inteligente
- Vector Store: Almacenamiento en memoria para búsqueda de similaridad
- LLM Integration: Servicio abstracto para integración con diferentes proveedores de LLM

### Servicios
- **Document Service**: Manejo de carga, validación y procesamiento de archivos
- **Vertex RAG Service**: Integración con Gemini API para embeddings y generación de texto
- **Vector Store**: Sistema de búsqueda semántica con cálculo de similaridad
- **Search Service**: Búsqueda semántica con ranking de relevancia

## Tecnologías Utilizadas

### Frontend
- **Next.js 14**: Framework React con App Router
- **TypeScript**: Tipado estático
- **TailwindCSS**: Framework CSS utilitario
- **React Hooks**: Manejo de estado y efectos
- **Axios**: Cliente HTTP

### Backend
- **FastAPI**: Framework web moderno para Python
- **Pydantic**: Validación de datos y serialización
- **Google Generative AI**: API de Gemini para embeddings y chat
- **PyPDF2**: Extracción de texto de PDFs
- **NumPy**: Operaciones vectoriales y cálculo de similaridad
- **Uvicorn**: Servidor ASGI de alto rendimiento

### DevOps
- **Docker & Docker Compose**: Contenedorización
- **Nginx**: Proxy reverso y balanceador de carga
- **Redis**: Cache y gestión de sesiones

## Prerequisitos

- **Docker** y **Docker Compose** instalados
- **Clave API de Google Gemini** (obtén una [aquí](https://ai.google.dev/))
- **Node.js 18+** (para desarrollo local)
- **Python 3.11+** (para desarrollo local)

## Instalación y Configuración

### 1. Clonar el Repositorio



### 2. Configurar Variables de Entorno



Edita el archivo `.env`:

```env
# Google Gemini API Configuration
GOOGLE_API_KEY=tu_clave_api_de_gemini
GEMINI_MODEL=gemini-2.0-flash-exp
EMBEDDING_MODEL=models/text-embedding-004

# Application Configuration
DEBUG=false
MAX_FILE_SIZE=10485760
ALLOWED_EXTENSIONS=pdf,txt
MAX_FILES=10
CHUNK_SIZE=4000
CHUNK_OVERLAP=200
SIMILARITY_THRESHOLD=0.4
SEARCH_LIMIT=5
```

### 3. Ejecutar con Docker Compose

#### Desarrollo
```bash
docker-compose -f docker-compose.dev.yml up --build
```



### 4. Acceder a la Aplicación

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000


## Uso de la Aplicación

### 1. Subir Documentos
- Ve a la sección "Upload Documents"
- Arrastra archivos PDF o TXT (máximo 10MB cada uno)
- Los documentos se procesan automáticamente al soltarlos

### 2. Modos de Búsqueda
- **Textual Search**: Encuentra coincidencias exactas en el texto
- **AI Reasoning Search**: Interpreta el contexto y responde de forma razonada

### 3. Preguntas y Respuestas
- Haz preguntas en lenguaje natural sobre tus documentos
- Recibe respuestas estructuradas con citas y fuentes
- Las respuestas incluyen referencias específicas a páginas y documentos

### 4. Gestión de Documentos
- Visualiza todos los documentos subidos
- Elimina documentos cuando ya no los necesites
- Monitorea el estado de procesamiento

## Estructura del Proyecto

```
Prueba-T-cnica/
├── src/                          # Frontend (Next.js)
│   ├── app/                      # App Router
│   ├── components/               # Componentes React
│   │   ├── atoms/               # Componentes básicos
│   │   ├── molecules/           # Componentes compuestos
│   │   └── organisms/           # Componentes complejos
│   ├── contexts/                # React Contexts
│   ├── services/                # Servicios API
│   ├── types/                   # Definiciones TypeScript
│   └── utils/                   # Utilidades
├── backend/                     # Backend (FastAPI)
│   ├── app/                     
│   │   ├── api/                 # Rutas API
│   │   ├── core/                # Configuración central
│   │   ├── models/              # Modelos Pydantic
│   │   └── services/            # Servicios de negocio
│   └── main.py                  # Punto de entrada
├── docker-compose.yml           # Configuración Docker producción
├── docker-compose.dev.yml       # Configuración Docker desarrollo
├── Dockerfile.frontend          # Imagen Docker frontend
├── Dockerfile.backend           # Imagen Docker backend
└── nginx.conf                   # Configuración Nginx
```

## API Endpoints

### Documentos
- `POST /api/documents/ingest` - Subir y procesar documentos
- `GET /api/documents` - Listar documentos
- `GET /api/documents/{id}` - Obtener documento específico
- `DELETE /api/documents/{id}` - Eliminar documento
- `GET /api/documents/stats` - Estadísticas de documentos

### Búsqueda
- `GET /api/search/?q={query}` - Búsqueda semántica
- `POST /api/search/` - Búsqueda avanzada

### Q&A
- `POST /api/qa/ask` - Hacer pregunta
- `POST /api/qa/explain` - Explicar respuesta
- `POST /api/qa/follow-up` - Pregunta de seguimiento

### Sistema
- `GET /api/health` - Estado del sistema
- `GET /` - Información de la API

## Características Técnicas

### Procesamiento de Documentos
- **Chunking Inteligente**: Fragmentación basada en oraciones (4000 caracteres por chunk)
- **Metadatos Enriquecidos**: Información detallada de cada fragmento
- **Validación de Archivos**: Verificación de tipo, tamaño y contenido

### Búsqueda Semántica
- **Embeddings de Gemini**: Generación de vectores de alta calidad
- **Similaridad de Coseno**: Algoritmo de búsqueda semántica
- **Umbral Configurable**: Ajuste fino de la relevancia (0.4 por defecto)

### Generación de Respuestas
- **Prompt Optimizado**: Instrucciones claras para respuestas estructuradas
- **Citas Automáticas**: Referencias a fuentes específicas
- **Formato Markdown**: Respuestas bien estructuradas y legibles

## Configuración Avanzada

### Variables de Entorno

```env
# Chunking Configuration
CHUNK_SIZE=4000              # Tamaño máximo de fragmentos
CHUNK_OVERLAP=200            # Solapamiento entre fragmentos

# Search Configuration
SIMILARITY_THRESHOLD=0.4     # Umbral de relevancia (0.0 - 1.0)
SEARCH_LIMIT=5               # Número máximo de resultados

# API Configuration
GOOGLE_API_KEY=your_key      # Clave API de Gemini
GEMINI_MODEL=gemini-2.0-flash-exp
EMBEDDING_MODEL=models/text-embedding-004
```

### Optimización de Rendimiento

- **Chunk Size**: Ajusta según el tipo de documentos
- **Similarity Threshold**: Reduce para más resultados, aumenta para mayor precisión
- **Search Limit**: Balance entre completitud y velocidad

## Decisiones Técnicas y Supuestos

### Arquitectura y Tecnologías Elegidas

**Google Vertex AI y Gemini API**
- Se eligió Vertex AI como motor principal de embeddings y generación de respuestas debido a la familiaridad previa con la herramienta
- Gemini 2.0 Flash Exp proporciona respuestas rápidas y de alta calidad para el análisis de documentos
- El modelo de embeddings `text-embedding-004` ofrece vectores de 768 dimensiones optimizados para búsqueda semántica es un modelo de embeddings liviano para este proyecto de prueba tecnica pero se deberia usar modelos mas grandes para soluciones mas robustas

**Arquitectura Modular**
- Diseño basado en principios SOLID para facilitar escalabilidad y mantenimiento
- Separación clara entre servicios: DocumentService, VertexRAGService, y VectorStore
- Estructura de componentes atómicos en el frontend (átomos, moléculas, organismos)
- Cada módulo puede ser modificado, reemplazado o extendido independientemente

**Almacenamiento Local vs. Cloud**
- **Decisión actual**: Almacenamiento local en memoria y persistencia en archivos JSON
- **Supuesto**: Información sensible que requiere privacidad y control total
- **Alternativa considerada**: Envío directo de documentos completos a Gemini para procesamiento en la nube directo sin pasar por una base de datos vectorial

### Limitaciones Técnicas Identificadas

**Almacenamiento**
- El almacenamiento en memoria limita la capacidad y persistencia del sistema
- Los metadatos de documentos podrían ser más ricos y estructurados
- Falta implementación de base de datos persistente para entornos de producción

**Escalabilidad**
- El sistema actual está optimizado para desarrollo y pruebas locales
- Para producción se recomendaría:
  - Base de datos vectorial dedicada (ChromaDB, Pinecone, Weaviate)
  - Sistema de colas para procesamiento asíncrono de documentos
  - Cache distribuido (Redis) para mejorar rendimiento

**Procesamiento de Documentos**
- Limitado a PDF y TXT, podría extenderse a DOCX, imágenes con OCR
- El chunking actual es básico, podría implementar estrategias más sofisticadas
- No hay procesamiento de tablas o elementos estructurados complejos

### Supuestos del Proyecto

1. **Privacidad de Datos**: Se asume que los documentos contienen información sensible que debe procesarse localmente
2. **Volumen de Datos**: Diseñado para manejar 3-10 documentos como especifica el reto
3. **Usuarios Concurrentes**: Optimizado para uso individual o equipos pequeños
4. **Idioma**: Principalmente diseñado para documentos en español, aunque funciona con otros idiomas
5. **Formatos**: PDF y TXT son suficientes para el caso de uso planteado

### Alternativas Consideradas

**Opción 1 - Procesamiento Cloud Completo**
- Enviar documentos completos a Gemini para procesamiento directo
- Ventajas: Mayor capacidad de procesamiento, menos infraestructura local
- Desventajas: Menor control sobre privacidad, dependencia de conectividad
- **No elegida por**: Requisitos de privacidad y especificaciones del reto

**Opción 2 - Búsqueda Clásica (TF-IDF/BM25)**
- Implementar búsqueda basada en frecuencia de términos sin LLM
- Ventajas: Mayor velocidad, menor dependencia de APIs externas
- Desventajas: Menor calidad en comprensión semántica
- **No elegida por**: La búsqueda semántica ofrece mejor experiencia de usuario

## Tiempo Real Invertido

### Fase 1: Prototipo Mínimo Viable (8 horas)
**Objetivo**: Implementar funcionalidades core del reto
- ✅ Setup inicial del proyecto (Docker, FastAPI, Next.js)
- ✅ Endpoint `/ingest` para subida y procesamiento de documentos
- ✅ Endpoint `/search` para búsqueda semántica básica
- ✅ Endpoint `/ask` para Q&A con citas
- ✅ Frontend básico con componentes esenciales
- ✅ Integración con Gemini API

**Estado al finalizar**: Sistema funcional que cumple todos los requisitos mínimos del reto

### Fase 2: Mejoras y Optimización (horas adicionales hasta la entrega)
**Objetivo**: Mejorar UX/UI y robustez del sistema
- Mejora de la interfaz de usuario basada en diseños específicos
- Optimización del prompt para respuestas más estructuradas
- Documentación completa del README
- Testing manual exhaustivo de todas las funcionalidades
- Refinamiento de la lógica de chunking y metadatos

### Fase 3: Revisión y Pulimiento (horas adicionales)
**Objetivo**: Verificar cumplimiento de requisitos y calidad
- Revisión completa de requisitos del reto
- Verificación de documentación técnica
- Corrección de bugs menores y optimizaciones
- Limpieza de código y eliminación de elementos no utilizados

**Tiempo Total Invertido**: 3 dias
- **Core MVP**: 8 horas 
- **Mejoras adicionales**: horas restantes para alcanzar calidad
## Instrucciones de Ejecución

**Nota**: El comando `docker-compose up` levanta automáticamente todos los servicios necesarios:


3. **Acceder a la aplicación**:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000


## Capturas de Pantalla

![2025-08-2020-44-33-Trim-ezgif com-video-to-gif-converter](https://github.com/user-attachments/assets/951ba773-afd2-491a-91f4-32453ca4112f)









