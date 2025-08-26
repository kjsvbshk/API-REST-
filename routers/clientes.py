from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from config.database import get_db
from models.models import Cliente, Prestamo, Pago
from schemas.schemas import ClienteCreate, ClienteUpdate, Cliente as ClienteSchema, ClienteConPrestamos
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/clientes", tags=["clientes"])

@router.post("/", response_model=ClienteSchema, status_code=status.HTTP_201_CREATED)
def crear_cliente(cliente: ClienteCreate, db: Session = Depends(get_db)):
    """
    Crear un nuevo cliente
    """
    try:
        db_cliente = Cliente(**cliente.dict())
        db.add(db_cliente)
        db.commit()
        db.refresh(db_cliente)
        return db_cliente
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email o documento de identidad ya existe"
        )

@router.get("/", response_model=List[ClienteSchema])
def obtener_clientes(
    skip: int = 0, 
    limit: int = 100, 
    activo: bool = True,  # Por defecto solo clientes activos
    db: Session = Depends(get_db)
):
    """
    Obtener lista de clientes con paginación y filtros
    Por defecto muestra solo clientes activos (activo=True)
    Para ver todos los clientes incluyendo inactivos, usar ?activo=
    """
    query = db.query(Cliente)
    
    if activo is not None:
        query = query.filter(Cliente.activo == activo)
    
    clientes = query.offset(skip).limit(limit).all()
    return clientes

@router.get("/{cliente_id}", response_model=ClienteSchema)
def obtener_cliente(cliente_id: int, db: Session = Depends(get_db)):
    """
    Obtener un cliente por ID
    """
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado"
        )
    return cliente

@router.get("/{cliente_id}/prestamos", response_model=ClienteConPrestamos)
def obtener_cliente_con_prestamos(cliente_id: int, db: Session = Depends(get_db)):
    """
    Obtener un cliente con todos sus préstamos
    """
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado"
        )
    return cliente

@router.put("/{cliente_id}", response_model=ClienteSchema)
def actualizar_cliente(
    cliente_id: int, 
    cliente_update: ClienteUpdate, 
    db: Session = Depends(get_db)
):
    """
    Actualizar un cliente existente
    """
    db_cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not db_cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado"
        )
    
    update_data = cliente_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_cliente, field, value)
    
    try:
        db.commit()
        db.refresh(db_cliente)
        return db_cliente
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error de integridad en los datos"
        )

@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_cliente(cliente_id: int, db: Session = Depends(get_db)):
    """
    Eliminar un cliente físicamente con eliminación en cascada
    """
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado"
        )
    
    try:
        # Eliminar pagos asociados a los préstamos del cliente
        prestamos_ids = db.query(Prestamo.id).filter(Prestamo.cliente_id == cliente_id).all()
        prestamos_ids = [p[0] for p in prestamos_ids]
        
        if prestamos_ids:
            # Eliminar pagos de los préstamos del cliente
            db.query(Pago).filter(Pago.prestamo_id.in_(prestamos_ids)).delete(synchronize_session=False)
            
            # Eliminar préstamos del cliente
            db.query(Prestamo).filter(Prestamo.cliente_id == cliente_id).delete(synchronize_session=False)
        
        # Eliminar el cliente
        db.delete(cliente)
        db.commit()
        
        return None
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar el cliente: {str(e)}"
        )
