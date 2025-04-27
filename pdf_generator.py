from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import os

class PDFGenerator:
    def generate_invoice(self, ordre, ordrelinjer, kunde, faktura_nummer):
        pdf_filename = f"faktura_{ordre[0]}.pdf"
        doc = SimpleDocTemplate(pdf_filename, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()

        # 🔽 Add a static PNG image at the top (e.g., logo)
        logo_path = r"static/logo.png" # Path to your logo
        img = Image(logo_path, width=100, height=50)  # Adjust size as needed
        img.hAlign = 'LEFT'
        elements.append(img)
        elements.append(Spacer(1, 12))

        # **Customer Information**
        customer_info = f"""
        <b>Fakturanummer:</b> {faktura_nummer}<br/>
        <b>Kunde:</b> {kunde[1]} {kunde[2]}<br/>
        <b>Adresse:</b> {kunde[3]}, {kunde[4]}<br/>
        """
        elements.append(Paragraph(customer_info, styles["Normal"]))
        elements.append(Spacer(1, 12))

        # **Order Table**
        table_data = [["Antall", "Beskrivelse", "Enhetspris", "Totalt"]]
        total_amount = 0

        for linje in ordrelinjer:
            quantity = int(float(linje[3]))
            unit_price = float(linje[2])
            line_total = quantity * unit_price

            table_data.append([
                f"{quantity:,}",
                f"{linje[4]}",
                f"{unit_price:,.2f} NOK",
                f"{line_total:,.2f} NOK"
            ])

            total_amount += line_total

        table = Table(table_data, colWidths=[60, 200, 100, 100])
        table.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("ALIGN", (1, 1), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold")
        ]))
        elements.append(table)

        # **Total Summary**
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(f"<b>Total (eks. MVA):</b> {total_amount:,.2f} NOK", styles["Normal"]))

        # Calculate 25% MVA
        mva_amount = total_amount * 0.25
        elements.append(Paragraph(f"<b>25% MVA:</b> {mva_amount:,.2f} NOK", styles["Normal"]))

        # Total including MVA
        total_with_mva = total_amount + mva_amount
        elements.append(Paragraph(f"<b>Total (inkl. MVA):</b> {total_with_mva:,.2f} NOK", styles["Normal"]))


        # Build PDF
        doc.build(elements, onFirstPage=add_footer, onLaterPages=add_footer)  #Legger til Footer på regninger
        os.startfile(pdf_filename)

from reportlab.lib.units import mm

def add_footer(canvas, doc):                                                  # Script for å legge til statisk footer
    footer_text = "Gruppe 1 AS | +47 911 | Gymnasvegen 27 | Org.nr: 987237910MVA"
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.grey)
    canvas.drawCentredString(A4[0] / 2.0, 15 * mm, footer_text)  # 15 mm from bottom
    canvas.restoreState()