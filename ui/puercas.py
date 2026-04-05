import customtkinter as ctk
from database.models import (
    agregar_puerca, obtener_puercas,
    registrar_parto,
    promedio_lechones_por_puerca
)
from logic.calculos import (
    calcular_rentabilidad_puercas_lechones,
    formatear_monto, validar_texto,
    validar_fecha
)
import tkinter.messagebox as messagebox

class Puercas(ctk.CTkFrame):
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
            text="Puercas Paridoras",
            font=ctk.CTkFont(size=24, weight="bold")
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            header,
            text="Registro individual y análisis de productividad",
            font=ctk.CTkFont(size=13),
            text_color="gray50"
        ).grid(row=1, column=0, sticky="w")

    def _crear_tarjetas(self):
        rentabilidad = calcular_rentabilidad_puercas_lechones()

        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        frame.grid_columnconfigure((0, 1, 2), weight=1)

        color_balance = "#1D9E75" if rentabilidad["balance"] >= 0 else "#E74C3C"

        tarjetas = [
            ("Total Gastos", formatear_monto(rentabilidad["total_gastos"]), "#E74C3C"),
            ("Total Ingresos", formatear_monto(rentabilidad["total_ingresos"]), "#1D9E75"),
            ("Balance", formatear_monto(rentabilidad["balance"]), color_balance),
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
            frame, text="Inventario de Puercas",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, padx=15, pady=(15, 10), sticky="w")

        columnas = ["ID Único", "Nombre", "Fecha Ingreso", "Total Lechones", "Promedio/Parto"]
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

        puercas = obtener_puercas()
        if not puercas:
            ctk.CTkLabel(
                self.tabla_frame,
                text="No hay puercas registradas",
                text_color="gray50"
            ).grid(row=0, column=0, pady=20)
            return

        for i, puerca in enumerate(puercas):
            resultado = promedio_lechones_por_puerca(puerca["id"])
            total = resultado["total"] or 0
            promedio = round(resultado["promedio"] or 0, 1)

            fila = [
                puerca["id_unico"], puerca["nombre"],
                puerca["fecha_ingreso"], str(total), str(promedio)
            ]

            bg = "#2b2b2b" if i % 2 == 0 else "#323232"
            row_frame = ctk.CTkFrame(self.tabla_frame, fg_color=bg, corner_radius=4)
            row_frame.grid(row=i, column=0, sticky="ew", pady=1)

            for j, valor in enumerate(fila):
                ctk.CTkLabel(
                    row_frame, text=valor,
                    font=ctk.CTkFont(size=13)
                ).grid(row=0, column=j, padx=8, pady=8, sticky="w")

    def _crear_formulario(self, parent):
        frame = ctk.CTkFrame(parent)
        frame.grid(row=0, column=1, sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            frame, text="Registrar Puerca",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, padx=15, pady=(15, 10), sticky="w")

        campos = [
            ("ID Único (ej: PR-001)", "id_unico"),
            ("Nombre / Alias", "nombre"),
            ("Fecha de ingreso (YYYY-MM-DD)", "fecha_ingreso"),
        ]

        self.entradas = {}
        for i, (label, key) in enumerate(campos):
            ctk.CTkLabel(
                frame, text=label,
                font=ctk.CTkFont(size=12),
                text_color="gray50"
            ).grid(row=i*2+1, column=0, padx=15, pady=(8, 2), sticky="w")

            entrada = ctk.CTkEntry(frame, placeholder_text=label)
            entrada.grid(row=i*2+2, column=0, padx=15, sticky="ew")
            self.entradas[key] = entrada

        ctk.CTkButton(
            frame, text="Guardar Puerca",
            command=self._guardar_puerca,
            fg_color="#1D9E75", hover_color="#0F6E56"
        ).grid(row=10, column=0, padx=15, pady=20, sticky="ew")

        ctk.CTkLabel(
            frame, text="Registrar Parto",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=11, column=0, padx=15, pady=(10, 10), sticky="w")

        ctk.CTkLabel(
            frame, text="ID Único de la puerca",
            font=ctk.CTkFont(size=12),
            text_color="gray50"
        ).grid(row=12, column=0, padx=15, pady=(8, 2), sticky="w")
        self.parto_id = ctk.CTkEntry(frame, placeholder_text="PR-001")
        self.parto_id.grid(row=13, column=0, padx=15, sticky="ew")

        ctk.CTkLabel(
            frame, text="Fecha del parto (YYYY-MM-DD)",
            font=ctk.CTkFont(size=12),
            text_color="gray50"
        ).grid(row=14, column=0, padx=15, pady=(8, 2), sticky="w")
        self.parto_fecha = ctk.CTkEntry(frame, placeholder_text="2024-01-15")
        self.parto_fecha.grid(row=15, column=0, padx=15, sticky="ew")

        ctk.CTkLabel(
            frame, text="Cantidad de lechones",
            font=ctk.CTkFont(size=12),
            text_color="gray50"
        ).grid(row=16, column=0, padx=15, pady=(8, 2), sticky="w")
        self.parto_lechones = ctk.CTkEntry(frame, placeholder_text="8")
        self.parto_lechones.grid(row=17, column=0, padx=15, sticky="ew")

        ctk.CTkButton(
            frame, text="Registrar Parto",
            command=self._guardar_parto,
            fg_color="#1D9E75", hover_color="#0F6E56"
        ).grid(row=18, column=0, padx=15, pady=20, sticky="ew")

    def _guardar_puerca(self):
        ok1, id_unico = validar_texto(self.entradas["id_unico"].get(), "ID Único")
        ok2, nombre = validar_texto(self.entradas["nombre"].get(), "Nombre")
        ok3, fecha = validar_fecha(self.entradas["fecha_ingreso"].get())

        if not ok1:
            messagebox.showerror("Error", id_unico)
            return
        if not ok2:
            messagebox.showerror("Error", nombre)
            return
        if not ok3:
            messagebox.showerror("Error", fecha)
            return

        try:
            agregar_puerca(nombre, id_unico, fecha)
            messagebox.showinfo("Éxito", f"Puerca {nombre} registrada correctamente")
            for e in self.entradas.values():
                e.delete(0, "end")
            self._cargar_tabla()
        except Exception:
            messagebox.showerror("Error", f"El ID Único ya existe: {id_unico}")

    def _guardar_parto(self):
        ok1, id_unico = validar_texto(self.parto_id.get(), "ID de puerca")
        ok2, fecha = validar_fecha(self.parto_fecha.get())

        try:
            cantidad = int(self.parto_lechones.get())
            if cantidad <= 0:
                raise ValueError
        except Exception:
            messagebox.showerror("Error", "La cantidad de lechones debe ser un número positivo")
            return

        if not ok1:
            messagebox.showerror("Error", id_unico)
            return
        if not ok2:
            messagebox.showerror("Error", fecha)
            return

        from database.database import get_connection
        conn = get_connection()
        puerca = conn.execute(
            "SELECT id FROM puercas WHERE id_unico = ?", (id_unico,)
        ).fetchone()
        conn.close()

        if not puerca:
            messagebox.showerror("Error", f"No existe una puerca con ID {id_unico}")
            return

        registrar_parto(puerca["id"], fecha, cantidad)
        messagebox.showinfo("Éxito", "Parto registrado correctamente")
        self.parto_id.delete(0, "end")
        self.parto_fecha.delete(0, "end")
        self.parto_lechones.delete(0, "end")
        self._cargar_tabla()