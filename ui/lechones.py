import customtkinter as ctk
from database.models import (
    vender_lechon,
    agregar_ingreso,
    obtener_lechones_con_puerca,
    contar_lechones,
    registrar_camada
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
            text="Control de camadas, ventas y rentabilidad",
            font=ctk.CTkFont(size=13),
            text_color="gray50"
        ).grid(row=1, column=0, sticky="w")

    #TARJETAS 

    def _crear_tarjetas(self):
        self.frame_tarjetas = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_tarjetas.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        self.frame_tarjetas.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self._actualizar_tarjetas()

    def _actualizar_tarjetas(self):
        for widget in self.frame_tarjetas.winfo_children():
            widget.destroy()

        try:
            rentabilidad = calcular_rentabilidad_puercas_lechones()
            total, vendidos = contar_lechones()
        except Exception:
            return

        color_balance = "#1D9E75" if rentabilidad["balance"] >= 0 else "#E74C3C"

        tarjetas = [
            ("Rentabilidad", formatear_monto(rentabilidad["balance"]), color_balance),
            ("Gastos", formatear_monto(rentabilidad["total_gastos"]), "#E74C3C"),
            ("Ingresos", formatear_monto(rentabilidad["total_ingresos"]), "#1D9E75"),
            ("Vendidos", f"{vendidos} / {total}", "#1D9E75"),
        ]

        for i, (titulo, valor, color) in enumerate(tarjetas):
            card = ctk.CTkFrame(self.frame_tarjetas)
            card.grid(row=0, column=i, padx=8, sticky="ew")

            ctk.CTkLabel(
                card,
                text=titulo,
                font=ctk.CTkFont(size=12),
                text_color="gray50"
            ).grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")

            ctk.CTkLabel(
                card,
                text=valor,
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color=color
            ).grid(row=1, column=0, padx=15, pady=(0, 15), sticky="w")

    # CONTENIDO 

    def _crear_contenido(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=2, column=0, sticky="nsew")

        frame.grid_columnconfigure(0, weight=2)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_rowconfigure(0, weight=1)

        self._crear_tabla(frame)
        self._crear_formulario(frame)

    # TABLA 

    def _crear_tabla(self, parent):
        frame = ctk.CTkFrame(parent)
        frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(2, weight=1)

        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.grid(row=0, column=0, padx=15, pady=(15, 10), sticky="ew")

        ctk.CTkLabel(
            header,
            text="Lechones Registrados",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, sticky="w")

        self.filtro_estado = ctk.CTkOptionMenu(
            header,
            values=["Todos", "Disponibles", "Vendidos"],
            command=lambda _: self._cargar_tabla()
        )
        self.filtro_estado.grid(row=0, column=1, sticky="e")

        columnas = ["ID", "Puerca", "Nacimiento", "Peso", "Estado", "Precio"]

        headers = ctk.CTkFrame(frame, fg_color="transparent")
        headers.grid(row=1, column=0, sticky="ew", padx=15)

        for i, col in enumerate(columnas):
            ctk.CTkLabel(
                headers,
                text=col,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="gray50"
            ).grid(row=0, column=i, padx=8, sticky="w")

        self.tabla_frame = ctk.CTkScrollableFrame(frame)
        self.tabla_frame.grid(row=2, column=0, sticky="nsew", padx=15, pady=(5, 15))

        self._cargar_tabla()

    def _cargar_tabla(self):
        for widget in self.tabla_frame.winfo_children():
            widget.destroy()

        try:
            lechones = obtener_lechones_con_puerca()
        except Exception:
            lechones = []

        filtro = self.filtro_estado.get()

        if filtro == "Disponibles":
            lechones = [l for l in lechones if l["estado"] == "disponible"]
        elif filtro == "Vendidos":
            lechones = [l for l in lechones if l["estado"] == "vendido"]

        if not lechones:
            ctk.CTkLabel(
                self.tabla_frame,
                text="No hay lechones",
                text_color="gray50"
            ).grid(row=0, column=0, pady=20)
            return

        for i, l in enumerate(lechones):

            estado = "Vendido" if l["estado"] == "vendido" else "Disponible"

            fila = [
                l["id"],
                f"{l['puerca_nombre']} ({l['puerca_id']})",
                l["fecha_nacimiento"],
                f"{l['peso_kg']} kg",
                estado,
                formatear_monto(l["precio_venta"]) if l["precio_venta"] else "—"
            ]

            bg = "#2b2b2b" if i % 2 == 0 else "#323232"
            row = ctk.CTkFrame(self.tabla_frame, fg_color=bg)
            row.grid(row=i, column=0, sticky="ew", pady=1)

            for j, val in enumerate(fila):
                color = None
                if j == 4:
                    color = "#1D9E75" if estado == "Vendido" else "#F39C12"

                ctk.CTkLabel(
                    row,
                    text=val,
                    font=ctk.CTkFont(size=13),
                    text_color=color if color else None
                ).grid(row=0, column=j, padx=8, pady=8, sticky="w")

    #FORMULARIO 

    def _crear_formulario(self, parent):
        frame = ctk.CTkScrollableFrame(parent)
        frame.grid(row=0, column=1, sticky="nsew")

        # CAMADA
        ctk.CTkLabel(frame, text="Registrar Camada",
                     font=ctk.CTkFont(size=16, weight="bold")
                     ).pack(pady=10)

        self.camada_puerca = ctk.CTkEntry(frame, placeholder_text="ID Puerca")
        self.camada_puerca.pack(padx=15, pady=5, fill="x")

        self.camada_cantidad = ctk.CTkEntry(frame, placeholder_text="Cantidad")
        self.camada_cantidad.pack(padx=15, pady=5, fill="x")

        self.camada_fecha = ctk.CTkEntry(frame)
        self.camada_fecha.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.camada_fecha.pack(padx=15, pady=5, fill="x")

        ctk.CTkButton(
            frame,
            text="Guardar Camada",
            command=self._guardar_camada
        ).pack(padx=15, pady=10, fill="x")

        # VENTA
        ctk.CTkLabel(frame, text="Venta",
                     font=ctk.CTkFont(size=16, weight="bold")
                     ).pack(pady=10)

        self.venta_id = ctk.CTkEntry(frame, placeholder_text="ID")
        self.venta_id.pack(padx=15, pady=5, fill="x")

        self.venta_precio = ctk.CTkEntry(frame, placeholder_text="Precio")
        self.venta_precio.pack(padx=15, pady=5, fill="x")

        self.venta_fecha = ctk.CTkEntry(frame)
        self.venta_fecha.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.venta_fecha.pack(padx=15, pady=5, fill="x")

        ctk.CTkButton(
            frame,
            text="Vender",
            command=self._guardar_venta
        ).pack(padx=15, pady=10, fill="x")

    # LÓGICA 

    def _guardar_camada(self):
        ok, puerca = validar_texto(self.camada_puerca.get())
        if not ok:
            messagebox.showerror("Error", puerca)
            return

        try:
            cantidad = int(self.camada_cantidad.get())
        except:
            messagebox.showerror("Error", "Cantidad inválida")
            return

        registrar_camada(puerca, self.camada_fecha.get(), cantidad)
        messagebox.showinfo("OK", "Camada registrada")
        self._refresh()

    def _guardar_venta(self):
        ok, precio = validar_monto(self.venta_precio.get())
        if not ok:
            messagebox.showerror("Error", precio)
            return

        try:
            vender_lechon(int(self.venta_id.get()), precio, self.venta_fecha.get())
            agregar_ingreso("lechones", "Venta", precio, self.venta_fecha.get())
            messagebox.showinfo("OK", "Venta realizada")
            self._refresh()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _refresh(self):
        self._cargar_tabla()
        self._actualizar_tarjetas()