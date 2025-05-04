import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from config import FIRMA_INFO

class PDFGenerator:
    def generate_invoice(self, ordre, ordrelinjer, kunde, faktura_nummer):
        """Genererer en PDF-faktura og lagrer den i fakturaer-mappen."""

        # Opprett 'fakturaer/' mappe hvis den ikke finnes
        faktura_mappe = "fakturaer"
        os.makedirs(faktura_mappe, exist_ok=True)

        # Sett filnavn i riktig mappe
        pdf_filename = os.path.join(faktura_mappe, f"faktura_{faktura_nummer}.pdf")

        # Start på PDF-dokument
        doc = SimpleDocTemplate(pdf_filename, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()

        # Firma-logo
        logo_path = r"static/logo.png"
        if os.path.exists(logo_path):
            img = Image(logo_path, width=100, height=50)
            img.hAlign = 'LEFT'
            elements.append(img)
            elements.append(Spacer(1, 12))

        # Firma-info
        firma_info = f"""
        <b>{FIRMA_INFO['navn']}</b><br/>
        {FIRMA_INFO['adresse']}<br/>
        {FIRMA_INFO['postnummer']} {FIRMA_INFO['sted']}<br/>
        Org.nr: {FIRMA_INFO['orgnr']}<br/>
        """
        if 'telefon' in FIRMA_INFO:
            firma_info += f"Tlf: {FIRMA_INFO['telefon']}<br/>"
        if 'epost' in FIRMA_INFO:
            firma_info += f"E-post: {FIRMA_INFO['epost']}<br/>"
        elements.append(Paragraph(firma_info, styles["Normal"]))
        elements.append(Spacer(1, 12))

        # Fakturainfo
        faktura_info = f"""
        <b>Fakturanummer:</b> {faktura_nummer}<br/>
        <b>Fakturadato:</b> {ordre.get('OrdreDato', 'N/A')}<br/>
        """
        elements.append(Paragraph(faktura_info, styles["Normal"]))
        elements.append(Spacer(1, 12))

        # Kundeinformasjon
        kunde_info = f"""
        <b>Til:</b><br/>
        {kunde.get('Fornavn', '')} {kunde.get('Etternavn', '')}<br/>
        {kunde.get('Adresse', '')}<br/>
        {kunde.get('PostNr', '')}<br/>
        """
        elements.append(Paragraph(kunde_info, styles["Normal"]))
        elements.append(Spacer(1, 12))

        # Ordredatoer (hvis tilgjengelig)
        if ordre.get('OrdreDato') or ordre.get('SendtDato') or ordre.get('BetaltDato'):
            ordre_dato_info = f"""
            <b>Ordredato:</b> {ordre.get('OrdreDato', 'N/A')}<br/>
            <b>Sendt dato:</b> {ordre.get('SendtDato', 'N/A')}<br/>
            <b>Betalt dato:</b> {ordre.get('BetaltDato', 'N/A')}<br/>
            """
            elements.append(Paragraph(ordre_dato_info, styles["Normal"]))
            elements.append(Spacer(1, 12))

        # Tabell med ordrelinjer
        table_data = [["Antall", "Beskrivelse", "Enhetspris", "Total"]]
        total_amount = 0

        for linje in ordrelinjer:
            quantity = int(float(linje.get('Antall', 0)))
            unit_price = float(linje.get('PrisPrEnhet', 0))
            line_total = quantity * unit_price

            table_data.append([
                f"{quantity}",
                linje.get('Betegnelse', ''),
                f"{unit_price:,.2f} NOK",
                f"{line_total:,.2f} NOK"
            ])
            total_amount += line_total

        table = Table(table_data, colWidths=[60, 240, 100, 100])
        table.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("ALIGN", (1, 1), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold")
        ]))
        elements.append(table)
        elements.append(Spacer(1, 12))

        # Totalsummer
        elements.append(Paragraph(f"<b>Sum eks. MVA:</b> {total_amount:,.2f} NOK", styles["Normal"]))
        mva_amount = total_amount * 0.25
        elements.append(Paragraph(f"<b>MVA (25%):</b> {mva_amount:,.2f} NOK", styles["Normal"]))
        total_with_mva = total_amount + mva_amount
        elements.append(Paragraph(f"<b>Total inkl. MVA:</b> {total_with_mva:,.2f} NOK", styles["Normal"]))

        # Bygg PDF
        doc.build(elements)

        try:
            os.startfile(pdf_filename)
        except Exception as e:
            print(f"Kunne ikke åpne PDF automatisk: {e}")
