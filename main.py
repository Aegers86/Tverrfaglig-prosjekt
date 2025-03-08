import tkinter as tk #Importerer tkinter
from tkinter import messagebox #Importerer messagebox fra tkinter
from tkinter import ttk #Importerer ttk fra tkinter
import mysql.connector #Importerer mysql connector
from dotenv import load_dotenv #Importerer load_dotenv fra dotenv
import os 

load_dotenv() #Laster inn .env filen og henter informasjonen fra .env filen så vi slipper å eksponere passord og brukernavn
#Husk og lage en fil som heter .gitignore og legg til .env i denne filen slik at .env filen ikke blir lastet opp til github
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

#Mysql connector som bruker informasjonen fra .env filen
db = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    passwd=DB_PASSWORD,
    port=DB_PORT,
    database=DB_NAME
    )

#Klasse for GUI
class GUI:
    def __init__(self):
        self.root = tk.Tk() #Lager et vindu
        self.root.geometry("800x1000") #Setter størrelsen på vinduet
        self.root.title("Tverrfaglig prosjekt") #Setter tittelen på vinduet

        #Lager en label
        self.label = tk.Label(self.root, text="Velkommen til tverrfaglig prosjekt", font=("Arial", 18)) #Lager en label
        self.label.pack(padx=10, pady=10) #Plasserer labelen i vinduet

        #lage en tekstboks
        self.textbox = tk.Text(self.root, height=10, width=50, font=("Arial", 14)) #Lager en tekstboks
        self.textbox.pack(padx=10, pady=10) #Plasserer tekstboksen i vinduet

        #Lager en knapp
        self.button = tk.Button(self.root, text="Klikk her", font=("Arial", 14), command=self.test_knapp) #Lager en knapp
        self.button.pack(padx=10, pady=10) #Plasserer knappen i vinduet

        #label over liste over varer på lager
        self.label = tk.Label(self.root, text="Varer på lager!", font=("Arial", 18)) #Lager en label
        self.label.pack(padx=10, pady=10) #Plasserer labelen i vinduet

        #Lager ett tre for å vise alle varer som er på lager
        self.colums = ("VNr", "Betegnelse", "Pris", "Antall") #Kolonnene i treet
        self.tree = ttk.Treeview(self.root, columns=self.colums, show="headings")
        self.tree.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        for col in self.colums:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="center")

        #Henter data fra databasen og legger det inn i treet
        self.db = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            passwd=DB_PASSWORD,
            port=DB_PORT,
            database=DB_NAME
        )
        c = self.db.cursor()
        c.execute("SELECT * FROM vare WHERE antall > 0 ORDER BY antall DESC;") #order by funker ikke for en eller annen grunn, sjekkes.
        data = c.fetchall()
        for rec in data:
            self.tree.insert("", "end", values=rec)
        c.close()
            
        self.root.protocol("WM_DELETE_WINDOW", self.terminate) #Lukker vinduet/avslutter programmet
        self.root.mainloop() #Starter grensesnittet

    def test_knapp(self):
        print("Knappen er trykket på")

    def terminate(self):
        if messagebox.askyesno("Avslutt", "Er du sikker på at du vil avslutte?"):
            self.root.destroy()

GUI() #Kjører programmet