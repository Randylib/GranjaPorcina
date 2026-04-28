from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from database.models import (
    obtener_puercas,
    obtener_cerdos_engorde,
    obtener_todos_medicamentos,
    obtener_todas_actividades,
    obtener_ventas,
    obtener_empleados,
    obtener_gastos_por_seccion,
    obtener_ingresos_por_seccion
)
from logic.calculos import (
    calcular_resumen_general,
    calcular_rentabilidad_puercas_lechones,
    calcular_valor_inventario,
    formatear_monto,
    generar_sugerencias,
    resumen_gastos_por_periodo
)
from datetime import datetime
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk

def generar_reporte_pdf(ruta="reporte.pdf"):
    doc = SimpleDocTemplate(ruta, pagesize=letter)
    styles = getSampleStyleSheet()
    contenido = []

    # Título
    contenido.append(Paragraph("REPORTE GRANJA PORCINA", styles["Title"]))
    contenido.append(Paragraph(datetime.now().strftime("%d/%m/%Y %H:%M"), styles["Normal"]))
    contenido.append(Spacer(1, 10))

    # Resumen general
    resumen = calcular_resumen_general()
    datos = [
        ["Concepto", "Monto"],
        ["Gastos", formatear_monto(resumen["total_gastos"])],
        ["Ingresos", formatear_monto(resumen["total_ingresos"])],
        ["Balance", formatear_monto(resumen["balance"])],
        ["Rentabilidad", f"{resumen.get('rentabilidad_pct',0)}%"]
    ]
    tabla = Table(datos, colWidths=[3*inch, 3*inch])
    tabla.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), colors.green),
                               ("TEXTCOLOR", (0,0), (-1,0), colors.white),
                               ("GRID", (0,0), (-1,-1), 0.5, colors.grey)]))
    contenido.append(tabla)
    contenido.append(Spacer(1, 15))

    # Puercas
    puercas = obtener_puercas()
    contenido.append(Paragraph("Puercas", styles["Heading2"]))
    for p in puercas:
        contenido.append(Paragraph(f"{p['nombre']} - {p['raza']} - {p['estado']}", styles["Normal"]))

    # Engorde
    cerdos = obtener_cerdos_engorde()
    valor = calcular_valor_inventario(cerdos)
    contenido.append(Spacer(1, 10))
    contenido.append(Paragraph("Engorde", styles["Heading2"]))
    contenido.append(Paragraph(f"Valor inventario: {formatear_monto(valor)}", styles["Normal"]))

    # Medicamentos
    meds = obtener_todos_medicamentos()
    contenido.append(Spacer(1, 10))
    contenido.append(Paragraph("Medicamentos", styles["Heading2"]))
    for m in meds[:10]:
        estado = "Aplicado" if m["aplicado"] else "Pendiente"
        contenido.append(Paragraph(f"{m['nombre']} - {estado}", styles["Normal"]))

    # Empleados
    empleados = obtener_empleados()
    contenido.append(Spacer(1, 10))
    contenido.append(Paragraph("Empleados", styles["Heading2"]))
    for e in empleados:
        contenido.append(Paragraph(f"{e['nombre']} - {e['tipo_pago']} - ${e['salario_base']}", styles["Normal"]))

    # Sugerencias
    sugerencias = generar_sugerencias(resumen)
    contenido.append(Spacer(1, 15))
    contenido.append(Paragraph("Sugerencias", styles["Heading2"]))
    for s in sugerencias:
        contenido.append(Paragraph(f"- {s}", styles["Normal"]))

    doc.build(contenido)
    return ruta

# VISTA PREVIA DEL REPORTE (usando Tkinter)
class ReportePreview(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Vista previa del reporte")
        self.geometry("800x600")
        self.grab_set()  # modal

        # Marco principal
        frame = ctk.CTkFrame(self)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Área de texto con scroll
        text_area = tk.Text(frame, wrap="word", bg="#2b2b2b", fg="white", font=("Courier", 10))
        scroll = ttk.Scrollbar(frame, orient="vertical", command=text_area.yview)
        text_area.configure(yscrollcommand=scroll.set)
        text_area.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        # Generar contenido
        contenido = self._generar_contenido_texto()
        text_area.insert("1.0", contenido)
        text_area.configure(state="disabled")

        # Botón exportar PDF
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkButton(btn_frame, text="Exportar a PDF", command=self._exportar).pack(side="right", padx=5)
        ctk.CTkButton(btn_frame, text="Cerrar", command=self.destroy).pack(side="right", padx=5)

    def _generar_contenido_texto(self):
        resumen = calcular_resumen_general()
        rentabilidad = calcular_rentabilidad_puercas_lechones()
        cerdos = obtener_cerdos_engorde()
        valor_inventario = calcular_valor_inventario(cerdos)
        empleados = obtener_empleados()
        gastos_mes = resumen_gastos_por_periodo("mes")
        lineas = []
        lineas.append("="*60)
        lineas.append("REPORTE DE GESTIÓN PORCINA")
        lineas.append(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        lineas.append("="*60)
        lineas.append("\n RESUMEN FINANCIERO")
        lineas.append(f"Total Gastos: {formatear_monto(resumen['total_gastos'])}")
        lineas.append(f"Total Ingresos: {formatear_monto(resumen['total_ingresos'])}")
        lineas.append(f"Balance: {formatear_monto(resumen['balance'])}")
        lineas.append(f"Rentabilidad: {resumen.get('rentabilidad_pct',0)}%")
        lineas.append("\n PUERCAS Y LECHONES")
        lineas.append(f"Gastos: {formatear_monto(rentabilidad['total_gastos'])}")
        lineas.append(f"Ingresos: {formatear_monto(rentabilidad['total_ingresos'])}")
        lineas.append(f"Balance: {formatear_monto(rentabilidad['balance'])}")
        lineas.append("\n ENGORDE")
        lineas.append(f"Valor inventario: {formatear_monto(valor_inventario)}")
        lineas.append(f"Cantidad de cerdos: {len(cerdos)}")
        lineas.append("\n EMPLEADOS")
        for e in empleados:
            lineas.append(f"  - {e['nombre']} ({e['tipo_pago']}) - Base: {formatear_monto(e['salario_base'])}")
        lineas.append("\n GASTOS DEL MES")
        lineas.append(f"Total: {formatear_monto(gastos_mes['total'])}")
        for cat, monto in gastos_mes['por_categoria'].items():
            lineas.append(f"  {cat}: {formatear_monto(monto)}")
        lineas.append("\n SUGERENCIAS")
        sugerencias = generar_sugerencias(resumen)
        for s in sugerencias:
            lineas.append(f"  • {s}")
        return "\n".join(lineas)

    def _exportar(self):
        from tkinter import filedialog
        ruta = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if ruta:
            generar_reporte_pdf(ruta)
            from tkinter import messagebox
            messagebox.showinfo("Éxito", f"Reporte guardado en:\n{ruta}")
            self.destroy()