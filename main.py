import tkinter as tk #Importerer tkinter
from tkinter import messagebox #Importerer messagebox fra tkinter
from tkinter import ttk #Importerer ttk fra tkinter
import mysql.connector #Importerer mysql connector
from dotenv import load_dotenv #Importerer load_dotenv fra dotenv
import os 

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

        #Lager knapper
        self.knapp1 = tk.Button(master=self.root, text="Vis varer på lager", font=("Arial", 14), command=self.hentVarerPåLager) #Lager en knapp
        self.knapp2 = tk.Button(master=self.root, text="Vis alle ordre", font=("Arial", 14), command=self.hentAlleOrdrer) #Lager en knapp
        self.knapp3 = tk.Button(master=self.root, text="exit", font=("Arial", 14), command=self.terminate) #Lager en knapp
        self.knapp1.grid(row=0, column=0, sticky="ew") #Plasserer knappen i vinduet
        self.knapp2.grid(row=0, column=1, sticky="ew") #Plasserer knappen i vinduet
        self.knapp3.grid(row=0, column=2, sticky="ew") #Plasserer knappen i vinduet

        #Lager ett tre for å vise alle varer som er på lager
        self.tree = ttk.Treeview(self.root, show="headings")
        self.tree.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")
        self.vsb = ttk.Scrollbar(self.root, orient="vertical", command=self.tree.yview)
        self.vsb.grid(row=1, column=3, sticky="ns")
        self.tree.configure(yscrollcommand=self.vsb.set)
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
        self.tømTre()
        self.oppdaterKolonner(("VNr", "Betegnelse", "Pris", "Antall")) 
        self.databaseConnection()
        c = self.db.cursor()
        c.execute("SELECT * FROM vare WHERE antall > 0 ORDER BY antall DESC;") #order by funker ikke for en eller annen grunn, sjekkes.
        data = c.fetchall()
        for i in data:
            self.tree.insert("", "end", values=i)
        c.close()

    def hentAlleOrdrer(self):
        #Tømmer treet
        self.tømTre()
        self.oppdaterKolonner(("OrdreNr", "OrdreDato", "SendtDato", "BetaltDato", "KNr")) 

        #Henter data fra databasen og legger det inn i treet
        self.databaseConnection()
        c = self.db.cursor()
        c.execute("SELECT * FROM ordre;") #order by funker ikke for en eller annen grunn, sjekkes.
        data = c.fetchall()
        for i in data:
            self.tree.insert("", "end", values=i)
        c.close()

    def visInfoOmOrdre(self, ordreNr):
        #Tømmer treet
        self.tømTre()
        self.oppdaterKolonner(("OrdreNr","VNr", "PrisPrEnhet", "Antall")) 

        #Henter data fra databasen og legger det inn i treet
        self.databaseConnection()
        c = self.db.cursor()
        c.execute(f"SELECT * FROM ordrelinje WHERE OrdreNr = {ordreNr};") #Må legge inn join fra kunde, legge sammen ordrelinjer og total pris på ordre
        data = c.fetchall()
        for i in data:
            self.tree.insert("", "end", values=i)
        c.close()

    def påTreKlikk(self, _): #Henter data fra treet og viser informasjon om ordrenummeret
        selected_item = self.tree.selection()[0]
        ordreNr = self.tree.item(selected_item, "values")[0]
        self.visInfoOmOrdre(ordreNr)

GUI() #Kjører programmet