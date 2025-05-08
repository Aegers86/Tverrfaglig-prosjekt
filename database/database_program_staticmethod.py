import mysql.connector
from dotenv import load_dotenv
import os

#Laster miljøvariabler fra .env-filen
load_dotenv()

#Henter databasekonfigurasjon fra miljøvariabler
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

class Database:
    def __init__(self):                         #Initialiserer databasen
        self.db = None                          #Setter db til None ved oppstart

    #Koble til databasen
    def connect(self):                          #Kobler til databasen
        self.db = mysql.connector.connect(      #Kobler til databasen med konfigurasjon fra miljøvariabler
            host=DB_HOST,                       #Vert for databasen
            user=DB_USER,                       #Brukernavn for databasen
            passwd=DB_PASSWORD,                 #Passord for databasen
            port=DB_PORT,                       #Port for databasen
            database=DB_NAME                    #Navn på databasen
        )

    #Lukk tilkoblingen til databasen
    def close(self):                            #Lukker tilkoblingen til databasen
        if self.db:                             #Sjekker om tilkoblingen eksisterer
            self.db.close()                     #Lukker tilkoblingen

    #Hent alle rader fra en spørring
    def fetch_all(self, query, params=None):    #Henter alle rader fra spørring
        self.connect()                          #Kobler til databasen
        cursor = self.db.cursor()               #Oppretter en cursor for å utføre spørringer
        cursor.execute(query, params or ())     #Kjører spørringen med parametere
        data = cursor.fetchall()                #Henter alle rader fra resultatene
        cursor.close()                          #Lukker cursoren
        self.close()                            #Lukker tilkoblingen
        return data                             #Returnerer resultatene

    #Hent en enkelt rad fra en spørring
    def fetch_one(self, query, params=None):    #Henter en enkelt rad fra spørring
        self.connect()                          #Kobler til databasen
        cursor = self.db.cursor()               #Oppretter en cursor for å utføre spørringer
        cursor.execute(query, params or ())     #Kjører spørringen med parametere
        data = cursor.fetchone()                #Henter en enkelt rad fra resultatene
        cursor.close()                          #Lukker cursoren
        self.close()                            #Lukker tilkoblingen
        return data                             #Returnerer resultatene
    
    #Hent resultatet av en lagret prosedyre
    def call_procedure(self, procedure, args=()):   #Henter resultatet av en lagret prosedyre
        self.connect()                              #Kobler til databasen
        cursor = self.db.cursor()                   #Oppretter en cursor for å utføre spørringer
        cursor.callproc(procedure, args)            #Kjører den lagrede prosedyren med argumenter
        results = []                                #Oppretter en tom liste for å lagre resultatene
        for result in cursor.stored_results():      #Itererer gjennom resultatene fra den lagrede prosedyren
            results.extend(result.fetchall())       #Henter alle rader fra resultatene og legger dem til i listen
        cursor.close()                              #Lukker cursoren
        self.close()                                #Lukker tilkoblingen
        return results                              #Returnerer resultatene

    #Oppdaterer en rad i databasen med en spørring og parametere
    def update_one(self, query, params):            #Oppdaterer en rad i databasen med en spørring og parametere
        self.connect()                              #Kobler til databasen
        cursor = self.db.cursor()                   #Oppretter en cursor for å utføre spørringer
        cursor.execute(query, params)               #Kjører spørringen med parametere
        self.db.commit()                            #Bekrefter endringer i databasen
        cursor.close()                              #Lukker cursoren
        self.close()                                #Lukker tilkoblingen

    #Lagrer en ny faktura i databasen og returnerer faktura-ID
    def insert_faktura(self, ordreNr, kNr):         #Lagrer en ny faktura i databasen og returnerer faktura-ID
        self.connect()                              #Kobler til databasen
        cursor = self.db.cursor()                   #Oppretter en cursor for å utføre spørringer
        #SQL spørring for å sette inn en ny rad i faktura-tabellen
        #Bruker ordreNr og kNr som parametere for å sette inn i tabellen
        insert_query = """          
        INSERT INTO faktura (OrdreNr, KNr)
        VALUES (%s, %s)
        """
        cursor.execute(insert_query, (ordreNr, kNr))#Kjører spørringen med parametere
        self.db.commit()                            #Bekrefter endringer i databasen
        faktura_id = cursor.lastrowid               #Henter ID-en til den sist innlagte fakturaen
        cursor.close()                              #Lukker cursoren
        self.close()                                #Lukker tilkoblingen
        return faktura_id                           #Returnerer faktura-ID

    #setter inn en ny kunde i databasen og finner den høyeste kNr
    def insert_kunde(self, Fornavn, Etternavn, Adresse, Postnr):    #Setter inn en ny kunde i databasen og finner den høyeste kNr
        self.connect()                                              #Kobler til databasen 
        cursor = self.db.cursor()                                   #Oppretter en cursor for å utføre spørringer
        cursor.execute("SELECT MAX(KNr) FROM kunde")                #SQL spørring for å finne den høyeste kNr i kunde-tabellen
        result = cursor.fetchone()                                  #Henter resultatet av spørringen
        max_kNr = result[0] if result[0] is not None else 0         #Sjekker om resultatet er None og setter max_kNr til 0 hvis det er tilfelle
        kNr = max_kNr + 1                                           #Setter kNr til max_kNr + 1 for å lage en ny unik ID for kunden
        #SQL spørring for å sette inn en ny rad i kunde-tabellen
        insert_query = """
        INSERT INTO kunde (KNr, Fornavn, Etternavn, Adresse, Postnr) VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (kNr, Fornavn, Etternavn, Adresse, Postnr))    #Kjører spørringen med parametere
        #print(f"Inserted Kunde with kNr: {kNr}")                                   #Debugging utskrift for å vise hvilken kNr som ble satt inn
        self.db.commit()                                                            #Bekrefter endringer i databasen
        cursor.close()                                                              #Lukker cursoren
        self.close()                                                                #Lukker tilkoblingen