from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime
from models.models import EstadoPrestamo, EstadoPago

# Esquemas para Cliente
class ClienteBase(BaseModel):
    nombre: str
    apellido: str
    email: EmailStr
    telefono: str
    direccion: str
    documento_identidad: str

class ClienteCreate(ClienteBase):
    pass

class ClienteUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    email: Optional[EmailStr] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    activo: Optional[bool] = None

class Cliente(ClienteBase):
    id: int
    fecha_registro: datetime
    activo: bool
    
    class Config:
        from_attributes = True

# Esquemas para Préstamo
class PrestamoBase(BaseModel):
    cliente_id: int
    monto: float
    tasa_interes: float
    plazo_meses: int
    
    @validator('monto')
    def monto_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('El monto debe ser mayor a 0')
        return v
    
    @validator('tasa_interes')
    def tasa_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('La tasa de interés debe ser mayor a 0')
        return v
    
    @validator('plazo_meses')
    def plazo_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('El plazo debe ser mayor a 0')
        return v

class PrestamoCreate(PrestamoBase):
    pass

class PrestamoUpdate(BaseModel):
    estado: Optional[EstadoPrestamo] = None
    saldo_pendiente: Optional[float] = None

class Prestamo(PrestamoBase):
    id: int
    fecha_inicio: datetime
    fecha_vencimiento: datetime
    estado: EstadoPrestamo
    saldo_pendiente: float
    cuota_mensual: float
    cliente: Cliente
    
    class Config:
        from_attributes = True

# Esquemas para Pago
class PagoBase(BaseModel):
    prestamo_id: int
    monto: float
    fecha_vencimiento: datetime
    numero_cuota: int
    
    @validator('monto')
    def monto_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('El monto debe ser mayor a 0')
        return v

class PagoCreate(PagoBase):
    pass

class PagoUpdate(BaseModel):
    estado: Optional[EstadoPago] = None
    fecha_pago: Optional[datetime] = None

class Pago(PagoBase):
    id: int
    fecha_pago: Optional[datetime]
    estado: EstadoPago
    
    class Config:
        from_attributes = True

# Esquemas para respuestas
class PrestamoConPagos(Prestamo):
    pagos: List[Pago]

class ClienteConPrestamos(Cliente):
    prestamos: List[Prestamo]

# Esquemas para cálculos
class CalculoCuota(BaseModel):
    monto: float
    tasa_interes: float
    plazo_meses: int
    cuota_mensual: float
    total_a_pagar: float
    total_intereses: float
