# utils/pdf_generator.py
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime
from config import FIRMA_INFO
import os

class PDFGenerator:
    def generate_invoice(self, ordre, ordrelinjer, kunde, faktura_nummer):
        """Genererer en profesjonell PDF-faktura."""
        pdf_filename = f"faktura_{faktura_nummer}.pdf"
        doc = SimpleDocTemplate(pdf_filename, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()

        # Legg til logo hvis den finnes
        logo_path = r"static/logo.png"
        if os.path.exists(logo_path):
            img = Image(logo_path, width=100, height=50)
            img.hAlign = 'LEFT'
            elements.append(img)
        else:
            print("Ingen logo funnet. Hopper over logo.")

        elements.append(Spacer(1, 12))

        # Firma-informasjon
        firma_info = f"""
        <b>{FIRMA_INFO.get('NAVN', 'Firmanavn')}</b><br/>
        {FIRMA_INFO.get('ADRESSE', '')}<br/>
        {FIRMA_INFO.get('POSTNUMMER', '')} {FIRMA_INFO.get('STED', '')}<br/>
        <b>Org.nr:</b> {FIRMA_INFO.get('ORGNR', '')}
        """
        elements.append(Paragraph(firma_info, styles["Normal"]))
        elements.append(Spacer(1, 20))

        # Fakturainfo
        faktura_info = f"""
        <b>Fakturanummer:</b> {faktura_nummer}<br/>
        <b>Fakturadato:</b> {datetime.now().strftime('%Y-%m-%d')}<br/>
        """
        elements.append(Paragraph(faktura_info, styles["Normal"]))
        elements.append(Spacer(1, 12))

        # Kundeinfo
        kunde_info = f"""
        <b>Til:</b><br/>
        {kunde.get('Fornavn', '')} {kunde.get('Etternavn', '')}<br/>
        {kunde.get('Adresse', '')}<br/>
        {kunde.get('PostNr', '')}
        """
        elements.append(Paragraph(kunde_info, styles["Normal"]))
        elements.append(Spacer(1, 12))

        # Ordreinfo
        ordre_info = f"""
        <b>Ordredato:</b> {ordre.get('OrdreDato', 'Ukjent')}<br/>
        <b>Sendt dato:</b> {ordre.get('SendtDato', 'Ikke sendt')}<br/>
        <b>Betalt dato:</b> {ordre.get('BetaltDato', 'Ikke betalt')}
        """
        elements.append(Paragraph(ordre_info, styles["Normal"]))
        elements.append(Spacer(1, 20))

        # Varelinjer
        table_data = [["Antall", "Beskrivelse", "Enhetspris", "Total"]]
        total_amount = 0

        for linje in ordrelinjer:
            quantity = int(float(linje.get('Antall', 0)))
            unit_price = float(linje.get('PrisPrEnhet', 0))
            line_total = quantity * unit_price

            table_data.append([
                f"{quantity}",
                f"{linje.get('Betegnelse', '')}",
                f"{unit_price:,.2f} NOK",
                f"{line_total:,.2f} NOK"
            ])
            total_amount += line_total

        table = Table(table_data, colWidths=[60, 260, 90, 90])
        table.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("ALIGN", (1, 1), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold")
        ]))
        elements.append(table)
        elements.append(Spacer(1, 20))

        # Totalsummer
        elements.append(Paragraph(f"<b>Sum eks. MVA:</b> {total_amount:,.2f} NOK", styles["Normal"]))
        mva_amount = total_amount * 0.25
        elements.append(Paragraph(f"<b>MVA (25%):</b> {mva_amount:,.2f} NOK", styles["Normal"]))
        total_with_mva = total_amount + mva_amount
        elements.append(Paragraph(f"<b>Total inkl. MVA:</b> {total_with_mva:,.2f} NOK", styles["Normal"]))

        # Lag PDF
        doc.build(elements)

        try:
            os.startfile(pdf_filename)  # Windows
        except Exception as e:
            print(f"Kunne ikke åpne PDF automatisk: {e}")
