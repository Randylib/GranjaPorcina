import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "granja.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def inicializar_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
    -- ─── PRODUCCIÓN ──────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS puercas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        id_unico TEXT UNIQUE NOT NULL,
        raza TEXT DEFAULT 'Criolla',
        fecha_ingreso TEXT NOT NULL,
        estado TEXT DEFAULT 'disponible'
    );

    CREATE TABLE IF NOT EXISTS inseminaciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        puerca_id INTEGER,
        fecha_inseminacion TEXT,
        tipo TEXT,
        fecha_probable_parto TEXT,
        estado TEXT DEFAULT 'activa',
        FOREIGN KEY (puerca_id) REFERENCES puercas(id)
    );

    CREATE TABLE IF NOT EXISTS partos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        puerca_id INTEGER NOT NULL,
        fecha_parto TEXT NOT NULL,
        cantidad_lechones INTEGER NOT NULL,
        FOREIGN KEY (puerca_id) REFERENCES puercas(id)
    );

    CREATE TABLE IF NOT EXISTS lechones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        puerca_id INTEGER NOT NULL,
        parto_id INTEGER NOT NULL,
        fecha_nacimiento TEXT NOT NULL,
        peso_kg REAL DEFAULT 0,
        estado TEXT DEFAULT 'disponible',
        precio_venta REAL DEFAULT 0,
        fecha_venta TEXT,
        FOREIGN KEY (puerca_id) REFERENCES puercas(id),
        FOREIGN KEY (parto_id) REFERENCES partos(id)
    );

    CREATE TABLE IF NOT EXISTS engorde (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_cerdo TEXT UNIQUE NOT NULL,
        lechon_id INTEGER,
        peso_individual_kg REAL NOT NULL,
        peso_lote_kg REAL NOT NULL,
        precio_mercado_kg REAL NOT NULL,
        fecha_registro TEXT NOT NULL,
        estado TEXT DEFAULT 'en_engorde',
        fecha_venta TEXT,
        precio_venta_total REAL DEFAULT 0,
        FOREIGN KEY (lechon_id) REFERENCES lechones(id)
    );

    -- ─── FINANZAS ─────────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS gastos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        seccion TEXT,
        categoria TEXT,
        monto REAL,
        fecha TEXT,
        notas TEXT
    );

    CREATE TABLE IF NOT EXISTS ingresos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        seccion TEXT,
        concepto TEXT,
        monto REAL,
        fecha TEXT,
        notas TEXT
    );

    -- ─── ALIMENTOS ────────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS alimentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        tipo TEXT,
        unidad TEXT
    );

    CREATE TABLE IF NOT EXISTS alimentacion (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        seccion TEXT,
        alimento_id INTEGER,
        cantidad REAL,
        precio_unidad REAL,
        total REAL,
        fecha TEXT,
        notas TEXT,
        FOREIGN KEY (alimento_id) REFERENCES alimentos(id)
    );

    -- ─── MEDICAMENTOS ─────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS medicamentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        seccion TEXT,
        animal_id TEXT,
        nombre TEXT,
        tipo TEXT,
        unidad TEXT,
        dosis_por_kg REAL,
        peso_animal_kg REAL,
        dosis_total REAL,
        frecuencia TEXT,
        dias INTEGER,
        fecha_inicio TEXT,
        proxima_dosis TEXT,
        fechas_json TEXT,
        costo REAL,
        aplicado INTEGER DEFAULT 0
    );

    -- ─── EMPLEADOS ────────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS empleados (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        tipo_pago TEXT NOT NULL,   -- 'fijo' o 'por_dia'
        salario_base REAL NOT NULL, -- monto por día o sueldo fijo mensual
        fecha_contrato TEXT,
        activo INTEGER DEFAULT 1
    );

    CREATE TABLE IF NOT EXISTS pagos_empleados (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        empleado_id INTEGER,
        monto REAL,
        fecha TEXT,
        concepto TEXT,
        FOREIGN KEY (empleado_id) REFERENCES empleados(id)
    );

    -- ─── ACTIVIDADES ──────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS actividades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT,
        descripcion TEXT,
        fecha TEXT,
        estado TEXT DEFAULT 'pendiente',
        responsable TEXT
    );

    -- ─── VENTAS ───────────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS ventas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo_animal TEXT,
        animal_id TEXT,
        cantidad INTEGER,
        peso_kg REAL,
        precio_unit REAL,
        total REAL,
        fecha TEXT,
        comprador TEXT,
        notas TEXT
    );
    """)

    conn.commit()
    conn.close()
    print("✅ Base de datos inicializada correctamente")

if __name__ == "__main__":
    inicializar_db()