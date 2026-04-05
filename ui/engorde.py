import customtkinter as ctk
from database.models import (
    agregar_cerdo_engorde,
    obtener_cerdos_engorde,
    agregar_gasto,
    agregar_ingreso,
    obtener_gastos_por_seccion,
    obtener_ingresos_por_seccion
)
from logic.calculos import (
    calcular_ganancia_estimada,
    calcular_ganancia_real,
    calcular_valor_inventario,
    formatear_monto,
    validar_peso,
    validar_monto,
    validar_fecha,
    validar_texto
)
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter.messagebox as messagebox
from datetime import datetime

class Engorde(ctk.CTkFrame):
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
            text="Cerdos de Engorde",
            font=ctk.CTkFont(size=24, weight="bold")
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            header,
            text="Control de peso, precio de mercado y rentabilidad",
            font=ctk.CTkFont(size=13),
            text_color="gray50"
        ).grid(row=1, column=0, sticky="w")

    def _crear_tarjetas(self):
        cerdos = obtener_cerdos_engorde()
        valor_inventario = calcular_valor_inventario(cerdos)
        gastos = obtener_gastos_por_seccion("engorde")
        ingresos = obtener_ingresos_por_seccion("engorde")
        total_gastos = sum(g["monto"] for g in gastos)
        total_ingresos = sum(i["monto"] for i in ingresos)
        balance = total_ingresos - total_gastos

        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        tarjetas = [
            ("Valor Inventario", formatear_monto(valor_inventario), "#1D9E75"),
            ("Total Gastos", formatear_monto(total_gastos), "#E74C3C"),
            ("Total Ingresos", formatear_monto(total_ingresos), "#1D9E75"),
            ("Balance", formatear_monto(balance),
             "#1D9E75" if balance >= 0 else "#E74C3C"),
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
            frame, text="Inventario de Engorde",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, padx=15, pady=(15, 10), sticky="w")

        columnas = ["ID", "Peso Ind. (kg)", "Peso Lote (kg)", "Precio RD$/kg", "Ganancia Est.", "Fecha"]
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

        cerdos = obtener_cerdos_engorde()
        if not cerdos:
            ctk.CTkLabel(
                self.tabla_frame,
                text="No hay cerdos registrados",
                text_color="gray50"
            ).grid(row=0, column=0, pady=20)
            return

        for i, cerdo in enumerate(cerdos):
            ganancia_est = calcular_ganancia_estimada(
                cerdo["peso_lote_kg"],
                cerdo["precio_mercado_kg"]
            )
            fila = [
                cerdo["id_cerdo"],
                f"{cerdo['peso_individual_kg']} kg",
                f"{cerdo['peso_lote_kg']} kg",
                formatear_monto(cerdo["precio_mercado_kg"]),
                formatear_monto(ganancia_est),
                cerdo["fecha_registro"]
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
            frame, text="Registrar Cerdo",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, padx=15, pady=(15, 10), sticky="w")

        campos = [
            ("ID del cerdo (ej: CE-001)", "id_cerdo"),
            ("Peso individual (kg)", "peso_individual"),
            ("Peso del lote (kg)", "peso_lote"),
            ("Precio mercado hoy (RD$/kg)", "precio_mercado"),
            ("Fecha (YYYY-MM-DD)", "fecha"),
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

        self.entradas["fecha"].insert(0, datetime.now().strftime("%Y-%m-%d"))

        ctk.CTkButton(
            frame, text="Guardar Cerdo",
            command=self._guardar_cerdo,
            fg_color="#1D9E75", hover_color="#0F6E56"
        ).grid(row=12, column=0, padx=15, pady=20, sticky="ew")

        ctk.CTkLabel(
            frame, text="Registrar Gasto",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=13, column=0, padx=15, pady=(10, 10), sticky="w")

        ctk.CTkLabel(
            frame, text="Categoría",
            font=ctk.CTkFont(size=12),
            text_color="gray50"
        ).grid(row=14, column=0, padx=15, pady=(8, 2), sticky="w")
        self.gasto_cat = ctk.CTkOptionMenu(
            frame,
            values=["Alimentación", "Medicina", "Vitaminas", "Mano de obra", "Otro"]
        )
        self.gasto_cat.grid(row=15, column=0, padx=15, sticky="ew")

        ctk.CTkLabel(
            frame, text="Monto (RD$)",
            font=ctk.CTkFont(size=12),
            text_color="gray50"
        ).grid(row=16, column=0, padx=15, pady=(8, 2), sticky="w")
        self.gasto_monto = ctk.CTkEntry(frame, placeholder_text="0.00")
        self.gasto_monto.grid(row=17, column=0, padx=15, sticky="ew")

        ctk.CTkLabel(
            frame, text="Fecha (YYYY-MM-DD)",
            font=ctk.CTkFont(size=12),
            text_color="gray50"
        ).grid(row=18, column=0, padx=15, pady=(8, 2), sticky="w")
        self.gasto_fecha = ctk.CTkEntry(frame, placeholder_text="2024-01-15")
        self.gasto_fecha.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.gasto_fecha.grid(row=19, column=0, padx=15, sticky="ew")

        ctk.CTkButton(
            frame, text="Guardar Gasto",
            command=self._guardar_gasto,
            fg_color="#E74C3C", hover_color="#C0392B"
        ).grid(row=20, column=0, padx=15, pady=20, sticky="ew")

    def _guardar_cerdo(self):
        ok1, id_cerdo = validar_texto(self.entradas["id_cerdo"].get(), "ID del cerdo")
        ok2, peso_ind = validar_peso(self.entradas["peso_individual"].get())
        ok3, peso_lote = validar_peso(self.entradas["peso_lote"].get())
        ok4, precio = validar_monto(self.entradas["precio_mercado"].get())
        ok5, fecha = validar_fecha(self.entradas["fecha"].get())

        if not ok1:
            messagebox.showerror("Error", id_cerdo); return
        if not ok2:
            messagebox.showerror("Error", peso_ind); return
        if not ok3:
            messagebox.showerror("Error", peso_lote); return
        if not ok4:
            messagebox.showerror("Error", precio); return
        if not ok5:
            messagebox.showerror("Error", fecha); return

        try:
            agregar_cerdo_engorde(id_cerdo, peso_ind, peso_lote, precio, fecha)
            messagebox.showinfo("Éxito", f"Cerdo {id_cerdo} registrado correctamente")
            for e in self.entradas.values():
                e.delete(0, "end")
            self.entradas["fecha"].insert(0, datetime.now().strftime("%Y-%m-%d"))
            self._cargar_tabla()
        except Exception:
            messagebox.showerror("Error", f"El ID {id_cerdo} ya existe")

    def _guardar_gasto(self):
        ok1, monto = validar_monto(self.gasto_monto.get())
        ok2, fecha = validar_fecha(self.gasto_fecha.get())

        if not ok1:
            messagebox.showerror("Error", monto); return
        if not ok2:
            messagebox.showerror("Error", fecha); return

        agregar_gasto("engorde", self.gasto_cat.get(), monto, fecha)
        messagebox.showinfo("Éxito", "Gasto registrado correctamente")
        self.gasto_monto.delete(0, "end")