# Ares Materials - API de Procesamiento de Datos

API REST desarrollada en Flask para procesar y almacenar datos de pruebas de materiales en laboratorios. Proporciona endpoints para análisis de tracción, CTE (Coeficiente de Expansión Térmica), DMA (Análisis Mecánico Dinámico), DSC (Calorimetría Diferencial de Barrido) y nanoindentación.

---

## 📌 Project Overview

### ¿Qué hace esta API?

Esta API procesa archivos de datos experimentales de pruebas de materiales y extrae propiedades mecánicas y térmicas mediante análisis numérico. Los archivos subidos se procesan en memoria, se analizan usando funciones especializadas y se almacenan automáticamente en AWS S3 para persistencia.

**Funcionalidades principales:**
- Procesamiento de archivos CSV y Excel de pruebas de materiales
- Extracción de propiedades mecánicas (módulo de Young, resistencia, etc.)
- Análisis de propiedades térmicas (temperatura de transición vítrea, CTE, etc.)
- Almacenamiento persistente en S3 con URLs prefirmadas para descarga
- Control de acceso mediante API key

### ¿Para qué existe?

La API resuelve el problema de procesamiento automatizado de datos experimentales de materiales, eliminando la necesidad de procesamiento manual y proporcionando:
- **Estandarización**: Procesamiento consistente de diferentes tipos de pruebas
- **Persistencia**: Almacenamiento seguro en S3 para auditoría y recuperación
- **Accesibilidad**: API REST que permite integración con otros sistemas
- **Escalabilidad**: Arquitectura que permite agregar nuevos tipos de pruebas fácilmente

### Contexto de desarrollo

Este proyecto fue desarrollado para mejorar las siguientes habilidades:
- Capacidad de refactorización de código legacy
- Implementación de mejores prácticas de arquitectura de software
- Integración con servicios cloud (AWS S3)
- Diseño de APIs RESTful con control de acceso
- Documentación técnica completa

---

## 🏗️ Architecture & Design Decisions

### Separación de Responsabilidades

La arquitectura sigue el principio de **separación de responsabilidades** (SoC) para facilitar mantenibilidad y escalabilidad:

#### 1. **Capa de Vistas (`src/views/`)**
- **Responsabilidad**: Manejo de requests HTTP y respuestas
- **Implementación**: Clases basadas en `MethodView` de Flask
- **Razón**: Centraliza la lógica de HTTP, validación de entrada y serialización de salida

#### 2. **Capa de Lógica de Negocio (`helpers.py`)**
- **Responsabilidad**: Procesamiento de datos y cálculos científicos
- **Implementación**: Funciones puras sin dependencias de Flask
- **Razón**: Permite reutilización, testing independiente y separación de concerns

#### 3. **Capa de Servicios (`src/s3_client.py`)**
- **Responsabilidad**: Interacción con servicios externos (S3)
- **Implementación**: Clase singleton `S3Client` con métodos encapsulados
- **Razón**: Abstrae la complejidad de boto3, facilita testing con mocks y permite cambiar de proveedor

#### 4. **Capa de Autenticación (`src/auth.py`)**
- **Responsabilidad**: Control de acceso y validación de credenciales
- **Implementación**: Decorador `@require_api_key` reutilizable
- **Razón**: Permite aplicar seguridad de forma declarativa y consistente

#### 5. **Capa de Enrutamiento (`src/routes.py`)**
- **Responsabilidad**: Mapeo URL → Vista
- **Implementación**: Función `register_routes()` centralizada
- **Razón**: Facilita mantenimiento de rutas y permite versionado futuro

### Generalización de Endpoints

**Problema identificado**: Los endpoints originales tenían mucho código duplicado (iteración de archivos, manejo de errores, serialización JSON).

**Solución implementada**: Clase base `BaseFileProcessingView` con patrón Template Method:

```python
class BaseFileProcessingView(MethodView):
    def post(self):
        # Lógica común: obtener archivos, iterar, manejar errores
        for file in files:
            result = self.process_single_file(file, form)
            # ...
    
    def process_single_file(self, file, form):
        # Template method: define el flujo, delega detalles a subclases
        form_params = self.extract_file_params(...)  # Específico
        file_data = self.read_file(file)              # Común
        helper_args = self.build_helper_args(...)     # Específico
        return self.get_helper_function()(**helper_args)  # Específico
```

**Beneficios**:
- **DRY (Don't Repeat Yourself)**: Eliminación de código duplicado
- **Mantenibilidad**: Cambios en lógica común se hacen en un solo lugar
- **Extensibilidad**: Agregar nuevo tipo de prueba requiere de menos lineas de código
- **Consistencia**: Comportamiento uniforme en manejo de errores y respuestas

### Integración con S3

**Decisión**: Usar AWS S3 como almacenamiento persistente en lugar de sistema de archivos local.

**Razones**:
1. **Escalabilidad**: S3 maneja petabytes sin problemas de infraestructura
2. **Durabilidad**: Muy buena durabilidad
3. **Acceso distribuido**: URLs prefirmadas permiten descarga directa sin pasar por el servidor
4. **Costo**: Pay-per-use, más económico que mantener storage propio
5. **Integración**: Compatible con LocalStack para desarrollo local sin costos

**Implementación**:
- Path fijo `minerva_archive/testing/` para organización
- Claves únicas con timestamp + UUID para evitar colisiones
- URLs prefirmadas con expiración configurable (default: 1 hora)
- Manejo robusto de errores (archivo no encontrado, permisos, etc.)

### Compatibilidad con API Original

**Estrategia**: Mantener 100% de compatibilidad con el comportamiento original mientras se mejora la estructura interna.

**Técnicas aplicadas**:
1. **Mismo formato de respuesta JSON**: Estructura idéntica a la original
2. **Mismos nombres de endpoints**: `/tensile`, `/cte`, `/dma`, `/dsc`, `/nanoindentation`
3. **Mismos parámetros de entrada**: Form-data con mismos nombres de campos
4. **Rutas legacy mantenidas**: `/download/*` disponibles por compatibilidad
5. **Procesamiento idéntico**: Mismas funciones helper, mismos cálculos

**Resultado**: Clientes existentes pueden migrar sin cambios, mientras internamente el código es más mantenible.

---

## 📁 Project Structure

```
aresmaterials/
├── run.py                    # Punto de entrada de la aplicación Flask
├── requirements.txt          # Dependencias del proyecto con versiones
├── helpers.py                # Funciones de procesamiento científico (lógica de negocio)
├── env.example               # Plantilla de variables de entorno
├── README.md                 # Documentación
└── src/
    ├── app.py                # Factory de aplicación Flask y carga de configuración
    ├── routes.py             # Registro centralizado de todas las rutas
    ├── auth.py               # Módulo de autenticación (decorador @require_api_key)
    ├── s3_client.py          # Cliente S3 con boto3 (upload, download, presigned URLs)
    └── views/                # Módulo de vistas (endpoints HTTP)
        ├── __init__.py       # Exporta todas las vistas
        ├── base.py           # Clase base BaseFileProcessingView (lógica común)
        ├── tensile.py        # Vista para pruebas de tracción
        ├── cte.py            # Vista para pruebas CTE
        ├── dma.py            # Vista para pruebas DMA
        ├── dsc.py            # Vista para pruebas DSC
        ├── nanoindentation.py # Vista para nanoindentación
        └── download.py       # Vistas para obtener URLs prefirmadas de S3
```

**Descripción de carpetas importantes**:

- **`src/views/`**: Contiene todas las vistas HTTP. Cada archivo representa un tipo de prueba de material.
- **`src/`**: Módulo principal de la aplicación. Separa código de aplicación de archivos de configuración raíz.
- **`helpers.py`** (raíz): Funciones puras de procesamiento científico, sin dependencias de Flask.

---

## ⚙️ Requirements

### Dependencias Principales

| Paquete | Versión | Propósito |
|---------|---------|-----------|
| `Flask` | >=2.3.0 | Framework web para API REST |
| `numpy` | >=1.24.0 | Procesamiento numérico de datos experimentales |
| `pandas` | >=2.0.0 | Lectura y manipulación de archivos Excel |
| `openpyxl` | >=3.1.0 | Soporte para archivos .xlsx en pandas |
| `boto3` | >=1.28.0 | SDK de AWS para integración con S3 |
| `python-dotenv` | >=1.0.0 | Carga de variables de entorno desde `.env` |
| `requests` | >=2.31.0 | Cliente HTTP para scripts de prueba |

### Versión de Python

- **Python 3.8+** (recomendado 3.10+)

---

## 🚀 Setup & Installation

### 5.1 Prerrequisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Acceso a AWS S3 o LocalStack para desarrollo local

### 5.2 Instalación Paso a Paso

#### Paso 1: Clonar el repositorio

```bash
git clone https://github.com/serosc95/api-refactor-challenge.git
cd api-refactor-challenge
```

#### Paso 2: Crear entorno virtual

```bash
# Linux/Mac
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

#### Paso 3: Instalar dependencias

```bash
pip install -r requirements.txt
```

#### Paso 4: Configurar variables de entorno

```bash
# Copiar plantilla
cp env.example .env

# Editar .env con tus valores
nano .env  # o usar tu editor preferido
```

Ver sección [6. 🔐 Environment Variables](#-environment-variables) para detalles de configuración.

#### Paso 5: Verificar instalación

```bash
python -c "import flask, numpy, pandas, boto3; print('✓ Dependencias instaladas correctamente')"
```

---

## 🔐 Environment Variables

### Variables Obligatorias

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `API_KEY` | Clave de API para autenticación. **Debe estar configurada siempre**. | `test-api-key-123` |
| `S3_BUCKET_NAME` | Nombre del bucket S3 donde se almacenarán los archivos | `aresmaterials-test` |

### Variables Opcionales (con defaults)

| Variable | Descripción | Default | Cuándo configurarla |
|----------|-------------|---------|---------------------|
| `AWS_ACCESS_KEY_ID` | Clave de acceso AWS | `test` | Para AWS real o LocalStack |
| `AWS_SECRET_ACCESS_KEY` | Clave secreta AWS | `test` | Para AWS real o LocalStack |
| `AWS_REGION` | Región de AWS | `us-east-1` | Para AWS real |
| `AWS_ENDPOINT_URL` | URL del endpoint S3 | `None` | Solo para LocalStack (ej: `http://localhost:4566`) |

### 6.1 Configuración para Desarrollo Local (LocalStack)

```bash
# .env
API_KEY=test-api-key-123
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
AWS_REGION=us-east-1
AWS_ENDPOINT_URL=http://localhost:4566
S3_BUCKET_NAME=aresmaterials-test
```

**Nota**: Para usar LocalStack, necesitas tenerlo corriendo. Opciones:
- Docker: `docker run -p 4566:4566 localstack/localstack`
- Instalación local: `pip install localstack`

### 6.2 Configuración para Producción (AWS Real)

```bash
# .env
API_KEY=tu-api-key-super-secreta-y-larga
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_REGION=us-east-1
# AWS_ENDPOINT_URL se deja vacío o no se define
S3_BUCKET_NAME=aresmaterials-prod
```

---

## ▶️ Running the Application

### 7.1 Modo Desarrollo

```bash
python run.py
```

El servidor se iniciará en `http://localhost:5000` con:
- **Debug mode**: Activado (recarga automática al cambiar código)
- **Host**: `0.0.0.0` (accesible desde cualquier IP)
- **Port**: `5000`

### 7.2 Modo Producción

Para producción, usa un servidor WSGI como Gunicorn:

```bash
# Instalar Gunicorn
pip install gunicorn

# Ejecutar con múltiples workers
gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 run:app
```

**Parámetros recomendados**:
- `-w 4`: 4 workers para balanceo de carga
- `--timeout 120`: Timeout de 120 segundos (archivos grandes pueden tardar)
- `run:app`: Módulo y variable de aplicación Flask

### 7.3 Verificar que la API está funcionando

```bash
# Debe retornar 401 (esperado, falta API key)
curl http://localhost:5000/tensile

# Con API key (debe retornar 400 o procesar según archivos)
curl -H "X-API-KEY: tu-api-key" http://localhost:5000/tensile
```

---

## 📡 API Endpoints

Todos los endpoints requieren el header `X-API-KEY` para autenticación. Ver sección [9. 🔑 Access Control](#-access-control).

### 8.1 Endpoints de Procesamiento (POST)

#### POST /tensile

Procesa archivos CSV de pruebas de tracción (tensile testing).

**Headers:**
```
X-API-KEY: tu-api-key-secreta
Content-Type: multipart/form-data
```

**Request:**
```
POST /tensile
Content-Type: multipart/form-data

files[]: [archivo1.csv, archivo2.csv, ...]
model: F105
label_archivo1.csv: Etiqueta para archivo 1
thickness_archivo1.csv: 62
height_archivo1.csv: 100
width_archivo1.csv: 5
label_archivo2.csv: Etiqueta para archivo 2
thickness_archivo2.csv: 63
...
```

**Response (200 OK):**
```json
[
  {
    "filename": "archivo1.csv",
    "label": "Etiqueta para archivo 1",
    "height": 100.0,
    "width": 5.0,
    "thickness": 62000.0,
    "young_modulus": null,
    "strength": null,
    "s3_file_key": "minerva_archive/testing/20240101_123456_uuid.csv",
    "s3_uploaded": true,
    "plot_data": {
      "strain": [],
      "stress": []
    }
  }
]
```

**Errores:**
- `401 Unauthorized`: Falta o API key inválida
- `400 Bad Request`: Parámetros faltantes o inválidos

---

#### POST /cte

Procesa archivos CSV de pruebas CTE (Coefficient of Thermal Expansion).

**Headers:**
```
X-API-KEY: tu-api-key-secreta
Content-Type: multipart/form-data
```

**Request:**
```
POST /cte
Content-Type: multipart/form-data

files[]: [archivo.csv]
label_archivo.csv: Mi prueba CTE
total_cycles_archivo.csv: 2
target_cycles_archivo.csv: 2
tg_archivo.csv: 150.5  # Opcional
```

**Response (200 OK):**
```json
[
  {
    "filename": "archivo.csv",
    "label": "Mi prueba CTE",
    "alpha_1": null,
    "alpha_2": null,
    "estimated_tg": null,
    "s3_file_key": "minerva_archive/testing/20240101_123456_uuid.csv",
    "s3_uploaded": true,
    "plot_data": {
      "temperature": [],
      "dimension_change_normalized": []
    }
  }
]
```

---

#### POST /dma

Procesa archivos CSV de pruebas DMA (Dynamic Mechanical Analysis).

**Headers:**
```
X-API-KEY: tu-api-key-secreta
Content-Type: multipart/form-data
```

**Request:**
```
POST /dma
Content-Type: multipart/form-data

files[]: [archivo.csv]
label_archivo.csv: Prueba DMA
```

**Response (200 OK):**
```json
[
  {
    "tg": null,
    "storage_modulus_reference_temperature": null,
    "storage_modulus_value": null,
    "s3_file_key": "minerva_archive/testing/20240101_123456_uuid.csv",
    "s3_uploaded": true,
    "plot_data": {
      "temperature": [25.0, 26.0, ...],
      "tan_delta": [0.1, 0.12, ...],
      "storage_modulus": [1000.0, 950.0, ...]
    }
  }
]
```

---

#### POST /dsc

Procesa archivos CSV de pruebas DSC (Differential Scanning Calorimetry).

**Headers:**
```
X-API-KEY: tu-api-key-secreta
Content-Type: multipart/form-data
```

**Request:**
```
POST /dsc
Content-Type: multipart/form-data

files: [archivo.csv]  # Nota: usa "files" no "files[]"
```

**Response (200 OK):**
```json
[
  {
    "filename": "archivo.csv",
    "tg": null,
    "s3_file_key": "minerva_archive/testing/20240101_123456_uuid.csv",
    "s3_uploaded": true,
    "plot_data": {
      "temperature": [25.0, 26.0, ...],
      "heat_flow": [0.5, 0.6, ...]
    }
  }
]
```

**Nota especial**: Este endpoint usa `files` en lugar de `files[]` para mantener compatibilidad con el código original.

---

#### POST /nanoindentation

Procesa archivos Excel (.xlsx) de pruebas de nanoindentación.

**Headers:**
```
X-API-KEY: tu-api-key-secreta
Content-Type: multipart/form-data
```

**Request:**
```
POST /nanoindentation
Content-Type: multipart/form-data

files[]: [archivo.xlsx]
label_archivo.xlsx: Prueba nanoindentación
```

**Response (200 OK):**
```json
[
  {
    "filename": "archivo.xlsx",
    "label": "Prueba nanoindentación",
    "martens_hardness_avg": null,
    "martens_hardness_std": null,
    "modulus_avg": null,
    "s3_file_key": "minerva_archive/testing/20240101_123456_uuid.xlsx",
    "s3_uploaded": true,
    "plot_data": []
  }
]
```

---

### 8.2 Endpoints de Descarga (GET)

#### GET /files/<file_key>

Obtiene una URL prefirmada para descargar un archivo desde S3 usando su clave completa.

**Headers:**
```
X-API-KEY: tu-api-key-secreta
```

**Request:**
```
GET /files/minerva_archive/testing/20240101_123456_uuid.csv?expiration=7200
```

**Parámetros:**
- `file_key` (path): Clave completa del archivo en S3
- `expiration` (query, opcional): Tiempo de expiración en segundos (default: 3600)

**Response (200 OK):**
```json
{
  "file_key": "minerva_archive/testing/20240101_123456_uuid.csv",
  "download_url": "https://s3.amazonaws.com/bucket/path?X-Amz-Algorithm=...",
  "expires_in": 7200,
  "expires_in_hours": 2.0
}
```

**Errores:**
- `401 Unauthorized`: Falta o API key inválida
- `404 Not Found`: Archivo no existe en S3

**Alternativa con query param:**
```
GET /files?file_key=minerva_archive/testing/20240101_123456_uuid.csv
```

---

#### GET /files/name/<filename>

Obtiene una URL prefirmada buscando el archivo más reciente por nombre original.

**Headers:**
```
X-API-KEY: tu-api-key-secreta
```

**Request:**
```
GET /files/name/1A_t1_62um.csv?expiration=3600
```

**Parámetros:**
- `filename` (path): Nombre original del archivo
- `expiration` (query, opcional): Tiempo de expiración en segundos (default: 3600)

**Response (200 OK):**
```json
{
  "filename": "1A_t1_62um.csv",
  "file_key": "minerva_archive/testing/20240101_123456_uuid.csv",
  "download_url": "https://s3.amazonaws.com/bucket/path?X-Amz-Algorithm=...",
  "expires_in": 3600,
  "expires_in_hours": 1.0
}
```

**Nota**: Si hay múltiples archivos con el mismo nombre, retorna el más reciente según fecha de modificación en S3.

**Alternativa con query param:**
```
GET /files/name?filename=1A_t1_62um.csv
```

---

### 8.3 Endpoints Legacy (Compatibilidad)

Los siguientes endpoints están disponibles por compatibilidad pero se recomienda usar `/files/*`:

- `GET /download/<file_key>` → Usar `GET /files/<file_key>`
- `GET /download/name/<filename>` → Usar `GET /files/name/<filename>`

---

## 🔑 Access Control

### 9.1 Cómo Funciona la Autenticación

La API utiliza autenticación basada en **API Key** mediante header HTTP:

```
X-API-KEY: tu-api-key-secreta
```

**Flujo de autenticación**:

1. Cliente envía petición con header `X-API-KEY`
2. Decorador `@require_api_key` intercepta la petición
3. Se verifica que:
   - El servidor tiene `API_KEY` configurada (si no → 500)
   - El header `X-API-KEY` está presente (si no → 401)
   - La API key coincide con la configurada (si no → 401)
4. Si todo es válido, se ejecuta el endpoint

### 9.2 Endpoints Protegidos

**Todos los endpoints están protegidos**:

- ✅ `POST /tensile`
- ✅ `POST /cte`
- ✅ `POST /dma`
- ✅ `POST /dsc`
- ✅ `POST /nanoindentation`
- ✅ `GET /files/<file_key>`
- ✅ `GET /files`
- ✅ `GET /files/name/<filename>`
- ✅ `GET /files/name`
- ✅ `GET /download/*`

### 9.3 Razones de la Protección

**Decisión de diseño**: Proteger todos los endpoints GET y POST.

**Razones**:

1. **Seguridad por defecto**: Principio de "denegar por defecto"
2. **Consistencia**: Mismo nivel de seguridad en toda la API
3. **Prevención de abuso**: Evita uso no autorizado de recursos (procesamiento, storage)
4. **Auditoría**: Todas las peticiones requieren identificación
5. **Simplicidad**: Un solo mecanismo de autenticación para toda la API

**No se protegen**:
- Endpoints de salud (`/health`) - si existieran
- Endpoints de documentación (`/docs`) - si existieran

### 9.4 Respuestas de Error

**401 Unauthorized - API key faltante:**
```json
{
  "error": "API key requerida",
  "message": "Debe proporcionar el header X-API-KEY"
}
```

**401 Unauthorized - API key inválida:**
```json
{
  "error": "API key inválida",
  "message": "La API key proporcionada no es válida"
}
```

**500 Internal Server Error - API key no configurada en servidor:**
```json
{
  "error": "API key no configurada en el servidor",
  "message": "El servidor no tiene configurada una API key válida. Contacte al administrador."
}
```

---

## 📦 S3 Storage Strategy

### 10.1 Path Fijo

Todos los archivos se almacenan bajo el path fijo:

```
minerva_archive/testing/
```

**Razón del path fijo**:
- **Organización**: Facilita gestión y políticas de S3
- **Auditoría**: Todos los archivos de prueba en un lugar conocido
- **Filtrado**: Permite listar solo archivos de testing
- **Políticas IAM**: Facilita configuración de permisos granulares

### 10.2 Estructura de Claves (file_key)

Cada archivo se almacena con una clave única generada así:

```
minerva_archive/testing/{timestamp}_{uuid}.{ext}
```

**Componentes**:
- `timestamp`: Formato `YYYYMMDD_HHMMSS` (UTC) - Ordenamiento cronológico
- `uuid`: UUID v4 - Garantiza unicidad
- `ext`: Extensión original del archivo - Preserva tipo de archivo

**Ejemplo**:
```
minerva_archive/testing/20240115_143022_a1b2c3d4-e5f6-7890-abcd-ef1234567890.csv
```

**Ventajas de esta estructura**:
- ✅ **Unicidad garantizada**: UUID previene colisiones
- ✅ **Ordenamiento temporal**: Timestamp permite ordenar por fecha
- ✅ **Trazabilidad**: Se puede identificar cuándo se subió cada archivo
- ✅ **Preservación de tipo**: Extensión permite identificar formato

### 10.3 Mapeo de Nombre de Archivo

**Problema**: Los archivos en S3 tienen claves únicas, pero los usuarios pueden querer buscar por nombre original.

**Solución implementada**:

1. **Al subir**: Se guarda el nombre original en metadatos (implícito en la clave con extensión)
2. **Al buscar por nombre**: 
   - Se lista todos los archivos en `minerva_archive/testing/`
   - Se busca coincidencias parciales o exactas del nombre
   - Se retorna el más reciente si hay múltiples coincidencias

**Limitación actual**: La búsqueda por nombre requiere listar todos los archivos. Para buckets grandes, esto puede ser lento.

**Mejora futura sugerida**: Usar DynamoDB o base de datos para indexar `filename → file_key`.

### 10.4 Manejo de Errores

#### Archivo No Encontrado (404)

**Cuándo ocurre**:
- Se solicita descarga con `file_key` que no existe
- Se busca por nombre y no hay coincidencias

**Respuesta**:
```json
{
  "error": "Archivo no encontrado",
  "file_key": "minerva_archive/testing/nonexistent.csv"
}
```

**Código HTTP**: `404 Not Found`

#### Error de Permisos S3 (403/500)

**Cuándo ocurre**:
- Credenciales AWS inválidas
- Bucket no existe o sin permisos
- Política IAM restrictiva

**Respuesta**:
```json
{
  "error": "Error al generar URL de descarga",
  "message": "An error occurred (AccessDenied) when calling the GetObject operation"
}
```

**Código HTTP**: `500 Internal Server Error` o `403 Forbidden` según el error de AWS

#### Bucket No Existe

**Comportamiento**: El cliente S3 intenta crear el bucket automáticamente si no existe.

**Para LocalStack**: Se crea sin `LocationConstraint`
**Para AWS Real**: Se crea con `LocationConstraint` según la región

**Si falla la creación**: Se registra error en logs, pero el procesamiento continúa (el archivo no se sube a S3).

### 10.5 URLs Prefirmadas

**¿Qué son?**: URLs temporales que permiten descargar archivos de S3 sin exponer credenciales.

**Ventajas**:
- ✅ **Seguridad**: No se exponen credenciales AWS
- ✅ **Eficiencia**: Descarga directa desde S3, no pasa por el servidor
- ✅ **Expiración automática**: URLs válidas solo por tiempo limitado (default: 1 hora)
- ✅ **Sin costo de ancho de banda**: El servidor no consume recursos para transferir archivos

**Formato de URL generada**:
```
https://s3.amazonaws.com/bucket-name/path/to/file?X-Amz-Algorithm=...&X-Amz-Credential=...&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=...
```

---

## 📝 Notes & Assumptions

### 11.1 Suposiciones Hechas

1. **Formato de archivos**: Se asume que los archivos CSV y Excel siguen formatos específicos:
   - CSV de tracción: 17 líneas de header
   - CSV de CTE: 9 líneas de header, delimitador `,`
   - CSV de DMA: 15 líneas de header, delimitador `,`
   - CSV de DSC: 10 líneas de header, delimitador `,`
   - Excel de nanoindentación: Hoja "Results" con índice en columna 0

2. **Unidades**: Se asumen unidades específicas:
   - Espesor en micrómetros (se convierte a milímetros)
   - Altura y ancho en milímetros
   - Temperaturas en Celsius

3. **S3 siempre disponible**: Se asume que S3 está disponible. Si falla, se registra error pero el procesamiento continúa.

4. **API key única**: Se asume una sola API key válida. No hay sistema de múltiples usuarios o roles.

### 11.2 Decisiones Simplificadas

1. **Autenticación simple**: API key única en lugar de OAuth2/JWT
   - **Razón**: Simplicidad y suficiencia para el caso de uso
   - **Mejora futura**: Implementar JWT con refresh tokens

2. **Sin base de datos**: No se almacena metadata de archivos
   - **Razón**: S3 es suficiente para el MVP
   - **Mejora futura**: Agregar DynamoDB para búsquedas rápidas

3. **Manejo de errores básico**: Errores se imprimen en consola
   - **Razón**: Suficiente para desarrollo
   - **Mejora futura**: Implementar logging estructurado (JSON) y métricas

4. **Sin versionado de API**: No hay `/v1/`, `/v2/` en URLs
   - **Razón**: Primera versión, compatibilidad mantenida
   - **Mejora futura**: Agregar versionado cuando haya breaking changes

5. **Procesamiento síncrono**: Archivos se procesan en el mismo request
   - **Razón**: Simplicidad
   - **Mejora futura**: Cola de trabajos (Celery, SQS) para archivos grandes

### 11.3 Qué No Se Implementó y Por Qué

1. **Sistema de usuarios y roles**
   - **Razón**: Fuera del alcance del proyecto
   - **Alternativa actual**: API key única

2. **Validación exhaustiva de archivos**
   - **Razón**: Se mantiene comportamiento original
   - **Mejora futura**: Validar formato antes de procesar

3. **Rate limiting**
   - **Razón**: No especificado en requisitos
   - **Mejora futura**: Implementar con Flask-Limiter

4. **Caché de resultados**
   - **Razón**: Cada procesamiento puede tener parámetros únicos
   - **Mejora futura**: Caché por hash de archivo + parámetros

5. **Webhooks o notificaciones**
   - **Razón**: No requerido
   - **Mejora futura**: Notificar cuando procesamiento termine

6. **Dashboard o UI**
   - **Razón**: Es una API, no una aplicación web completa
   - **Mejora futura**: Frontend separado que consuma esta API

### 11.4 Decisiones de Diseño Adicionales

1. **Patrón Template Method en vistas**: Permite reutilización máxima de código
2. **Singleton en S3Client**: Evita múltiples conexiones a S3
3. **Decorador para autenticación**: Permite aplicar seguridad de forma declarativa
4. **Separación views/helpers**: Facilita testing y reutilización
5. **Rutas legacy mantenidas**: Facilita migración gradual de clientes

---

## 📚 Referencias

- [Flask Documentation](https://flask.palletsprojects.com/)
- [boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [AWS S3 Presigned URLs](https://docs.aws.amazon.com/AmazonS3/latest/userguide/PresignedUrlUploadObject.html)
- [LocalStack Documentation](https://docs.localstack.cloud/)
