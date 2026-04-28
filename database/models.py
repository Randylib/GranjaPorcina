from database.database import get_connection
from contextlib import contextmanager
from datetime import datetime, timedelta
import json

# CONTEXT MANAGER 
@contextmanager
def db_connection():
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

# PUERCAS 
def agregar_puerca(nombre, id_unico, raza, fecha_ingreso):
    with db_connection() as conn:
        conn.execute("""
            INSERT INTO puercas (nombre, id_unico, raza, fecha_ingreso)
            VALUES (?, ?, ?, ?)
        """, (nombre, id_unico, raza, fecha_ingreso))

def obtener_puercas():
    with db_connection() as conn:
        return conn.execute(
            "SELECT * FROM puercas WHERE estado != 'baja' ORDER BY id_unico"
        ).fetchall()

def eliminar_puerca(puerca_id):
    with db_connection() as conn:
        conn.execute("UPDATE puercas SET estado = 'baja' WHERE id = ?", (puerca_id,))

def obtener_resumen_puercas():
    with db_connection() as conn:
        total = conn.execute("SELECT COUNT(*) as c FROM puercas WHERE estado != 'baja'").fetchone()["c"]
        camadas = conn.execute("SELECT COUNT(*) as c FROM partos").fetchone()["c"]
        lechones = conn.execute("SELECT COUNT(*) as c FROM lechones").fetchone()["c"]
        return {"total": total, "camadas": camadas, "lechones": lechones}

# INSEMINACIONES 
def registrar_inseminacion(puerca_id, fecha, tipo):
    fecha_dt = datetime.strptime(fecha, "%Y-%m-%d")
    fecha_parto = fecha_dt + timedelta(days=114)
    with db_connection() as conn:
        conn.execute("""
            INSERT INTO inseminaciones (puerca_id, fecha_inseminacion, tipo, fecha_probable_parto)
            VALUES (?, ?, ?, ?)
        """, (puerca_id, fecha, tipo, fecha_parto.strftime("%Y-%m-%d")))
        conn.execute("UPDATE puercas SET estado = 'gestacion' WHERE id = ?", (puerca_id,))

def obtener_partos_proximos():
    with db_connection() as conn:
        return conn.execute("""
            SELECT p.nombre, i.fecha_probable_parto
            FROM inseminaciones i JOIN puercas p ON p.id = i.puerca_id
            WHERE i.estado = 'activa' ORDER BY i.fecha_probable_parto
        """).fetchall()

#  PARTOS 
def registrar_parto(puerca_id, fecha_parto, cantidad_lechones):
    with db_connection() as conn:
        conn.execute("""
            INSERT INTO partos (puerca_id, fecha_parto, cantidad_lechones)
            VALUES (?, ?, ?)
        """, (puerca_id, fecha_parto, cantidad_lechones))
        conn.execute("UPDATE puercas SET estado = 'disponible' WHERE id = ?", (puerca_id,))

def obtener_partos_por_puerca(puerca_id):
    with db_connection() as conn:
        return conn.execute("""
            SELECT * FROM partos WHERE puerca_id = ? ORDER BY fecha_parto DESC
        """, (puerca_id,)).fetchall()

def promedio_lechones_por_puerca(puerca_id):
    with db_connection() as conn:
        return conn.execute("""
            SELECT AVG(cantidad_lechones) as promedio, SUM(cantidad_lechones) as total
            FROM partos WHERE puerca_id = ?
        """, (puerca_id,)).fetchone()

#  LECHONES 
def registrar_camada(id_unico_puerca, fecha, cantidad):
    with db_connection() as conn:
        puerca = conn.execute("SELECT id FROM puercas WHERE id_unico = ?", (id_unico_puerca,)).fetchone()
        if not puerca:
            raise ValueError("Puerca no encontrada")
        cur = conn.execute("""
            INSERT INTO partos (puerca_id, fecha_parto, cantidad_lechones)
            VALUES (?, ?, ?)
        """, (puerca["id"], fecha, cantidad))
        parto_id = cur.lastrowid
        for _ in range(cantidad):
            conn.execute("""
                INSERT INTO lechones (puerca_id, parto_id, fecha_nacimiento)
                VALUES (?, ?, ?)
            """, (puerca["id"], parto_id, fecha))
        return parto_id

def obtener_lechones_con_puerca():
    with db_connection() as conn:
        return conn.execute("""
            SELECT l.id, l.puerca_id, l.fecha_nacimiento, l.peso_kg, l.estado, l.precio_venta,
                   p.nombre as puerca_nombre, p.id_unico as puerca_id
            FROM lechones l JOIN puercas p ON l.puerca_id = p.id
            ORDER BY l.fecha_nacimiento DESC
        """).fetchall()

def vender_lechon(lechon_id, precio, fecha):
    with db_connection() as conn:
        conn.execute("""
            UPDATE lechones SET estado='vendido', precio_venta=?, fecha_venta=?
            WHERE id=?
        """, (precio, fecha, lechon_id))

def contar_lechones():
    with db_connection() as conn:
        total = conn.execute("SELECT COUNT(*) as c FROM lechones").fetchone()["c"]
        vendidos = conn.execute("SELECT COUNT(*) as c FROM lechones WHERE estado='vendido'").fetchone()["c"]
        return total, vendidos

#  ENGORDE
def agregar_cerdo_engorde(id_cerdo, peso_individual, peso_lote, precio_mercado, fecha):
    with db_connection() as conn:
        existe = conn.execute("SELECT id FROM engorde WHERE id_cerdo = ?", (id_cerdo,)).fetchone()
        if existe:
            raise ValueError(f"Ya existe cerdo con ID {id_cerdo}")
        conn.execute("""
            INSERT INTO engorde (id_cerdo, peso_individual_kg, peso_lote_kg, precio_mercado_kg, fecha_registro, estado)
            VALUES (?, ?, ?, ?, ?, 'en_engorde')
        """, (id_cerdo, peso_individual, peso_lote, precio_mercado, fecha))

def obtener_cerdos_engorde():
    with db_connection() as conn:
        return conn.execute("SELECT * FROM engorde WHERE estado='en_engorde'").fetchall()

def vender_cerdo_engorde(id_cerdo, peso_final, precio_kg, fecha_venta):
    with db_connection() as conn:
        cerdo = conn.execute("SELECT * FROM engorde WHERE id_cerdo = ? AND estado='en_engorde'", (id_cerdo,)).fetchone()
        if not cerdo:
            raise ValueError(f"Cerdo {id_cerdo} no encontrado en engorde")
        total = peso_final * precio_kg
        conn.execute("""
            UPDATE engorde SET estado='vendido', fecha_venta=?, precio_venta_total=?, peso_lote_kg=?
            WHERE id_cerdo = ?
        """, (fecha_venta, total, peso_final, id_cerdo))
        conn.execute("""
            INSERT INTO ingresos (seccion, concepto, monto, fecha)
            VALUES ('engorde', ?, ?, ?)
        """, (f"Venta cerdo {id_cerdo} - {peso_final}kg", total, fecha_venta))
        return total

# EMPLEADOS 
def agregar_empleado(nombre, tipo_pago, salario_base, fecha_contrato):
    with db_connection() as conn:
        conn.execute("""
            INSERT INTO empleados (nombre, tipo_pago, salario_base, fecha_contrato, activo)
            VALUES (?, ?, ?, ?, 1)
        """, (nombre, tipo_pago, salario_base, fecha_contrato))

def obtener_empleados(activo=True):
    with db_connection() as conn:
        if activo:
            return conn.execute("SELECT * FROM empleados WHERE activo=1 ORDER BY nombre").fetchall()
        return conn.execute("SELECT * FROM empleados ORDER BY nombre").fetchall()

def registrar_pago_empleado(empleado_id, monto, fecha, concepto):
    with db_connection() as conn:
        conn.execute("""
            INSERT INTO pagos_empleados (empleado_id, monto, fecha, concepto)
            VALUES (?, ?, ?, ?)
        """, (empleado_id, monto, fecha, concepto))
        conn.execute("""
            INSERT INTO gastos (seccion, categoria, monto, fecha, notas)
            VALUES ('empleados', 'Salario', ?, ?, ?)
        """, (monto, fecha, concepto))

def obtener_pagos_empleado(empleado_id):
    with db_connection() as conn:
        return conn.execute("""
            SELECT * FROM pagos_empleados WHERE empleado_id = ? ORDER BY fecha DESC
        """, (empleado_id,)).fetchall()

def obtener_resumen_empleados():
    with db_connection() as conn:
        total_empleados = conn.execute("SELECT COUNT(*) as c FROM empleados WHERE activo=1").fetchone()["c"]
        total_pagado = conn.execute("SELECT COALESCE(SUM(monto),0) as c FROM pagos_empleados").fetchone()["c"]
        return {"total_empleados": total_empleados, "total_pagado": total_pagado}

# GASTOS E INGRESOS 
def agregar_gasto(seccion, categoria, monto, fecha, notas=""):
    with db_connection() as conn:
        conn.execute("""
            INSERT INTO gastos (seccion, categoria, monto, fecha, notas)
            VALUES (?, ?, ?, ?, ?)
        """, (seccion, categoria, monto, fecha, notas))

def agregar_ingreso(seccion, concepto, monto, fecha, notas=""):
    with db_connection() as conn:
        conn.execute("""
            INSERT INTO ingresos (seccion, concepto, monto, fecha, notas)
            VALUES (?, ?, ?, ?, ?)
        """, (seccion, concepto, monto, fecha, notas))

def obtener_gastos_por_seccion(seccion=None, fecha_desde=None, fecha_hasta=None):
    with db_connection() as conn:
        query = "SELECT * FROM gastos WHERE 1=1"
        params = []
        if seccion:
            query += " AND seccion = ?"
            params.append(seccion)
        if fecha_desde:
            query += " AND fecha >= ?"
            params.append(fecha_desde)
        if fecha_hasta:
            query += " AND fecha <= ?"
            params.append(fecha_hasta)
        query += " ORDER BY fecha DESC"
        rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]

def obtener_ingresos_por_seccion(seccion=None, fecha_desde=None, fecha_hasta=None):
    with db_connection() as conn:
        query = "SELECT * FROM ingresos WHERE 1=1"
        params = []
        if seccion:
            query += " AND seccion = ?"
            params.append(seccion)
        if fecha_desde:
            query += " AND fecha >= ?"
            params.append(fecha_desde)
        if fecha_hasta:
            query += " AND fecha <= ?"
            params.append(fecha_hasta)
        query += " ORDER BY fecha DESC"
        rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]

def obtener_resumen_general():
    with db_connection() as conn:
        gastos = conn.execute("SELECT COALESCE(SUM(monto),0) FROM gastos").fetchone()[0]
        ingresos = conn.execute("SELECT COALESCE(SUM(monto),0) FROM ingresos").fetchone()[0]
        return {"total_gastos": gastos, "total_ingresos": ingresos, "balance": ingresos - gastos}

# MEDICAMENTOS 
def agregar_medicamento(seccion, animal_id, nombre, tipo, unidad, dosis_por_kg,
                        peso_animal, dosis_total, frecuencia, dias,
                        fecha_inicio, proxima_dosis, fechas, costo):
    with db_connection() as conn:
        conn.execute("""
            INSERT INTO medicamentos 
            (seccion, animal_id, nombre, tipo, unidad, dosis_por_kg,
             peso_animal_kg, dosis_total, frecuencia, dias,
             fecha_inicio, proxima_dosis, fechas_json, costo, aplicado)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
        """, (seccion, animal_id, nombre, tipo, unidad, dosis_por_kg,
              peso_animal, dosis_total, frecuencia, dias,
              fecha_inicio, proxima_dosis, json.dumps(fechas), costo))

def obtener_medicamentos(seccion=None):
    with db_connection() as conn:
        if seccion:
            return conn.execute("""
                SELECT * FROM medicamentos WHERE seccion = ? ORDER BY fecha_inicio DESC
            """, (seccion,)).fetchall()
        return conn.execute("SELECT * FROM medicamentos ORDER BY fecha_inicio DESC").fetchall()

def obtener_todos_medicamentos():
    return obtener_medicamentos()

def marcar_medicamento_aplicado(medicamento_id):
    with db_connection() as conn:
        conn.execute("UPDATE medicamentos SET aplicado = 1 WHERE id = ?", (medicamento_id,))

def eliminar_medicamento(medicamento_id):
    with db_connection() as conn:
        conn.execute("DELETE FROM medicamentos WHERE id = ?", (medicamento_id,))

def obtener_resumen_medicamentos():
    with db_connection() as conn:
        total = conn.execute("SELECT COUNT(*) as c FROM medicamentos").fetchone()["c"]
        aplicados = conn.execute("SELECT COUNT(*) as c FROM medicamentos WHERE aplicado=1").fetchone()["c"]
        costo_total = conn.execute("SELECT COALESCE(SUM(costo),0) as c FROM medicamentos").fetchone()["c"]
        return {"total": total, "aplicados": aplicados, "pendientes": total - aplicados, "costo_total": costo_total}

def obtener_medicamentos_pendientes_hoy():
    hoy = datetime.now().strftime("%Y-%m-%d")
    with db_connection() as conn:
        todos = conn.execute("SELECT * FROM medicamentos WHERE aplicado=0").fetchall()
        pendientes = []
        for med in todos:
            try:
                fechas = json.loads(med["fechas_json"])
                if any(f.startswith(hoy) for f in fechas):
                    pendientes.append(dict(med))
            except:
                continue
        return pendientes


def registrar_venta_lechon(lechon_id, precio, fecha, comprador=""):
    with db_connection() as conn:
        lechon = conn.execute("SELECT * FROM lechones WHERE id=? AND estado='disponible'", (lechon_id,)).fetchone()
        if not lechon:
            raise ValueError("Lechón no disponible")
        conn.execute("UPDATE lechones SET estado='vendido', precio_venta=?, fecha_venta=? WHERE id=?", (precio, fecha, lechon_id))
        conn.execute("""
            INSERT INTO ventas (tipo_animal, animal_id, cantidad, precio_unit, total, fecha, comprador)
            VALUES ('lechon', ?, 1, ?, ?, ?, ?)
        """, (str(lechon_id), precio, precio, fecha, comprador))
        conn.execute("INSERT INTO ingresos (seccion, concepto, monto, fecha) VALUES ('lechones', ?, ?, ?)",
                     (f"Venta lechón #{lechon_id}", precio, fecha))

def obtener_ventas(tipo=None):
    with db_connection() as conn:
        if tipo:
            return conn.execute("SELECT * FROM ventas WHERE tipo_animal = ? ORDER BY fecha DESC", (tipo,)).fetchall()
        return conn.execute("SELECT * FROM ventas ORDER BY fecha DESC").fetchall()

def obtener_resumen_ventas():
    with db_connection() as conn:
        total = conn.execute("SELECT COALESCE(SUM(total),0) as c FROM ventas").fetchone()["c"]
        lechones = conn.execute("SELECT COALESCE(SUM(cantidad),0) as c FROM ventas WHERE tipo_animal='lechon'").fetchone()["c"]
        engorde = conn.execute("SELECT COUNT(*) as c FROM ventas WHERE tipo_animal='engorde'").fetchone()["c"]
        return {"total": total, "lechones_vendidos": lechones, "engorde_vendidos": engorde}

#  ACTIVIDADES 
def agregar_actividad(titulo, descripcion, fecha, responsable):
    with db_connection() as conn:
        conn.execute("""
            INSERT INTO actividades (titulo, descripcion, fecha, responsable, estado)
            VALUES (?, ?, ?, ?, 'pendiente')
        """, (titulo, descripcion, fecha, responsable))

def obtener_todas_actividades():
    with db_connection() as conn:
        return conn.execute("SELECT * FROM actividades ORDER BY fecha DESC").fetchall()