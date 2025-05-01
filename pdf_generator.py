#importering av elementer for å lage PDF generatoren Reportlab
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, Image  
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
import os

class PDFGenerator:                                                             #Klasse for PDF generering
    def generate_invoice(self, ordre, ordrelinjer, kunde, faktura_nummer):      #Funksjon for å hente elementer til PDF-en
        pdf_filename = f"faktura_{faktura_nummer}.pdf"                          #lager navn på PDF dokumentet faktura_nummer.pdf
        doc = SimpleDocTemplate(pdf_filename, pagesize=A4)                      #Setter maltype på dokumentet og setter størrelse
        elements = []                                                           #Tom liste for strukturering i generatoren
        styles = getSampleStyleSheet()                                          #Styleelement (stil) med fonter osv i PDF-en
        logo_path = r"static/logo.png"                                          #Henter logo fra sti
        img = Image(logo_path, width=100, height=50)                            #Setter høyde og bredde på bildet
        img.hAlign = 'LEFT'                                                     #Setter bildet til venstre på skjermen
        elements.append(img)                                                    #legger til bilde i PDF-en som et element
        elements.append(Spacer(1, 12))                                          #legger til en spacer i PDF-en som et element

        #Kundeinfo - linje 21-25: variabel for å hente kundeinfo fra def generate_invoice
        customer_info = f"""
        <b>Fakturanummer:</b> {faktura_nummer}<br/>
        <b>Kunde:</b> {kunde[1]} {kunde[2]}<br/>
        <b>Adresse:</b> {kunde[3]}, {kunde[4]}<br/>
        """
        elements.append(Paragraph(customer_info, styles["Normal"]))             #legge til innholdet i variabelen over i dokumentet
        elements.append(Spacer(1, 12))                                          #legger til en spacer i PDF-en som et element

        #ordretabell
        table_data = [["Antall", "Beskrivelse", "Enhetspris", "Totalt"]]        #definerer kolonnenavnene i dokumentet
        totalt = 0                                                              #variabel som kalkulerer totalsum

        #For-loop for å gå gjennom alle ordrelinjer
        for linje in ordrelinjer:                                               #starter for-loop
            Antall = int(float(linje[3]))                                       #tar ut antall 
            Enhetspris = float(linje[2])                                        #tar ut enhetspris
            linje_total = Antall * Enhetspris                                   #regner sammen totalprisen ved å gange antall og enhetspris

            table_data.append([                                                 #legger til informasjonen som er hentet ut over
                f"{Antall:,}",                                                  #legger til antall
                f"{linje[4]}",                                                  #legger til beskrivelsen
                f"{Enhetspris:,.2f} NOK",                                       #legger til enhetspris med to desimaler (.2f) og viser pris med NOK bak
                f"{linje_total:,.2f} NOK"                                       #legger til totalprisen med to desimaler (.2f) og viser pris med NOK bak
            ])          

            totalt += linje_total                                               #variabel for å regne sammen totalsummen

        #table for å definere utsende på kolonnene
        table = Table(table_data, colWidths=[60, 200, 100, 100])                #oppretter tabellen med data fra tabledata
        table.setStyle(TableStyle([                                             #setter utseende på tabellen
            ("GRID", (0, 0), (-1, -1), 1, colors.black),                        #setter stil på linje i tabell sort
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),                  #setter stil på bakgrunn (øverste rad) i tabell grå
            ("ALIGN", (1, 1), (-1, -1), "CENTER"),                              #sentrerer og setter hvor ting skal være på skjermen
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold")                     #setter font helvetica-bold
        ]))
        elements.append(table)                                                  #legge til tabellen i dokumentet

        elements.append(Spacer(1, 12))                                                                         #legger til mellomrom mellom tabell og totalen (spacer)
        elements.append(Paragraph(f"<b>Total (eks. MVA):</b> {totalt:,.2f} NOK", styles["Normal"]))            #legger til informasjonen i dokumentet

        mva_beløp = totalt * 0.25                                                                              #beregner 25% MVA
        elements.append(Paragraph(f"<b>25% MVA:</b> {mva_beløp:,.2f} NOK", styles["Normal"]))                  #legger til informasjonen i dokumentet

        totalpris_mmva = totalt + mva_beløp                                                                    #beregner ny totalpris ved å ta med moms + totalverdi uten
        elements.append(Paragraph(f"<b>Total (inkl. MVA):</b> {totalpris_mmva:,.2f} NOK", styles["Normal"]))   #legger til informasjonen i dokumentet


        #generer PDF
        doc.build(elements, onFirstPage=add_footer, onLaterPages=add_footer)                                   #lager fil ut ifra elementer
        os.startfile(pdf_filename)                                                                             #åpner filen som er laget

def add_footer(canvas, doc):                                                                                   #funksjon for å legge til footer
    footer_text = "Gruppe 1 AS | +47 911 | Gymnasvegen 27 | Org.nr: 987237910MVA"                              #legger til informasjon om "organisasjonen"                                                                                        #
    canvas.setFont("Helvetica-Bold", 8)                                                                        #legger til font og skriftstørrelse         
    canvas.setFillColor(colors.grey)                                                                           #setter farge på tekst
    canvas.drawCentredString(A4[0] / 2.0, 15 * mm, footer_text)                                                #plasserer footer og setter størrelse på footer