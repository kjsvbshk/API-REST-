# API de Microcréditos

Sistema de gestión de microcréditos desarrollado con FastAPI y PostgreSQL, que permite gestionar clientes, préstamos y pagos con cálculo automático de intereses y cuotas.

## Características

- **Gestión de Clientes**: Registro, consulta, actualización y eliminación de clientes
- **Gestión de Préstamos**: Creación de préstamos con cálculo automático de cuotas e intereses
- **Sistema de Pagos**: Registro y seguimiento de pagos de cuotas
- **Cálculos Automáticos**: Cálculo de cuotas mensuales, saldos pendientes y estados
- **API REST Completa**: Endpoints para todas las operaciones CRUD
- **Base de Datos PostgreSQL**: Con ORM SQLAlchemy y migraciones Alembic

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

- **Actualización de dependencias** a versiones compatibles con Python 3.13
- **Configuración completa de PostgreSQL** incluyendo inicialización del directorio de datos
- **Instalación de todas las dependencias** en el entorno virtual correcto
- **Modificación de la lógica de inicio** para evitar conexiones prematuras a la BD
- **Verificación completa** de todas las funcionalidades de la API

## Estructura de la Base de Datos

### Diagrama de Entidades
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     CLIENTES    │    │    PRÉSTAMOS    │    │      PAGOS      │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ id (PK)         │    │ id (PK)         │    │ id (PK)         │
│ nombre          │    │ cliente_id (FK) │    │ prestamo_id(FK) │
│ apellido        │    │ monto           │    │ monto           │
│ email (UNIQUE)  │    │ tasa_interes    │    │ fecha_pago      │
│ telefono        │    │ plazo_meses     │    │ fecha_vencim.   │
│ direccion       │    │ fecha_inicio    │    │ estado          │
│ documento_id    │    │ fecha_vencim.   │    │ numero_cuota    │
│ fecha_registro  │    │ estado          │    └─────────────────┘
│ activo          │    │ saldo_pendiente │
└─────────────────┘    │ cuota_mensual   │
         │              └─────────────────┘
         │                       │
         └───────────────────────┘
```

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
- `activo`: Préstamo en curso con pagos pendientes
- `pagado`: Préstamo completamente saldado
- `vencido`: Préstamo con cuotas vencidas
- `cancelado`: Préstamo cancelado antes de completarse

#### EstadoPago
- `pendiente`: Cuota aún no pagada
- `realizado`: Cuota pagada correctamente
- `vencido`: Cuota vencida sin pago

### Relaciones y Restricciones

#### Clave Foránea: PRÉSTAMOS → CLIENTES
- `prestamos.cliente_id` → `clientes.id`
- Restricción: Un préstamo debe pertenecer a un cliente válido
- Comportamiento: CASCADE en eliminación (si se elimina cliente, se eliminan préstamos)

#### Clave Foránea: PAGOS → PRÉSTAMOS
- `pagos.prestamo_id` → `prestamos.id`
- Restricción: Un pago debe pertenecer a un préstamo válido
- Comportamiento: CASCADE en eliminación (si se elimina préstamo, se eliminan pagos)

### Índices y Optimización
- **Índice primario**: Todas las tablas tienen índice en `id`
- **Índice único**: `clientes.email`, `clientes.documento_identidad`
- **Índice de búsqueda**: `prestamos.cliente_id`, `pagos.prestamo_id`
- **Índice de estado**: `prestamos.estado`, `pagos.estado`

## Requisitos

- Python 3.8+
- PostgreSQL 12+
- pip (gestor de paquetes de Python)

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
```bash
uvicorn main:app --reload
```

La API estará disponible en: http://localhost:8000

### Documentación automática
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

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
├── main.py                  # Aplicación principal
├── requirements.txt         # Dependencias
├── alembic.ini             # Configuración de migraciones
└── README.md               # Este archivo
```

## Endpoints de la API

### Clientes (`/clientes`)
- `POST /` - Crear cliente
- `GET /` - Listar clientes
- `GET /{id}` - Obtener cliente por ID
- `GET /{id}/prestamos` - Obtener cliente con préstamos
- `PUT /{id}` - Actualizar cliente
- `DELETE /{id}` - Eliminar cliente (marcar como inactivo)

### Préstamos (`/prestamos`)
- `POST /` - Crear préstamo
- `GET /` - Listar préstamos
- `GET /{id}` - Obtener préstamo por ID
- `GET /{id}/detalle` - Obtener préstamo con pagos
- `PUT /{id}` - Actualizar préstamo
- `DELETE /{id}` - Cancelar préstamo
- `GET /{id}/saldo` - Obtener saldo pendiente
- `POST /{id}/actualizar-estado` - Actualizar estado del préstamo
- `POST /calcular-cuota` - Calcular cuota mensual

### Pagos (`/pagos`)
- `POST /` - Registrar pago
- `GET /` - Listar pagos
- `GET /{id}` - Obtener pago por ID
- `GET /prestamo/{id}` - Obtener pagos de un préstamo
- `PUT /{id}` - Actualizar pago
- `DELETE /{id}` - Eliminar pago
- `GET /resumen/prestamo/{id}` - Resumen de pagos de un préstamo

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

- **FastAPI**: Framework web moderno y rápido
- **SQLAlchemy**: ORM para Python
- **PostgreSQL**: Base de datos robusta y escalable
- **Pydantic**: Validación de datos y serialización
- **Alembic**: Sistema de migraciones de base de datos
- **CORS**: Soporte para peticiones cross-origin
- **Documentación automática**: Generada automáticamente con OpenAPI

## Lógica de Negocio

### Cálculo de Cuotas
El sistema utiliza la **fórmula de amortización francesa** para calcular las cuotas mensuales:

```
Cuota = P × (r × (1 + r)^n) / ((1 + r)^n - 1)
```

Donde:
- `P` = Principal (monto del préstamo)
- `r` = Tasa de interés mensual (tasa anual ÷ 12)
- `n` = Número total de cuotas

### Generación Automática de Cuotas
Al crear un préstamo, el sistema:
1. Calcula la cuota mensual
2. Genera automáticamente todas las cuotas del préstamo
3. Establece fechas de vencimiento mensuales
4. Inicializa el estado como "pendiente"

### Control de Estados
- **Préstamo Activo**: Con cuotas pendientes y sin vencimientos
- **Préstamo Vencido**: Con cuotas vencidas sin pagar
- **Préstamo Pagado**: Saldo pendiente = 0
- **Préstamo Cancelado**: Marcado manualmente como cancelado

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
