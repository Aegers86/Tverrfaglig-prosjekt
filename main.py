import tkinter as tk #Importerer tkinter
from tkinter import messagebox #Importerer messagebox fra tkinter
from tkinter import ttk #Importerer ttk fra tkinter
import mysql.connector #Importerer mysql connector
from dotenv import load_dotenv #Importerer load_dotenv fra dotenv
import os 
import pdfkit

load_dotenv() #Laster inn .env filen og henter informasjonen fra .env filen så vi slipper å eksponere passord og brukernavn
#Husk og lage en fil som heter .gitignore(Ser ut som den kommer med på pull request) og legg til .env i denne filen slik at .env filen ikke blir lastet opp til github
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

#Klasse for GUI
class GUI:
    def __init__(self):
        self.root = tk.Tk() #Lager et vindu
        self.root.geometry("800x1000") #Setter størrelsen på vinduet
        self.root.title("Tverrfaglig prosjekt") #Setter tittelen på vinduet
        self.root.columnconfigure(0, weight=2) #Setter vekt på kolonne 0
        self.root.columnconfigure(1, weight=1) #Setter vekt på kolonne 1
        self.root.columnconfigure(2, weight=1) #Setter vekt på kolonne 2
        self.root.rowconfigure(1, weight=1) #Setter vekt på rad 1

        #Lager knapper, lager en dictionary med knappene og funksjonene de skal utføre
        buttons = {
            "Vis varer på lager": self.hentVarerPåLager,
            "Vis alle ordre": self.hentAlleOrdrer,
            "Avslutt": self.terminate,
            "Print pdf": self.printPdf
        }
        #Lager knappene og plasserer de i vinduet ut i fra dictionaryen over
        for i, (text, command) in enumerate(buttons.items()):
            button = tk.Button(master=self.root, text=text, font=("Arial", 14), command=command)
            button.grid(row=0, column=i, sticky="ew")

        #Lager ett tre for å vise alle varer som er på lager
        self.tree = ttk.Treeview(self.root, show="headings")
        self.tree.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")
        #Lager en vertikal scrollbar for treet
        self.vsb = ttk.Scrollbar(self.root, orient="vertical", command=self.tree.yview)
        self.vsb.grid(row=1, column=3, sticky="ns") #Plasserer scrollbaren i vinduet
        self.tree.configure(yscrollcommand=self.vsb.set) #Knytter scrollbaren til treet

        #Koble klikk event til treet
        self.tree.bind("<Double-1>", self.påTreKlikk)
           
        self.root.protocol("WM_DELETE_WINDOW", self.terminate) #Lukker vinduet/avslutter programmet
        self.root.mainloop() #Starter grensesnittet

    def terminate(self):
        if messagebox.askyesno("Avslutt", "Er du sikker på at du vil avslutte?"): #Bekreftelse på at bruker vil avslutte
            self.root.destroy()

    def databaseConnection(self): #En metode for å koble til databasen
        self.db = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            passwd=DB_PASSWORD,
            port=DB_PORT,
            database=DB_NAME
        )
    
    def tømTre(self): #Tømmer treet
        for i in self.tree.get_children():
            self.tree.delete(i)
        
    def oppdaterKolonner(self, kolonner): #Oppdaterer kolonnene i treet
        self.tree["columns"] = kolonner #Setter kolonnene i treet
        for col in kolonner: #Legger til kolonnene i treet
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="center")

    def hentVarerPåLager(self): #Henter data fra databasen og legger det inn i treet
        self.tømTre() #Tømmer treet
        self.oppdaterKolonner(("VNr", "Betegnelse", "Pris", "Antall")) 
        self.databaseConnection() 
        c = self.db.cursor()
        c.execute("SELECT * FROM vare WHERE antall > 0 ORDER BY antall DESC;") #order by funker ikke for en eller annen grunn, sjekkes.
        data = c.fetchall()
        for i in data:
            self.tree.insert("", "end", values=i)
        c.close()

    def hentAlleOrdrer(self): #Henter data fra databasen og legger det inn i treet
        self.tømTre() #Tømmer treet
        self.oppdaterKolonner(("OrdreNr", "OrdreDato", "SendtDato", "BetaltDato", "KNr")) 
        self.databaseConnection() 
        c = self.db.cursor()
        c.execute("SELECT * FROM ordre;")
        data = c.fetchall()
        for i in data:
            self.tree.insert("", "end", values=i)
        c.close()

    def visInfoOmOrdre(self, ordreNr):
        self.tømTre() #Tømmer treet
        self.oppdaterKolonner(("OrdreNr","VNr", "PrisPrEnhet", "Antall")) 
        self.databaseConnection() #Henter data fra databasen og legger det inn i treet
        c = self.db.cursor()
        c.execute(f"SELECT * FROM ordrelinje WHERE OrdreNr = {ordreNr};") #Må legge inn join fra kunde, legge sammen ordrelinjer og total pris på ordre
        data = c.fetchall()
        for i in data:
            self.tree.insert("", "end", values=i)
        c.close()

    def påTreKlikk(self, _): #Henter data fra treet og viser informasjon om ordrenummeret
        selected_item = self.tree.selection()[0] #Henter ut det valgte elementet i treet
        ordreNr = self.tree.item(selected_item, "values")[0] #Henter ut ordrenummeret va valgte elementet
        self.visInfoOmOrdre(ordreNr) #Viser informasjon om ordrenummeret


    def printPdf(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Ingen valgt", "Vennligst velg en ordre å skrive ut.")
            return

        ordreNr = self.tree.item(selected_item[0], "values")[0]
        self.databaseConnection()
        c = self.db.cursor()
        c.execute(f"SELECT * FROM ordrelinje WHERE OrdreNr = {ordreNr};") #kanskje bedre å ta dette i en egen metode, eller i en join?
        ordrelinjer = c.fetchall()
        c.execute(f"SELECT * FROM ordre WHERE OrdreNr = {ordreNr};")
        ordre = c.fetchone()
        c.execute(f"SELECT * FROM kunde WHERE KNr = {ordre[4]};")
        kunde = c.fetchone()
        c.close()

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

        # Spesifiserer lokasjonen av programmet wkhtmltopdf
        path_to_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
        config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)

        pdf_filename = f"faktura_{ordreNr}.pdf"
        pdfkit.from_string(html_content, pdf_filename, configuration=config)
        messagebox.showinfo("Suksess", f"Faktura lagret som {pdf_filename}")

        # Åpne PDF-filen
        os.startfile(pdf_filename)

GUI() #Kjører programmet