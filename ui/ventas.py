import customtkinter as ctk
import tkinter.messagebox as messagebox
from database.models import (
    obtener_ventas,
    obtener_resumen_ventas,
    registrar_venta_lechon,
    vender_cerdo_engorde,
    obtener_lechones_con_puerca,
    obtener_cerdos_engorde
)
from logic.calculos import formatear_monto, validar_monto, validar_fecha, validar_texto
from datetime import datetime


class Ventas(ctk.CTkFrame):
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
            header, text="Módulo de Ventas",
            font=ctk.CTkFont(size=24, weight="bold")
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            header, text="Centraliza todas las ventas — lechones y cerdos de engorde",
            font=ctk.CTkFont(size=13), text_color="gray50"
        ).grid(row=1, column=0, sticky="w")


    def _crear_tarjetas(self):
        self.frame_tarjetas = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_tarjetas.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        self.frame_tarjetas.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self._cargar_tarjetas()

    def _cargar_tarjetas(self):
        for w in self.frame_tarjetas.winfo_children():
            w.destroy()
        res = obtener_resumen_ventas()
        total_transacciones = len(obtener_ventas())
        tarjetas = [
            ("Total Ventas", formatear_monto(res["total"]), "#1D9E75"),
            ("Lechones Vendidos", str(res["lechones_vendidos"]), "#1D9E75"),
            ("Engorde Vendido", str(res["engorde_vendidos"]), "#1D9E75"),
            ("Transacciones", str(total_transacciones), "#1D9E75"),
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
        self._crear_panel_izquierdo(frame)
        self._crear_panel_derecho(frame)

    

    def _crear_panel_izquierdo(self, parent):
        frame = ctk.CTkFrame(parent)
        frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_rowconfigure(3, weight=1)

        #  Disponibles para vender 
        ctk.CTkLabel(
            frame, text="Disponibles para vender",
            font=ctk.CTkFont(size=15, weight="bold")
        ).grid(row=0, column=0, padx=15, pady=(15, 8), sticky="w")

        # Selector tipo
        selector_frame = ctk.CTkFrame(frame, fg_color="transparent")
        selector_frame.grid(row=0, column=0, padx=15, pady=(15, 8), sticky="e")
        self.tipo_disponibles = ctk.CTkSegmentedButton(
            selector_frame,
            values=["Lechones", "Engorde"],
            command=self._cambiar_disponibles,
            width=200
        )
        self.tipo_disponibles.set("Lechones")
        self.tipo_disponibles.pack()

        self.disponibles_frame = ctk.CTkScrollableFrame(
            frame, fg_color="transparent", height=200
        )
        self.disponibles_frame.grid(row=1, column=0, sticky="nsew",
                                     padx=15, pady=(0, 10))
        self.disponibles_frame.grid_columnconfigure(0, weight=1)

        # Separador
        ctk.CTkFrame(frame, height=1, fg_color="gray30"
                     ).grid(row=2, column=0, sticky="ew", padx=15, pady=5)

        # Historial 
        hist_header = ctk.CTkFrame(frame, fg_color="transparent")
        hist_header.grid(row=2, column=0, sticky="ew", padx=15, pady=(10, 5))
        hist_header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            hist_header, text="Historial de Ventas",
            font=ctk.CTkFont(size=15, weight="bold")
        ).grid(row=0, column=0, sticky="w")

        self.filtro_tipo = ctk.CTkOptionMenu(
            hist_header,
            values=["Todas", "lechon", "engorde"],
            command=lambda _: self._cargar_historial(),
            width=120
        )
        self.filtro_tipo.grid(row=0, column=1, sticky="e")

        # Encabezados tabla
        cols_frame = ctk.CTkFrame(frame, fg_color="transparent")
        cols_frame.grid(row=2, column=0, sticky="ew", padx=15, pady=(45, 0))
        for i, col in enumerate(["Tipo", "ID", "Cant./Peso", "Total", "Fecha", "Comprador"]):
            ctk.CTkLabel(
                cols_frame, text=col,
                font=ctk.CTkFont(size=11, weight="bold"), text_color="gray50"
            ).grid(row=0, column=i, padx=6, sticky="w")

        self.historial_frame = ctk.CTkScrollableFrame(
            frame, fg_color="transparent"
        )
        self.historial_frame.grid(row=3, column=0, sticky="nsew",
                                   padx=15, pady=(5, 15))

        self._cargar_disponibles()
        self._cargar_historial()

    def _cambiar_disponibles(self, _):
        self._cargar_disponibles()

    def _cargar_disponibles(self):
        for w in self.disponibles_frame.winfo_children():
            w.destroy()

        tipo = self.tipo_disponibles.get()

        if tipo == "Lechones":
            items = [l for l in obtener_lechones_con_puerca()
                     if l["estado"] == "disponible"]
            if not items:
                ctk.CTkLabel(
                    self.disponibles_frame,
                    text="No hay lechones disponibles",
                    text_color="gray50", font=ctk.CTkFont(size=12)
                ).grid(row=0, column=0, pady=15, padx=10)
                return

            for i, l in enumerate(items):
                bg = "#2b2b2b" if i % 2 == 0 else "#323232"
                row = ctk.CTkFrame(self.disponibles_frame,
                                   fg_color=bg, corner_radius=6)
                row.grid(row=i, column=0, sticky="ew", pady=2)
                row.grid_columnconfigure(0, weight=1)

                info = (f"#{l['id']}  •  Madre: {l['puerca_nombre']} "
                        f"({l['puerca_id']})  •  Nació: {l['fecha_nacimiento']}"
                        f"  •  Peso: {l['peso_kg']} kg")

                ctk.CTkLabel(
                    row, text=info,
                    font=ctk.CTkFont(size=12), text_color="gray80"
                ).grid(row=0, column=0, padx=10, pady=8, sticky="w")

                ctk.CTkButton(
                    row, text=" Vender",
                    width=90, height=28,
                    fg_color="#1D9E75", hover_color="#0F6E56",
                    font=ctk.CTkFont(size=12),
                    command=lambda lechon=dict(l): self._ventana_venta_lechon(lechon)
                ).grid(row=0, column=1, padx=8)

        else:  # Engorde
            items = obtener_cerdos_engorde()
            if not items:
                ctk.CTkLabel(
                    self.disponibles_frame,
                    text="No hay cerdos en engorde",
                    text_color="gray50", font=ctk.CTkFont(size=12)
                ).grid(row=0, column=0, pady=15, padx=10)
                return

            for i, c in enumerate(items):
                bg = "#2b2b2b" if i % 2 == 0 else "#323232"
                row = ctk.CTkFrame(self.disponibles_frame,
                                   fg_color=bg, corner_radius=6)
                row.grid(row=i, column=0, sticky="ew", pady=2)
                row.grid_columnconfigure(0, weight=1)

                info = (f"{c['id_cerdo']}  •  Lote: {c['peso_lote_kg']} kg  "
                        f"•  Precio ref: {formatear_monto(c['precio_mercado_kg'])}/kg  "
                        f"•  Valor est: {formatear_monto(c['peso_lote_kg'] * c['precio_mercado_kg'])}")

                ctk.CTkLabel(
                    row, text=info,
                    font=ctk.CTkFont(size=12), text_color="gray80"
                ).grid(row=0, column=0, padx=10, pady=8, sticky="w")

                ctk.CTkButton(
                    row, text="💰 Vender",
                    width=90, height=28,
                    fg_color="#1D9E75", hover_color="#0F6E56",
                    font=ctk.CTkFont(size=12),
                    command=lambda cerdo=dict(c): self._ventana_venta_engorde(cerdo)
                ).grid(row=0, column=1, padx=8)

    def _cargar_historial(self):
        for w in self.historial_frame.winfo_children():
            w.destroy()

        tipo = self.filtro_tipo.get() if hasattr(self, "filtro_tipo") else "Todas"
        ventas = obtener_ventas(None if tipo == "Todas" else tipo)

        if not ventas:
            ctk.CTkLabel(
                self.historial_frame, text="No hay ventas registradas",
                text_color="gray50"
            ).grid(row=0, column=0, pady=15, padx=15)
            return

        for i, v in enumerate(ventas):
            bg = "#2b2b2b" if i % 2 == 0 else "#323232"
            row = ctk.CTkFrame(self.historial_frame, fg_color=bg, corner_radius=4)
            row.grid(row=i, column=0, sticky="ew", pady=1)

            tipo_txt = "Lechón" if v["tipo_animal"] == "lechon" else "Engorde"
            cant_peso = (f"{v['peso_kg']} kg" if v["peso_kg"]
                         else f"{v['cantidad']} ud.")

            fila = [
                tipo_txt,
                str(v["animal_id"]),
                cant_peso,
                formatear_monto(v["total"]),
                v["fecha"],
                v["comprador"] or "—"
            ]
            for j, val in enumerate(fila):
                color = "#1D9E75" if j == 3 else None
                ctk.CTkLabel(
                    row, text=val, font=ctk.CTkFont(size=12),
                    text_color=color if color else (
                        "gray90" if ctk.get_appearance_mode() == "Dark"
                        else "gray10")
                ).grid(row=0, column=j, padx=6, pady=6, sticky="w")

    

    def _ventana_venta_lechon(self, lechon):
        """Ventana emergente para vender un lechón directamente."""
        win = ctk.CTkToplevel(self)
        win.title(f"Vender Lechón #{lechon['id']}")
        win.geometry("400x380")
        win.grab_set()
        win.resizable(False, False)

        ctk.CTkLabel(
            win, text=f"Lechón #{lechon['id']}",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(20, 5))

        ctk.CTkLabel(
            win,
            text=f"Madre: {lechon['puerca_nombre']} ({lechon['puerca_id']})"
                 f"  •  Nació: {lechon['fecha_nacimiento']}",
            font=ctk.CTkFont(size=12), text_color="gray50"
        ).pack(pady=(0, 20))

        ctk.CTkLabel(win, text="Precio de venta (RD$)",
                     font=ctk.CTkFont(size=12), text_color="gray50"
                     ).pack(anchor="w", padx=25)
        precio_entry = ctk.CTkEntry(win, placeholder_text="3500", height=38)
        precio_entry.pack(fill="x", padx=25, pady=(3, 10))
        precio_entry.focus()

        ctk.CTkLabel(win, text="Comprador (opcional)",
                     font=ctk.CTkFont(size=12), text_color="gray50"
                     ).pack(anchor="w", padx=25)
        comprador_entry = ctk.CTkEntry(win, placeholder_text="Nombre del comprador",
                                        height=38)
        comprador_entry.pack(fill="x", padx=25, pady=(3, 10))

        ctk.CTkLabel(win, text="Fecha (YYYY-MM-DD)",
                     font=ctk.CTkFont(size=12), text_color="gray50"
                     ).pack(anchor="w", padx=25)
        fecha_entry = ctk.CTkEntry(win, height=38)
        fecha_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        fecha_entry.pack(fill="x", padx=25, pady=(3, 15))

        def confirmar():
            ok1, precio = validar_monto(precio_entry.get())
            ok2, fecha = validar_fecha(fecha_entry.get())
            if not ok1:
                messagebox.showerror("Error", precio, parent=win); return
            if not ok2:
                messagebox.showerror("Error", fecha, parent=win); return

            if not messagebox.askyesno(
                "Confirmar venta",
                f"¿Vender lechón #{lechon['id']} por {formatear_monto(precio)}?",
                parent=win
            ):
                return

            try:
                registrar_venta_lechon(
                    lechon["id"], precio, fecha,
                    comprador=comprador_entry.get().strip()
                )
                messagebox.showinfo(
                    "Venta registrada",
                    f"Lechón #{lechon['id']} vendido por {formatear_monto(precio)}",
                    parent=win
                )
                win.destroy()
                self._refresh()
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=win)

        ctk.CTkButton(
            win, text="Confirmar Venta",
            command=confirmar,
            fg_color="#1D9E75", hover_color="#0F6E56",
            height=40
        ).pack(fill="x", padx=25, pady=5)

        ctk.CTkButton(
            win, text="Cancelar",
            command=win.destroy,
            fg_color="transparent", border_width=1,
            height=36
        ).pack(fill="x", padx=25, pady=(0, 15))

    def _ventana_venta_engorde(self, cerdo):
        """Ventana emergente para vender un cerdo de engorde directamente."""
        win = ctk.CTkToplevel(self)
        win.title(f"Vender Cerdo {cerdo['id_cerdo']}")
        win.geometry("420x440")
        win.grab_set()
        win.resizable(False, False)

        ctk.CTkLabel(
            win, text=f"Cerdo {cerdo['id_cerdo']}",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(20, 5))

        ctk.CTkLabel(
            win,
            text=f"Peso actual: {cerdo['peso_lote_kg']} kg  "
                 f"•  Precio ref: {formatear_monto(cerdo['precio_mercado_kg'])}/kg",
            font=ctk.CTkFont(size=12), text_color="gray50"
        ).pack(pady=(0, 20))

        ctk.CTkLabel(win, text="Peso final del lote (kg)",
                     font=ctk.CTkFont(size=12), text_color="gray50"
                     ).pack(anchor="w", padx=25)
        peso_entry = ctk.CTkEntry(win, height=38)
        peso_entry.insert(0, str(cerdo["peso_lote_kg"]))
        peso_entry.pack(fill="x", padx=25, pady=(3, 10))

        ctk.CTkLabel(win, text="Precio de mercado (RD$/kg)",
                     font=ctk.CTkFont(size=12), text_color="gray50"
                     ).pack(anchor="w", padx=25)
        precio_kg_entry = ctk.CTkEntry(win, height=38)
        precio_kg_entry.insert(0, str(cerdo["precio_mercado_kg"]))
        precio_kg_entry.pack(fill="x", padx=25, pady=(3, 10))
        precio_kg_entry.focus()

        # Label total calculado
        total_label = ctk.CTkLabel(
            win, text=f"Total: {formatear_monto(cerdo['peso_lote_kg'] * cerdo['precio_mercado_kg'])}",
            font=ctk.CTkFont(size=16, weight="bold"), text_color="#1D9E75"
        )
        total_label.pack(pady=(0, 10))

        def actualizar_total(event=None):
            try:
                p = float(peso_entry.get())
                pk = float(precio_kg_entry.get())
                total_label.configure(text=f"Total: {formatear_monto(p * pk)}")
            except ValueError:
                total_label.configure(text="Total: RD$ 0.00")

        peso_entry.bind("<KeyRelease>", actualizar_total)
        precio_kg_entry.bind("<KeyRelease>", actualizar_total)

        ctk.CTkLabel(win, text="Comprador (opcional)",
                     font=ctk.CTkFont(size=12), text_color="gray50"
                     ).pack(anchor="w", padx=25)
        comprador_entry = ctk.CTkEntry(win, placeholder_text="Nombre del comprador",
                                        height=38)
        comprador_entry.pack(fill="x", padx=25, pady=(3, 10))

        ctk.CTkLabel(win, text="Fecha (YYYY-MM-DD)",
                     font=ctk.CTkFont(size=12), text_color="gray50"
                     ).pack(anchor="w", padx=25)
        fecha_entry = ctk.CTkEntry(win, height=38)
        fecha_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        fecha_entry.pack(fill="x", padx=25, pady=(3, 15))

        def confirmar():
            ok1, peso = validar_monto(peso_entry.get())
            ok2, precio_kg = validar_monto(precio_kg_entry.get())
            ok3, fecha = validar_fecha(fecha_entry.get())
            if not ok1:
                messagebox.showerror("Error", peso, parent=win); return
            if not ok2:
                messagebox.showerror("Error", precio_kg, parent=win); return
            if not ok3:
                messagebox.showerror("Error", fecha, parent=win); return

            total = peso * precio_kg
            if not messagebox.askyesno(
                "Confirmar venta",
                f"¿Vender cerdo {cerdo['id_cerdo']}?\n"
                f"{peso} kg × RD${precio_kg}/kg = {formatear_monto(total)}",
                parent=win
            ):
                return

            try:
                vender_cerdo_engorde(cerdo["id_cerdo"], peso, precio_kg, fecha)
                messagebox.showinfo(
                    "Venta registrada",
                    f"Cerdo {cerdo['id_cerdo']} vendido\nTotal: {formatear_monto(total)}",
                    parent=win
                )
                win.destroy()
                self._refresh()
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=win)

        ctk.CTkButton(
            win, text="Confirmar Venta",
            command=confirmar,
            fg_color="#1D9E75", hover_color="#0F6E56",
            height=40
        ).pack(fill="x", padx=25, pady=5)

        ctk.CTkButton(
            win, text="Cancelar",
            command=win.destroy,
            fg_color="transparent", border_width=1,
            height=36
        ).pack(fill="x", padx=25, pady=(0, 15))

    

    def _crear_panel_derecho(self, parent):
        frame = ctk.CTkScrollableFrame(parent)
        frame.grid(row=0, column=1, sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            frame, text="Venta Manual",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")

        ctk.CTkLabel(
            frame, text="Usa el panel izquierdo para ventas rápidas.\nAquí puedes registrar una venta manual.",
            font=ctk.CTkFont(size=11), text_color="gray50"
        ).grid(row=1, column=0, padx=15, pady=(0, 10), sticky="w")

        ctk.CTkLabel(frame, text="Tipo de animal",
                     font=ctk.CTkFont(size=12), text_color="gray50"
                     ).grid(row=2, column=0, padx=15, pady=(8, 2), sticky="w")
        self.tipo_venta = ctk.CTkSegmentedButton(
            frame, values=["Lechón", "Engorde"],
            command=self._cambiar_tipo_form
        )
        self.tipo_venta.set("Lechón")
        self.tipo_venta.grid(row=3, column=0, padx=15, sticky="ew", pady=(0, 5))

        self.form_container = ctk.CTkFrame(frame, fg_color="transparent")
        self.form_container.grid(row=4, column=0, sticky="ew")
        self.form_container.grid_columnconfigure(0, weight=1)
        self._form_lechon()

    def _cambiar_tipo_form(self, valor):
        for w in self.form_container.winfo_children():
            w.destroy()
        if valor == "Lechón":
            self._form_lechon()
        else:
            self._form_engorde()

    def _form_lechon(self):
        f = self.form_container

        ctk.CTkLabel(f, text="ID del lechón",
                     font=ctk.CTkFont(size=12), text_color="gray50"
                     ).grid(row=0, column=0, padx=15, pady=(8, 2), sticky="w")
        self.v_id = ctk.CTkEntry(f, placeholder_text="Número ID")
        self.v_id.grid(row=1, column=0, padx=15, sticky="ew")

        ctk.CTkLabel(f, text="Precio de venta (RD$)",
                     font=ctk.CTkFont(size=12), text_color="gray50"
                     ).grid(row=2, column=0, padx=15, pady=(8, 2), sticky="w")
        self.v_precio = ctk.CTkEntry(f, placeholder_text="3500")
        self.v_precio.grid(row=3, column=0, padx=15, sticky="ew")

        ctk.CTkLabel(f, text="Comprador (opcional)",
                     font=ctk.CTkFont(size=12), text_color="gray50"
                     ).grid(row=4, column=0, padx=15, pady=(8, 2), sticky="w")
        self.v_comprador = ctk.CTkEntry(f, placeholder_text="Nombre")
        self.v_comprador.grid(row=5, column=0, padx=15, sticky="ew")

        ctk.CTkLabel(f, text="Fecha (YYYY-MM-DD)",
                     font=ctk.CTkFont(size=12), text_color="gray50"
                     ).grid(row=6, column=0, padx=15, pady=(8, 2), sticky="w")
        self.v_fecha = ctk.CTkEntry(f)
        self.v_fecha.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.v_fecha.grid(row=7, column=0, padx=15, sticky="ew")

        ctk.CTkButton(
            f, text="Registrar Venta",
            command=self._vender_lechon_manual,
            fg_color="#1D9E75", hover_color="#0F6E56"
        ).grid(row=8, column=0, padx=15, pady=15, sticky="ew")

    def _form_engorde(self):
        f = self.form_container

        ctk.CTkLabel(f, text="ID del cerdo",
                     font=ctk.CTkFont(size=12), text_color="gray50"
                     ).grid(row=0, column=0, padx=15, pady=(8, 2), sticky="w")
        self.v_id = ctk.CTkEntry(f, placeholder_text="CE-001")
        self.v_id.grid(row=1, column=0, padx=15, sticky="ew")

        ctk.CTkLabel(f, text="Peso final del lote (kg)",
                     font=ctk.CTkFont(size=12), text_color="gray50"
                     ).grid(row=2, column=0, padx=15, pady=(8, 2), sticky="w")
        self.v_peso = ctk.CTkEntry(f, placeholder_text="900")
        self.v_peso.grid(row=3, column=0, padx=15, sticky="ew")
        self.v_peso.bind("<KeyRelease>", self._calcular_total)

        ctk.CTkLabel(f, text="Precio (RD$/kg)",
                     font=ctk.CTkFont(size=12), text_color="gray50"
                     ).grid(row=4, column=0, padx=15, pady=(8, 2), sticky="w")
        self.v_precio_kg = ctk.CTkEntry(f, placeholder_text="120")
        self.v_precio_kg.grid(row=5, column=0, padx=15, sticky="ew")
        self.v_precio_kg.bind("<KeyRelease>", self._calcular_total)

        self.v_total_label = ctk.CTkLabel(
            f, text="RD$ 0.00",
            font=ctk.CTkFont(size=15, weight="bold"), text_color="#1D9E75"
        )
        self.v_total_label.grid(row=6, column=0, padx=15, pady=5, sticky="w")

        ctk.CTkLabel(f, text="Comprador (opcional)",
                     font=ctk.CTkFont(size=12), text_color="gray50"
                     ).grid(row=7, column=0, padx=15, pady=(8, 2), sticky="w")
        self.v_comprador = ctk.CTkEntry(f, placeholder_text="Nombre")
        self.v_comprador.grid(row=8, column=0, padx=15, sticky="ew")

        ctk.CTkLabel(f, text="Fecha (YYYY-MM-DD)",
                     font=ctk.CTkFont(size=12), text_color="gray50"
                     ).grid(row=9, column=0, padx=15, pady=(8, 2), sticky="w")
        self.v_fecha = ctk.CTkEntry(f)
        self.v_fecha.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.v_fecha.grid(row=10, column=0, padx=15, sticky="ew")

        ctk.CTkButton(
            f, text="Registrar Venta",
            command=self._vender_engorde_manual,
            fg_color="#1D9E75", hover_color="#0F6E56"
        ).grid(row=11, column=0, padx=15, pady=15, sticky="ew")

    def _calcular_total(self, event=None):
        try:
            peso = float(self.v_peso.get())
            precio = float(self.v_precio_kg.get())
            self.v_total_label.configure(text=f"RD$ {peso * precio:,.2f}")
        except (ValueError, AttributeError):
            pass

    # GUARDAR MANUAL

    def _vender_lechon_manual(self):
        ok1, fecha = validar_fecha(self.v_fecha.get())
        ok2, precio = validar_monto(self.v_precio.get())
        if not ok1: messagebox.showerror("Error", fecha); return
        if not ok2: messagebox.showerror("Error", precio); return
        try:
            lechon_id = int(self.v_id.get())
        except ValueError:
            messagebox.showerror("Error", "El ID del lechón debe ser un número")
            return

        if not messagebox.askyesno("Confirmar",
                                   f"¿Vender lechón #{lechon_id} por {formatear_monto(precio)}?"):
            return
        try:
            registrar_venta_lechon(
                lechon_id, precio, fecha,
                comprador=self.v_comprador.get().strip()
            )
            messagebox.showinfo("Éxito", f"Lechón #{lechon_id} vendido")
            self.v_id.delete(0, "end")
            self.v_precio.delete(0, "end")
            self.v_comprador.delete(0, "end")
            self._refresh()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _vender_engorde_manual(self):
        ok1, fecha = validar_fecha(self.v_fecha.get())
        ok2, peso = validar_monto(self.v_peso.get())
        ok3, precio_kg = validar_monto(self.v_precio_kg.get())
        ok4, cerdo_id = validar_texto(self.v_id.get(), "ID del cerdo")
        if not ok1: messagebox.showerror("Error", fecha); return
        if not ok2: messagebox.showerror("Error", peso); return
        if not ok3: messagebox.showerror("Error", precio_kg); return
        if not ok4: messagebox.showerror("Error", cerdo_id); return

        total = peso * precio_kg
        if not messagebox.askyesno("Confirmar",
                                   f"¿Vender cerdo {cerdo_id}?\n"
                                   f"{peso} kg × RD${precio_kg}/kg = {formatear_monto(total)}"):
            return
        try:
            vender_cerdo_engorde(cerdo_id, peso, precio_kg, fecha)
            messagebox.showinfo("Éxito", f"Venta: {formatear_monto(total)}")
            self.v_id.delete(0, "end")
            self.v_peso.delete(0, "end")
            self.v_precio_kg.delete(0, "end")
            self.v_comprador.delete(0, "end")
            self.v_total_label.configure(text="RD$ 0.00")
            self._refresh()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    

    def _refresh(self):
        self._cargar_tarjetas()
        self._cargar_historial()
        self._cargar_disponibles()