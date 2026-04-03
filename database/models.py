from database.database import get_connection
from datetime import datetime

# ─── PUERCAS ───────────────────────────────────────────

def agregar_puerca(nombre, id_unico, fecha_ingreso):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO puercas (nombre, id_unico, fecha_ingreso)
        VALUES (?, ?, ?)
    """, (nombre, id_unico, fecha_ingreso))
    conn.commit()
    conn.close()

def obtener_puercas():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM puercas WHERE estado = 'activa'")
    puercas = cursor.fetchall()
    conn.close()
    return puercas

# ─── PARTOS ────────────────────────────────────────────

def registrar_parto(puerca_id, fecha_parto, cantidad_lechones):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO partos (puerca_id, fecha_parto, cantidad_lechones)
        VALUES (?, ?, ?)
    """, (puerca_id, fecha_parto, cantidad_lechones))
    conn.commit()
    conn.close()

def obtener_partos_por_puerca(puerca_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM partos WHERE puerca_id = ?
        ORDER BY fecha_parto DESC
    """, (puerca_id,))
    partos = cursor.fetchall()
    conn.close()
    return partos

def promedio_lechones_por_puerca(puerca_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT AVG(cantidad_lechones) as promedio,
               SUM(cantidad_lechones) as total
        FROM partos WHERE puerca_id = ?
    """, (puerca_id,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado

# ─── LECHONES ──────────────────────────────────────────

def agregar_lechon(puerca_id, parto_id, fecha_nacimiento, peso_kg=0):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO lechones (puerca_id, parto_id, fecha_nacimiento, peso_kg)
        VALUES (?, ?, ?, ?)
    """, (puerca_id, parto_id, fecha_nacimiento, peso_kg))
    conn.commit()
    conn.close()

def vender_lechon(lechon_id, precio_venta, fecha_venta):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE lechones SET estado = 'vendido',
        precio_venta = ?, fecha_venta = ?
        WHERE id = ?
    """, (precio_venta, fecha_venta, lechon_id))
    conn.commit()
    conn.close()

# ─── ENGORDE ───────────────────────────────────────────

def agregar_cerdo_engorde(id_cerdo, peso_individual, peso_lote, precio_mercado, fecha):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO engorde (id_cerdo, peso_individual_kg, peso_lote_kg, precio_mercado_kg, fecha_registro)
        VALUES (?, ?, ?, ?, ?)
    """, (id_cerdo, peso_individual, peso_lote, precio_mercado, fecha))
    conn.commit()
    conn.close()

def obtener_cerdos_engorde():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM engorde WHERE estado = 'en_engorde'")
    cerdos = cursor.fetchall()
    conn.close()
    return cerdos

# ─── GASTOS E INGRESOS ─────────────────────────────────

def agregar_gasto(seccion, categoria, monto, fecha):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO gastos (seccion, categoria, monto, fecha)
        VALUES (?, ?, ?, ?)
    """, (seccion, categoria, monto, fecha))
    conn.commit()
    conn.close()

def agregar_ingreso(seccion, concepto, monto, fecha):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO ingresos (seccion, concepto, monto, fecha)
        VALUES (?, ?, ?, ?)
    """, (seccion, concepto, monto, fecha))
    conn.commit()
    conn.close()

def obtener_gastos_por_seccion(seccion):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM gastos WHERE seccion = ?
        ORDER BY fecha DESC
    """, (seccion,))
    gastos = cursor.fetchall()
    conn.close()
    return gastos

def obtener_ingresos_por_seccion(seccion):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM ingresos WHERE seccion = ?
        ORDER BY fecha DESC
    """, (seccion,))
    ingresos = cursor.fetchall()
    conn.close()
    return ingresos

def obtener_resumen_general():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(monto) as total FROM gastos")
    total_gastos = cursor.fetchone()["total"] or 0
    cursor.execute("SELECT SUM(monto) as total FROM ingresos")
    total_ingresos = cursor.fetchone()["total"] or 0
    conn.close()
    return {
        "total_gastos": total_gastos,
        "total_ingresos": total_ingresos,
        "balance": total_ingresos - total_gastos
    }