import customtkinter as ctk
import tkinter.messagebox as messagebox
from database.models import (
    agregar_empleado, obtener_empleados,
    registrar_pago_empleado, obtener_pagos_empleado,
    obtener_resumen_empleados
)
from logic.calculos import formatear_monto, validar_texto, validar_fecha, validar_monto
from datetime import datetime


# Mapa de tipos de pago legibles
TIPOS_PAGO = {
    "mensual":   "Sueldo Mensual",
    "quincenal": "Pago Quincenal",
    "semanal":   "Pago Semanal",
    "diario":    "Pago por Día",
    "ajuste":    "Trabajo por Ajuste"
}

TIPOS_PAGO_INVERSO = {v: k for k, v in TIPOS_PAGO.items()}


class Empleados(ctk.CTkFrame):
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
            header, text="Gestión de Empleados",
            font=ctk.CTkFont(size=24, weight="bold")
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            header, text="Control de personal, tipos de pago y nómina",
            font=ctk.CTkFont(size=13), text_color="gray50"
        ).grid(row=1, column=0, sticky="w")

    #  TARJETAS 

    def _crear_tarjetas(self):
        self.frame_tarjetas = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_tarjetas.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        self.frame_tarjetas.grid_columnconfigure((0, 1, 2), weight=1)
        self._cargar_tarjetas()

    def _cargar_tarjetas(self):
        for w in self.frame_tarjetas.winfo_children():
            w.destroy()
        res = obtener_resumen_empleados()
        total_emp = res["total_empleados"]
        total_pag = res["total_pagado"]
        promedio = total_pag / max(1, total_emp)

        tarjetas = [
            ("Empleados Activos", str(total_emp), "#1D9E75"),
            ("Total Pagado", formatear_monto(total_pag), "#E74C3C"),
            ("Promedio por empleado", formatear_monto(promedio), "#1D9E75"),
        ]
        for i, (tit, val, col) in enumerate(tarjetas):
            card = ctk.CTkFrame(self.frame_tarjetas)
            card.grid(row=0, column=i, padx=8, sticky="ew")
            ctk.CTkLabel(card, text=tit,
                         font=ctk.CTkFont(size=12), text_color="gray50"
                         ).grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")
            ctk.CTkLabel(card, text=val,
                         font=ctk.CTkFont(size=18, weight="bold"), text_color=col
                         ).grid(row=1, column=0, padx=15, pady=(0, 15), sticky="w")

    #CONTENIDO

    def _crear_contenido(self):
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.grid(row=2, column=0, sticky="nsew")
        main.grid_columnconfigure(0, weight=2)
        main.grid_columnconfigure(1, weight=1)
        main.grid_rowconfigure(0, weight=1)
        self._crear_tabla(main)
        self._crear_formulario(main)

    #TABLA 

    def _crear_tabla(self, parent):
        frame = ctk.CTkFrame(parent)
        frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            frame, text="Lista de Empleados",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, padx=15, pady=(15, 10), sticky="w")

        self.tabla_frame = ctk.CTkScrollableFrame(frame)
        self.tabla_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        self._cargar_tabla()

    def _cargar_tabla(self):
        for w in self.tabla_frame.winfo_children():
            w.destroy()
        empleados = obtener_empleados(activo=True)
        if not empleados:
            ctk.CTkLabel(
                self.tabla_frame, text="No hay empleados registrados",
                text_color="gray50"
            ).pack(pady=20)
            return
        for i, e in enumerate(empleados):
            bg = "#2b2b2b" if i % 2 == 0 else "#323232"
            row = ctk.CTkFrame(self.tabla_frame, fg_color=bg, corner_radius=4)
            row.pack(fill="x", pady=1)
            row.grid_columnconfigure(0, weight=1)

            tipo_legible = TIPOS_PAGO.get(e["tipo_pago"], e["tipo_pago"])
            total_pagado = sum(
                p["monto"] for p in obtener_pagos_empleado(e["id"])
            )

            texto = (f"{e['nombre']}  •  {tipo_legible}  •  "
                     f"Base: {formatear_monto(e['salario_base'])}  •  "
                     f"Pagado: {formatear_monto(total_pagado)}  •  "
                     f"Desde: {e['fecha_contrato']}")

            ctk.CTkLabel(
                row, text=texto, font=ctk.CTkFont(size=12)
            ).grid(row=0, column=0, padx=10, pady=6, sticky="w")

            ctk.CTkButton(
                row, text="Pagar", width=65, height=26,
                fg_color="#1D9E75", hover_color="#0F6E56",
                command=lambda emp=e: self._abrir_ventana_pago(emp)
            ).grid(row=0, column=1, padx=4)

            ctk.CTkButton(
                row, text="Historial", width=75, height=26,
                fg_color="transparent", border_width=1,
                command=lambda emp=e: self._ver_historial(emp)
            ).grid(row=0, column=2, padx=4)

    # VENTANA DE PAGO 

    def _abrir_ventana_pago(self, empleado):
        tipo = empleado["tipo_pago"]
        base = empleado["salario_base"]
        tipo_legible = TIPOS_PAGO.get(tipo, tipo)

        win = ctk.CTkToplevel(self)
        win.title(f"Pago — {empleado['nombre']}")
        win.geometry("440x560")
        win.grab_set()
        win.resizable(False, False)

        # Encabezado
        ctk.CTkLabel(
            win, text=empleado["nombre"],
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(20, 3))

        ctk.CTkLabel(
            win,
            text=f"Tipo: {tipo_legible}  •  Base: {formatear_monto(base)}",
            font=ctk.CTkFont(size=12), text_color="gray50"
        ).pack(pady=(0, 15))

        ctk.CTkFrame(win, height=1, fg_color="gray30").pack(fill="x", padx=20, pady=(0, 15))

        scroll = ctk.CTkScrollableFrame(win, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=5)

        def lbl(texto):
            ctk.CTkLabel(scroll, text=texto,
                         font=ctk.CTkFont(size=12), text_color="gray50"
                         ).pack(anchor="w", padx=15, pady=(8, 2))

        #  Concepto (OptionMenu + campo libre combinados) 
        lbl("Tipo de concepto")
        conceptos = self._conceptos_por_tipo(tipo)
        concepto_menu = ctk.CTkOptionMenu(
            scroll, values=conceptos,
            command=lambda v: concepto_libre.delete(0, "end") or concepto_libre.insert(0, v)
        )
        concepto_menu.pack(fill="x", padx=15, pady=(0, 4))

        lbl("Concepto personalizado (editable)")
        concepto_libre = ctk.CTkEntry(
            scroll, placeholder_text="Describe el pago..."
        )
        concepto_libre.insert(0, conceptos[0])
        concepto_libre.pack(fill="x", padx=15)

        #  Período que cubre 
        lbl("Período que cubre (opcional)")
        periodo_entry = ctk.CTkEntry(
            scroll,
            placeholder_text="Ej: semana 21-28 abril / mes abril 2026"
        )
        periodo_entry.pack(fill="x", padx=15)

        #  Campos especiales según tipo 
        dias_entry = None
        if tipo == "diario":
            lbl("Días trabajados")
            dias_frame = ctk.CTkFrame(scroll, fg_color="transparent")
            dias_frame.pack(fill="x", padx=15)
            dias_frame.grid_columnconfigure(0, weight=1)
            dias_entry = ctk.CTkEntry(dias_frame, placeholder_text="Nº días")
            dias_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
            ctk.CTkLabel(dias_frame, text=f"× {formatear_monto(base)}/día",
                         font=ctk.CTkFont(size=12), text_color="gray50"
                         ).pack(side="left")

        if tipo == "ajuste":
            lbl("Descripción del trabajo realizado")
            desc_entry = ctk.CTkEntry(
                scroll,
                placeholder_text="Ej: limpieza general corrales, vacunación lote CE-001"
            )
            desc_entry.pack(fill="x", padx=15)
        else:
            desc_entry = None

        #  Monto 
        lbl("Monto a pagar (RD$)")
        monto_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        monto_frame.pack(fill="x", padx=15)
        monto_frame.grid_columnconfigure(0, weight=1)

        monto_entry = ctk.CTkEntry(monto_frame, placeholder_text="0.00")
        monto_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        # Botón para pre-llenar con monto base
        def prellenar_monto():
            monto_entry.delete(0, "end")
            if tipo == "diario" and dias_entry:
                try:
                    dias = float(dias_entry.get())
                    monto_entry.insert(0, str(round(dias * base, 2)))
                    return
                except ValueError:
                    pass
            monto_entry.insert(0, str(base))

        ctk.CTkButton(
            monto_frame, text="Base", width=55, height=32,
            fg_color="#3A7EBF", hover_color="#2C6094",
            command=prellenar_monto
        ).pack(side="left")

        # Fecha
        lbl("Fecha del pago (YYYY-MM-DD)")
        fecha_entry = ctk.CTkEntry(scroll)
        fecha_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        fecha_entry.pack(fill="x", padx=15)

        # Notas 
        lbl("Notas adicionales (opcional)")
        notas_entry = ctk.CTkEntry(scroll, placeholder_text="Cualquier observación")
        notas_entry.pack(fill="x", padx=15)

        # Botones 
        ctk.CTkFrame(win, height=1, fg_color="gray30").pack(fill="x", padx=20, pady=(10, 0))

        def guardar():
            ok1, monto = validar_monto(monto_entry.get())
            ok2, fecha = validar_fecha(fecha_entry.get())
            if not ok1: messagebox.showerror("Error", monto, parent=win); return
            if not ok2: messagebox.showerror("Error", fecha, parent=win); return

            # Armar concepto final
            concepto_final = concepto_libre.get().strip() or conceptos[0]
            periodo = periodo_entry.get().strip()
            if periodo:
                concepto_final += f" ({periodo})"
            if desc_entry:
                desc = desc_entry.get().strip()
                if desc:
                    concepto_final += f" — {desc}"
            notas = notas_entry.get().strip()
            if notas:
                concepto_final += f" | {notas}"

            if not messagebox.askyesno(
                "Confirmar pago",
                f"¿Registrar pago de {formatear_monto(monto)}\na {empleado['nombre']}?",
                parent=win
            ):
                return

            registrar_pago_empleado(empleado["id"], monto, fecha, concepto_final)
            messagebox.showinfo(
                "Pago registrado",
                f"Se registró {formatear_monto(monto)} para {empleado['nombre']}",
                parent=win
            )
            win.destroy()
            self._refresh()

        btn_frame = ctk.CTkFrame(win, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=10)
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            btn_frame, text="Confirmar Pago",
            command=guardar,
            fg_color="#1D9E75", hover_color="#0F6E56"
        ).grid(row=0, column=0, padx=(0, 5), sticky="ew")

        ctk.CTkButton(
            btn_frame, text="Cancelar",
            command=win.destroy,
            fg_color="transparent", border_width=1
        ).grid(row=0, column=1, padx=(5, 0), sticky="ew")

    def _conceptos_por_tipo(self, tipo):
        mapa = {
            "mensual":   ["Salario mensual", "Salario mensual + bono", "Adelanto"],
            "quincenal": ["1ra quincena", "2da quincena", "Quincena + extra"],
            "semanal":   ["Pago semanal", "Semana regular", "Semana + horas extra"],
            "diario":    ["Jornada diaria", "Días trabajados", "Jornada + extra"],
            "ajuste":    ["Trabajo por ajuste", "Trabajo especial",
                          "Limpieza general", "Vacunación", "Carga/Descarga"]
        }
        return mapa.get(tipo, ["Pago general"])

    def _calcular_monto_sugerido(self, tipo, base):
        """Pre-llena el monto según el tipo de pago."""
        if tipo == "mensual":
            return base
        elif tipo == "quincenal":
            return base
        elif tipo == "semanal":
            return base
        elif tipo == "diario":
            return base
        elif tipo == "ajuste":
            return base
        return base

    # HISTORIAL DE PAGOS 

    def _ver_historial(self, empleado):
        win = ctk.CTkToplevel(self)
        win.title(f"Historial — {empleado['nombre']}")
        win.geometry("500x400")
        win.grab_set()

        ctk.CTkLabel(
            win, text=f"Historial de pagos — {empleado['nombre']}",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(15, 5))

        scroll = ctk.CTkScrollableFrame(win)
        scroll.pack(fill="both", expand=True, padx=15, pady=10)

        pagos = obtener_pagos_empleado(empleado["id"])
        if not pagos:
            ctk.CTkLabel(scroll, text="Sin pagos registrados",
                         text_color="gray50").pack(pady=20)
        else:
            total = 0
            for i, p in enumerate(pagos):
                bg = "#2b2b2b" if i % 2 == 0 else "#323232"
                row = ctk.CTkFrame(scroll, fg_color=bg, corner_radius=4)
                row.pack(fill="x", pady=1)
                ctk.CTkLabel(
                    row,
                    text=f"{p['fecha']}  •  {p['concepto']}  •  {formatear_monto(p['monto'])}",
                    font=ctk.CTkFont(size=12)
                ).pack(side="left", padx=10, pady=6)
                total += p["monto"]

            ctk.CTkLabel(
                win, text=f"Total pagado: {formatear_monto(total)}",
                font=ctk.CTkFont(size=13, weight="bold"), text_color="#1D9E75"
            ).pack(pady=10)

    
    # FORMULARIO NUEVO EMPLEADO 

    def _crear_formulario(self, parent):
        frame = ctk.CTkScrollableFrame(parent)
        frame.grid(row=0, column=1, sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            frame, text="Registrar Empleado",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, padx=15, pady=(15, 10), sticky="w")

        ctk.CTkLabel(frame, text="Nombre completo",
                     font=ctk.CTkFont(size=12), text_color="gray50"
                     ).grid(row=1, column=0, padx=15, pady=(8, 2), sticky="w")
        self.e_nombre = ctk.CTkEntry(frame, placeholder_text="Nombre del empleado")
        self.e_nombre.grid(row=2, column=0, padx=15, sticky="ew")

        ctk.CTkLabel(frame, text="Tipo de pago",
                     font=ctk.CTkFont(size=12), text_color="gray50"
                     ).grid(row=3, column=0, padx=15, pady=(8, 2), sticky="w")
        self.e_tipo = ctk.CTkOptionMenu(
            frame,
            values=list(TIPOS_PAGO.values()),
            command=self._actualizar_label_base
        )
        self.e_tipo.grid(row=4, column=0, padx=15, sticky="ew")

        self.e_base_label = ctk.CTkLabel(
            frame, text="Monto base (RD$)",
            font=ctk.CTkFont(size=12), text_color="gray50"
        )
        self.e_base_label.grid(row=5, column=0, padx=15, pady=(8, 2), sticky="w")
        self.e_salario = ctk.CTkEntry(frame, placeholder_text="Monto")
        self.e_salario.grid(row=6, column=0, padx=15, sticky="ew")

        ctk.CTkLabel(frame, text="Fecha de contrato (YYYY-MM-DD)",
                     font=ctk.CTkFont(size=12), text_color="gray50"
                     ).grid(row=7, column=0, padx=15, pady=(8, 2), sticky="w")
        self.e_fecha = ctk.CTkEntry(frame)
        self.e_fecha.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.e_fecha.grid(row=8, column=0, padx=15, sticky="ew")

        ctk.CTkButton(
            frame, text="Guardar Empleado",
            command=self._guardar_empleado,
            fg_color="#1D9E75", hover_color="#0F6E56"
        ).grid(row=9, column=0, padx=15, pady=20, sticky="ew")

    def _actualizar_label_base(self, tipo_legible):
        """Actualiza el label del monto base según el tipo de pago seleccionado."""
        textos = {
            "Sueldo Mensual":     "Sueldo mensual (RD$)",
            "Pago Quincenal":     "Monto por quincena (RD$)",
            "Pago Semanal":       "Monto por semana (RD$)",
            "Pago por Día":       "Monto por día (RD$)",
            "Trabajo por Ajuste": "Monto base por ajuste (RD$)"
        }
        self.e_base_label.configure(
            text=textos.get(tipo_legible, "Monto base (RD$)")
        )

    def _guardar_empleado(self):
        ok1, nombre = validar_texto(self.e_nombre.get(), "Nombre")
        ok2, salario = validar_monto(self.e_salario.get())
        ok3, fecha = validar_fecha(self.e_fecha.get())

        if not ok1: messagebox.showerror("Error", nombre); return
        if not ok2: messagebox.showerror("Error", salario); return
        if not ok3: messagebox.showerror("Error", fecha); return

        tipo_legible = self.e_tipo.get()
        tipo_interno = TIPOS_PAGO_INVERSO.get(tipo_legible, "mensual")

        agregar_empleado(nombre, tipo_interno, salario, fecha)
        messagebox.showinfo("Éxito", f"Empleado {nombre} registrado")
        self.e_nombre.delete(0, "end")
        self.e_salario.delete(0, "end")
        self._refresh()

 

    def _refresh(self):
        self._cargar_tabla()
        self._cargar_tarjetas()