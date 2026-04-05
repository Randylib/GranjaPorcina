import customtkinter as ctk
from database.database import inicializar_db

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

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
            ("Dashboard", self.mostrar_dashboard),
            ("Puercas Paridoras", self.mostrar_puercas),
            ("Cerdos de Engorde", self.mostrar_engorde),
            ("Lechones", self.mostrar_lechones),
        ]

        self.botones_sidebar = []
        for i, (texto, comando) in enumerate(botones):
            btn = ctk.CTkButton(
                self.sidebar,
                text=texto,
                command=comando,
                anchor="w",
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray70", "gray30")
            )
            btn.grid(row=i+1, column=0, padx=10, pady=5, sticky="ew")
            self.botones_sidebar.append(btn)

        self.version_label = ctk.CTkLabel(
            self.sidebar,
            text="v1.0.0",
            font=ctk.CTkFont(size=11),
            text_color="gray50"
        )
        self.version_label.grid(row=7, column=0, padx=20, pady=20)

    def _crear_contenido(self):
        self.contenido = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.contenido.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.contenido.grid_columnconfigure(0, weight=1)
        self.contenido.grid_rowconfigure(0, weight=1)

    def _limpiar_contenido(self):
        for widget in self.contenido.winfo_children():
            widget.destroy()

    def mostrar_dashboard(self):
        self._limpiar_contenido()
        from ui.dashboard import Dashboard
        Dashboard(self.contenido).grid(row=0, column=0, sticky="nsew")

    def mostrar_puercas(self):
        self._limpiar_contenido()
        from ui.puercas import Puercas
        Puercas(self.contenido).grid(row=0, column=0, sticky="nsew")

    def mostrar_engorde(self):
        self._limpiar_contenido()
        from ui.engorde import Engorde
        Engorde(self.contenido).grid(row=0, column=0, sticky="nsew")

    def mostrar_lechones(self):
        self._limpiar_contenido()
        from ui.lechones import Lechones
        Lechones(self.contenido).grid(row=0, column=0, sticky="nsew")

if __name__ == "__main__":
    inicializar_db()
    app = GranjaPorcina()
    app.mainloop()