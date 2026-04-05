from database.models import (
    obtener_gastos_por_seccion,
    obtener_ingresos_por_seccion,
    obtener_resumen_general,
    promedio_lechones_por_puerca
)

# ENGORDE 

def calcular_ganancia_estimada(peso_lote_kg, precio_mercado_kg):
    """Calcula la ganancia potencial antes de descontar gastos"""
    return peso_lote_kg * precio_mercado_kg

def calcular_ganancia_real(peso_lote_kg, precio_mercado_kg, seccion="engorde"):
    """Calcula la ganancia real descontando gastos de alimentación"""
    ganancia_bruta = calcular_ganancia_estimada(peso_lote_kg, precio_mercado_kg)
    gastos = obtener_gastos_por_seccion(seccion)
    total_gastos = sum(g["monto"] for g in gastos)
    return ganancia_bruta - total_gastos

def calcular_valor_inventario(cerdos):
    """Calcula el valor total del inventario de engorde"""
    total = 0
    for cerdo in cerdos:
        total += cerdo["peso_lote_kg"] * cerdo["precio_mercado_kg"]
    return total

# PUERCAS Y LECHONES 

def calcular_rentabilidad_puercas_lechones():
    """
    Calcula rentabilidad combinada de puercas + lechones.
    Las puercas no se venden, su costo se descuenta de
    los ingresos por venta de lechones.
    """
    gastos_puercas = obtener_gastos_por_seccion("puercas")
    gastos_lechones = obtener_gastos_por_seccion("lechones")
    ingresos_lechones = obtener_ingresos_por_seccion("lechones")

    total_gastos = sum(g["monto"] for g in gastos_puercas) + \
                   sum(g["monto"] for g in gastos_lechones)
    total_ingresos = sum(i["monto"] for i in ingresos_lechones)
    balance = total_ingresos - total_gastos

    return {
        "total_gastos": total_gastos,
        "total_ingresos": total_ingresos,
        "balance": balance,
        "rentable": balance >= 0
    }

def calcular_estimado_lechones(puerca_id, precio_por_lechon):
    """
    Estima los ingresos futuros basado en el promedio
    de lechones por parto de una puerca específica
    """
    resultado = promedio_lechones_por_puerca(puerca_id)
    if not resultado or not resultado["promedio"]:
        return 0
    promedio = resultado["promedio"]
    return promedio * precio_por_lechon

# RESUMEN GENERAL 

def calcular_resumen_general():
    """Resumen financiero de toda la granja"""
    resumen = obtener_resumen_general()
    balance = resumen["balance"]
    total_gastos = resumen["total_gastos"]

    rentabilidad_pct = 0
    if total_gastos > 0:
        rentabilidad_pct = (balance / total_gastos) * 100

    return {
        "total_gastos": total_gastos,
        "total_ingresos": resumen["total_ingresos"],
        "balance": balance,
        "rentabilidad_pct": round(rentabilidad_pct, 2),
        "rentable": balance >= 0
    }

# UTILIDADES 

def formatear_monto(monto):
    """Formatea un número como moneda en RD$"""
    return f"RD$ {monto:,.2f}"

def calcular_porcentaje_cambio(valor_actual, valor_anterior):
    """Calcula el porcentaje de cambio entre dos períodos"""
    if valor_anterior == 0:
        return 0
    return round(((valor_actual - valor_anterior) / valor_anterior) * 100, 2)
from datetime import datetime

def validar_peso(peso):
    try:
        peso = float(peso)
        if peso <= 0:
            return False, "El peso debe ser mayor a 0"
        return True, peso
    except (ValueError, TypeError):
        return False, "El peso debe ser un número válido"

def validar_monto(monto):
    try:
        monto = float(monto)
        if monto <= 0:
            return False, "El monto debe ser mayor a 0"
        return True, monto
    except (ValueError, TypeError):
        return False, "El monto debe ser un número válido"

def validar_fecha(fecha):
    try:
        datetime.strptime(fecha, "%Y-%m-%d")
        return True, fecha
    except ValueError:
        return False, "La fecha debe tener el formato YYYY-MM-DD"

def validar_texto(texto, campo="Campo"):
    if not texto or texto.strip() == "":
        return False, f"{campo} no puede estar vacío"
    return True, texto.strip()