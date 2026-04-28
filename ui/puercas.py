import customtkinter as ctk
import tkinter.messagebox as messagebox
from database.models import (
    agregar_puerca,
    obtener_puercas,
    eliminar_puerca,
    obtener_resumen_puercas,
    registrar_parto,
    registrar_camada,
    promedio_lechones_por_puerca,
    registrar_inseminacion,
    obtener_partos_proximos
)
from logic.calculos import validar_texto, validar_fecha, formatear_monto
from datetime import datetime


class Puercas(ctk.CTkFrame):
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
            header, text="Gestión de Puercas",
            font=ctk.CTkFont(size=24, weight="bold")
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            header, text="Control de madres reproductoras y productividad",
            font=ctk.CTkFont(size=13), text_color="gray50"
        ).grid(row=1, column=0, sticky="w")

    

    def _crear_tarjetas(self):
        self.frame_tarjetas = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_tarjetas.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        self.frame_tarjetas.grid_columnconfigure((0, 1, 2), weight=1)
        self._cargar_tarjetas()

    def _cargar_tarjetas(self):
        for w in self.frame_tarjetas.winfo_children():
            w.destroy()
        res = obtener_resumen_puercas()
        tarjetas = [
            ("Total Puercas", str(res["total"]), "#1D9E75"),
            ("Camadas", str(res["camadas"]), "#1D9E75"),
            ("Lechones Generados", str(res["lechones"]), "#1D9E75"),
        ]
        for i, (titulo, valor, color) in enumerate(tarjetas):
            card = ctk.CTkFrame(self.frame_tarjetas)
            card.grid(row=0, column=i, padx=8, sticky="ew")
            ctk.CTkLabel(card, text=titulo,
                         font=ctk.CTkFont(size=12), text_color="gray50"
                         ).grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")
            ctk.CTkLabel(card, text=valor,
                         font=ctk.CTkFont(size=18, weight="bold"), text_color=color
                         ).grid(row=1, column=0, padx=15, pady=(0, 15), sticky="w")

    

    def _crear_contenido(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=2, column=0, sticky="nsew")
        frame.grid_columnconfigure(0, weight=2)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_rowconfigure(0, weight=1)
        self._crear_tabla(frame)
        self._crear_formulario(frame)

    

    def _crear_tabla(self, parent):
        frame = ctk.CTkFrame(parent)
        frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            frame, text="Puercas Registradas",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, padx=15, pady=(15, 10), sticky="w")

        self.tabla_frame = ctk.CTkScrollableFrame(frame)
        self.tabla_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        self._cargar_tabla()

    def _cargar_tabla(self):
        for w in self.tabla_frame.winfo_children():
            w.destroy()
        puercas = obtener_puercas()
        if not puercas:
            ctk.CTkLabel(
                self.tabla_frame, text="No hay puercas registradas",
                text_color="gray50"
            ).grid(row=0, column=0, pady=20)
            return
        for i, p in enumerate(puercas):
            bg = "#2b2b2b" if i % 2 == 0 else "#323232"
            row = ctk.CTkFrame(self.tabla_frame, fg_color=bg, corner_radius=4)
            row.grid(row=i, column=0, sticky="ew", pady=1)
            row.grid_columnconfigure(0, weight=1)

            resultado = promedio_lechones_por_puerca(p["id"])
            total_lechones = resultado["total"] or 0
            promedio = round(resultado["promedio"] or 0, 1)

            texto = (f"{p['id_unico']}  •  {p['nombre']}  •  {p['raza']}  •  "
                     f"Ingreso: {p['fecha_ingreso']}  •  "
                     f"Lechones: {total_lechones} (prom. {promedio}/parto)  •  "
                     f"Estado: {p['estado']}")

            ctk.CTkLabel(
                row, text=texto,
                font=ctk.CTkFont(size=12)
            ).grid(row=0, column=0, padx=10, pady=6, sticky="w")

            ctk.CTkButton(
                row, text="Eliminar", width=70, height=24,
                fg_color="#E74C3C", hover_color="#C0392B",
                command=lambda pid=p["id"]: self._eliminar(pid)
            ).grid(row=0, column=1, padx=5)

    # FORMULARIO

    def _crear_formulario(self, parent):
        frame = ctk.CTkScrollableFrame(parent)
        frame.grid(row=0, column=1, sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)

        # REGISTRAR PUERCA 
        ctk.CTkLabel(frame, text="Registrar Puerca",
                     font=ctk.CTkFont(size=16, weight="bold")
                     ).grid(row=0, column=0, padx=15, pady=(15, 10), sticky="w")

        ctk.CTkLabel(frame, text="ID Único (ej: PR-001)",
                     font=ctk.CTkFont(size=12), text_color="gray50"
                     ).grid(row=1, column=0, padx=15, pady=(6, 2), sticky="w")
        self.f_id = ctk.CTkEntry(frame, placeholder_text="PR-001")
        self.f_id.grid(row=2, column=0, padx=15, sticky="ew")

        ctk.CTkLabel(frame, text="Nombre / Alias",
                     font=ctk.CTkFont(size=12), text_color="gray50"
                     ).grid(row=3, column=0, padx=15, pady=(6, 2), sticky="w")
        self.f_nombre = ctk.CTkEntry(frame, placeholder_text="Nombre")
        self.f_nombre.grid(row=4, column=0, padx=15, sticky="ew")

        ctk.CTkLabel(frame, text="Raza",
                     font=ctk.CTkFont(size=12), text_color="gray50"
                     ).grid(row=5, column=0, padx=15, pady=(6, 2), sticky="w")
        self.f_raza = ctk.CTkEntry(frame, placeholder_text="Landrace / Criolla")
        self.f_raza.grid(row=6, column=0, padx=15, sticky="ew")

        ctk.CTkLabel(frame, text="Fecha de ingreso (YYYY-MM-DD)",
                     font=ctk.CTkFont(size=12), text_color="gray50"
                     ).grid(row=7, column=0, padx=15, pady=(6, 2), sticky="w")
        self.f_fecha = ctk.CTkEntry(frame)
        self.f_fecha.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.f_fecha.grid(row=8, column=0, padx=15, sticky="ew")

        ctk.CTkButton(
            frame, text="Guardar Puerca",
            command=self._guardar,
            fg_color="#1D9E75", hover_color="#0F6E56"
        ).grid(row=9, column=0, padx=15, pady=15, sticky="ew")

        # REGISTRAR PARTO 
        ctk.CTkFrame(frame, height=1, fg_color="gray30"
                     ).grid(row=10, column=0, sticky="ew", padx=15, pady=5)
        ctk.CTkLabel(frame, text="Registrar Parto",
                     font=ctk.CTkFont(size=16, weight="bold")
                     ).grid(row=11, column=0, padx=15, pady=(5, 10), sticky="w")

        ctk.CTkLabel(frame, text="ID de la puerca",
                     font=ctk.CTkFont(size=12), text_color="gray50"
                     ).grid(row=12, column=0, padx=15, pady=(6, 2), sticky="w")
        self.p_id = ctk.CTkEntry(frame, placeholder_text="PR-001")
        self.p_id.grid(row=13, column=0, padx=15, sticky="ew")

        ctk.CTkLabel(frame, text="Fecha del parto (YYYY-MM-DD)",
                     font=ctk.CTkFont(size=12), text_color="gray50"
                     ).grid(row=14, column=0, padx=15, pady=(6, 2), sticky="w")
        self.p_fecha = ctk.CTkEntry(frame)
        self.p_fecha.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.p_fecha.grid(row=15, column=0, padx=15, sticky="ew")

        ctk.CTkLabel(frame, text="Cantidad de lechones",
                     font=ctk.CTkFont(size=12), text_color="gray50"
                     ).grid(row=16, column=0, padx=15, pady=(6, 2), sticky="w")
        self.p_cantidad = ctk.CTkEntry(frame, placeholder_text="8")
        self.p_cantidad.grid(row=17, column=0, padx=15, sticky="ew")

        ctk.CTkButton(
            frame, text="Registrar Parto",
            command=self._guardar_parto,
            fg_color="#1D9E75", hover_color="#0F6E56"
        ).grid(row=18, column=0, padx=15, pady=15, sticky="ew")

        # INSEMINACIÓN 
        ctk.CTkFrame(frame, height=1, fg_color="gray30"
                     ).grid(row=19, column=0, sticky="ew", padx=15, pady=5)
        ctk.CTkLabel(frame, text="Registrar Inseminación",
                     font=ctk.CTkFont(size=16, weight="bold")
                     ).grid(row=20, column=0, padx=15, pady=(5, 10), sticky="w")

        ctk.CTkLabel(frame, text="ID de la puerca",
                     font=ctk.CTkFont(size=12), text_color="gray50"
                     ).grid(row=21, column=0, padx=15, pady=(6, 2), sticky="w")
        self.i_id = ctk.CTkEntry(frame, placeholder_text="PR-001")
        self.i_id.grid(row=22, column=0, padx=15, sticky="ew")

        ctk.CTkLabel(frame, text="Fecha (YYYY-MM-DD)",
                     font=ctk.CTkFont(size=12), text_color="gray50"
                     ).grid(row=23, column=0, padx=15, pady=(6, 2), sticky="w")
        self.i_fecha = ctk.CTkEntry(frame)
        self.i_fecha.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.i_fecha.grid(row=24, column=0, padx=15, sticky="ew")

        ctk.CTkLabel(frame, text="Tipo",
                     font=ctk.CTkFont(size=12), text_color="gray50"
                     ).grid(row=25, column=0, padx=15, pady=(6, 2), sticky="w")
        self.i_tipo = ctk.CTkOptionMenu(
            frame, values=["Natural", "Artificial"]
        )
        self.i_tipo.grid(row=26, column=0, padx=15, sticky="ew")

        ctk.CTkButton(
            frame, text="Registrar Inseminación",
            command=self._guardar_inseminacion,
            fg_color="#3A7EBF", hover_color="#2C6094"
        ).grid(row=27, column=0, padx=15, pady=15, sticky="ew")

        # PRÓXIMOS PARTOS 
        ctk.CTkFrame(frame, height=1, fg_color="gray30"
                     ).grid(row=28, column=0, sticky="ew", padx=15, pady=5)
        ctk.CTkLabel(frame, text="Próximos Partos",
                     font=ctk.CTkFont(size=14, weight="bold")
                     ).grid(row=29, column=0, padx=15, pady=(5, 5), sticky="w")
        self.proximos_frame = ctk.CTkFrame(frame, fg_color="transparent")
        self.proximos_frame.grid(row=30, column=0, padx=15, sticky="ew")
        self._cargar_proximos_partos()

    def _cargar_proximos_partos(self):
        for w in self.proximos_frame.winfo_children():
            w.destroy()
        try:
            proximos = obtener_partos_proximos()
        except Exception:
            proximos = []
        if not proximos:
            ctk.CTkLabel(
                self.proximos_frame, text="No hay partos próximos registrados",
                text_color="gray50", font=ctk.CTkFont(size=12)
            ).pack(anchor="w")
            return
        for p in proximos:
            ctk.CTkLabel(
                self.proximos_frame,
                text=f"• {p['nombre']}  →  {p['fecha_probable_parto']}",
                font=ctk.CTkFont(size=12), text_color="#F39C12"
            ).pack(anchor="w", pady=2)

    # ACCIONES 

    def _guardar(self):
        ok1, id_unico = validar_texto(self.f_id.get(), "ID Único")
        ok2, nombre = validar_texto(self.f_nombre.get(), "Nombre")
        ok3, raza = validar_texto(self.f_raza.get(), "Raza")
        ok4, fecha = validar_fecha(self.f_fecha.get())

        if not ok1: messagebox.showerror("Error", id_unico); return
        if not ok2: messagebox.showerror("Error", nombre); return
        if not ok3: messagebox.showerror("Error", raza); return
        if not ok4: messagebox.showerror("Error", fecha); return

        try:
            # firma correcta: (nombre, id_unico, raza, fecha_ingreso)
            agregar_puerca(nombre, id_unico, raza, fecha)
            messagebox.showinfo("Éxito", f"Puerca {nombre} registrada")
            self.f_id.delete(0, "end")
            self.f_nombre.delete(0, "end")
            self.f_raza.delete(0, "end")
            self._refresh()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _guardar_parto(self):
        ok1, id_unico = validar_texto(self.p_id.get(), "ID de puerca")
        ok2, fecha = validar_fecha(self.p_fecha.get())
        try:
            cantidad = int(self.p_cantidad.get())
            if cantidad <= 0:
                raise ValueError
        except Exception:
            messagebox.showerror("Error", "Cantidad debe ser un número positivo")
            return
        if not ok1: messagebox.showerror("Error", id_unico); return
        if not ok2: messagebox.showerror("Error", fecha); return

        try:
            registrar_camada(id_unico, fecha, cantidad)
            messagebox.showinfo("Éxito", f"{cantidad} lechones registrados")
            self.p_id.delete(0, "end")
            self.p_cantidad.delete(0, "end")
            self._refresh()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def _guardar_inseminacion(self):
        ok1, id_unico = validar_texto(self.i_id.get(), "ID de puerca")
        ok2, fecha = validar_fecha(self.i_fecha.get())
        if not ok1: messagebox.showerror("Error", id_unico); return
        if not ok2: messagebox.showerror("Error", fecha); return

        try:
            from database.models import db_connection
            with db_connection() as conn:
                puerca = conn.execute(
                    "SELECT id FROM puercas WHERE id_unico = ?", (id_unico,)
                ).fetchone()
            if not puerca:
                messagebox.showerror("Error", f"No existe puerca con ID {id_unico}")
                return
            registrar_inseminacion(puerca["id"], fecha, self.i_tipo.get())
            messagebox.showinfo("Éxito", "Inseminación registrada. Parto probable en 114 días.")
            self.i_id.delete(0, "end")
            self._cargar_proximos_partos()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _eliminar(self, pid):
        if messagebox.askyesno("Confirmar", "¿Dar de baja esta puerca?"):
            eliminar_puerca(pid)
            self._refresh()

    def _refresh(self):
        self._cargar_tabla()
        self._cargar_tarjetas()