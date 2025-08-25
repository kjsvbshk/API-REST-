#!/usr/bin/env python3
"""
Script de inicialización de la base de datos
Crea las tablas y agrega datos de ejemplo
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from config.database import engine, SessionLocal
from models.models import Base, Cliente, Prestamo, Pago, EstadoPrestamo, EstadoPago
from datetime import datetime, timedelta

def init_database():
    """Inicializa la base de datos creando las tablas"""
    print("🗃️  Creando tablas en la base de datos...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas creadas correctamente")

def create_sample_data():
    """Crea datos de ejemplo para la aplicación"""
    db = SessionLocal()
    
    try:
        # Verificar si ya hay datos
        if db.query(Cliente).count() > 0:
            print("ℹ️  La base de datos ya contiene datos, saltando creación de ejemplos")
            return
        
        print("📝 Creando datos de ejemplo...")
        
        # Crear clientes de ejemplo
        clientes = [
            Cliente(
                nombre="Juan",
                apellido="Pérez",
                email="juan.perez@email.com",
                telefono="123456789",
                direccion="Calle Principal 123, Ciudad",
                documento_identidad="12345678"
            ),
            Cliente(
                nombre="María",
                apellido="García",
                email="maria.garcia@email.com",
                telefono="987654321",
                direccion="Avenida Central 456, Ciudad",
                documento_identidad="87654321"
            ),
            Cliente(
                nombre="Carlos",
                apellido="López",
                email="carlos.lopez@email.com",
                telefono="555666777",
                direccion="Plaza Mayor 789, Ciudad",
                documento_identidad="11223344"
            )
        ]
        
        for cliente in clientes:
            db.add(cliente)
        
        db.commit()
        print(f"✅ {len(clientes)} clientes creados")
        
        # Crear préstamos de ejemplo
        prestamos = [
            Prestamo(
                cliente_id=1,
                monto=5000.0,
                tasa_interes=12.5,
                plazo_meses=12,
                fecha_vencimiento=datetime.now() + timedelta(days=365),
                saldo_pendiente=5000.0,
                cuota_mensual=450.0
            ),
            Prestamo(
                cliente_id=2,
                monto=10000.0,
                tasa_interes=15.0,
                plazo_meses=24,
                fecha_vencimiento=datetime.now() + timedelta(days=730),
                saldo_pendiente=10000.0,
                cuota_mensual=485.0
            )
        ]
        
        for prestamo in prestamos:
            db.add(prestamo)
        
        db.commit()
        print(f"✅ {len(prestamos)} préstamos creados")
        
        # Crear pagos de ejemplo
        pagos = [
            Pago(
                prestamo_id=1,
                monto=450.0,
                fecha_vencimiento=datetime.now() + timedelta(days=30),
                numero_cuota=1
            ),
            Pago(
                prestamo_id=1,
                monto=450.0,
                fecha_vencimiento=datetime.now() + timedelta(days=60),
                numero_cuota=2
            ),
            Pago(
                prestamo_id=2,
                monto=485.0,
                fecha_vencimiento=datetime.now() + timedelta(days=30),
                numero_cuota=1
            )
        ]
        
        for pago in pagos:
            db.add(pago)
        
        db.commit()
        print(f"✅ {len(pagos)} pagos creados")
        
        print("🎉 Datos de ejemplo creados exitosamente")
        
    except Exception as e:
        print(f"❌ Error al crear datos de ejemplo: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    """Función principal"""
    print("🚀 Inicializando base de datos...")
    
    try:
        init_database()
        create_sample_data()
        print("✅ Inicialización completada exitosamente")
    except Exception as e:
        print(f"❌ Error durante la inicialización: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
