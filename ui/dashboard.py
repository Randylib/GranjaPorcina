import customtkinter as ctk
from logic.calculos import calcular_resumen_general, formatear_monto
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from database.models import (
    obtener_gastos_por_seccion,
    obtener_ingresos_por_seccion,
    obtener_medicamentos_pendientes_hoy
)
from datetime import datetime
import tkinter.messagebox as messagebox
import os
import subprocess
import sys


class Dashboard(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self._canvas_matplotlib = None
        self._fig = None
        self._construir()

    def _construir(self):
        self._crear_header()
        self._crear_alerta_medicamentos()
        self._crear_tarjetas()
        self._crear_grafica()

    #HEADER 

    def _crear_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            header, text="Panel de Control",
            font=ctk.CTkFont(size=24, weight="bold")
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            header,
            text=f"Bienvenido — {datetime.now().strftime('%d/%m/%Y')}",
            font=ctk.CTkFont(size=13), text_color="gray50"
        ).grid(row=1, column=0, sticky="w")

        botones = ctk.CTkFrame(header, fg_color="transparent")
        botones.grid(row=0, column=1, rowspan=2, sticky="e")

        ctk.CTkButton(
            botones, text="↻ Actualizar",
            command=self._refrescar,
            fg_color="#3A7EBF", hover_color="#2C6094",
            width=120
        ).grid(row=0, column=0, padx=(0, 8))

        ctk.CTkButton(
            botones, text="Exportar PDF",
            command=self._exportar_pdf,
            fg_color="#1D9E75", hover_color="#0F6E56",
            width=130
        ).grid(row=0, column=1)

    # ALERTA MEDICAMENTOS 

    def _crear_alerta_medicamentos(self):
        # Limpiar alerta anterior si existe
        for w in self.winfo_children():
            if getattr(w, "_es_alerta", False):
                w.destroy()

        try:
            pendientes = obtener_medicamentos_pendientes_hoy()
        except Exception:
            pendientes = []

        if not pendientes:
            return

        alerta = ctk.CTkFrame(self, fg_color="#7B2D00", corner_radius=8)
        alerta._es_alerta = True
        alerta.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        ctk.CTkLabel(
            alerta,
            text=f"⚠  Tienes {len(pendientes)} medicamento(s) pendiente(s) de aplicar hoy",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#FFDAB5"
        ).pack(padx=15, pady=10, anchor="w")

    # TARJETAS 

    def _crear_tarjetas(self):
        self.frame_tarjetas = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_tarjetas.grid(row=2, column=0, sticky="ew", pady=(0, 15))
        self.frame_tarjetas.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self._cargar_tarjetas()

    def _cargar_tarjetas(self):
        for w in self.frame_tarjetas.winfo_children():
            w.destroy()

        try:
            resumen = calcular_resumen_general()
        except Exception:
            resumen = {
                "total_gastos": 0, "total_ingresos": 0,
                "balance": 0, "rentabilidad_pct": 0, "rentable": True
            }

        tarjetas = [
            ("Gastos", formatear_monto(resumen["total_gastos"]), "#E74C3C"),
            ("Ingresos", formatear_monto(resumen["total_ingresos"]), "#1D9E75"),
            ("Balance", formatear_monto(resumen["balance"]),
             "#1D9E75" if resumen["balance"] >= 0 else "#E74C3C"),
            ("Rentabilidad", f"{resumen['rentabilidad_pct']}%",
             "#1D9E75" if resumen["rentable"] else "#E74C3C"),
        ]

        for i, (titulo, valor, color) in enumerate(tarjetas):
            card = ctk.CTkFrame(self.frame_tarjetas)
            card.grid(row=0, column=i, padx=8, sticky="ew")
            ctk.CTkLabel(card, text=titulo,
                         font=ctk.CTkFont(size=12), text_color="gray50"
                         ).pack(padx=15, pady=(12, 4), anchor="w")
            ctk.CTkLabel(card, text=valor,
                         font=ctk.CTkFont(size=18, weight="bold"), text_color=color
                         ).pack(padx=15, pady=(0, 12), anchor="w")

    # GRÁFICA 

    def _crear_grafica(self):
        self.frame_grafica = ctk.CTkFrame(self)
        self.frame_grafica.grid(row=3, column=0, sticky="nsew", pady=(0, 10))
        self.frame_grafica.grid_columnconfigure(0, weight=1)
        self.frame_grafica.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(
            self.frame_grafica, text="Flujo de Caja — Comparativa Mensual",
            font=ctk.CTkFont(size=15, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")

        ctk.CTkLabel(
            self.frame_grafica, text="Gastos vs Ingresos por mes",
            font=ctk.CTkFont(size=12), text_color="gray50"
        ).grid(row=1, column=0, padx=20, pady=(0, 8), sticky="w")

        self.grafica_container = ctk.CTkFrame(
            self.frame_grafica, fg_color="transparent"
        )
        self.grafica_container.grid(row=2, column=0, sticky="nsew",
                                    padx=15, pady=(0, 15))
        self.grafica_container.grid_columnconfigure(0, weight=1)
        self.grafica_container.grid_rowconfigure(0, weight=1)

        self._dibujar_grafica()

    def _dibujar_grafica(self):
        
        if self._canvas_matplotlib:
            self._canvas_matplotlib.get_tk_widget().destroy()
        if self._fig:
            plt.close(self._fig)

        secciones = ["puercas", "lechones", "engorde", "general", "empleados"]
        meses = ["ENE", "FEB", "MAR", "ABR", "MAY", "JUN",
                 "JUL", "AGO", "SEP", "OCT", "NOV", "DIC"]
        gastos_totales = [0.0] * 12
        ingresos_totales = [0.0] * 12

        for seccion in secciones:
            try:
                for g in obtener_gastos_por_seccion(seccion):
                    mes = int(g["fecha"].split("-")[1]) - 1
                    if 0 <= mes <= 11:
                        gastos_totales[mes] += g["monto"]
            except Exception:
                pass
            try:
                for ing in obtener_ingresos_por_seccion(seccion):
                    mes = int(ing["fecha"].split("-")[1]) - 1
                    if 0 <= mes <= 11:
                        ingresos_totales[mes] += ing["monto"]
            except Exception:
                pass

        self._fig, ax = plt.subplots(figsize=(10, 3.5))
        self._fig.patch.set_facecolor("#2b2b2b")
        ax.set_facecolor("#2b2b2b")

        x = range(12)
        width = 0.35
        ax.bar([i - width / 2 for i in x], ingresos_totales,
               width, label="Ingresos", color="#1D9E75", alpha=0.85)
        ax.bar([i + width / 2 for i in x], gastos_totales,
               width, label="Gastos", color="#E74C3C", alpha=0.85)

        ax.set_xticks(list(x))
        ax.set_xticklabels(meses, color="white", fontsize=9)
        ax.tick_params(colors="white")
        ax.yaxis.set_tick_params(labelcolor="white")
        ax.spines[:].set_color("#444444")
        ax.legend(facecolor="#3b3b3b", labelcolor="white", fontsize=9)
        ax.set_ylabel("RD$", color="white", fontsize=9)

        if all(v == 0 for v in gastos_totales + ingresos_totales):
            ax.text(0.5, 0.5, "Sin datos registrados aún",
                    transform=ax.transAxes, ha="center", va="center",
                    color="gray", fontsize=12)

        plt.tight_layout()

        self._canvas_matplotlib = FigureCanvasTkAgg(
            self._fig, master=self.grafica_container
        )
        self._canvas_matplotlib.draw()
        self._canvas_matplotlib.get_tk_widget().grid(
            row=0, column=0, sticky="nsew"
        )

    #REFRESH 

    def _refrescar(self):
        """Actualiza datos sin destruir el widget padre."""
        self._crear_alerta_medicamentos()
        self._cargar_tarjetas()
        self._dibujar_grafica()

    #EXPORTAR PDF 

    def _exportar_pdf(self):
        from logic.reportes import generar_reporte_pdf
        try:
            ruta = generar_reporte_pdf()

            # Abrir automáticamente el PDF con el visor del sistema
            if sys.platform == "win32":
                os.startfile(ruta)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", ruta])
            else:
                subprocess.Popen(["xdg-open", ruta])

            messagebox.showinfo(
                "PDF Generado",
                f"Reporte guardado y abierto:\n\n{ruta}"
            )
        except PermissionError:
            messagebox.showerror(
                "Error de permisos",
                "No se pudo guardar el PDF.\n"
                "Cierra el archivo si ya está abierto e intenta de nuevo."
            )
        except Exception as e:
            messagebox.showerror("Error al generar PDF", str(e))
           