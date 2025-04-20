#GUI-RAMMEVERK
import tkinter as tk                             #Her bruker vi tkinter som GUI-rammeverk og importerer det
from tkinter import messagebox                   #Her importerer vi modulen messagebox som vi senere skal bruke til en popup messagebox for å spørre om brukeren vil avslutte vinduet
from tkinter import ttk                          #Her importerer vi modulen ttk som vi senere skal bruke til treeview (linjer/result i db spørringer)
from database.database_program import Database   #Her importerer vi db som vi har laget i mappen "database", fra filen database_program.py. Class (klassen) i filen heter "Database". 
from pdf_generator import PDFGenerator           #Vi har valgt å prøve oss på valgfri del og har derfor laget en PDF generator som vi importerer her. 

#CLASS GUI - klasse for å konstruere applikasjon/programmet. 
class GUI:
    def __init__(self):                                                     #Denne kjøres automatisk når du konstruerer/lager et objekt. Denne initialiserer/genererer programmet.  
        self.root = tk.Tk()                                                 #Oppretter hovedvinduet
        self.root.geometry("800x1000")                                      #Setter størrelsen på vinduet
        self.root.title("Tverrfaglig prosjekt")                             #Setter tittelen på vinduet
        #Legger til menylinje
        self.menubar = tk.Menu(self.root)                                   #Oppretter menylinjen
        self.root.config(menu=self.menubar)                                 #Knytter menylinjen til vinduet

        self.filemeny = tk.Menu(self.menubar, tearoff=0)                    #Oppretter undermenyen i menylinjen
        self.menubar.add_cascade(label="Fil", menu=self.filemeny)           #Legger undermenyen til menylinjen
        self.filemeny.add_command(label="Print PDF", command=self.printPdf) #Legger til kommandoen "Print PDF" i undermenyen
        self.filemeny.add_separator()                                       #Legger til en separator i undermenyen
        self.filemeny.add_command(label="Avslutt", command=self.terminate)  #Legger til kommandoen "Avslutt" i undermenyen

        self.hjelpmeny = tk.Menu(self.menubar, tearoff=0)                   #Oppretter hjelp i menylinjen
        self.menubar.add_cascade(label="Hjelp", menu=self.hjelpmeny)        #Legger til hjelpen i menylinjen
        self.hjelpmeny.add_command(label="Om", command=self.omVindu)        #Legger til kommandoen "Om" i undermenyen

        self.root.columnconfigure(0, weight=1)                              #Konfigurerer kolonne 0
        self.root.columnconfigure(1, weight=1)                              #Konfigurerer kolonne 1
        self.root.columnconfigure(2, weight=1)                              #Konfigurerer kolonne 2
        self.root.columnconfigure(3, weight=1)                              #Konfigurerer kolonne 3
        self.root.columnconfigure(4, weight=0)                              #Konfigurerer kolonne 4
        
        self.root.rowconfigure(1, weight=1)                                 #Konfigurerer rad 1

        #Oppretter knapper med tilhørende kommandoer
        buttons = {
            "Vis varer på lager": self.hentVarerPåLager,
            "Vis alle ordre": self.hentAlleOrdrer,
            "Vis alle kunder": self.hentAlleKunder,
            "Avslutt": self.terminate
        }
        for i, (text, command) in enumerate(buttons.items()):                                       #For loop for å generere knappene på en enkel måte (Øyvind ville bare teste dette)
            button = tk.Button(master=self.root, text=text, font=("Arial", 14), command=command)    #Lager knapp ut ifra satte krav (i dictonary Buttons)
            button.grid(row=0, column=i, sticky="ew")                                               #Plasserer knappene i grid. Vi valgte å bruke grid som metode for å strukturere GUI. 

        #Treeview opprettelse for å vise resultat fra SQL spørringer
        self.tree = ttk.Treeview(self.root, show="headings")                                        #Oppretter tre for å vise data
        self.tree.grid(row=1, column=0, columnspan=5, padx=10, pady=10, sticky="nsew")              #Setter størrelse og plassering i GUI. North, South, East, West (nsew)
        self.vsb = ttk.Scrollbar(self.root, orient="vertical", command=self.tree.yview)             #Vertical scrollbar (vsb)
        self.vsb.grid(row=1, column=5, sticky="ns", padx=(0, 10))                                   #Plassering i grid
        self.tree.configure(yscrollcommand=self.vsb.set)                                            #Knytter vertical scrollbar til treeview 
        self.tree.bind("<Double-1>", self.påTreKlikk)                                               #Binder dobbeltklikk til funksjonen påTreKlikk

        self.db = Database()                                                                        #Initialiserer databaseobjektet

        self.root.protocol("WM_DELETE_WINDOW", self.terminate)                                      #Håndterer lukking av vinduet
        self.root.mainloop()                                                                        #Starter hovedløkken

    def terminate(self):                                                                            #Funksjon for å avslutte/terminere programmet
        if messagebox.askyesno("Avslutt", "Er du sikker på at du vil avslutte?"):                   #Spør om brukeren er sikker, opprettet vindu med messagebox modul
            self.root.destroy()                                                                     #Lukker vinduet

    def tømTre(self):                                                                               #Funksjon for å fjerne alle tidligere resultat og kunne vise nye i treeview
        for i in self.tree.get_children():                                                          #for loop for å gå gjennom alle underelementer
            self.tree.delete(i)                                                                     #Sletter elementet

    def oppdaterKolonner(self, kolonner):                                                           #Setter opp kolonnene i treet
        self.tree["columns"] = kolonner                                                             #Oppdaterer kolonnene i treet
        for col in kolonner:                                                                        #for loop for å gå gjennom kolonnene
            self.tree.heading(col, text=col)                                                        #Setter overskrift i kolonnen
            self.tree.column(col, width=100, anchor="center")                                       #Setter bredde og justerer for kolonnen

    def hentVarerPåLager(self):                                                                     #Funksjon for å hente varer på lager
        self.tømTre()                                                                               #Kjører funksjonen for å tømme treet
        self.oppdaterKolonner(("varenummer", "Betegnelse", "Pris", "Antall"))                       #Oppdaterer kolonnene
        data = self.db.fetch_all("SELECT * FROM vare WHERE antall > 0 ORDER BY antall DESC;")       #Variabel som lagrer data som er hentet fra databasen og sier at den skal vise i synkende rekkefølge når den senere kalles. 
        for i in data:                                                                              #Henter dataene som ligger i data
            self.tree.insert("", "end", values=i)                                                   #Setter inn data i treet

    def hentAlleOrdrer(self):                                                                             #Funksjon for å hente orderer
        self.tømTre()                                                                                     #Kjører funksjonen for å tømme treet
        self.oppdaterKolonner(("Ordrenummer", "Ordre dato", "Dato sendt", "Betalt Dato", "Kundenummer"))  #Oppdaterer kolonnene
        data = self.db.fetch_all("SELECT * FROM ordre;")                                                  #Henter data fra databasen
        for i in data:                                                                                    #Henter dataene som ligger i data
            self.tree.insert("", "end", values=i)                                                         #Setter inn data i treet

    def visInfoOmOrdre(self, ordreNr):                                                              #Funksjon som tar ett parameter som er ordrenummeret den skal hente informasjon om
        self.tømTre()                                                                               #Kjører funksjonen for å tømme treet
        self.oppdaterKolonner(("Ordrenummer", "Varenummer", "Enhetspris", "Antall"))                #Oppdaterer kolonnene
        data = self.db.fetch_all("SELECT * FROM ordrelinje WHERE OrdreNr = %s;", (ordreNr,))        #Henter data fra databasen med beskyttet parameter for SQL-injeksjon
        for i in data:                                                                              #Henter dataene som ligger i data
            self.tree.insert("", "end", values=i)                                                   #Setter inn data i treet

    def påTreKlikk(self, _):                                                                        #Funksjon som kjøres når du dobbeltklikker på et element i treeview-en
        selected_item = self.tree.selection()                                                       #Lagrer valget ditt (klikket ditt) i variablen selected_item
        if not selected_item:                                                                       #En if statement som kjører dersom du ikke velger noe/klikker på et tomt element
            messagebox.showwarning("Ingen valgt", "Vennligst velg en ordre.")                       #Ber bruker om å velge en ordre og kommer opp som en messagebox/varsel
            return                                                                                  #Avslutter funksjonen

        ordreNr = self.tree.item(selected_item[0], "values")[0]                                     #Lagrer ordrenummeret brukeren har klikket på

        # Lager nytt vindu for ordre detaljer
        details_window = tk.Toplevel(self.root)                                                     #Lager popupvindu
        details_window.title(f"Ordre detaljer - OrdreNr: {ordreNr}")                                #Setter navn på popupvindu basert på ordrenummer
        details_window.geometry("1000x400")                                                          #Setter størrelse på popupvinduet

        # Legge til ordreinfo
        kundenummer = self.tree.item(selected_item[0], "values")[4]                                                                                                                     #Variabel for å lagre brukervalg i ordre
        kundedata = self.db.fetch_one("SELECT * ,Poststed.Poststed FROM kunde inner join Poststed on Kunde.PostNr = Poststed.PostNr WHERE KNr = %s;", (kundenummer,))                   #Variabel som lagrer resultat fra SQL-spørring. Her skal vi vise adresse til kunde og må koble sammen postnummer og poststed for å få riktig visning slik vi vil ha det. Dette gjør vi med inner join og henter fra to tabeller "poststed" og "kunde".    
        kundelabel = tk.Label(details_window, text = f"Kundenummer: {kundedata[0]}\nNavn: {kundedata[1]} {kundedata[2]}\n Adresse: {kundedata[3]}, {kundedata[4]} {kundedata[6]}")      #Viser kundeprofil        
        kundelabel.pack(pady = 100, side="left")                                                                                                                                        #Pakker det hele sammen. Vi velger også å vise kundedataene til venstre i visningsvinduet

        # Legger til en knapp for å generere faktura
        generate_invoice_button = tk.Button(details_window, text="Generer faktura", command=lambda: self.printPdf())    #Lager knapp som heter "Generer faktura" og kjører funksjonen printPdf()
        generate_invoice_button.pack(pady=10)                                                                           #I dette vinduet ønsket vi å prøve pack istedet for grid, for å oppleve forskjellen

        # Treeview ordredetaljer detaljer
        details_tree = ttk.Treeview(details_window, show="headings")                                #Lager Treeview for å vise ordre detaljer
        details_tree.pack(fill="both", expand=True, padx=10, pady=10, side="left")                  #Setter størrelse og plassering i GUI. 

        # Legger til scrollbar for Treeview i nytt vindu
        details_vsb = ttk.Scrollbar(details_window, orient="vertical", command=details_tree.yview)  #Lager Treeview for å vise ordre detaljer i nytt vindu
        details_vsb.pack(side="right", fill="y")                                                    #Setter størrelse og plassering i GUI.
        details_tree.configure(yscrollcommand=details_vsb.set)                                      #Kobler sammen treet og scrollbaren

        # Henter data for ordre detaljer
        details_tree["columns"] = ("Ordrenummer", "Varenummer", "Enhetspris", "Antall")             #Setter inn kolonner
        for col in details_tree["columns"]:                                                         #for loop som den kjører gjennom
            details_tree.heading(col, text=col)                                                     #Setter overskrift
            details_tree.column(col, width=100, anchor="center")                                    #Forteller at kolonnen skal være 100px bred og midtstilt
        
        data = self.db.fetch_all("SELECT * FROM ordrelinje WHERE OrdreNr = %s;", (ordreNr,))        #Henter fra ordrenummer variabelen ordrenummer og er beskyttet mot SQL injeksjon
        for i in data:                                                                              #Henter dataene som ligger i data
            details_tree.insert("", "end", values=i)                                                #Legger til verdiene som er hentet fra databasen
 
    def printPdf(self):                                                                             #Funksjon for å printe PDF faktura - valgfri oppgave. 
        selected_item = self.tree.selection()                                                       #Variabel for å lagre valget brukeren gjør
        if not selected_item:                                                                       #If statement som kjører hvis man ikke har valgt noe
            messagebox.showwarning("Ingen valgt", "Vennligst velg en ordre å skrive ut.")           #Oppretter messagebox/advarsel dersom man ikke har gjort noen valg eller velger et tomt element
            return                                                                                  #Avslutter funksjonen

        ordreNr = self.tree.item(selected_item[0], "values")[0]                                                                                                                    #Variabel som lagrer ordrenummeret for faktura som vi skal skrive ut
        ordrelinjer = self.db.fetch_all("SELECT ordrelinje.*, vare.betegnelse FROM ordrelinje JOIN vare ON ordrelinje.VNr = vare.VNr WHERE ordrelinje.ordreNr = %s;", (ordreNr,))  #Henter ordrelinjer fra databasen med beskyttet parameter for SQL-injeksjon.
        ordre = self.db.fetch_one("SELECT * FROM ordre WHERE OrdreNr = %s;", (ordreNr,))                                                                                           #Henter ordre data fra databasen med beskyttet parameter for SQL-injeksjon.
        kunde = self.db.fetch_one("SELECT * FROM kunde WHERE knr = %s;", (ordre[4],))                                                                                              #Henter kunde data fra databasen med beskyttet parameter for SQL-injeksjon.
        #print(f"ordre {ordre},ordrelinje {ordrelinjer}, kunde {kunde}")                                                                                                           #debugging print, vi lar denne stå for å vise hvordan vi jobbet med å finne rett måte å velge rett index.
        pdfgen = PDFGenerator()                                                                                                                                                    #Initialiserer/kjører PDF-generatoren
        pdfgen.generate_invoice(ordre,ordrelinjer,kunde)                                                                                                                           #Genererer PDF med informasjon lagret i variablene over
    
    def hentAlleKunder(self):                                                                      #Funksjon for å se kundedb med stored procedures
        self.tømTre()                                                                              #Kjører funksjonen for å tømme treet
        self.oppdaterKolonner(("Kundenummer", "Fornavn", "Etternavn", "Adresse", "Post Nummer"))   #Oppdaterer kolonnene
        data = self.db.call_procedure("hent_alle_kunder")                                          #Henter data fra databasen med følgende store procedures: "SELECT * FROM varehusdb.kunde;"
        for i in data:                                                                             #Henter dataene som ligger i variablen data
            self.tree.insert("", "end", values=i)  
            
    def omVindu(self):                                                                                                                  #Funksjon for å vise informasjon om programmet
        # Lager nytt vindu for å vise informasjon om programmet
        about_window = tk.Toplevel(self.root)                                                                                           #Lager popupvindu
        about_window.title("Om programmet")                                                                                             #Setter navn på popupvindu
        about_window.geometry("300x200")                                                                                                #Setter størrelse på popupvinduet
        about_label = tk.Label(about_window, text="Tverrfaglig prosjekt\n\nGruppe 1\n\nLaget av:\n\nCharlotte, Knut, Truls og Øyvind")  #Lager tekst i vinduet                                          
        about_label.pack(pady=20)                                                                                                       #Setter plassering i vinduet
        close_button = tk.Button(about_window, text="Lukk", command=about_window.destroy)                                               #Lager lukkeknapp i vinduet    
        close_button.pack(padx=10)                                                                                                      #Setter lukkeknapp i vinduet

GUI()  #Starter GUI
