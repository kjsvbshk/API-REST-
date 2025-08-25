# API de Microcréditos

Sistema de gestión de microcréditos desarrollado con FastAPI y PostgreSQL, que permite gestionar clientes, préstamos y pagos con cálculo automático de intereses y cuotas.

## Índice

* [Características](#características)
* [Problema Resuelto](#problema-resuelto)
* [Estructura de la Base de Datos](#estructura-de-la-base-de-datos)
* [Requisitos](#requisitos)
* [Instalación](#instalación)
* [Uso](#uso)
* [Estructura del Proyecto](#estructura-del-proyecto)
* [Endpoints de la API](#endpoints-de-la-api)
* [Ejemplos de Uso](#ejemplos-de-uso)
* [Características Técnicas](#características-técnicas)
* [Lógica de Negocio](#lógica-de-negocio)
* [Configuración de Desarrollo](#configuración-de-desarrollo)
* [Testing](#testing)
* [Troubleshooting](#troubleshooting)
* [Deployment](#deployment)
* [Contribución](#contribución)
* [Licencia](#licencia)
* [Soporte](#soporte)

## Características

* **Gestión de Clientes**: Registro, consulta, actualización y eliminación de clientes
* **Gestión de Préstamos**: Creación de préstamos con cálculo automático de cuotas e intereses
* **Sistema de Pagos**: Registro y seguimiento de pagos de cuotas
* **Cálculos Automáticos**: Cálculo de cuotas mensuales, saldos pendientes y estados
* **API REST Completa**: Endpoints para todas las operaciones CRUD
* **Base de Datos PostgreSQL**: Con ORM SQLAlchemy y migraciones Alembic

## Problema Resuelto

### Descripción del Problema
Durante el desarrollo inicial, se encontraron varios obstáculos técnicos que impedían la ejecución correcta de la aplicación:

1. **Incompatibilidad de Versiones**: Python 3.13 es muy reciente y algunas librerías como `psycopg2-binary` y `pydantic-core` no eran compatibles inicialmente
2. **Dependencias Faltantes**: Librerías esenciales como SQLAlchemy, FastAPI y validadores no estaban instaladas
3. **PostgreSQL No Configurado**: El servicio de base de datos no estaba ejecutándose ni inicializado
4. **Validadores Incompletos**: Faltaba el validador de email para Pydantic
5. **Conexión Prematura a BD**: La aplicación intentaba conectarse a la base de datos durante la importación

### Solución Implementada
Se resolvieron todos los problemas mediante:

* **Actualización de dependencias** a versiones compatibles con Python 3.13
* **Configuración completa de PostgreSQL** incluyendo inicialización del directorio de datos
* **Instalación de todas las dependencias** en el entorno virtual correcto
* **Modificación de la lógica de inicio** para evitar conexiones prematuras a la BD
* **Verificación completa** de todas las funcionalidades de la API

## Estructura de la Base de Datos

### Diagrama de Entidades

![Diagrama ER](DB.png)
*Diagrama ERD (Entity Relationship Diagram) de la API de Microcréditos*

### Descripción de las Relaciones

* **CLIENTES → PRÉSTAMOS**: Un cliente puede tener múltiples préstamos (1:N)
* **PRÉSTAMOS → PAGOS**: Un préstamo genera múltiples pagos/cuotas (1:N)
* **Restricciones**: 
  - `cliente_id` en PRESTAMOS referencia `id` en CLIENTES
  - `prestamo_id` en PAGOS referencia `id` en PRESTAMOS

### Tabla: CLIENTES
| Campo              | Tipo         | Restricciones           | Descripción                    |
|--------------------|--------------|-------------------------|--------------------------------|
| `id`               | SERIAL       | PRIMARY KEY             | Identificador único            |
| `nombre`           | VARCHAR(100) | NOT NULL                | Nombre del cliente             |
| `apellido`         | VARCHAR(100) | NOT NULL                | Apellido del cliente           |
| `email`            | VARCHAR(100) | NOT NULL, UNIQUE        | Email único del cliente        |
| `telefono`         | VARCHAR(20)  | NOT NULL                | Número de teléfono            |
| `direccion`        | TEXT         | NOT NULL                | Dirección completa             |
| `documento_identidad` | VARCHAR(20) | NOT NULL, UNIQUE        | DNI o documento único         |
| `fecha_registro`   | TIMESTAMP    | DEFAULT NOW()           | Fecha de registro automática   |
| `activo`           | BOOLEAN      | DEFAULT TRUE            | Estado activo/inactivo         |

### Tabla: PRÉSTAMOS
| Campo              | Tipo         | Restricciones           | Descripción                    |
|--------------------|--------------|-------------------------|--------------------------------|
| `id`               | SERIAL       | PRIMARY KEY             | Identificador único            |
| `cliente_id`       | INTEGER      | FOREIGN KEY, NOT NULL   | Referencia al cliente         |
| `monto`            | DECIMAL      | NOT NULL, > 0           | Monto del préstamo            |
| `tasa_interes`     | DECIMAL      | NOT NULL, > 0           | Tasa anual en porcentaje      |
| `plazo_meses`      | INTEGER      | NOT NULL, > 0           | Duración en meses             |
| `fecha_inicio`     | TIMESTAMP    | DEFAULT NOW()           | Fecha de inicio automática    |
| `fecha_vencimiento`| TIMESTAMP    | NOT NULL                | Fecha de vencimiento          |
| `estado`           | ENUM         | DEFAULT 'activo'        | Estado: activo/pagado/vencido |
| `saldo_pendiente`  | DECIMAL      | NOT NULL                | Saldo restante por pagar      |
| `cuota_mensual`    | DECIMAL      | NOT NULL                | Cuota mensual calculada       |

### Tabla: PAGOS
| Campo              | Tipo         | Restricciones           | Descripción                    |
|--------------------|--------------|-------------------------|--------------------------------|
| `id`               | SERIAL       | PRIMARY KEY             | Identificador único            |
| `prestamo_id`      | INTEGER      | FOREIGN KEY, NOT NULL   | Referencia al préstamo        |
| `monto`            | DECIMAL      | NOT NULL, > 0           | Monto del pago                |
| `fecha_pago`       | TIMESTAMP    | NULL                    | Fecha cuando se realizó       |
| `fecha_vencimiento`| TIMESTAMP    | NOT NULL                | Fecha límite de pago          |
| `estado`           | ENUM         | DEFAULT 'pendiente'     | Estado: pendiente/realizado   |
| `numero_cuota`     | INTEGER      | NOT NULL                | Número secuencial de cuota    |

### Enums Utilizados

#### EstadoPrestamo
* `activo`: Préstamo en curso con pagos pendientes
* `pagado`: Préstamo completamente saldado
* `vencido`: Préstamo con cuotas vencidas
* `cancelado`: Préstamo cancelado antes de completarse

#### EstadoPago
* `pendiente`: Cuota aún no pagada
* `realizado`: Cuota pagada correctamente
* `vencido`: Cuota vencida sin pago

### Relaciones y Restricciones

#### Clave Foránea: PRÉSTAMOS → CLIENTES
* `prestamos.cliente_id` → `clientes.id`
* Restricción: Un préstamo debe pertenecer a un cliente válido
* Comportamiento: CASCADE en eliminación (si se elimina cliente, se eliminan préstamos)

#### Clave Foránea: PAGOS → PRÉSTAMOS
* `pagos.prestamo_id` → `prestamos.id`
* Restricción: Un pago debe pertenecer a un préstamo válido
* Comportamiento: CASCADE en eliminación (si se elimina préstamo, se eliminan pagos)

### Índices y Optimización
* **Índice primario**: Todas las tablas tienen índice en `id`
* **Índice único**: `clientes.email`, `clientes.documento_identidad`
* **Índice de búsqueda**: `prestamos.cliente_id`, `pagos.prestamo_id`
* **Índice de estado**: `prestamos.estado`, `pagos.estado`

## Requisitos

* Python 3.8+
* PostgreSQL 12+
* pip (gestor de paquetes de Python)

## Instalación

### 1. Clonar el repositorio
```bash
git clone <url-del-repositorio>
cd API-REST
```

### 2. Crear entorno virtual
```bash
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar base de datos PostgreSQL

Crear una base de datos llamada `microcreditos`:
```sql
CREATE DATABASE microcreditos;
```

### 5. Configurar variables de entorno

Crear un archivo `.env` en la raíz del proyecto:
```env
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/microcreditos
```

O modificar directamente en `config/database.py`:
```python
DATABASE_URL = "postgresql://usuario:contraseña@localhost:5432/microcreditos"
```

### 6. Ejecutar migraciones (opcional)
```bash
alembic upgrade head
```

## Uso

### Ejecutar la aplicación

Opción A) uvicorn directamente (modo desarrollo)
```bash
uvicorn main:app --reload
```

Opción B) usando script de arranque (recomendado)
```bash
chmod +x start.sh
./start.sh
```

Requisitos para el script:
- PostgreSQL en ejecución en localhost:5432
- Base de datos `microcreditos` creada (el script la crea si no existe)
- Dependencias instaladas (el script las instala en `.venv`)

La API estará disponible en: http://localhost:8000

### Documentación automática
* **Swagger UI**: http://localhost:8000/docs
* **ReDoc**: http://localhost:8000/redoc

## Estructura del Proyecto

```
API-REST/
├── config/
│   └── database.py          # Configuración de base de datos
├── models/
│   ├── __init__.py
│   └── models.py            # Modelos SQLAlchemy
├── schemas/
│   ├── __init__.py
│   └── schemas.py           # Esquemas Pydantic
├── services/
│   ├── __init__.py
│   └── prestamo_service.py  # Lógica de negocio
├── routers/
│   ├── __init__.py
│   ├── clientes.py          # Endpoints de clientes
│   ├── prestamos.py         # Endpoints de préstamos
│   └── pagos.py             # Endpoints de pagos
├── docs/                    # Documentación técnica
│   ├── README.md            # Documentación del directorio
│   ├── database_diagram.png # Diagrama visual de la BD
│   └── database_diagram.md  # Diagrama en formato Mermaid
├── scripts/
│   ├── init_db.py           # Inicialización de BD
│   └── generate_diagram.py  # Generador de diagramas
├── main.py                  # Aplicación principal
├── requirements.txt         # Dependencias
├── alembic.ini             # Configuración de migraciones
└── README.md               # Este archivo
```

## Endpoints de la API

### Clientes (`/clientes`)
* `POST /` - Crear cliente
* `GET /` - Listar clientes
* `GET /{id}` - Obtener cliente por ID
* `GET /{id}/prestamos` - Obtener cliente con préstamos
* `PUT /{id}` - Actualizar cliente
* `DELETE /{id}` - Eliminar cliente (marcar como inactivo)

### Préstamos (`/prestamos`)
* `POST /` - Crear préstamo
* `GET /` - Listar préstamos
* `GET /{id}` - Obtener préstamo por ID
* `GET /{id}/detalle` - Obtener préstamo con pagos
* `PUT /{id}` - Actualizar préstamo
* `DELETE /{id}` - Cancelar préstamo
* `GET /{id}/saldo` - Obtener saldo pendiente
* `POST /{id}/actualizar-estado` - Actualizar estado del préstamo
* `POST /calcular-cuota` - Calcular cuota mensual

### Pagos (`/pagos`)
* `POST /` - Registrar pago
* `GET /` - Listar pagos
* `GET /{id}` - Obtener pago por ID
* `GET /prestamo/{id}` - Obtener pagos de un préstamo
* `PUT /{id}` - Actualizar pago
* `DELETE /{id}` - Eliminar pago
* `GET /resumen/prestamo/{id}` - Resumen de pagos de un préstamo

## Ejemplos de Uso

### Crear un cliente
```bash
curl -X POST "http://localhost:8000/clientes/" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Juan",
    "apellido": "Pérez",
    "email": "juan@example.com",
    "telefono": "123456789",
    "direccion": "Calle Principal 123",
    "documento_identidad": "12345678"
  }'
```

### Crear un préstamo
```bash
curl -X POST "http://localhost:8000/prestamos/" \
  -H "Content-Type: application/json" \
  -d '{
    "cliente_id": 1,
    "monto": 10000,
    "tasa_interes": 12.5,
    "plazo_meses": 12
  }'
```

### Registrar un pago
```bash
curl -X POST "http://localhost:8000/pagos/" \
  -H "Content-Type: application/json" \
  -d '{
    "prestamo_id": 1,
    "monto": 1000,
    "numero_cuota": 1
  }'
```

## Características Técnicas

* **FastAPI**: Framework web moderno y rápido
* **SQLAlchemy**: ORM para Python
* **PostgreSQL**: Base de datos robusta y escalable
* **Pydantic**: Validación de datos y serialización
* **Alembic**: Sistema de migraciones de base de datos
* **CORS**: Soporte para peticiones cross-origin
* **Documentación automática**: Generada automáticamente con OpenAPI

## Lógica de Negocio

### Cálculo de Cuotas
El sistema utiliza la **fórmula de amortización francesa** para calcular las cuotas mensuales:

```
Cuota = P × (r × (1 + r)^n) / ((1 + r)^n - 1)
```

Donde:
* `P` = Principal (monto del préstamo)
* `r` = Tasa de interés mensual (tasa anual ÷ 12)
* `n` = Número total de cuotas

### Generación Automática de Cuotas
Al crear un préstamo, el sistema:
1. Calcula la cuota mensual
2. Genera automáticamente todas las cuotas del préstamo
3. Establece fechas de vencimiento mensuales
4. Inicializa el estado como "pendiente"

### Control de Estados
* **Préstamo Activo**: Con cuotas pendientes y sin vencimientos
* **Préstamo Vencido**: Con cuotas vencidas sin pagar
* **Préstamo Pagado**: Saldo pendiente = 0
* **Préstamo Cancelado**: Marcado manualmente como cancelado

## Configuración de Desarrollo

### Variables de Entorno Recomendadas

Crear un archivo `.env` con las siguientes variables:

```env
# Base de datos
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/microcreditos
DATABASE_TEST_URL=postgresql://usuario:contraseña@localhost:5432/microcreditos_test

# Configuración de la aplicación
DEBUG=True
LOG_LEVEL=INFO
SECRET_KEY=tu_clave_secreta_aqui

# Configuración de CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080

# Configuración de rate limiting
RATE_LIMIT_PER_MINUTE=100
```

### Scripts de Desarrollo

Agregar estos scripts a tu `package.json` o crear scripts bash:

```bash
# Inicializar base de datos de desarrollo
./scripts/init_dev_db.sh

# Ejecutar tests
python -m pytest tests/

# Ejecutar linting
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

# Formatear código
black .

# Verificar tipos
mypy .
```

### Configuración de IDE

#### VS Code
Crear `.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": "./.venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false
}
```

#### PyCharm
* Configurar el intérprete de Python al entorno virtual
* Habilitar inspecciones de código
* Configurar pytest como framework de testing

## Testing

### Estructura de Tests

```
tests/
├── __init__.py
├── conftest.py              # Configuración de pytest
├── test_clientes.py         # Tests de endpoints de clientes
├── test_prestamos.py        # Tests de endpoints de préstamos
├── test_pagos.py           # Tests de endpoints de pagos
├── test_services.py        # Tests de servicios
└── test_models.py          # Tests de modelos
```

### Ejecutar Tests

```bash
# Ejecutar todos los tests
pytest

# Ejecutar tests con coverage
pytest --cov=app --cov-report=html

# Ejecutar tests específicos
pytest tests/test_clientes.py::test_crear_cliente

# Ejecutar tests en modo verbose
pytest -v

# Ejecutar tests y generar reporte
pytest --cov=app --cov-report=xml
```

### Tests de Integración

```python
# Ejemplo de test de integración
def test_crear_prestamo_completo(client, db_session):
    # Crear cliente
    cliente_data = {
        "nombre": "Test",
        "apellido": "User",
        "email": "test@example.com",
        "telefono": "123456789",
        "direccion": "Test Address",
        "documento_identidad": "12345678"
    }
    response = client.post("/clientes/", json=cliente_data)
    assert response.status_code == 200
    cliente_id = response.json()["id"]
    
    # Crear préstamo
    prestamo_data = {
        "cliente_id": cliente_id,
        "monto": 10000,
        "tasa_interes": 12.5,
        "plazo_meses": 12
    }
    response = client.post("/prestamos/", json=prestamo_data)
    assert response.status_code == 200
    prestamo_id = response.json()["id"]
    
    # Verificar que se generaron las cuotas
    response = client.get(f"/pagos/prestamo/{prestamo_id}")
    assert response.status_code == 200
    pagos = response.json()
    assert len(pagos) == 12  # 12 cuotas mensuales
```

## Troubleshooting

### Problemas Comunes

#### 1. Error de Conexión a PostgreSQL
```
Error: could not connect to server: Connection refused
```

**Solución:**
```bash
# Verificar si PostgreSQL está ejecutándose
sudo systemctl status postgresql

# Iniciar PostgreSQL si no está ejecutándose
sudo systemctl start postgresql

# Verificar configuración de conexión
psql -h localhost -U usuario -d microcreditos
```

#### 2. Error de Dependencias
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solución:**
```bash
# Activar entorno virtual
source .venv/bin/activate

# Reinstalar dependencias
pip install -r requirements.txt

# Verificar instalación
pip list | grep fastapi
```

#### 3. Error de Migraciones
```
alembic.util.exc.CommandError: Can't locate revision identified by 'head'
```

**Solución:**
```bash
# Inicializar Alembic
alembic init alembic

# Crear migración inicial
alembic revision --autogenerate -m "Initial migration"

# Aplicar migraciones
alembic upgrade head
```

#### 4. Error de Permisos de Base de Datos
```
permission denied for database microcreditos
```

**Solución:**
```sql
-- Conectar como superusuario
sudo -u postgres psql

-- Crear usuario y base de datos
CREATE USER mi_usuario WITH PASSWORD 'mi_password';
CREATE DATABASE microcreditos OWNER mi_usuario;
GRANT ALL PRIVILEGES ON DATABASE microcreditos TO mi_usuario;
```

#### 5. Error de CORS
```
Access to fetch at 'http://localhost:8000/clientes' from origin 'http://localhost:3000' has been blocked by CORS policy
```

**Solución:**
```python
# En main.py, configurar CORS correctamente
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Logs y Debugging

#### Habilitar Logs Detallados
```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

#### Verificar Estado de la Base de Datos
```sql
-- Verificar tablas existentes
\dt

-- Verificar datos en tablas
SELECT COUNT(*) FROM clientes;
SELECT COUNT(*) FROM prestamos;
SELECT COUNT(*) FROM pagos;

-- Verificar restricciones
SELECT conname, contype, pg_get_constraintdef(oid) 
FROM pg_constraint 
WHERE conrelid = 'clientes'::regclass;
```

## Deployment

### Docker

#### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Docker Compose
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/microcreditos
    depends_on:
      - db
    volumes:
      - .:/app

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=microcreditos
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

### Producción

#### Configuración de Producción
```python
# config/production.py
import os

DATABASE_URL = os.getenv("DATABASE_URL")
DEBUG = False
LOG_LEVEL = "WARNING"

# Configuración de seguridad
SECRET_KEY = os.getenv("SECRET_KEY")
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")

# Configuración de rate limiting
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
```

#### Variables de Entorno de Producción
```env
DATABASE_URL=postgresql://user:password@prod-db:5432/microcreditos
SECRET_KEY=tu_clave_secreta_muy_segura
DEBUG=False
LOG_LEVEL=WARNING
ALLOWED_HOSTS=api.tudominio.com,www.tudominio.com
RATE_LIMIT_PER_MINUTE=100
```

#### Comandos de Deployment
```bash
# Construir imagen Docker
docker build -t microcreditos-api .

# Ejecutar en producción
docker run -d \
  --name microcreditos-api \
  -p 8000:8000 \
  --env-file .env.production \
  microcreditos-api

# Usando Docker Compose
docker-compose -f docker-compose.prod.yml up -d
```

### Monitoreo y Logs

#### Configuración de Logs
```python
import logging
from logging.handlers import RotatingFileHandler

# Configurar logging para producción
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler('app.log', maxBytes=10000000, backupCount=5),
        logging.StreamHandler()
    ]
)
```

#### Health Check Endpoint
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }
```

## Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## Soporte

Para soporte técnico o preguntas, por favor abre un issue en el repositorio.