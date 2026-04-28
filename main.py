import customtkinter as ctk
from database.database import inicializar_db

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")


class GranjaPorcina(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Gestión Porcina")
        self.geometry("1280x750")
        self.minsize(1100, 650)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._btn_activo = None
        self._crear_sidebar()
        self._crear_contenido()
        self.mostrar_dashboard()

    def _crear_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=215, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(20, weight=1)
        self.sidebar.grid_propagate(False)

        # Logo
        logo = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo.grid(row=0, column=0, padx=15, pady=(25, 15), sticky="ew")
        ctk.CTkLabel(logo, text="Gestión\nPorcina",
                     font=ctk.CTkFont(size=20, weight="bold")
                     ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(logo, text="v2.0.0",
                     font=ctk.CTkFont(size=10), text_color="gray50"
                     ).grid(row=1, column=0, sticky="w")

        ctk.CTkFrame(self.sidebar, height=1, fg_color="gray30"
                     ).grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 8))

        # Menú: (texto, comando o None para separador)
        menu = [
            ("Dashboard",        self.mostrar_dashboard),
            ("— Producción —",   None),
            ("Puercas",          self.mostrar_puercas),
            ("Lechones",         self.mostrar_lechones),
            ("Engorde",          self.mostrar_engorde),
            ("— Operaciones —",  None),
            ("Medicamentos",     self.mostrar_medicamentos),
            ("Ventas",           self.mostrar_ventas),
            ("— Finanzas —",     None),
            ("Gastos",           self.mostrar_gastos),
            ("— Personal —",     None),
            ("Empleados",        self.mostrar_empleados),
        ]

        self.botones_nav = []
        fila = 2
        for texto, comando in menu:
            if comando is None:
                ctk.CTkLabel(
                    self.sidebar, text=texto,
                    font=ctk.CTkFont(size=10), text_color="gray50"
                ).grid(row=fila, column=0, padx=20, pady=(10, 2), sticky="w")
            else:
                btn = ctk.CTkButton(
                    self.sidebar, text=f"  {texto}",
                    anchor="w",
                    fg_color="transparent",
                    text_color=("gray10", "gray90"),
                    hover_color=("gray75", "gray28"),
                    height=34, corner_radius=8
                )
                btn.configure(command=lambda c=comando, b=btn: self._navegar(c, b))
                btn.grid(row=fila, column=0, padx=10, pady=2, sticky="ew")
                self.botones_nav.append(btn)
            fila += 1

        ctk.CTkLabel(
            self.sidebar, text="Randy © 2026",
            font=ctk.CTkFont(size=10), text_color="gray50"
        ).grid(row=21, column=0, padx=20, pady=20, sticky="sw")

    def _navegar(self, comando, boton):
        if self._btn_activo:
            self._btn_activo.configure(
                fg_color="transparent",
                text_color=("gray10", "gray90")
            )
        if boton:
            boton.configure(fg_color=("gray75", "gray28"))
            self._btn_activo = boton
        comando()

    def _crear_contenido(self):
        self.contenido = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.contenido.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.contenido.grid_columnconfigure(0, weight=1)
        self.contenido.grid_rowconfigure(0, weight=1)

    def _limpiar_contenido(self):
        for w in self.contenido.winfo_children():
            w.destroy()

    # ─── NAVEGACIÓN ───────────────────────────────────────

    def mostrar_dashboard(self):
        self._limpiar_contenido()
        from ui.dashboard import Dashboard
        Dashboard(self.contenido).grid(row=0, column=0, sticky="nsew")

    def mostrar_puercas(self):
        self._limpiar_contenido()
        from ui.puercas import Puercas
        Puercas(self.contenido).grid(row=0, column=0, sticky="nsew")

    def mostrar_lechones(self):
        self._limpiar_contenido()
        from ui.lechones import Lechones
        Lechones(self.contenido).grid(row=0, column=0, sticky="nsew")

    def mostrar_engorde(self):
        self._limpiar_contenido()
        from ui.engorde import Engorde
        Engorde(self.contenido).grid(row=0, column=0, sticky="nsew")

    def mostrar_medicamentos(self):
        self._limpiar_contenido()
        from ui.medicamentos import Medicamentos
        Medicamentos(self.contenido).grid(row=0, column=0, sticky="nsew")

    def mostrar_ventas(self):
        self._limpiar_contenido()
        from ui.ventas import Ventas
        Ventas(self.contenido).grid(row=0, column=0, sticky="nsew")

    def mostrar_gastos(self):
        self._limpiar_contenido()
        from ui.gastos import Gastos
        Gastos(self.contenido).grid(row=0, column=0, sticky="nsew")

    def mostrar_empleados(self):
        self._limpiar_contenido()
        from ui.empleados import Empleados
        Empleados(self.contenido).grid(row=0, column=0, sticky="nsew")


if __name__ == "__main__":
    inicializar_db()
    app = GranjaPorcina()
    app.mainloop()