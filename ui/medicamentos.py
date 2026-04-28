import customtkinter as ctk
import tkinter.messagebox as messagebox
from database.models import (
    agregar_medicamento,
    obtener_medicamentos,
    obtener_medicamentos_pendientes_hoy,
    marcar_medicamento_aplicado,
    eliminar_medicamento,
    obtener_resumen_medicamentos
)
from logic.calculos import (
    formatear_monto,
    validar_texto,
    validar_fecha,
    validar_monto,
    validar_peso,
    calcular_fechas_aplicacion,
    calcular_dosis_total  # 🔥 reutilizamos lógica
)
from datetime import datetime, date
import calendar
import json


class Medicamentos(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.mes_actual = datetime.now().month
        self.anio_actual = datetime.now().year

        self._crear_header()
        self._crear_tarjetas()
        self._crear_contenido()

    # ───────────────── HEADER ─────────────────

    def _crear_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 15))

        ctk.CTkLabel(
            header, text="Control de Medicamentos",
            font=ctk.CTkFont(size=24, weight="bold")
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            header,
            text="Registro sanitario, calendario y control de tratamientos",
            font=ctk.CTkFont(size=13),
            text_color="gray50"
        ).grid(row=1, column=0, sticky="w")

    # ───────────────── TARJETAS ─────────────────

    def _crear_tarjetas(self):
        self.frame_tarjetas = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_tarjetas.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        self.frame_tarjetas.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self._cargar_tarjetas()

    def _cargar_tarjetas(self):
        for w in self.frame_tarjetas.winfo_children():
            w.destroy()

        res = obtener_resumen_medicamentos()

        tarjetas = [
            ("Total", str(res["total"]), "#1D9E75"),
            ("Aplicados", str(res["aplicados"]), "#1D9E75"),
            ("Pendientes", str(res["pendientes"]),
             "#E74C3C" if res["pendientes"] > 0 else "#1D9E75"),
            ("Costo Total", formatear_monto(res["costo_total"]), "#E74C3C"),
        ]

        for i, (titulo, valor, color) in enumerate(tarjetas):
            card = ctk.CTkFrame(self.frame_tarjetas)
            card.grid(row=0, column=i, padx=8, sticky="ew")

            ctk.CTkLabel(card, text=titulo, text_color="gray50"
                         ).grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")

            ctk.CTkLabel(card, text=valor,
                         font=ctk.CTkFont(size=18, weight="bold"),
                         text_color=color
                         ).grid(row=1, column=0, padx=15, pady=(0, 15), sticky="w")

    # ───────────────── CONTENIDO ─────────────────

    def _crear_contenido(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=2, column=0, sticky="nsew")

        frame.grid_columnconfigure(0, weight=3)
        frame.grid_columnconfigure(1, weight=2)

        self._crear_tabla(frame)
        self._crear_formulario(frame)

    # ───────────────── TABLA ─────────────────

    def _crear_tabla(self, parent):
        frame = ctk.CTkFrame(parent)
        frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        self.tabla_frame = ctk.CTkScrollableFrame(frame)
        self.tabla_frame.pack(fill="both", expand=True)

        self._cargar_tabla()

    def _cargar_tabla(self):
        for w in self.tabla_frame.winfo_children():
            w.destroy()

        meds = obtener_medicamentos(None)

        if not meds:
            ctk.CTkLabel(
                self.tabla_frame,
                text="No hay medicamentos registrados",
                text_color="gray50"
            ).pack(pady=20)
            return

        for med in meds:
            estado = "Aplicado" if med["aplicado"] else "Pendiente"
            color = "#1D9E75" if med["aplicado"] else "#F39C12"

            fila = f"{med['nombre']} | {med['dosis_total']} {med['unidad']} | {estado}"

            row = ctk.CTkFrame(self.tabla_frame)
            row.pack(fill="x", pady=2, padx=5)

            ctk.CTkLabel(row, text=fila, text_color=color
                         ).pack(side="left", padx=10)

            if not med["aplicado"]:
                ctk.CTkButton(
                    row, text="✓",
                    width=30,
                    command=lambda mid=med["id"]: self._marcar(mid)
                ).pack(side="right", padx=5)

    def _marcar(self, med_id):
        marcar_medicamento_aplicado(med_id)
        self._refresh()

    # ───────────────── FORMULARIO ─────────────────

    def _crear_formulario(self, parent):
        frame = ctk.CTkScrollableFrame(parent)
        frame.grid(row=0, column=1, sticky="nsew")

        def label(txt):
            ctk.CTkLabel(frame, text=txt, text_color="gray50"
                         ).pack(anchor="w", padx=15, pady=(8, 2))

        def entry(ph):
            e = ctk.CTkEntry(frame, placeholder_text=ph)
            e.pack(fill="x", padx=15)
            return e

        label("Nombre")
        self.nombre = entry("Ivermectina")

        label("Dosis por kg")
        self.dosis_kg = entry("0.5")

        label("Peso animal")
        self.peso = entry("120")

        label("Costo")
        self.costo = entry("500")

        label("Fecha inicio")
        self.fecha = entry("2026-04-08")

        self.fecha.insert(0, datetime.now().strftime("%Y-%m-%d"))

        ctk.CTkButton(
            frame,
            text="Guardar",
            command=self._guardar,
            fg_color="#1D9E75"
        ).pack(padx=15, pady=20, fill="x")

    # ───────────────── GUARDAR ─────────────────

    def _guardar(self):

        ok1, nombre = validar_texto(self.nombre.get(), "Nombre")
        ok2, fecha = validar_fecha(self.fecha.get())
        ok3, costo = validar_monto(self.costo.get())
        ok4, peso = validar_peso(self.peso.get())

        if not ok1:
            messagebox.showerror("Error", nombre)
            return
        if not ok2:
            messagebox.showerror("Error", fecha)
            return
        if not ok3:
            messagebox.showerror("Error", costo)
            return
        if not ok4:
            messagebox.showerror("Error", peso)
            return

        try:
            dosis_kg = float(self.dosis_kg.get())
            dosis_total = calcular_dosis_total(dosis_kg, peso)
        except:
            messagebox.showerror("Error", "Dosis inválida")
            return

        fechas = calcular_fechas_aplicacion(fecha, "Cada 24 horas", 7)

        agregar_medicamento(
            seccion="engorde",
            animal_id="",
            nombre=nombre,
            tipo="Inyección",
            unidad="mL",
            dosis_por_kg=dosis_kg,
            peso_animal=peso,
            dosis_total=dosis_total,
            frecuencia="Cada 24 horas",
            dias=7,
            fecha_inicio=fecha,
            proxima_dosis=fechas[-1],
            fechas=fechas,
            costo=costo
        )

        messagebox.showinfo("Éxito", "Medicamento registrado")
        self._refresh()

    # ───────────────── REFRESH ─────────────────

    def _refresh(self):
        self._cargar_tarjetas()
        self._cargar_tabla()