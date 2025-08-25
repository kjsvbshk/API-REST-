from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from config.database import get_db
from models.models import Prestamo, Cliente
from schemas.schemas import PrestamoCreate, PrestamoUpdate, Prestamo as PrestamoSchema, PrestamoConPagos, CalculoCuota
from services.prestamo_service import PrestamoService

router = APIRouter(prefix="/prestamos", tags=["prestamos"])

@router.post("/", response_model=PrestamoSchema, status_code=status.HTTP_201_CREATED)
def crear_prestamo(prestamo: PrestamoCreate, db: Session = Depends(get_db)):
    """
    Crear un nuevo préstamo
    """
    # Verificar que el cliente existe
    cliente = db.query(Cliente).filter(Cliente.id == prestamo.cliente_id).first()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado"
        )
    
    if not cliente.activo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El cliente no está activo"
        )
    
    try:
        nuevo_prestamo = PrestamoService.crear_prestamo(db, prestamo)
        return nuevo_prestamo
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/", response_model=List[PrestamoSchema])
def obtener_prestamos(
    skip: int = 0, 
    limit: int = 100, 
    estado: str = None,
    cliente_id: int = None,
    db: Session = Depends(get_db)
):
    """
    Obtener lista de préstamos con filtros
    """
    query = db.query(Prestamo)
    
    if estado:
        query = query.filter(Prestamo.estado == estado)
    
    if cliente_id:
        query = query.filter(Prestamo.cliente_id == cliente_id)
    
    prestamos = query.offset(skip).limit(limit).all()
    return prestamos

@router.get("/{prestamo_id}", response_model=PrestamoSchema)
def obtener_prestamo(prestamo_id: int, db: Session = Depends(get_db)):
    """
    Obtener un préstamo por ID
    """
    prestamo = db.query(Prestamo).filter(Prestamo.id == prestamo_id).first()
    if not prestamo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Préstamo no encontrado"
        )
    return prestamo

@router.get("/{prestamo_id}/detalle", response_model=PrestamoConPagos)
def obtener_prestamo_con_pagos(prestamo_id: int, db: Session = Depends(get_db)):
    """
    Obtener un préstamo con todos sus pagos
    """
    prestamo = db.query(Prestamo).filter(Prestamo.id == prestamo_id).first()
    if not prestamo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Préstamo no encontrado"
        )
    return prestamo

@router.put("/{prestamo_id}", response_model=PrestamoSchema)
def actualizar_prestamo(
    prestamo_id: int, 
    prestamo_update: PrestamoUpdate, 
    db: Session = Depends(get_db)
):
    """
    Actualizar un préstamo existente
    """
    db_prestamo = db.query(Prestamo).filter(Prestamo.id == prestamo_id).first()
    if not db_prestamo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Préstamo no encontrado"
        )
    
    update_data = prestamo_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_prestamo, field, value)
    
    db.commit()
    db.refresh(db_prestamo)
    return db_prestamo

@router.delete("/{prestamo_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_prestamo(prestamo_id: int, db: Session = Depends(get_db)):
    """
    Cancelar un préstamo (marcar como cancelado)
    """
    prestamo = db.query(Prestamo).filter(Prestamo.id == prestamo_id).first()
    if not prestamo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Préstamo no encontrado"
        )
    
    if prestamo.estado in ["pagado", "cancelado"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede cancelar un préstamo ya pagado o cancelado"
        )
    
    prestamo.estado = "cancelado"
    db.commit()
    
    return None

@router.get("/{prestamo_id}/saldo", response_model=dict)
def obtener_saldo_prestamo(prestamo_id: int, db: Session = Depends(get_db)):
    """
    Obtener el saldo pendiente de un préstamo
    """
    prestamo = db.query(Prestamo).filter(Prestamo.id == prestamo_id).first()
    if not prestamo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Préstamo no encontrado"
        )
    
    saldo = PrestamoService.calcular_saldo_pendiente(db, prestamo_id)
    
    return {
        "prestamo_id": prestamo_id,
        "monto_original": prestamo.monto,
        "saldo_pendiente": saldo,
        "total_pagado": prestamo.monto - saldo,
        "estado": prestamo.estado
    }

@router.post("/{prestamo_id}/actualizar-estado", response_model=PrestamoSchema)
def actualizar_estado_prestamo(prestamo_id: int, db: Session = Depends(get_db)):
    """
    Actualizar el estado del préstamo basado en pagos y fechas
    """
    prestamo = db.query(Prestamo).filter(Prestamo.id == prestamo_id).first()
    if not prestamo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Préstamo no encontrado"
        )
    
    PrestamoService.actualizar_estado_prestamo(db, prestamo_id)
    
    # Refrescar el préstamo para obtener el estado actualizado
    db.refresh(prestamo)
    return prestamo

@router.post("/calcular-cuota", response_model=CalculoCuota)
def calcular_cuota(monto: float, tasa_interes: float, plazo_meses: int):
    """
    Calcular cuota mensual para un préstamo
    """
    try:
        calculo = PrestamoService.calcular_cuota_mensual(monto, tasa_interes, plazo_meses)
        return calculo
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
