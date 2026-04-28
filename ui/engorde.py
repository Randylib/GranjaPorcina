import customtkinter as ctk
from database.models import (
    agregar_cerdo_engorde,
    obtener_cerdos_engorde,
    vender_cerdo_engorde,
    obtener_gastos_por_seccion,
    obtener_ingresos_por_seccion
)
from logic.calculos import (
    calcular_ganancia_estimada,
    calcular_valor_inventario,
    formatear_monto,
    validar_peso,
    validar_monto,
    validar_fecha,
    validar_texto
)
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

    # HEADER 

    def _crear_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 15))

        ctk.CTkLabel(
            header, text="Cerdos de Engorde",
            font=ctk.CTkFont(size=24, weight="bold")
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            header,
            text="Control de inventario y ventas",
            font=ctk.CTkFont(size=13),
            text_color="gray50"
        ).grid(row=1, column=0, sticky="w")

    # TARJETAS 

    def _crear_tarjetas(self):
        cerdos = obtener_cerdos_engorde()
        valor_inventario = calcular_valor_inventario(cerdos)

        gastos = obtener_gastos_por_seccion("engorde")
        ingresos = obtener_ingresos_por_seccion("engorde")

        total_gastos = sum(g["monto"] for g in gastos)
        total_ingresos = sum(i["monto"] for i in ingresos)
        balance = total_ingresos - total_gastos

        self.frame_tarjetas = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_tarjetas.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        self.frame_tarjetas.grid_columnconfigure((0, 1, 2, 3), weight=1)

        tarjetas = [
            ("Inventario", formatear_monto(valor_inventario), "#1D9E75"),
            ("Gastos", formatear_monto(total_gastos), "#E74C3C"),
            ("Ingresos", formatear_monto(total_ingresos), "#1D9E75"),
            ("Balance", formatear_monto(balance),
             "#1D9E75" if balance >= 0 else "#E74C3C"),
        ]

        for i, (titulo, valor, color) in enumerate(tarjetas):
            card = ctk.CTkFrame(self.frame_tarjetas)
            card.grid(row=0, column=i, padx=8, sticky="ew")

            ctk.CTkLabel(card, text=titulo, text_color="gray50"
                         ).pack(padx=15, pady=(10, 5), anchor="w")

            ctk.CTkLabel(card, text=valor,
                         font=ctk.CTkFont(size=18, weight="bold"),
                         text_color=color
                         ).pack(padx=15, pady=(0, 10), anchor="w")

    # CONTENIDO 

    def _crear_contenido(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=2, column=0, sticky="nsew")

        frame.grid_columnconfigure(0, weight=2)
        frame.grid_columnconfigure(1, weight=1)

        self._crear_tabla(frame)
        self._crear_formulario(frame)

    # TABLA 

    def _crear_tabla(self, parent):
        frame = ctk.CTkFrame(parent)
        frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        ctk.CTkLabel(
            frame, text="Inventario",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 10))

        columnas = ["ID", "Peso Lote", "Precio/kg", "Valor", "Estado", "Fecha"]

        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.pack(fill="x", padx=15)

        for i, col in enumerate(columnas):
            ctk.CTkLabel(header, text=col, text_color="gray50"
                         ).grid(row=0, column=i, padx=8, sticky="w")

        self.tabla_frame = ctk.CTkScrollableFrame(frame)
        self.tabla_frame.pack(fill="both", expand=True, padx=15, pady=10)

        self._cargar_tabla()

    def _cargar_tabla(self):
        for w in self.tabla_frame.winfo_children():
            w.destroy()

        cerdos = obtener_cerdos_engorde()

        if not cerdos:
            ctk.CTkLabel(self.tabla_frame, text="No hay registros"
                         ).pack(pady=20)
            return

        for i, c in enumerate(cerdos):

            valor = c["peso_lote_kg"] * c["precio_mercado_kg"]
            estado = "🟢 Activo" if c["estado"] == "en_engorde" else "🔴 Vendido"

            fila = [
                c["id_cerdo"],
                f"{c['peso_lote_kg']} kg",
                formatear_monto(c["precio_mercado_kg"]),
                formatear_monto(valor),
                estado,
                c["fecha_registro"]
            ]

            row = ctk.CTkFrame(self.tabla_frame)
            row.pack(fill="x", pady=2)

            for j, val in enumerate(fila):
                ctk.CTkLabel(row, text=val).grid(row=0, column=j, padx=8, pady=6, sticky="w")

    #  FORMULARIO 

    def _crear_formulario(self, parent):
        frame = ctk.CTkScrollableFrame(parent)
        frame.grid(row=0, column=1, sticky="nsew")

        # REGISTRAR CERDO
        ctk.CTkLabel(frame, text="Registrar",
                     font=ctk.CTkFont(size=16, weight="bold")
                     ).pack(anchor="w", padx=15, pady=10)

        self.id_entry = ctk.CTkEntry(frame, placeholder_text="ID (CE-001)")
        self.id_entry.pack(fill="x", padx=15, pady=5)

        self.peso_lote = ctk.CTkEntry(frame, placeholder_text="Peso lote kg")
        self.peso_lote.pack(fill="x", padx=15, pady=5)

        self.precio = ctk.CTkEntry(frame, placeholder_text="Precio kg")
        self.precio.pack(fill="x", padx=15, pady=5)

        self.fecha = ctk.CTkEntry(frame)
        self.fecha.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.fecha.pack(fill="x", padx=15, pady=5)

        ctk.CTkButton(
            frame, text="Guardar",
            command=self._guardar_cerdo,
            fg_color="#1D9E75"
        ).pack(fill="x", padx=15, pady=10)

        # VENTA
        ctk.CTkLabel(frame, text="Venta",
                     font=ctk.CTkFont(size=16, weight="bold")
                     ).pack(anchor="w", padx=15, pady=10)

        self.venta_id = ctk.CTkEntry(frame, placeholder_text="ID")
        self.venta_id.pack(fill="x", padx=15, pady=5)

        self.venta_peso = ctk.CTkEntry(frame, placeholder_text="Peso final")
        self.venta_peso.pack(fill="x", padx=15, pady=5)

        self.venta_precio = ctk.CTkEntry(frame, placeholder_text="Precio kg")
        self.venta_precio.pack(fill="x", padx=15, pady=5)

        ctk.CTkButton(
            frame, text="Vender",
            command=self._guardar_venta,
            fg_color="#E67E22"
        ).pack(fill="x", padx=15, pady=10)

    # GUARDAR CERDO 

    def _guardar_cerdo(self):
        ok1, id_cerdo = validar_texto(self.id_entry.get())
        ok2, peso = validar_peso(self.peso_lote.get())
        ok3, precio = validar_monto(self.precio.get())
        ok4, fecha = validar_fecha(self.fecha.get())

        if not ok1:
            return messagebox.showerror("Error", id_cerdo)

        try:
            agregar_cerdo_engorde(id_cerdo, peso, peso, precio, fecha)
            messagebox.showinfo("OK", "Registrado")
            self._limpiar()
            self._refresh()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # VENTA 

    def _guardar_venta(self):
        ok1, id_cerdo = validar_texto(self.venta_id.get())
        ok2, peso = validar_peso(self.venta_peso.get())
        ok3, precio = validar_monto(self.venta_precio.get())

        if not ok1:
            return messagebox.showerror("Error", id_cerdo)

        try:
            total = vender_cerdo_engorde(id_cerdo, peso, precio, datetime.now().strftime("%Y-%m-%d"))
            messagebox.showinfo("Venta", f"Total: {formatear_monto(total)}")
            self._refresh()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    

    def _limpiar(self):
        self.id_entry.delete(0, "end")
        self.peso_lote.delete(0, "end")
        self.precio.delete(0, "end")

    def _refresh(self):
        self._cargar_tabla()
        for w in self.frame_tarjetas.winfo_children():
            w.destroy()
        self._crear_tarjetas()