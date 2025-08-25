from .schemas import (
    ClienteCreate, ClienteUpdate, Cliente,
    PrestamoCreate, PrestamoUpdate, Prestamo,
    PagoCreate, PagoUpdate, Pago,
    ClienteConPrestamos, PrestamoConPagos, CalculoCuota
)

__all__ = [
    "ClienteCreate", "ClienteUpdate", "Cliente",
    "PrestamoCreate", "PrestamoUpdate", "Prestamo",
    "PagoCreate", "PagoUpdate", "Pago",
    "ClienteConPrestamos", "PrestamoConPagos", "CalculoCuota"
]
