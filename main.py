from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.database import engine
from models.models import Base
from routers import clientes, prestamos, pagos

app = FastAPI(
    title="API de Microcréditos",
    description="Sistema de gestión de microcréditos con FastAPI y PostgreSQL",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir los routers
app.include_router(clientes.router)
app.include_router(prestamos.router)
app.include_router(pagos.router)

@app.on_event("startup")
async def startup_event():
    """Crear las tablas al iniciar la aplicación"""
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Base de datos inicializada correctamente")
    except Exception as e:
        print(f"⚠️  Error al conectar con la base de datos: {e}")
        print("   Asegúrate de que PostgreSQL esté ejecutándose")

@app.get("/")
def read_root():
    return {
        "message": "API de Microcréditos",
        "version": "1.0.0",
        "endpoints": {
            "clientes": "/clientes",
            "prestamos": "/prestamos",
            "pagos": "/pagos",
            "documentacion": "/docs"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "API funcionando correctamente"}