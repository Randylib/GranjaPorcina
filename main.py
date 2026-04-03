import customtkinter as ctk
from database.database import inicializar_db

# ─── CONFIGURACIÓN GLOBAL ──────────────────────────────

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

# ─── VENTANA PRINCIPAL ─────────────────────────────────

class GranjaPorcina(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Gestión Porcina")
        self.geometry("1200x700")
        self.minsize(1000, 600)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._crear_sidebar()
        self._crear_contenido()
        self.mostrar_dashboard()

    def _crear_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(6, weight=1)

        self.logo_label = ctk.CTkLabel(
            self.sidebar,
            text="Gestión\nPorcina",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=30)

        botones = [
            ("Dashboard",         self.mostrar_dashboard),
            ("Puercas Paridoras", self.mostrar_puercas),
            ("Cerdos de Engorde", self.mostrar_engorde),
            ("Lechones",          self.mostrar_lechones),
        ]

        self.botones_sidebar = []
        for i, (texto, comando) in enumerate(botones):
            btn = ctk.CTkButton(
                self.sidebar,
                text=texto,
                command=comando,
                anchor="w",
                fg_color="transparent",
                text_co