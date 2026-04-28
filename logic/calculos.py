from database.models import (
    obtener_gastos_por_seccion,
    obtener_ingresos_por_seccion,
    obtener_resumen_general,
    promedio_lechones_por_puerca,
    obtener_empleados,
    obtener_pagos_empleado,
    obtener_cerdos_engorde
)
from datetime import datetime, timedelta

# FORMATO 

def formatear_monto(monto):
    try:
        return f"RD$ {float(monto):,.2f}"
    except (TypeError, ValueError):
        return "RD$ 0.00"

#VALIDACIONES 

def validar_texto(texto, campo="Campo"):
    if not texto or str(texto).strip() == "":
        return False, f"{campo} no puede estar vacío"
    return True, str(texto).strip()

def validar_monto(monto):
    try:
        valor = float(monto)
        if valor <= 0:
            return False, "El monto debe ser mayor a 0"
        return True, valor
    except (ValueError, TypeError):
        return False, "El monto debe ser un número válido"

def validar_peso(peso):
    try:
        valor = float(peso)
        if valor <= 0:
            return False, "El peso debe ser mayor a 0"
        return True, valor
    except (ValueError, TypeError):
        return False, "El peso debe ser un número válido"

def validar_fecha(fecha):
    try:
        datetime.strptime(str(fecha), "%Y-%m-%d")
        return True, str(fecha)
    except ValueError:
        return False, "La fecha debe tener el formato YYYY-MM-DD"

# CÁLCULOS DE PRODUCCIÓN 

def calcular_ganancia_estimada(peso_lote_kg, precio_mercado_kg):
    return peso_lote_kg * precio_mercado_kg

def calcular_valor_inventario(cerdos):
    return sum(c["peso_lote_kg"] * c["precio_mercado_kg"] for c in cerdos)

def calcular_rentabilidad_puercas_lechones():
    gastos_puercas = obtener_gastos_por_seccion("puercas")
    gastos_lechones = obtener_gastos_por_seccion("lechones")
    ingresos_lechones = obtener_ingresos_por_seccion("lechones")

    total_gastos = (
        sum(g["monto"] for g in gastos_puercas) +
        sum(g["monto"] for g in gastos_lechones)
    )
    total_ingresos = sum(i["monto"] for i in ingresos_lechones)
    balance = total_ingresos - total_gastos

    return {
        "total_gastos": total_gastos,
        "total_ingresos": total_ingresos,
        "balance": balance,
        "rentable": balance >= 0
    }

# RESUMEN GENERAL 

def calcular_resumen_general():
    resumen = obtener_resumen_general()
    balance = resumen["balance"]
    total_gastos = resumen["total_gastos"]

    rentabilidad_pct = 0
    if total_gastos > 0:
        rentabilidad_pct = round((balance / total_gastos) * 100, 2)

    return {
        "total_gastos": total_gastos,
        "total_ingresos": resumen["total_ingresos"],
        "balance": balance,
        "rentabilidad_pct": rentabilidad_pct,
        "rentable": balance >= 0
    }

#MEDICAMENTOS 

def calcular_fechas_aplicacion(fecha_inicio, frecuencia, dias_tratamiento=1):
    fecha = datetime.strptime(fecha_inicio, "%Y-%m-%d")
    fechas = []

    if frecuencia == "Dosis única":
        fechas.append(fecha_inicio)
    elif frecuencia == "Cada 24 horas":
        for i in range(dias_tratamiento):
            fechas.append((fecha + timedelta(days=i)).strftime("%Y-%m-%d"))
    elif frecuencia == "Cada 12 horas":
        for i in range(dias_tratamiento):
            dia = (fecha + timedelta(days=i)).strftime("%Y-%m-%d")
            fechas.append(f"{dia} 08:00")
            fechas.append(f"{dia} 20:00")
    elif frecuencia == "Cada 8 horas":
        for i in range(dias_tratamiento):
            dia = (fecha + timedelta(days=i)).strftime("%Y-%m-%d")
            fechas.append(f"{dia} 06:00")
            fechas.append(f"{dia} 14:00")
            fechas.append(f"{dia} 22:00")

    return fechas

def calcular_dosis_total(dosis_por_kg, peso_animal_kg):
    return round(dosis_por_kg * peso_animal_kg, 4)

# EMPLEADOS 

def calcular_nomina_mensual():
    """Estima la nómina mensual según el tipo de pago de cada empleado."""
    empleados = obtener_empleados()
    total = 0
    for emp in empleados:
        tipo = emp["tipo_pago"]
        base = emp["salario_base"]
        if tipo == "mensual":
            total += base
        elif tipo == "quincenal":
            total += base * 2
        elif tipo == "semanal":
            total += base * 4
        elif tipo == "diario":
            total += base * 22   # días laborables promedio
        elif tipo == "ajuste":
            pass                 # pago único por tarea, no se proyecta
    return total

def calcular_pagos_empleado(empleado_id):
    pagos = obtener_pagos_empleado(empleado_id)
    return sum(p["monto"] for p in pagos)

# GASTOS CON FILTRO 

def filtrar_gastos_por_periodo(seccion=None, periodo="mes"):
    hoy = datetime.now()

    if periodo == "dia":
        fecha_desde = hoy.strftime("%Y-%m-%d")
        fecha_hasta = hoy.strftime("%Y-%m-%d")
    elif periodo == "semana":
        inicio = hoy - timedelta(days=hoy.weekday())
        fecha_desde = inicio.strftime("%Y-%m-%d")
        fecha_hasta = hoy.strftime("%Y-%m-%d")
    elif periodo == "mes":
        fecha_desde = hoy.replace(day=1).strftime("%Y-%m-%d")
        fecha_hasta = hoy.strftime("%Y-%m-%d")
    elif periodo == "año":
        fecha_desde = hoy.replace(month=1, day=1).strftime("%Y-%m-%d")
        fecha_hasta = hoy.strftime("%Y-%m-%d")
    else:
        fecha_desde = None
        fecha_hasta = None

    return obtener_gastos_por_seccion(seccion, fecha_desde, fecha_hasta)

def resumen_gastos_por_periodo(periodo="mes"):
    gastos = filtrar_gastos_por_periodo(periodo=periodo)
    total = sum(g["monto"] for g in gastos)
    por_categoria = {}
    for g in gastos:
        cat = g.get("categoria", "Sin categoría")
        por_categoria[cat] = por_categoria.get(cat, 0) + g["monto"]
    return {"total": total, "por_categoria": por_categoria, "detalle": gastos}

#  SUGERENCIAS 

def generar_sugerencias(resumen):
    """Genera sugerencias automáticas según el estado financiero."""
    sugerencias = []
    balance = resumen.get("balance", 0)
    total_gastos = resumen.get("total_gastos", 0)
    total_ingresos = resumen.get("total_ingresos", 0)
    rentabilidad = resumen.get("rentabilidad_pct", 0)

    if balance < 0:
        sugerencias.append("El balance general es negativo. Revisa los gastos de mayor impacto.")

    if rentabilidad < 10 and total_gastos > 0:
        sugerencias.append("La rentabilidad está por debajo del 10%. Considera aumentar precios de venta.")

    if total_ingresos == 0:
        sugerencias.append("No hay ingresos registrados aún. Registra tus primeras ventas.")

    if total_gastos == 0:
        sugerencias.append("No hay gastos registrados. Asegúrate de registrar todos los egresos.")

    if not sugerencias:
        sugerencias.append("Las finanzas están en buen estado. Sigue registrando todas las operaciones.")

    return sugerencias