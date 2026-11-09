import uuid
from datetime import date, datetime, timezone
from typing import Optional

from sqlalchemy import (
    JSON, Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text, Uuid
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def ahora():
    return datetime.now(timezone.utc)


class SyncMixin:
    """Campos comunes para poder sincronizar con la app móvil."""
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=ahora)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=ahora, onupdate=ahora)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class Puerca(SyncMixin, Base):
    __tablename__ = "puercas"
    nombre: Mapped[str] = mapped_column(String(100))
    id_unico: Mapped[str] = mapped_column(String(50), unique=True)
    raza: Mapped[str] = mapped_column(String(50), default="Criolla")
    fecha_ingreso: Mapped[date] = mapped_column(Date)
    estado: Mapped[str] = mapped_column(String(30), default="disponible")


class Inseminacion(SyncMixin, Base):
    __tablename__ = "inseminaciones"
    puerca_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("puercas.id"), nullable=True)
    fecha_inseminacion: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    tipo: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    fecha_probable_parto: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    estado: Mapped[str] = mapped_column(String(30), default="activa")


class Parto(SyncMixin, Base):
    __tablename__ = "partos"
    puerca_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("puercas.id"))
    fecha_parto: Mapped[date] = mapped_column(Date)
    cantidad_lechones: Mapped[int] = mapped_column(Integer)


class Lechon(SyncMixin, Base):
    __tablename__ = "lechones"
    puerca_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("puercas.id"))
    parto_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("partos.id"))
    fecha_nacimiento: Mapped[date] = mapped_column(Date)
    peso_kg: Mapped[float] = mapped_column(Float, default=0)
    estado: Mapped[str] = mapped_column(String(30), default="disponible")
    precio_venta: Mapped[float] = mapped_column(Float, default=0)
    fecha_venta: Mapped[Optional[date]] = mapped_column(Date, nullable=True)


class Engorde(SyncMixin, Base):
    __tablename__ = "engorde"
    id_cerdo: Mapped[str] = mapped_column(String(50), unique=True)
    lechon_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("lechones.id"), nullable=True)
    peso_individual_kg: Mapped[float] = mapped_column(Float)
    peso_lote_kg: Mapped[float] = mapped_column(Float)
    precio_mercado_kg: Mapped[float] = mapped_column(Float)
    fecha_registro: Mapped[date] = mapped_column(Date)
    estado: Mapped[str] = mapped_column(String(30), default="en_engorde")
    fecha_venta: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    precio_venta_total: Mapped[float] = mapped_column(Float, default=0)


class Gasto(SyncMixin, Base):
    __tablename__ = "gastos"
    seccion: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    categoria: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    monto: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    fecha: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    notas: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class Ingreso(SyncMixin, Base):
    __tablename__ = "ingresos"
    seccion: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    concepto: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    monto: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    fecha: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    notas: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class Alimento(SyncMixin, Base):
    __tablename__ = "alimentos"
    nombre: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    tipo: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    unidad: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)


class Alimentacion(SyncMixin, Base):
    __tablename__ = "alimentacion"
    seccion: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    alimento_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("alimentos.id"), nullable=True)
    cantidad: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    precio_unidad: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    total: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    fecha: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    notas: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class Medicamento(SyncMixin, Base):
    __tablename__ = "medicamentos"
    seccion: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    animal_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    nombre: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    tipo: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    unidad: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    dosis_por_kg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    peso_animal_kg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    dosis_total: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    frecuencia: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    dias: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    fecha_inicio: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    proxima_dosis: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    fechas_json: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    costo: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    aplicado: Mapped[bool] = mapped_column(Boolean, default=False)


class Empleado(SyncMixin, Base):
    __tablename__ = "empleados"
    nombre: Mapped[str] = mapped_column(String(100))
    tipo_pago: Mapped[str] = mapped_column(String(20))  # 'fijo' o 'por_dia'
    salario_base: Mapped[float] = mapped_column(Float)
    fecha_contrato: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)


class PagoEmpleado(SyncMixin, Base):
    __tablename__ = "pagos_empleados"
    empleado_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("empleados.id"), nullable=True)
    monto: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    fecha: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    concepto: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)


class Actividad(SyncMixin, Base):
    __tablename__ = "actividades"
    titulo: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    fecha: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    estado: Mapped[str] = mapped_column(String(30), default="pendiente")
    responsable: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)


class Venta(SyncMixin, Base):
    __tablename__ = "ventas"
    tipo_animal: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    animal_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    cantidad: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    peso_kg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    precio_unit: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    total: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    fecha: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    comprador: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    notas: Mapped[Optional[str]] = mapped_column(Text, nullable=True)