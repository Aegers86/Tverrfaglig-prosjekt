import pdfkit
import os
from tkinter import messagebox

class PDFGenerator:
    def __init__(self, path_to_wkhtmltopdf):
        self.config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)

    def generate_invoice(self, ordre, ordrelinjer, kunde):
        html_content = f"""
        <html>
        <head><title>Faktura</title></head>
        <body>
            <h1>Faktura</h1>
            <p><strong>OrdreNr:</strong> {ordre[0]}</p>
            <p><strong>OrdreDato:</strong> {ordre[1]}</p>
            <p><strong>SendtDato:</strong> {ordre[2]}</p>
            <p><strong>BetaltDato:</strong> {ordre[3]}</p>
            <p><strong>Kunde:</strong> {kunde[1]} {kunde[2]}</p>
            <table border="1">
                <tr>
                    <th>VNr</th>
                    <th>PrisPrEnhet</th>
                    <th>Antall</th>
                </tr>
        """
        for linje in ordrelinjer:
            html_content += f"""
                <tr>
                    <td>{linje[1]}</td>
                    <td>{linje[2]}</td>
                    <td>{linje[3]}</td>
                </tr>
            """
        html_content += """
            </table>
        </body>
        </html>
        """

        pdf_filename = f"faktura_{ordre[0]}.pdf"
        pdfkit.from_string(html_content, pdf_filename, configuration=self.config)
        messagebox.showinfo("Suksess", f"Faktura lagret som {pdf_filename}")

        #Åpne PDF-filen
        os.startfile(pdf_filename)