import customtkinter as ctk
from logic.calculos import calcular_resumen_general, formatear_monto
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from database.models import obtener_gastos_por_seccion, obtener_ingresos_por_seccion
from datetime import datetime

class Dashboard(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._crear_header()
        self._crear_tarjetas()
        self._crear_grafica()

    def _crear_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 20))

        ctk.CTkLabel(
            header,
            text="Panel de Control",
            font=ctk.CTkFont(size=24, weight="bold")
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            header,
            text=f"Bienvenido — {datetime.now().strftime('%d/%m/%Y')}",
            font=ctk.CTkFont(size=13),
            text_color="gray50"
        ).grid(row=1, column=0, sticky="w")

    def _crear_tarjetas(self):
        resumen = calcular_resumen_general()

        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        frame.grid_columnconfigure((0,1,2,3), weight=1)

        tarjetas = [
            ("Total Gastos", formatear_monto(resumen["total_gastos"]), "#E74C3C"),
            ("Total Ingresos", formatear_monto(resumen["total_ingresos"]), "#1D9E75"),
            ("Balance General", formatear_monto(resumen["balance"]),
             "#1D9E75" if resumen["balance"] >= 0 else "#E74C3C"),
            ("Rentabilidad", f"{resumen['rentabilidad_pct']}%",
             "#1D9E75" if resumen["rentable"] else "#E74C3C"),
        ]

        for i, (titulo, valor, color) in enumerate(tarjetas):
            card = ctk.CTkFrame(frame)
            card.grid(row=0, column=i, padx=8, sticky="ew")

            ctk.CTkLabel(
                card,
                text=titulo,
                font=ctk.CTkFont(size=12),
                text_color="gray50"
            ).grid(row=0, column=0, padx=15, pady=(15,5), sticky="w")

            ctk.CTkLabel(
                card,
                text=valor,
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color=color
            ).grid(row=1, column=0, padx=15, pady=(0,15), sticky="w")

    def _crear_grafica(self):
        frame = ctk.CTkFrame(self)
        frame.grid(row=2, column=0, sticky="nsew", pady=(0, 10))
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(
            frame,
            text="Análisis de Flujo de Caja",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=(15,5), sticky="w")

        ctk.CTkLabel(
            frame,
            text="Comparativa mensual de Gastos vs Ingresos",
            font=ctk.CTkFont(size=12),
            text_color="gray50"
        ).grid(row=1, column=0, padx=20, pady=(0,10), sticky="w")

        secciones = ["puercas", "lechones", "engorde"]
        meses = ["ENE","FEB","MAR","ABR","MAY","JUN",
                 "JUL","AGO","SEP","OCT","NOV","DIC"]

        gastos_totales = [0] * 12
        ingresos_totales = [0] * 12

        for seccion in secciones:
            for g in obtener_gastos_por_seccion(seccion):
                try:
                    mes = int(g["fecha"].split("-")[1]) - 1
                    gastos_totales[mes] += g["monto"]
                except:
                    pass
            for i in obtener_ingresos_por_seccion(seccion):
                try:
                    mes = int(i["fecha"].split("-")[1]) - 1
                    ingresos_totales[mes] += i["monto"]
                except:
                    pass

        fig, ax = plt.subplots(figsize=(10, 4))
        fig.patch.set_facecolor("#2b2b2b")
        ax.set_facecolor("#2b2b2b")

        x = range(len(meses))
        width = 0.35

        ax.bar([i - width/2 for i in x], ingresos_totales,
               width, label="Ingresos", color="#1D9E75", alpha=0.85)
        ax.bar([i + width/2 for i in x], gastos_totales,
               width, label="Gastos", color="#E74C3C", alpha=0.85)

        ax.set_xticks(list(x))
        ax.set_xticklabels(meses, color="white", fontsize=10)
        ax.tick_params(colors="white")
        ax.yaxis.set_tick_params(labelcolor="white")
        ax.spines[:].set_color("#444444")
        ax.legend(facecolor="#3b3b3b", labelcolor="white")
        ax.set_ylabel("RD$", color="white")

        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().grid(row=2, column=0, padx=15, pady=(0,15), sticky="nsew")