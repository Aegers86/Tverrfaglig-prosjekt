from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import os

class PDFGenerator:
    def generate_invoice(self, ordre, ordrelinjer, kunde):
        pdf_filename = f"faktura_{ordre[0]}.pdf"
        doc = SimpleDocTemplate(pdf_filename, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()

        # **Customer Information**
        customer_info = f"""
        <b>Kunde:</b> {kunde[1]} {kunde[2]}<br/>
        <b>Adresse:</b> {kunde[3]}, {kunde[4]}<br/>
        <b>Epost:</b> {kunde[5]}
        """
        elements.append(Paragraph(customer_info, styles["Normal"]))
        elements.append(Spacer(1, 12))

        # **Order Table**
        table_data = [["Antall", "Beskrivelse", "Enhetspris", "Totalt"]]
        total_amount = 0

        for linje in ordrelinjer:
            quantity = int(float(linje[3]))  # Ensuring whole numbers for quantity
            unit_price = float(linje[2])  # Convert to float to avoid errors
            line_total = quantity * unit_price

            table_data.append([
                f"{quantity:,}",  # Formats with thousands separator
                f"Vare {linje[1]}",
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
        elements.append(Paragraph(f"<b>Total:</b> {total_amount:,.2f} NOK", styles["Normal"]))

        doc.build(elements)
        os.startfile(pdf_filename)

