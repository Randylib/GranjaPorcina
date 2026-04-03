import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "granja.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def inicializar_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS puercas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            id_unico TEXT UNIQUE NOT NULL,
            fecha_ingreso TEXT NOT NULL,
            estado TEXT DEFAULT 'activa'
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
            peso_individual_kg REAL NOT NULL,
            peso_lote_kg REAL NOT NULL,
            precio_mercado_kg REAL NOT NULL,
            fecha_registro TEXT NOT NULL,
            estado TEXT DEFAULT 'en_engorde'
        );

        CREATE TABLE IF NOT EXISTS gastos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            seccion TEXT NOT NULL,
            categoria TEXT NOT NULL,
            monto REAL NOT NULL,
            fecha TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS ingresos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            seccion TEXT NOT NULL,
            concepto TEXT NOT NULL,
            monto REAL NOT NULL,
            fecha TEXT NOT NULL
        );
    """)

    conn.commit()
    conn.close()
    print("Base de datos inicializada correctamente")

if __name__ == "__main__":
    inicializar_db()