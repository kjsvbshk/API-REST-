#!/usr/bin/env python3
"""
Script para inicializar la base de datos con datos de ejemplo
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from config.database import SessionLocal, engine
from models.models import Base, Cliente, Prestamo, Pago, EstadoPrestamo, EstadoPago
from services.prestamo_service import PrestamoService
from datetime import datetime, timedelta

def init_db():
    """Inicializar la base de datos con datos de ejemplo"""
    
    # Crear todas las tablas
    Base.metadata.create_all(bind=engine)
    
    # Crear sesión de base de datos
    db = SessionLocal()
    
    try:
        # Verificar si ya hay datos
        if db.query(Cliente).count() > 0:
            print("La base de datos ya contiene datos. Saltando inicialización.")
            return
        
        print("Creando datos de ejemplo...")
        
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
                documento_identidad="55556666"
            )
        ]
        
        for cliente in clientes:
            db.add(cliente)
        
        db.commit()
        print(f"✓ {len(clientes)} clientes creados")
        
        # Crear préstamos de ejemplo
        prestamos = [
            {
                "cliente_id": 1,
                "monto": 5000,
                "tasa_interes": 12.5,
                "plazo_meses": 6
            },
            {
                "cliente_id": 2,
                "monto": 10000,
                "tasa_interes": 15.0,
                "plazo_meses": 12
            },
            {
                "cliente_id": 3,
                "monto": 7500,
                "tasa_interes": 10.0,
                "plazo_meses": 8
            }
        ]
        
        for prestamo_data in prestamos:
            try:
                prestamo = PrestamoService.crear_prestamo(db, prestamo_data)
                print(f"✓ Préstamo creado para cliente {prestamo_data['cliente_id']}: ${prestamo_data['monto']}")
            except Exception as e:
                print(f"✗ Error creando préstamo: {e}")
        
        # Registrar algunos pagos de ejemplo
        pagos_ejemplo = [
            {"prestamo_id": 1, "monto": 1000, "numero_cuota": 1},
            {"prestamo_id": 1, "monto": 1000, "numero_cuota": 2},
            {"prestamo_id": 2, "monto": 1200, "numero_cuota": 1},
        ]
        
        for pago_data in pagos_ejemplo:
            try:
                pago = PrestamoService.registrar_pago(
                    db, 
                    pago_data["prestamo_id"], 
                    pago_data["monto"], 
                    pago_data["numero_cuota"]
                )
                print(f"✓ Pago registrado: ${pago_data['monto']} para préstamo {pago_data['prestamo_id']}")
            except Exception as e:
                print(f"✗ Error registrando pago: {e}")
        
        print("\n✅ Base de datos inicializada exitosamente!")
        print("\nDatos creados:")
        print(f"- {db.query(Cliente).count()} clientes")
        print(f"- {db.query(Prestamo).count()} préstamos")
        print(f"- {db.query(Pago).count()} pagos")
        
    except Exception as e:
        print(f"Error durante la inicialización: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
