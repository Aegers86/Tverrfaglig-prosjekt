import tkinter as tk #Importerer tkinter
import mysql.connector #Importerer mysql connector
from dotenv import load_dotenv #Importerer load_dotenv fra dotenv
import os 

load_dotenv() #Laster inn .env filen
#Henter informasjonen fra .env filen så vi slipper å eksponere passord og brukernavn
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

db.close() #Lukker databasen

#Klasse for GUI
class GUI:
    def __init__(self):
        self.root = tk.Tk() #Lager et vindu
        self.root.geometry("800x500") #Setter størrelsen på vinduet
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

        self.root.mainloop() #Starter grensesnittet

    def test_knapp(self):
        print("Knappen er trykket på")

GUI() #Kjører programmet