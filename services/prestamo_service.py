from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from models.models import Prestamo, Pago, EstadoPrestamo, EstadoPago
from schemas.schemas import PrestamoCreate, CalculoCuota
import math

class PrestamoService:
    
    @staticmethod
    def calcular_cuota_mensual(monto: float, tasa_interes: float, plazo_meses: int) -> CalculoCuota:
        """
        Calcula la cuota mensual usando la fórmula de amortización francesa
        """
        # Convertir tasa anual a mensual
        tasa_mensual = tasa_interes / 100 / 12
        
        if tasa_mensual == 0:
            cuota_mensual = monto / plazo_meses
        else:
            # Fórmula de amortización francesa
            cuota_mensual = monto * (tasa_mensual * (1 + tasa_mensual) ** plazo_meses) / ((1 + tasa_mensual) ** plazo_meses - 1)
        
        total_a_pagar = cuota_mensual * plazo_meses
        total_intereses = total_a_pagar - monto
        
        return CalculoCuota(
            monto=monto,
            tasa_interes=tasa_interes,
            plazo_meses=plazo_meses,
            cuota_mensual=round(cuota_mensual, 2),
            total_a_pagar=round(total_a_pagar, 2),
            total_intereses=round(total_intereses, 2)
        )
    
    @staticmethod
    def crear_prestamo(db: Session, prestamo_data: PrestamoCreate) -> Prestamo:
        """
        Crea un nuevo préstamo y genera las cuotas automáticamente
        """
        # Calcular cuota mensual
        calculo = PrestamoService.calcular_cuota_mensual(
            prestamo_data.monto,
            prestamo_data.tasa_interes,
            prestamo_data.plazo_meses
        )
        
        # Calcular fecha de vencimiento
        fecha_vencimiento = datetime.now() + timedelta(days=prestamo_data.plazo_meses * 30)
        
        # Crear el préstamo
        prestamo = Prestamo(
            cliente_id=prestamo_data.cliente_id,
            monto=prestamo_data.monto,
            tasa_interes=prestamo_data.tasa_interes,
            plazo_meses=prestamo_data.plazo_meses,
            fecha_vencimiento=fecha_vencimiento,
            saldo_pendiente=prestamo_data.monto,
            cuota_mensual=calculo.cuota_mensual
        )
        
        db.add(prestamo)
        db.commit()
        db.refresh(prestamo)
        
        # Generar cuotas automáticamente
        PrestamoService.generar_cuotas(db, prestamo.id, calculo.cuota_mensual)
        
        return prestamo
    
    @staticmethod
    def generar_cuotas(db: Session, prestamo_id: int, cuota_mensual: float):
        """
        Genera las cuotas mensuales para un préstamo
        """
        prestamo = db.query(Prestamo).filter(Prestamo.id == prestamo_id).first()
        if not prestamo:
            return
        
        cuotas = []
        for i in range(prestamo.plazo_meses):
            fecha_vencimiento = prestamo.fecha_inicio + timedelta(days=(i + 1) * 30)
            cuota = Pago(
                prestamo_id=prestamo_id,
                monto=cuota_mensual,
                fecha_vencimiento=fecha_vencimiento,
                numero_cuota=i + 1
            )
            cuotas.append(cuota)
        
        db.add_all(cuotas)
        db.commit()
    
    @staticmethod
    def registrar_pago(db: Session, prestamo_id: int, monto: float, numero_cuota: int) -> Pago:
        """
        Registra un pago de cuota
        """
        # Buscar la cuota
        cuota = db.query(Pago).filter(
            Pago.prestamo_id == prestamo_id,
            Pago.numero_cuota == numero_cuota
        ).first()
        
        if not cuota:
            raise ValueError("Cuota no encontrada")
        
        if cuota.estado == EstadoPago.REALIZADO:
            raise ValueError("Esta cuota ya fue pagada")
        
        # Actualizar la cuota
        cuota.estado = EstadoPago.REALIZADO
        cuota.fecha_pago = datetime.now()
        
        # Actualizar saldo pendiente del préstamo
        prestamo = db.query(Prestamo).filter(Prestamo.id == prestamo_id).first()
        prestamo.saldo_pendiente -= monto
        
        # Verificar si el préstamo está completamente pagado
        if prestamo.saldo_pendiente <= 0:
            prestamo.estado = EstadoPrestamo.PAGADO
            prestamo.saldo_pendiente = 0
        
        db.commit()
        db.refresh(cuota)
        
        return cuota
    
    @staticmethod
    def calcular_saldo_pendiente(db: Session, prestamo_id: int) -> float:
        """
        Calcula el saldo pendiente de un préstamo
        """
        prestamo = db.query(Prestamo).filter(Prestamo.id == prestamo_id).first()
        if not prestamo:
            return 0
        
        # Calcular total pagado
        total_pagado = db.query(Pago).filter(
            Pago.prestamo_id == prestamo_id,
            Pago.estado == EstadoPago.REALIZADO
        ).with_entities(func.sum(Pago.monto)).scalar() or 0
        
        saldo_pendiente = prestamo.monto - total_pagado
        return max(0, saldo_pendiente)
    
    @staticmethod
    def actualizar_estado_prestamo(db: Session, prestamo_id: int):
        """
        Actualiza el estado del préstamo basado en pagos y fechas
        """
        prestamo = db.query(Prestamo).filter(Prestamo.id == prestamo_id).first()
        if not prestamo:
            return
        
        # Verificar si está pagado
        if prestamo.saldo_pendiente <= 0:
            prestamo.estado = EstadoPrestamo.PAGADO
            db.commit()
            return
        
        # Verificar si está vencido
        if datetime.now() > prestamo.fecha_vencimiento:
            prestamo.estado = EstadoPrestamo.VENCIDO
            db.commit()
            return
        
        # Verificar cuotas vencidas
        cuotas_vencidas = db.query(Pago).filter(
            Pago.prestamo_id == prestamo_id,
            Pago.fecha_vencimiento < datetime.now(),
            Pago.estado == EstadoPago.PENDIENTE
        ).count()
        
        if cuotas_vencidas > 0:
            prestamo.estado = EstadoPrestamo.VENCIDO
        else:
            prestamo.estado = EstadoPrestamo.ACTIVO
        
        db.commit()
