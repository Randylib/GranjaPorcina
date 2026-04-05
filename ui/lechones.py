import customtkinter as ctk
from database.models import (
    agregar_lechon,
    vender_lechon,
    agregar_gasto,
    agregar_ingreso,
    obtener_gastos_por_seccion,
    obtener_ingresos_por_seccion
)
from logic.calculos import (
    calcular_rentabilidad_puercas_lechones,
    formatear_monto,
    validar_monto,
    validar_fecha,
    validar_texto
)
import tkinter.messagebox as messagebox
from datetime import datetime
from database.database import get_connection

class Lechones(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._crear_header()
        self._crear_tarjetas()
        self._crear_contenido()

    def _crear_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 15))

        ctk.CTkLabel(
            header,
            text="Lechones para Venta",
            font=ctk.CTkFont(size=24, weight="bold")
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            header,
            text="Control de camadas, ventas y rentabilidad combinada",
            font=ctk.CTkFont(size=13),
            text_color="gray50"
        ).grid(row=1, column=0, sticky="w")

    def _crear_tarjetas(self):
        rentabilidad = calcular_rentabilidad_puercas_lechones()
        color_balance = "#1D9E75" if rentabilidad["balance"] >= 0 else "#E74C3C"

        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        conn = get_connection()
        total_lechones = conn.execute(
            "SELECT COUNT(*) as total FROM lechones"
        ).fetchone()["total"]
        vendidos = conn.execute(
            "SELECT COUNT(*) as total FROM lechones WHERE estado = 'vendido'"
        ).fetchone()["total"]
        conn.close()

        tarjetas = [
            ("Rentabilidad Combinada", formatear_monto(rentabilidad["balance"]), color_balance),
            ("Total Gastos", formatear_monto(rentabilidad["total_gastos"]), "#E74C3C"),
            ("Total Ingresos", formatear_monto(rentabilidad["total_ingresos"]), "#1D9E75"),
            ("Lechones Vendidos", f"{vendidos} / {total_lechones}", "#1D9E75"),
        ]

        for i, (titulo, valor, color) in enumerate(tarjetas):
            card = ctk.CTkFrame(frame)
            card.grid(row=0, column=i, padx=8, sticky="ew")
            ctk.CTkLabel(
                card, text=titulo,
                font=ctk.CTkFont(size=12),
                text_color="gray50"
            ).grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")
            ctk.CTkLabel(
                card, text=valor,
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color=color
            ).grid(row=1, column=0, padx=15, pady=(0, 15), sticky="w")

    def _crear_contenido(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=2, column=0, sticky="nsew")
        frame.grid_columnconfigure(0, weight=2)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_rowconfigure(0, weight=1)

        self._crear_tabla(frame)
        self._crear_formulario(frame)

    def _crear_tabla(self, parent):
        frame = ctk.CTkFrame(parent)
        frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(
            frame, text="Lechones Registrados",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, padx=15, pady=(15, 10), sticky="w")

        columnas = ["ID", "Puerca Madre", "Nacimiento", "Peso (kg)", "Estado", "Precio Venta"]
        headers = ctk.CTkFrame(frame, fg_color="transparent")
        headers.grid(row=1, column=0, sticky="ew", padx=15)

        for i, col in enumerate(columnas):
            ctk.CTkLabel(
                headers, text=col,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="gray50"
            ).grid(row=0, column=i, padx=8, sticky="w")

        self.tabla_frame = ctk.CTkScrollableFrame(frame, fg_color="transparent")
        self.tabla_frame.grid(row=2, column=0, sticky="nsew", padx=15, pady=(5, 15))

        self._cargar_tabla()

    def _cargar_tabla(self):
        for widget in self.tabla_frame.winfo_children():
            widget.destroy()

        conn = get_connection()
        lechones = conn.execute("""
            SELECT l.id, p.nombre as puerca_nombre, p.id_unico as puerca_id,
                   l.fecha_nacimiento, l.peso_kg, l.estado, l.precio_venta
            FROM lechones l
            JOIN puercas p ON l.puerca_id = p.id
            ORDER BY l.fecha_nacimiento DESC
        """).fetchall()
        conn.close()

        if not lechones:
            ctk.CTkLabel(
                self.tabla_frame,
                text="No hay lechones registrados",
                text_color="gray50"
            ).grid(row=0, column=0, pady=20)
            return

        for i, l in enumerate(lechones):
            fila = [
                str(l["id"]),
                f"{l['puerca_nombre']} ({l['puerca_id']})",
                l["fecha_nacimiento"],
                f"{l['peso_kg']} kg",
                l["estado"],
                formatear_monto(l["precio_venta"]) if l["precio_venta"] else "—"
            ]

            bg = "#2b2b2b" if i % 2 == 0 else "#323232"
            row_frame = ctk.CTkFrame(self.tabla_frame, fg_color=bg, corner_radius=4)
            row_frame.grid(row=i, column=0, sticky="ew", pady=1)

            for j, valor in enumerate(fila):
                color = "gray50"
                if valor == "vendido":
                    color = "#1D9E75"
                elif valor == "disponible":
                    color = "#F39C12"
                ctk.CTkLabel(
                    row_frame, text=valor,
                    font=ctk.CTkFont(size=13),
                    text_color=color if j == 4 else None
                ).grid(row=0, column=j, padx=8, pady=8, sticky="w")

    def _crear_formulario(self, parent):
        frame = ctk.CTkFrame(parent)
        frame.grid(row=0, column=1, sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            frame, text="Registrar Camada",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, padx=15, pady=(15, 10), sticky="w")

        ctk.CTkLabel(
            frame, text="ID de la puerca madre",
            font=ctk.CTkFont(size=12),
            text_color="gray50"
        ).grid(row=1, column=0, padx=15, pady=(8, 2), sticky="w")
        self.camada_puerca = ctk.CTkEntry(frame, placeholder_text="PR-001")
        self.camada_puerca.grid(row=2, column=0, padx=15, sticky="ew")

        ctk.CTkLabel(
            frame, text="Cantidad de lechones",
            font=ctk.CTkFont(size=12),
            text_color="gray50"
        ).grid(row=3, column=0, padx=15, pady=(8, 2), sticky="w")
        self.camada_cantidad = ctk.CTkEntry(frame, placeholder_text="8")
        self.camada_cantidad.grid(row=4, column=0, padx=15, sticky="ew")

        ctk.CTkLabel(
            frame, text="Fecha de nacimiento (YYYY-MM-DD)",
            font=ctk.CTkFont(size=12),
            text_color="gray50"
        ).grid(row=5, column=0, padx=15, pady=(8, 2), sticky="w")
        self.camada_fecha = ctk.CTkEntry(frame, placeholder_text="2024-01-15")
        self.camada_fecha.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.camada_fecha.grid(row=6, column=0, padx=15, sticky="ew")

        ctk.CTkButton(
            frame, text="Registrar Camada",
            command=self._guardar_camada,
            fg_color="#1D9E75", hover_color="#0F6E56"
        ).grid(row=7, column=0, padx=15, pady=15, sticky="ew")

        ctk.CTkLabel(
            frame, text="Registrar Venta",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=8, column=0, padx=15, pady=(10, 10), sticky="w")

        ctk.CTkLabel(
            frame, text="ID del lechón",
            font=ctk.CTkFont(size=12),
            text_color="gray50"
        ).grid(row=9, column=0, padx=15, pady=(8, 2), sticky="w")
        self.venta_id = ctk.CTkEntry(frame, placeholder_text="1")
        self.venta_id.grid(row=10, column=0, padx=15, sticky="ew")

        ctk.CTkLabel(
            frame, text="Precio de venta (RD$)",
            font=ctk.CTkFont(size=12),
            text_color="gray50"
        ).grid(row=11, column=0, padx=15, pady=(8, 2), sticky="w")
        self.venta_precio = ctk.CTkEntry(frame, placeholder_text="3500")
        self.venta_precio.grid(row=12, column=0, padx=15, sticky="ew")

        ctk.CTkLabel(
            frame, text="Fecha de venta (YYYY-MM-DD)",
            font=ctk.CTkFont(size=12),
            text_color="gray50"
        ).grid(row=13, column=0, padx=15, pady=(8, 2), sticky="w")
        self.venta_fecha = ctk.CTkEntry(frame, placeholder_text="2024-01-15")
        self.venta_fecha.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.venta_fecha.grid(row=14, column=0, padx=15, sticky="ew")

        ctk.CTkButton(
            frame, text="Registrar Venta",
            command=self._guardar_venta,
            fg_color="#1D9E75", hover_color="#0F6E56"
        ).grid(row=15, column=0, padx=15, pady=15, sticky="ew")

    def _guardar_camada(self):
        ok1, puerca_id = validar_texto(self.camada_puerca.get(), "ID de puerca")
        ok2, fecha = validar_fecha(self.camada_fecha.get())

        try:
            cantidad = int(self.camada_cantidad.get())
            if cantidad <= 0:
                raise ValueError
        except Exception:
            messagebox.showerror("Error", "La cantidad debe ser un número positivo")
            return

        if not ok1:
            messagebox.showerror("Error", puerca_id); return
        if not ok2:
            messagebox.showerror("Error", fecha); return

        conn = get_connection()
        puerca = conn.execute(
            "SELECT id FROM puercas WHERE id_unico = ?", (puerca_id,)
        ).fetchone()

        if not puerca:
            conn.close()
            messagebox.showerror("Error", f"No existe una puerca con ID {puerca_id}")
            return

        parto = conn.execute("""
            INSERT INTO partos (puerca_id, fecha_parto, cantidad_lechones)
            VALUES (?, ?, ?)
        """, (puerca["id"], fecha, cantidad))
        parto_id = parto.lastrowid
        conn.commit()

        for _ in range(cantidad):
            conn.execute("""
                INSERT INTO lechones (puerca_id, parto_id, fecha_nacimiento)
                VALUES (?, ?, ?)
            """, (puerca["id"], parto_id, fecha))
        conn.commit()
        conn.close()

        messagebox.showinfo("Éxito", f"{cantidad} lechones registrados correctamente")
        self.camada_puerca.delete(0, "end")
        self.camada_cantidad.delete(0, "end")
        self._cargar_tabla()

    def _guardar_venta(self):
        ok1, precio = validar_monto(self.venta_precio.get())
        ok2, fecha = validar_fecha(self.venta_fecha.get())

        try:
            lechon_id = int(self.venta_id.get())
        except Exception:
            messagebox.showerror("Error", "El ID del lechón debe ser un número")
            return

        if not ok1:
            messagebox.showerror("Error", precio); return
        if not ok2:
            messagebox.showerror("Error", fecha); return

        vender_lechon(lechon_id, precio, fecha)
        agregar_ingreso("lechones", "Venta de lechón", precio, fecha)
        messagebox.showinfo("Éxito", "Venta registrada correctamente")
        self.venta_id.delete(0, "end")
        self.venta_precio.delete(0, "end")
        self._cargar_tabla()