from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from config.database import get_db
from models.models import Pago, Prestamo
from schemas.schemas import PagoCreate, PagoUpdate, Pago as PagoSchema
from services.prestamo_service import PrestamoService
from sqlalchemy import func

router = APIRouter(prefix="/pagos", tags=["pagos"])

@router.post("/", response_model=PagoSchema, status_code=status.HTTP_201_CREATED)
def registrar_pago(
    pago_data: PagoCreate,
    db: Session = Depends(get_db)
):
    """
    Registrar un pago de cuota
    """
    # Verificar que el préstamo existe
    prestamo = db.query(Prestamo).filter(Prestamo.id == pago_data.prestamo_id).first()
    if not prestamo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Préstamo no encontrado"
        )
    
    if prestamo.estado in ["pagado", "cancelado"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pueden registrar pagos en un préstamo pagado o cancelado"
        )
    
    try:
        pago = PrestamoService.registrar_pago(
            db, 
            pago_data.prestamo_id, 
            pago_data.monto, 
            pago_data.numero_cuota
        )
        return pago
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/", response_model=List[PagoSchema])
def obtener_pagos(
    skip: int = 0, 
    limit: int = 100, 
    prestamo_id: int = None,
    estado: str = None,
    db: Session = Depends(get_db)
):
    """
    Obtener lista de pagos con filtros
    """
    query = db.query(Pago)
    
    if prestamo_id:
        query = query.filter(Pago.prestamo_id == prestamo_id)
    
    if estado:
        query = query.filter(Pago.estado == estado)
    
    pagos = query.offset(skip).limit(limit).all()
    return pagos

@router.get("/{pago_id}", response_model=PagoSchema)
def obtener_pago(pago_id: int, db: Session = Depends(get_db)):
    """
    Obtener un pago por ID
    """
    pago = db.query(Pago).filter(Pago.id == pago_id).first()
    if not pago:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pago no encontrado"
        )
    return pago

@router.get("/prestamo/{prestamo_id}", response_model=List[PagoSchema])
def obtener_pagos_prestamo(prestamo_id: int, db: Session = Depends(get_db)):
    """
    Obtener todos los pagos de un préstamo específico
    """
    # Verificar que el préstamo existe
    prestamo = db.query(Prestamo).filter(Prestamo.id == prestamo_id).first()
    if not prestamo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Préstamo no encontrado"
        )
    
    pagos = db.query(Pago).filter(Pago.prestamo_id == prestamo_id).all()
    return pagos

@router.put("/{pago_id}", response_model=PagoSchema)
def actualizar_pago(
    pago_id: int, 
    pago_update: PagoUpdate, 
    db: Session = Depends(get_db)
):
    """
    Actualizar un pago existente
    """
    db_pago = db.query(Pago).filter(Pago.id == pago_id).first()
    if not db_pago:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pago no encontrado"
        )
    
    # Solo permitir actualizar el estado si no está realizado
    if db_pago.estado == "realizado":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede modificar un pago ya realizado"
        )
    
    update_data = pago_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_pago, field, value)
    
    db.commit()
    db.refresh(db_pago)
    return db_pago

@router.delete("/{pago_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_pago(pago_id: int, db: Session = Depends(get_db)):
    """
    Eliminar un pago (solo si no está realizado)
    """
    pago = db.query(Pago).filter(Pago.id == pago_id).first()
    if not pago:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pago no encontrado"
        )
    
    if pago.estado == "realizado":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar un pago ya realizado"
        )
    
    db.delete(pago)
    db.commit()
    
    return None

@router.get("/resumen/prestamo/{prestamo_id}", response_model=dict)
def obtener_resumen_pagos_prestamo(prestamo_id: int, db: Session = Depends(get_db)):
    """
    Obtener resumen de pagos de un préstamo
    """
    # Verificar que el préstamo existe
    prestamo = db.query(Prestamo).filter(Prestamo.id == prestamo_id).first()
    if not prestamo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Préstamo no encontrado"
        )
    
    # Obtener estadísticas de pagos
    total_pagos = db.query(Pago).filter(
        Pago.prestamo_id == prestamo_id,
        Pago.estado == "realizado"
    ).count()
    
    total_pagado = db.query(Pago).filter(
        Pago.prestamo_id == prestamo_id,
        Pago.estado == "realizado"
    ).with_entities(func.sum(Pago.monto)).scalar() or 0
    
    pagos_pendientes = db.query(Pago).filter(
        Pago.prestamo_id == prestamo_id,
        Pago.estado == "pendiente"
    ).count()
    
    pagos_vencidos = db.query(Pago).filter(
        Pago.prestamo_id == prestamo_id,
        Pago.estado == "vencido"
    ).count()
    
    return {
        "prestamo_id": prestamo_id,
        "monto_original": prestamo.monto,
        "total_pagado": total_pagado,
        "saldo_pendiente": prestamo.monto - total_pagado,
        "cuotas_pagadas": total_pagos,
        "cuotas_pendientes": pagos_pendientes,
        "cuotas_vencidas": pagos_vencidos,
        "estado_prestamo": prestamo.estado
    }
