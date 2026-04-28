import customtkinter as ctk
import tkinter.messagebox as messagebox
from database.models import obtener_gastos_por_seccion, agregar_gasto
from logic.calculos import (
    formatear_monto, validar_monto, validar_fecha,
    filtrar_gastos_por_periodo, resumen_gastos_por_periodo
)
from datetime import datetime


class Gastos(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self._crear_header()
        self._crear_contenido()

    

    def _crear_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        ctk.CTkLabel(
            header, text="Control de Gastos",
            font=ctk.CTkFont(size=24, weight="bold")
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            header, text="Registro y análisis de todos los egresos de la granja",
            font=ctk.CTkFont(size=13), text_color="gray50"
        ).grid(row=1, column=0, sticky="w")

    

    def _crear_contenido(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=2, column=0, sticky="nsew")
        frame.grid_columnconfigure(0, weight=2)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_rowconfigure(0, weight=1)
        self._crear_panel_tabla(frame)
        self._crear_formulario(frame)

    # PANEL TABLA + FILTROS 

    def _crear_panel_tabla(self, parent):
        frame = ctk.CTkFrame(parent)
        frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(2, weight=1)

        # Tarjeta resumen
        self.resumen_frame = ctk.CTkFrame(frame, fg_color="transparent")
        self.resumen_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 5))
        self.resumen_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self._cargar_resumen()

        # Filtros
        filtros = ctk.CTkFrame(frame, fg_color="transparent")
        filtros.grid(row=1, column=0, sticky="ew", padx=15, pady=(5, 8))

        ctk.CTkLabel(filtros, text="Período:",
                     font=ctk.CTkFont(size=12), text_color="gray50"
                     ).grid(row=0, column=0, padx=(0, 5))
        self.filtro_periodo = ctk.CTkOptionMenu(
            filtros,
            values=["mes", "dia", "semana", "año", "todo"],
            command=lambda _: self._aplicar_filtro(),
            width=110
        )
        self.filtro_periodo.grid(row=0, column=1, padx=(0, 10))

        ctk.CTkLabel(filtros, text="Sección:",
                     font=ctk.CTkFont(size=12), text_color="gray50"
                     ).grid(row=0, column=2, padx=(0, 5))
        self.filtro_seccion = ctk.CTkOptionMenu(
            filtros,
            values=["todas", "puercas", "lechones", "engorde", "empleados", "general"],
            command=lambda _: self._aplicar_filtro(),
            width=120
        )
        self.filtro_seccion.grid(row=0, column=3, padx=(0, 10))

        ctk.CTkLabel(filtros, text="Categoría:",
                     font=ctk.CTkFont(size=12), text_color="gray50"
                     ).grid(row=0, column=4, padx=(0, 5))
        self.filtro_categoria = ctk.CTkOptionMenu(
            filtros,
            values=["todas", "Alimentación", "Medicina", "Mano de obra",
                    "Salario", "Veterinario", "Mantenimiento", "Otro"],
            command=lambda _: self._aplicar_filtro(),
            width=140
        )
        self.filtro_categoria.grid(row=0, column=5)

        # Tabla
        cols_frame = ctk.CTkFrame(frame, fg_color="transparent")
        cols_frame.grid(row=1, column=0, sticky="ew", padx=15, pady=(40, 0))
        for i, col in enumerate(["Fecha", "Sección", "Categoría", "Monto", "Notas"]):
            ctk.CTkLabel(
                cols_frame, text=col,
                font=ctk.CTkFont(size=11, weight="bold"), text_color="gray50"
            ).grid(row=0, column=i, padx=8, sticky="w")

        self.tabla_frame = ctk.CTkScrollableFrame(frame, fg_color="transparent")
        self.tabla_frame.grid(row=2, column=0, sticky="nsew", padx=15, pady=(5, 15))
        self._aplicar_filtro()

    def _cargar_resumen(self):
        for w in self.resumen_frame.winfo_children():
            w.destroy()
        resumen = resumen_gastos_por_periodo(self.filtro_periodo.get()
                                             if hasattr(self, "filtro_periodo") else "mes")
        total = resumen["total"]
        por_cat = resumen["por_categoria"]
        # Top 3 categorías
        top = sorted(por_cat.items(), key=lambda x: x[1], reverse=True)[:3]

        card = ctk.CTkFrame(self.resumen_frame)
        card.grid(row=0, column=0, padx=8, sticky="ew")
        ctk.CTkLabel(card, text="Total período",
                     font=ctk.CTkFont(size=12), text_color="gray50"
                     ).grid(row=0, column=0, padx=15, pady=(10, 3), sticky="w")
        ctk.CTkLabel(card, text=formatear_monto(total),
                     font=ctk.CTkFont(size=16, weight="bold"), text_color="#E74C3C"
                     ).grid(row=1, column=0, padx=15, pady=(0, 10), sticky="w")

        for i, (cat, monto) in enumerate(top):
            card2 = ctk.CTkFrame(self.resumen_frame)
            card2.grid(row=0, column=i + 1, padx=8, sticky="ew")
            ctk.CTkLabel(card2, text=cat[:18],
                         font=ctk.CTkFont(size=12), text_color="gray50"
                         ).grid(row=0, column=0, padx=15, pady=(10, 3), sticky="w")
            ctk.CTkLabel(card2, text=formatear_monto(monto),
                         font=ctk.CTkFont(size=14, weight="bold"), text_color="#E74C3C"
                         ).grid(row=1, column=0, padx=15, pady=(0, 10), sticky="w")

    def _aplicar_filtro(self):
        periodo = self.filtro_periodo.get() if hasattr(self, "filtro_periodo") else "mes"
        seccion = self.filtro_seccion.get() if hasattr(self, "filtro_seccion") else "todas"
        categoria = self.filtro_categoria.get() if hasattr(self, "filtro_categoria") else "todas"

        sec = None if seccion == "todas" else seccion
        gastos = filtrar_gastos_por_periodo(seccion=sec, periodo=periodo)

        if categoria != "todas":
            gastos = [g for g in gastos if g.get("categoria", "") == categoria]

        self.gastos_actuales = gastos
        self._cargar_tabla()
        self._cargar_resumen()

    def _cargar_tabla(self):
        for w in self.tabla_frame.winfo_children():
            w.destroy()

        gastos = getattr(self, "gastos_actuales", [])

        if not gastos:
            ctk.CTkLabel(
                self.tabla_frame, text="No hay gastos en este período",
                text_color="gray50"
            ).grid(row=0, column=0, pady=20, padx=15)
            return

        for i, g in enumerate(gastos):
            bg = "#2b2b2b" if i % 2 == 0 else "#323232"
            row = ctk.CTkFrame(self.tabla_frame, fg_color=bg, corner_radius=4)
            row.grid(row=i, column=0, sticky="ew", pady=1)

            fila = [
                g.get("fecha", ""),
                g.get("seccion", ""),
                g.get("categoria", ""),
                formatear_monto(g.get("monto", 0)),
                g.get("notas", "")[:40] or "—"
            ]
            for j, val in enumerate(fila):
                color = "#E74C3C" if j == 3 else None
                ctk.CTkLabel(
                    row, text=val,
                    font=ctk.CTkFont(size=12),
                    text_color=color if color else (
                        "gray90" if ctk.get_appearance_mode() == "Dark" else "gray10")
                ).grid(row=0, column=j, padx=8, pady=6, sticky="w")

    #FORMULARIO NUEVO GASTO 

    def _crear_formulario(self, parent):
        frame = ctk.CTkScrollableFrame(parent)
        frame.grid(row=0, column=1, sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            frame, text="Registrar Gasto",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, padx=15, pady=(15, 10), sticky="w")

        # Sección (dónde se gastó)
        ctk.CTkLabel(frame, text="Sección (¿dónde se gastó?)",
                     font=ctk.CTkFont(size=12), text_color="gray50"
                     ).grid(row=1, column=0, padx=15, pady=(8, 2), sticky="w")
        self.g_seccion = ctk.CTkOptionMenu(
            frame,
            values=["puercas", "lechones", "engorde", "general"]
        )
        self.g_seccion.grid(row=2, column=0, padx=15, sticky="ew")

        # Categoría (en qué se gastó)
        ctk.CTkLabel(frame, text="Categoría (¿en qué se gastó?)",
                     font=ctk.CTkFont(size=12), text_color="gray50"
                     ).grid(row=3, column=0, padx=15, pady=(8, 2), sticky="w")
        self.g_categoria = ctk.CTkOptionMenu(
            frame,
            values=["Alimentación", "Medicina", "Vitaminas",
                    "Mano de obra", "Veterinario", "Mantenimiento",
                    "Transporte", "Insumos", "Otro"],
            command=self._cambiar_categoria
        )
        self.g_categoria.grid(row=4, column=0, padx=15, sticky="ew")

        # Contenedor dinámico según categoría
        self.g_detalle_frame = ctk.CTkFrame(frame, fg_color="transparent")
        self.g_detalle_frame.grid(row=5, column=0, sticky="ew")
        self.g_detalle_frame.grid_columnconfigure(0, weight=1)
        self._mostrar_form_alimentacion()

        # Monto
        ctk.CTkLabel(frame, text="Monto total (RD$)",
                     font=ctk.CTkFont(size=12), text_color="gray50"
                     ).grid(row=6, column=0, padx=15, pady=(8, 2), sticky="w")
        self.g_monto = ctk.CTkEntry(frame, placeholder_text="0.00")
        self.g_monto.grid(row=7, column=0, padx=15, sticky="ew")

        # Fecha
        ctk.CTkLabel(frame, text="Fecha (YYYY-MM-DD)",
                     font=ctk.CTkFont(size=12), text_color="gray50"
                     ).grid(row=8, column=0, padx=15, pady=(8, 2), sticky="w")
        self.g_fecha = ctk.CTkEntry(frame)
        self.g_fecha.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.g_fecha.grid(row=9, column=0, padx=15, sticky="ew")

        # Notas
        ctk.CTkLabel(frame, text="Notas (opcional)",
                     font=ctk.CTkFont(size=12), text_color="gray50"
                     ).grid(row=10, column=0, padx=15, pady=(8, 2), sticky="w")
        self.g_notas = ctk.CTkEntry(frame, placeholder_text="Descripción adicional")
        self.g_notas.grid(row=11, column=0, padx=15, sticky="ew")

        ctk.CTkButton(
            frame, text="Guardar Gasto",
            command=self._guardar,
            fg_color="#E74C3C", hover_color="#C0392B"
        ).grid(row=12, column=0, padx=15, pady=20, sticky="ew")

    #  FORMULARIOS DINÁMICOS POR CATEGORÍA 

    def _cambiar_categoria(self, seleccion):
        for w in self.g_detalle_frame.winfo_children():
            w.destroy()
        if seleccion == "Alimentación":
            self._mostrar_form_alimentacion()
        elif seleccion in ("Medicina", "Vitaminas"):
            self._mostrar_form_medicina()
        elif seleccion == "Mano de obra":
            self._mostrar_form_mano_obra()
        else:
            pass  # solo monto y fecha — campos base suficientes

    def _mostrar_form_alimentacion(self):
        f = self.g_detalle_frame
        ctk.CTkLabel(f, text="Tipo de alimento",
                     font=ctk.CTkFont(size=12), text_color="gray50"
                     ).grid(row=0, column=0, padx=15, pady=(6, 2), sticky="w")
        self.ali_tipo = ctk.CTkOptionMenu(
            f, values=["Inicio", "Crecimiento", "Engorde", "Lactancia", "Gestación", "Otro"]
        )
        self.ali_tipo.grid(row=1, column=0, padx=15, sticky="ew")

        ctk.CTkLabel(f, text="Unidad",
                     font=ctk.CTkFont(size=12), text_color="gray50"
                     ).grid(row=2, column=0, padx=15, pady=(6, 2), sticky="w")
        self.ali_unidad = ctk.CTkOptionMenu(f, values=["Sacos", "Libras", "Kg"])
        self.ali_unidad.grid(row=3, column=0, padx=15, sticky="ew")

        ctk.CTkLabel(f, text="Cantidad",
                     font=ctk.CTkFont(size=12), text_color="gray50"
                     ).grid(row=4, column=0, padx=15, pady=(6, 2), sticky="w")
        self.ali_cantidad = ctk.CTkEntry(f, placeholder_text="3")
        self.ali_cantidad.grid(row=5, column=0, padx=15, sticky="ew")
        self.ali_cantidad.bind("<KeyRelease>", self._calcular_alimentacion)

        ctk.CTkLabel(f, text="Precio por unidad (RD$)",
                     font=ctk.CTkFont(size=12), text_color="gray50"
                     ).grid(row=6, column=0, padx=15, pady=(6, 2), sticky="w")
        self.ali_precio = ctk.CTkEntry(f, placeholder_text="850")
        self.ali_precio.grid(row=7, column=0, padx=15, sticky="ew")
        self.ali_precio.bind("<KeyRelease>", self._calcular_alimentacion)

        self.ali_total_label = ctk.CTkLabel(
            f, text="RD$ 0.00",
            font=ctk.CTkFont(size=14, weight="bold"), text_color="#1D9E75"
        )
        self.ali_total_label.grid(row=8, column=0, padx=15, pady=5, sticky="w")

    def _calcular_alimentacion(self, event=None):
        try:
            cant = float(self.ali_cantidad.get())
            precio = float(self.ali_precio.get())
            total = cant * precio
            self.ali_total_label.configure(text=f"RD$ {total:,.2f}")
            self.g_monto.delete(0, "end")
            self.g_monto.insert(0, f"{total:.2f}")
        except (ValueError, AttributeError):
            pass

    def _mostrar_form_medicina(self):
        f = self.g_detalle_frame
        ctk.CTkLabel(f, text="Nombre del medicamento",
                     font=ctk.CTkFont(size=12), text_color="gray50"
                     ).grid(row=0, column=0, padx=15, pady=(6, 2), sticky="w")
        self.med_nombre_g = ctk.CTkEntry(f, placeholder_text="Ej: Ivermectina")
        self.med_nombre_g.grid(row=1, column=0, padx=15, sticky="ew")

    def _mostrar_form_mano_obra(self):
        f = self.g_detalle_frame
        ctk.CTkLabel(f, text="Tipo de trabajo",
                     font=ctk.CTkFont(size=12), text_color="gray50"
                     ).grid(row=0, column=0, padx=15, pady=(6, 2), sticky="w")
        self.mo_tipo_g = ctk.CTkOptionMenu(
            f, values=["Limpieza", "Alimentación", "Vacunación",
                       "Mantenimiento", "Carga/Descarga", "Otro"]
        )
        self.mo_tipo_g.grid(row=1, column=0, padx=15, sticky="ew")

        ctk.CTkLabel(f, text="Tipo de pago",
                     font=ctk.CTkFont(size=12), text_color="gray50"
                     ).grid(row=2, column=0, padx=15, pady=(6, 2), sticky="w")
        self.mo_pago_g = ctk.CTkOptionMenu(
            f, values=["Precio fijo", "Por días"],
            command=self._cambiar_pago_mano_obra_g
        )
        self.mo_pago_g.grid(row=3, column=0, padx=15, sticky="ew")

        self.mo_extra_frame = ctk.CTkFrame(f, fg_color="transparent")
        self.mo_extra_frame.grid(row=4, column=0, sticky="ew")
        self.mo_extra_frame.grid_columnconfigure(0, weight=1)
        self._form_precio_fijo_g()

    def _cambiar_pago_mano_obra_g(self, sel):
        for w in self.mo_extra_frame.winfo_children():
            w.destroy()
        if sel == "Precio fijo":
            self._form_precio_fijo_g()
        else:
            self._form_por_dias_g()

    def _form_precio_fijo_g(self):
        pass  # el monto base ya captura el total

    def _form_por_dias_g(self):
        f = self.mo_extra_frame
        ctk.CTkLabel(f, text="Días trabajados",
                     font=ctk.CTkFont(size=12), text_color="gray50"
                     ).grid(row=0, column=0, padx=15, pady=(6, 2), sticky="w")
        self.mo_dias_g = ctk.CTkEntry(f, placeholder_text="5")
        self.mo_dias_g.grid(row=1, column=0, padx=15, sticky="ew")
        self.mo_dias_g.bind("<KeyRelease>", self._calcular_dias_g)

        ctk.CTkLabel(f, text="Precio por día (RD$)",
                     font=ctk.CTkFont(size=12), text_color="gray50"
                     ).grid(row=2, column=0, padx=15, pady=(6, 2), sticky="w")
        self.mo_precio_dia_g = ctk.CTkEntry(f, placeholder_text="800")
        self.mo_precio_dia_g.grid(row=3, column=0, padx=15, sticky="ew")
        self.mo_precio_dia_g.bind("<KeyRelease>", self._calcular_dias_g)

        self.mo_total_label_g = ctk.CTkLabel(
            f, text="RD$ 0.00",
            font=ctk.CTkFont(size=14, weight="bold"), text_color="#1D9E75"
        )
        self.mo_total_label_g.grid(row=4, column=0, padx=15, pady=5, sticky="w")

    def _calcular_dias_g(self, event=None):
        try:
            dias = float(self.mo_dias_g.get())
            precio = float(self.mo_precio_dia_g.get())
            total = dias * precio
            self.mo_total_label_g.configure(text=f"RD$ {total:,.2f}")
            self.g_monto.delete(0, "end")
            self.g_monto.insert(0, f"{total:.2f}")
        except (ValueError, AttributeError):
            pass

    # GUARDAR 

    def _guardar(self):
        ok1, monto = validar_monto(self.g_monto.get())
        ok2, fecha = validar_fecha(self.g_fecha.get())

        if not ok1: messagebox.showerror("Error", monto); return
        if not ok2: messagebox.showerror("Error", fecha); return

        seccion = self.g_seccion.get()
        categoria = self.g_categoria.get()
        notas = self.g_notas.get().strip()

        # Enriquecer notas según categoría
        try:
            if categoria == "Alimentación" and hasattr(self, "ali_tipo"):
                tipo = self.ali_tipo.get()
                unidad = self.ali_unidad.get()
                cant = self.ali_cantidad.get()
                precio_u = self.ali_precio.get()
                notas = notas or f"{tipo} — {cant} {unidad} x RD${precio_u}"
            elif categoria in ("Medicina", "Vitaminas") and hasattr(self, "med_nombre_g"):
                nombre_med = self.med_nombre_g.get().strip()
                if nombre_med:
                    notas = notas or nombre_med
            elif categoria == "Mano de obra" and hasattr(self, "mo_tipo_g"):
                notas = notas or self.mo_tipo_g.get()
        except Exception:
            pass

        agregar_gasto(seccion, categoria, monto, fecha, notas)
        messagebox.showinfo("Éxito", f"Gasto de {formatear_monto(monto)} registrado en {seccion}")

        # Limpiar campos
        self.g_monto.delete(0, "end")
        self.g_notas.delete(0, "end")
        self._aplicar_filtro()