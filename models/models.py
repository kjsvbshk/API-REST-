from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.database import Base
import enum

class EstadoPrestamo(str, enum.Enum):
    ACTIVO = "activo"
    PAGADO = "pagado"
    VENCIDO = "vencido"
    CANCELADO = "cancelado"

class EstadoPago(str, enum.Enum):
    PENDIENTE = "pendiente"
    REALIZADO = "realizado"
    VENCIDO = "vencido"

class Cliente(Base):
    __tablename__ = "clientes"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    telefono = Column(String(20), nullable=False)
    direccion = Column(Text, nullable=False)
    documento_identidad = Column(String(20), unique=True, nullable=False)
    fecha_registro = Column(DateTime(timezone=True), server_default=func.now())
    activo = Column(Boolean, default=True)
    
    # Relaciones
    prestamos = relationship("Prestamo", back_populates="cliente")

class Prestamo(Base):
    __tablename__ = "prestamos"
    
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    monto = Column(Float, nullable=False)
    tasa_interes = Column(Float, nullable=False)  # Tasa anual en porcentaje
    plazo_meses = Column(Integer, nullable=False)
    fecha_inicio = Column(DateTime(timezone=True), server_default=func.now())
    fecha_vencimiento = Column(DateTime(timezone=True), nullable=False)
    estado = Column(Enum(EstadoPrestamo), default=EstadoPrestamo.ACTIVO)
    saldo_pendiente = Column(Float, nullable=False)
    cuota_mensual = Column(Float, nullable=False)
    
    # Relaciones
    cliente = relationship("Cliente", back_populates="prestamos")
    pagos = relationship("Pago", back_populates="prestamo")

class Pago(Base):
    __tablename__ = "pagos"
    
    id = Column(Integer, primary_key=True, index=True)
    prestamo_id = Column(Integer, ForeignKey("prestamos.id"), nullable=False)
    monto = Column(Float, nullable=False)
    fecha_pago = Column(DateTime(timezone=True), server_default=func.now())
    fecha_vencimiento = Column(DateTime(timezone=True), nullable=False)
    estado = Column(Enum(EstadoPago), default=EstadoPago.PENDIENTE)
    numero_cuota = Column(Integer, nullable=False)
    
    # Relaciones
    prestamo = relationship("Prestamo", back_populates="pagos")
