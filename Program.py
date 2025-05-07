#GUI-RAMMEVERK
import tkinter as tk                             #Her bruker vi tkinter som GUI-rammeverk og importerer det
from tkinter import messagebox                   #Her importerer vi modulen messagebox som vi senere skal bruke til en popup messagebox for å spørre om brukeren vil avslutte vinduet
from tkinter import ttk                          #Her importerer vi modulen ttk som vi senere skal bruke til treeview (linjer/result i db spørringer)
from database.database_program_staticmethod import Database   #Her importerer vi db som vi har laget i mappen "database", fra filen database_program.py. Class (klassen) i filen heter "Database". 
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

        self.root.columnconfigure(0, weight=0)                              #Konfigurerer kolonne 0
        self.root.columnconfigure(1, weight=1)                              #Konfigurerer kolonne 1
        
        self.root.rowconfigure(0, weight=1)                                 #Konfigurerer rad 0

        # Oppretter en ramme for knappene
        button_frame = tk.Frame(self.root)                                  #Oppretter en ramme for knappene
        button_frame.grid(row=0, column=0, sticky="ns", padx=10, pady=10)   #Setter størrelse og plassering i GUI.
        button_frame.columnconfigure(0, weight=1)                           #Konfigurerer kolonne 0 i knapperammen

        # Oppretter knapper med tilhørende kommandoer
        buttons = {                                                         #Oppretter en dictionary med knapper og tilhørende kommandoer
            "Vis alle ordre": self.hentAlleOrdrer,
            "Vis varer på lager": self.hentVarerPåLager,
            "Kunder": self.hentAlleKunder,
            "Avslutt": self.terminate
        }
        for i, (text, command) in enumerate(buttons.items()):                                       #For loop for å generere knappene på en enkel måte
            button = tk.Button(master=button_frame, text=text, font=("Arial", 14), command=command) #Lager knapp ut ifra satte krav (i dictonary Buttons)
            button.grid(row=i, column=0, sticky="ew", pady=5)                                       #Plasserer knappene i grid

        # Treeview opprettelse for å vise resultat fra SQL spørringer
        self.tree = ttk.Treeview(self.root, show="headings")                                        #Oppretter tre for å vise data
        self.tree.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")                            #Setter størrelse og plassering i GUI. North, South, East, West (nsew)
        self.vsb = ttk.Scrollbar(self.root, orient="vertical", command=self.tree.yview)             #Vertical scrollbar (vsb)
        self.vsb.grid(row=0, column=2, sticky="ns", padx=(0, 10))                                   #Plassering i grid
        self.tree.configure(yscrollcommand=self.vsb.set)                                            #Knytter vertical scrollbar til treeview 
        self.tree.bind("<Double-1>", self.påTreKlikk)                                               #Binder dobbeltklikk til funksjonen påTreKlikk

        self.db = Database()                                                                        #Initialiserer databaseobjektet

        self.root.protocol("WM_DELETE_WINDOW", self.terminate)                                      #Håndterer lukking av vinduet
        self.hentAlleOrdrer()
        self.root.mainloop()                                                                        #Starter hovedløkken
   
    #Dette er en dekoratør, den brukes for å legge til feilhåndtering uten å endre den opprinnelige funksjonen direkte. Vi benytter en wrapper som tar imot alle argumentene som sendes til den opprinnelige funksjonen og prøver å kjøre funksjonen med argumentene. Hvis det oppstår en feil vil wrapperen fange feilen og printe beskjed til terminalen da det er det vi sagt den skal gjøre dersom det oppstår en feil. 
    @staticmethod                                                                            
    def sikkerhetsSjekk(func):                                                                      #Funksjon for å sjekke om det skjer feil med funksjonen 
        def wrapper(*args, **kwargs):                                                               #Wrapper funksjoner for å håndtere feil
            try:
                return func(*args, **kwargs)                                                        #Kjører funksjonen som er sendt inn, med parametere
            except Exception as e:                                                                  #Hvis det skjer en feil, så kjører vi koden under
                print(f"feil på funksjon {func.__name__}: {e}")                                     #Printer feilmeldingen i terminal og viser hvilken funksjon det er snakk om
                messagebox.showerror("Feil", f"Det skjedde en feil: {e}")                           #Viser feilmeldingen i en messagebox
        return wrapper                                                                              #Returnerer wrapperen
    
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

    @sikkerhetsSjekk
    def hentVarerPåLager(self):                                                                     #Funksjon for å hente varer på lager
        #Lager nytt vindu for alle varer
        varelager_window = tk.Toplevel(self.root)                                                               #Lager popupvindu
        varelager_window.title("Varer")                                                                         #Setter navn på popupvindu
        varelager_window.geometry("1080x400")                                                                   #Setter størrelse på popupvinduet
                                                              
        # Treeview varedetaljer detaljer
        self.vare_tree = ttk.Treeview(varelager_window, show="headings")                                        #Lager Treeview for å vise vare detaljer
        self.vare_tree.pack(fill="both", expand=True, padx=10, pady=10, side="left")                            #Setter størrelse og plassering i GUI. 

        # Legger til scrollbar for Treeview i nytt vindu
        vare_vsb = ttk.Scrollbar(varelager_window, orient="vertical", command=self.vare_tree.yview)             #Lager Treeview for å vise vare detaljer i nytt vindu
        vare_vsb.pack(side="right", fill="y")                                                                   #Setter størrelse og plassering i GUI.
        self.vare_tree.configure(yscrollcommand=vare_vsb.set)                                                   #Kobler sammen treet og scrollbaren

        # Henter varer
        self.vare_tree["columns"] = ("varenummer", "Betegnelse", "Pris", "Antall")                              #Setter inn kolonner
        for col in self.vare_tree["columns"]:                                                                   #for loop som den kjører gjennom
            self.vare_tree.heading(col, text=col)                                                               #Setter overskrift
            self.vare_tree.column(col, width=100, anchor="center")                                              #Setter størrelse på varetreet
        data = self.db.fetch_all("SELECT * FROM vare WHERE antall > 0 ORDER BY antall DESC;")                   #Variabel som lagrer data som er hentet fra databasen og sier at den skal vise i synkende rekkefølge når den senere kalles. 
        for i in data:                                                                                          #Henter dataene som ligger i data
            self.vare_tree.insert("", "end", values=i)                                                          #Setter inn data i treet

    @sikkerhetsSjekk
    def hentAlleOrdrer(self):                                                                             #Funksjon for å hente orderer
        self.tømTre()                                                                                     #Kjører funksjonen for å tømme treet
        self.oppdaterKolonner(("Ordrenummer", "Ordre dato", "Dato sendt", "Betalt Dato", "Kundenummer"))  #Oppdaterer kolonnene
        data = self.db.fetch_all("SELECT * FROM ordre;")                                                  #Henter data fra databasen
        for i in data:                                                                                    #Henter dataene som ligger i data
            self.tree.insert("", "end", values=i)                                                         #Setter inn data i treet

    @sikkerhetsSjekk
    def visInfoOmOrdre(self, ordreNr):                                                              #Funksjon som tar ett parameter som er ordrenummeret den skal hente informasjon om
        self.tømTre()                                                                               #Kjører funksjonen for å tømme treet
        self.oppdaterKolonner(("Ordrenummer", "Varenummer", "Enhetspris", "Antall"))                #Oppdaterer kolonnene
        data = self.db.fetch_all("SELECT * FROM ordrelinje WHERE OrdreNr = %s;", (ordreNr,))        #Henter data fra databasen med beskyttet parameter for SQL-injeksjon
        for i in data:                                                                              #Henter dataene som ligger i data
            self.tree.insert("", "end", values=i)                                                   #Setter inn data i treet

    @sikkerhetsSjekk
    def påTreKlikk(self, _):                                                                        #Funksjon som kjøres når du dobbeltklikker på et element i treeview-en
        selected_item = self.tree.selection()                                                       #Lagrer valget ditt (klikket ditt) i variablen selected_item
        if not selected_item:                                                                       #En if statement som kjører dersom du ikke velger noe/klikker på et tomt element
            messagebox.showwarning("Ingen valgt", "Vennligst velg en ordre.")                       #Ber bruker om å velge en ordre og kommer opp som en messagebox/varsel
            return                                                                                  #Avslutter funksjonen

        ordreNr = self.tree.item(selected_item[0], "values")[0]                                     #Lagrer ordrenummeret brukeren har klikket på

        # Lager nytt vindu for ordre detaljer
        details_window = tk.Toplevel(self.root)                                                     #Lager popupvindu
        details_window.title(f"Ordre detaljer - OrdreNr: {ordreNr}")                                #Setter navn på popupvindu basert på ordrenummer
        details_window.geometry("1000x400")                                                         #Setter størrelse på popupvinduet

        # Legge til kundeinfo i ordrevindu
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
        details_tree["columns"] = ("Varenummer", "Enhetspris", "Antall", "Sum")                     #Setter inn kolonner
        for col in details_tree["columns"]:                                                         #for loop som den kjører gjennom
            details_tree.heading(col, text=col)                                                     #Setter overskrift
            details_tree.column(col, width=100, anchor="center")                                    #Forteller at kolonnen skal være 100px bred og midtstilt
        
        data = self.db.fetch_all("SELECT VNr, PrisPrEnhet, Antall, PrisPrEnhet*Antall as Sum FROM ordrelinje WHERE OrdreNr = %s;", (ordreNr,))        #Henter fra ordrenummer variabelen ordrenummer og er beskyttet mot SQL injeksjon
        for i in data:                                                                                                                                #Henter dataene som ligger i data
            details_tree.insert("", "end", values=i)                                                                                                  #Legger til verdiene som er hentet fra databasen
 
        #Legge til label for totalsum
        Totalsum = 0                                                                                #Variabel som lages for å ha en plass å lagre informasjon i forloopen
        for i in data:                                                                              #Forloop for å velge alle elementene i ordren
            Totalsum += i[3]                                                                        #Kode for å gå gjennom elementene i kolonnen sum (den 4 kolonnen, den skrives som 3 da det telles fra 0) og legge dem sammen
        Totalsumlabel = tk.Label(details_window, text = f"Totalsum: {Totalsum}")                    #Her lager vi label som vi kaller Totalsumlabel, den viser innholdet i utregningen over
        Totalsumlabel.pack(pady = 100)                                                              #Her definierer vi hvor labelen skal være i visningsvinduet

    @sikkerhetsSjekk
    def printPdf(self):                                                                             #Funksjon for å printe PDF faktura - valgfri oppgave. 
        selected_item = self.tree.selection()                                                       #Variabel for å lagre valget brukeren gjør
        if not selected_item:                                                                       #If statement som kjører hvis man ikke har valgt noe
            messagebox.showwarning("Ingen valgt", "Vennligst velg en ordre å skrive ut.")           #Oppretter messagebox/advarsel dersom man ikke har gjort noen valg eller velger et tomt element
            return                                                                                  #Avslutter funksjonen

        ordreNr = self.tree.item(selected_item[0], "values")[0]                                                                                                                    #Variabel som lagrer ordrenummeret for faktura som vi skal skrive ut
        ordrelinjer = self.db.fetch_all("SELECT ordrelinje.*, vare.betegnelse FROM ordrelinje JOIN vare ON ordrelinje.VNr = vare.VNr WHERE ordrelinje.ordreNr = %s;", (ordreNr,))  #Henter ordrelinjer fra databasen med beskyttet parameter for SQL-injeksjon.
        ordre = self.db.fetch_one("SELECT * FROM ordre WHERE OrdreNr = %s;", (ordreNr,))                                                                                           #Henter ordre data fra databasen med beskyttet parameter for SQL-injeksjon.
        kunde = self.db.fetch_one("SELECT * FROM kunde WHERE knr = %s;", (ordre[4],))                                                                                              #Henter kunde data fra databasen med beskyttet parameter for SQL-injeksjon.
        faktura_nummer = self.db.insert_faktura(ordre[0],kunde[0])                                                                                                                 #Lager faktura i databasen med ordrenummer og kundenummer.
        #print(f"faktura_nummer: {faktura_nummer}")                                                                                                                                #debugging print, vi lar denne stå for å vise hvordan vi jobbet med å finne rett måte å velge rett index.
        #print(f"ordre {ordre},ordrelinje {ordrelinjer}, kunde {kunde}")                                                                                                           #debugging print, vi lar denne stå for å vise hvordan vi jobbet med å finne rett måte å velge rett index.
        pdfgen = PDFGenerator()                                                                                                                                                    #Initialiserer/kjører PDF-generatoren
        pdfgen.generate_invoice(ordre,ordrelinjer,kunde,faktura_nummer)                                                                                                            #Genererer PDF med informasjon lagret i variablene over

    @sikkerhetsSjekk    
    def hentAlleKunder(self):                                                                               #Funksjon for å se kundedb med stored procedures
        #Lager nytt vindu for alle kunder
        kunde_window = tk.Toplevel(self.root)                                                               #Lager popupvindu
        kunde_window.title("Kunde")                                                                         #Setter navn på popupvindu basert på ordrenummer
        kunde_window.geometry("1080x400")                                                                   #Setter størrelse på popupvinduet
        #Knapper
        LeggTilKunde = tk.Button(kunde_window, text="Legg til kunde", command=lambda: self.opprettKunde())  #Lager knapp som heter "Legg til kunde" og kjører funksjonen insert_kunde() i db.py
        LeggTilKunde.pack(pady=10)                                                              
        AdministrerKunde = tk.Button(kunde_window, text="Administrer kunde", command=lambda: self.administrerKundeVindu())  #Lager knapp som heter "Administrer kunde" og kjører funksjonen update_kunde() i db.py
        AdministrerKunde.pack(pady=10) 
                                                              
        # Treeview kundedetaljer detaljer
        self.kunde_tree = ttk.Treeview(kunde_window, show="headings")                                       #Lager Treeview for å vise ordre detaljer
        self.kunde_tree.pack(fill="both", expand=True, padx=10, pady=10, side="left")                       #Setter størrelse og plassering i GUI. 

        # Legger til scrollbar for Treeview i nytt vindu
        kunde_vsb = ttk.Scrollbar(kunde_window, orient="vertical", command=self.kunde_tree.yview)           #Lager Treeview for å vise ordre detaljer i nytt vindu
        kunde_vsb.pack(side="right", fill="y")                                                              #Setter størrelse og plassering i GUI.
        self.kunde_tree.configure(yscrollcommand=kunde_vsb.set)                                             #Kobler sammen treet og scrollbaren

        # Henter kunder
        self.kunde_tree["columns"] = ("Kundenummer", "Fornavn", "Etternavn", "Adresse", "Post Nummer")      #Setter inn kolonner
        for col in self.kunde_tree["columns"]:                                                              #for loop som den kjører gjennom
            self.kunde_tree.heading(col, text=col)                                                          #Setter overskrift
            self.kunde_tree.column(col, width=100, anchor="center")                                         #Forteller at kolonnen skal være 100px bred og midtstilt
                                                                                                            #Kaller på funksjonen som henter alle kunder fra databasen
        data = self.db.call_procedure("hent_alle_kunder")                                                   #Henter data fra databasen med følgende store procedures: "SELECT * FROM varehusdb.kunde;"
        for i in data:                                                                                      #Henter dataene som ligger i variablen data
            self.kunde_tree.insert("", "end", values=i)  
                     
    def omVindu(self):                                                                                                                  #Funksjon for å vise informasjon om programmet
        # Lager nytt vindu for å vise informasjon om programmet
        about_window = tk.Toplevel(self.root)                                                                                           #Lager popupvindu
        about_window.title("Om programmet")                                                                                             #Setter navn på popupvindu
        about_window.geometry("300x200")                                                                                                #Setter størrelse på popupvinduet
        about_label = tk.Label(about_window, text="Tverrfaglig prosjekt\nGruppe 1\nLaget av:\nCharlotte, Knut, Truls og Øyvind")        #Lager tekst i vinduet                                          
        about_label.pack(pady=20)                                                                                                       #Setter plassering i vinduet
        close_button = tk.Button(about_window, text="Lukk", command=about_window.destroy)                                               #Lager lukkeknapp i vinduet    
        close_button.pack(padx=10)                                                                                                      #Setter lukkeknapp i vinduet

    def administrerKundeVindu(self):                                                                      #Funksjon for å se kundedb med stored procedures
        selected_item = self.kunde_tree.selection()                                                       #Lagrer valget ditt (klikket ditt) i variablen selected_item
        if not selected_item:                                                                             #En if statement som kjører dersom du ikke velger noe/klikker på et tomt element
            messagebox.showwarning("Ingen valgt", "Vennligst velg en kunde.")
            return                                                                                 
        
        #Lager nytt vindu for ordre detaljer
        self.kunde_window = tk.Toplevel(self.root)                                                        #Lager popupvindu
        self.kunde_window.title("Kunde")                                                                  #Setter navn på popupvindu basert på ordrenummer
        self.kunde_window.geometry("1080x400") 
        self.kunde_window.columnconfigure(0, minsize=5)
        self.kunde_window.columnconfigure(1, weight=1)
        self.kunde_window.rowconfigure(1, minsize=5)
        self.kunde_window.rowconfigure(2, minsize=5)
        self.kunde_window.rowconfigure(0, minsize=5)
        self.kunde_window.rowconfigure(3, minsize=5)                                                                 
        self.kunde_window.rowconfigure(4, minsize=5)
        self.kunde_window.rowconfigure(5, minsize=5)
        self.kunde_window.rowconfigure(6, minsize=5)        

        self.labelkundenummer = tk.Label(self.kunde_window, text="Kundenummer: ")                                     #Setter navn på labelen i vinduet
        self.labelkundenummer.grid(row=0, column=0, padx=10, pady=10, sticky="e")                                     #Pakker og plasserer labelen i vinduet
        self.kundenummer_box = tk.Entry(self.kunde_window)                                                            #Lager entryboks for kundenummer
        self.kundenummer_box.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")                                   #Pakker og plasserer labelen i vinduet   
        self.kundenummer_box.insert(0,self.kunde_tree.item(selected_item[0], "values")[0])                            #Pakker det hele sammen. Vi velger også å vise kundedataene til venstre i visningsvinduet
        
        self.labelFornavn = tk.Label(self.kunde_window, text="Fornavn: ")
        self.labelFornavn.grid(row=1, column=0, padx=10, pady=10, sticky="e")                                         #Setter størrelse på popupvinduet
        self.fornavn_box = tk.Entry(self.kunde_window)                                                                #Lager entryboks for fornavn
        self.fornavn_box.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")  
        self.fornavn_box.insert(0,self.kunde_tree.item(selected_item[0], "values")[1])                                #Pakker det hele sammen. Vi velger også å vise kundedataene til venstre i visningsvinduet
        
        self.labelEtternavn = tk.Label(self.kunde_window, text="Etternavn: ")
        self.labelEtternavn.grid(row=2, column=0, padx=10, pady=10, sticky="e")
        self.etternavn_box = tk.Entry(self.kunde_window)                                                              #Lager entryboks for etternavn
        self.etternavn_box.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")                                     #Pakker det hele sammen. Vi velger også å vise kundedataene til venstre i visningsvinduet
        self.etternavn_box.insert(0,self.kunde_tree.item(selected_item[0], "values")[2] )                             #Pakker det hele sammen. Vi velger også å vise kundedataene til venstre i visningsvinduet
        
        self.labelAdresse = tk.Label(self.kunde_window, text="Adresse: ")
        self.labelAdresse.grid(row=3, column=0, padx=10, pady=10, sticky="e")
        self.addresse_box = tk.Entry(self.kunde_window)                                                               #Lager entryboks for adresse
        self.addresse_box.grid(row=3, column=1, padx=10, pady=10, sticky="nsew")                                      #Pakker det hele sammen. Vi velger også å vise kundedataene til venstre i visningsvinduet
        self.addresse_box.insert(0,self.kunde_tree.item(selected_item[0], "values")[3])                               #Pakker det hele sammen. Vi velger også å vise kundedataene til venstre i visningsvinduet
        
        self.laberlPostnr = tk.Label(self.kunde_window, text="Postnummer: ")
        self.laberlPostnr.grid(row=4, column=0, padx=10, pady=10, sticky="e")                                         #Setter størrelse på popupvinduet
        self.postnr_box = tk.Entry(self.kunde_window)                                                                 #Lager entryboks for postnummer
        self.postnr_box.grid(row=4, column=1, padx=10, pady=10, sticky="nsew")                                        #Pakker det hele sammen. Vi velger også å vise kundedataene til venstre i visningsvinduet
        self.postnr_box.insert(0,self.kunde_tree.item(selected_item[0], "values")[4] )                                #Pakker det hele sammen. Vi velger også å vise kundedataene til venstre i visningsvinduet
        
        self.SlettKunde = tk.Button(self.kunde_window, text="Slett kunde", bg="red", fg="white", command=lambda: self.slettKunde())  #Lager knapp som heter "Slett kunde" og kjører funksjonen delete_kunde() i db.py
        self.SlettKunde.grid(row=6, column=0, padx=10, pady=10, sticky="nsew")

        self.lagreKunde = tk.Button(self.kunde_window, text="Lagre kunde", command=lambda: self.oppdaterKundeiDb())    #Lager knapp som heter "Lagre kunde" og kjører funksjonen insert_kunde() i db.py
        self.lagreKunde.grid(row=6, column=1, padx=10, pady=10, sticky="nsew")                                         #Pakker det hele sammen. Vi velger også å vise kundedataene til venstre i visningsvinduet

    @sikkerhetsSjekk    
    def oppdaterKundeiDb(self):  #Lager knapp som heter "Lagre kunde" og kjører funksjonen insert_kunde() i db.py
        self.db.update_one("UPDATE kunde SET Fornavn = %s, Etternavn = %s, Adresse = %s, PostNr = %s WHERE KNr = %s;", (self.fornavn_box.get(), self.etternavn_box.get(), self.addresse_box.get(), self.postnr_box.get(), self.kundenummer_box.get()))  #Lager entryboks for fornavn
        #print(f"UPDATE kunde SET Fornavn = {self.fornavn_box.get()}, Etternavn = {self.etternavn_box.get()}, Adresse = {self.addresse_box.get()}, PostNr = {self.postnr_box.get()} WHERE KNr = {self.kundenummer_box.get()};")  #Lager entryboks for fornavn

        self.kunde_tree.delete(*self.kunde_tree.get_children())                                                        #Tømmer kunde_tree før oppdatering
        # Henter kunder
        self.kunde_tree["columns"] = ("Kundenummer", "Fornavn", "Etternavn", "Adresse", "Post Nummer")                 #Setter inn kolonner
        for col in self.kunde_tree["columns"]:                                                                         #for loop som den kjører gjennom
            self.kunde_tree.heading(col, text=col)                                                                     #Setter overskrift
            self.kunde_tree.column(col, width=100, anchor="center")                                                    #Forteller at kolonnen skal være 100px bred og midtstilt
        
        data = self.db.call_procedure("hent_alle_kunder")                                                              #Henter data fra databasen med følgende store procedures: "SELECT * FROM varehusdb.kunde;"
        for i in data:                                                                                                 #Henter dataene som ligger i variablen data
            self.kunde_tree.insert("", "end", values=i)  
        
        #slette kunde
        self.slettKunde(self)
        self.kunde_window.destroy()                                                                                    #Lukker vinduet etter oppdatering

    def opprettKunde(self):                                                                                            #Funksjon for å se kundedb med stored procedures
        #Lager nytt vindu for ordre detaljer
        self.kunde_window = tk.Toplevel(self.root)                                                                     #Lager popupvindu
        self.kunde_window.title("Kunde")                                                                               #Setter navn på popupvindu basert på ordrenummer
        self.kunde_window.geometry("1080x400") 
        self.kunde_window.columnconfigure(0, minsize=5)
        self.kunde_window.columnconfigure(1, weight=1)
        self.kunde_window.rowconfigure(1, minsize=5)
        self.kunde_window.rowconfigure(2, minsize=5)
        self.kunde_window.rowconfigure(0, minsize=5)
        self.kunde_window.rowconfigure(3, minsize=5)                                                                   #Setter størrelse på popupvinduet
        self.kunde_window.rowconfigure(4, minsize=5)
        self.kunde_window.rowconfigure(5, minsize=5)
        self.kunde_window.rowconfigure(6, minsize=5)        
                                                                      
        self.labelFornavn = tk.Label(self.kunde_window, text="Fornavn: ")
        self.labelFornavn.grid(row=1, column=0, padx=10, pady=10, sticky="e")                                          #Setter størrelse på popupvinduet
        self.fornavn_box = tk.Entry(self.kunde_window)                                                                 #Lager entryboks for fornavn
        self.fornavn_box.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")  
                                                                      
        self.labelEtternavn = tk.Label(self.kunde_window, text="Etternavn: ")
        self.labelEtternavn.grid(row=2, column=0, padx=10, pady=10, sticky="e")
        self.etternavn_box = tk.Entry(self.kunde_window)                                                                #Lager entryboks for etternavn
        self.etternavn_box.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")                                       #Pakker det hele sammen. Vi velger også å vise kundedataene til venstre i visningsvinduet
        
        self.labelAdresse = tk.Label(self.kunde_window, text="Adresse: ")
        self.labelAdresse.grid(row=3, column=0, padx=10, pady=10, sticky="e")
        self.addresse_box = tk.Entry(self.kunde_window)                                                                 #Lager entryboks for adresse
        self.addresse_box.grid(row=3, column=1, padx=10, pady=10, sticky="nsew")                                        #Pakker det hele sammen. Vi velger også å vise kundedataene til venstre i visningsvinduet
        
        self.laberlPostnr = tk.Label(self.kunde_window, text="Postnummer: ")
        self.laberlPostnr.grid(row=4, column=0, padx=10, pady=10, sticky="e")                                           #Setter størrelse på popupvinduet
        self.postnr_box = tk.Entry(self.kunde_window)                                                                   #Lager entryboks for postnummer
        self.postnr_box.grid(row=4, column=1, padx=10, pady=10, sticky="nsew")                                          #Pakker det hele sammen. Vi velger også å vise kundedataene til venstre i visningsvinduet
        
        self.lagreKunde = tk.Button(self.kunde_window, text="Lagre kunde", command=lambda: self.lagreKundeiDb())        #Lager knapp som heter "Lagre kunde" og kjører funksjonen insert_kunde() i db.py
        self.lagreKunde.grid(row=6, column=1, padx=10, pady=10, sticky="nsew")

    @sikkerhetsSjekk                                                                        
    def lagreKundeiDb(self):  
        self.db.insert_kunde(self.fornavn_box.get(), self.etternavn_box.get(), self.addresse_box.get(), self.postnr_box.get())  #Lager entryboks for fornavn
        self.kunde_window.destroy()                                                         
        self.kunde_tree.delete(*self.kunde_tree.get_children())                                                         #Tømmer kunde_tree før oppdatering
        # Henter kunder
        self.kunde_tree["columns"] = ("Kundenummer", "Fornavn", "Etternavn", "Adresse", "Post Nummer")                  #Setter inn kolonner
        for col in self.kunde_tree["columns"]:                                                                          #for loop som den kjører gjennom
            self.kunde_tree.heading(col, text=col)                                                                      #Setter overskrift
            self.kunde_tree.column(col, width=100, anchor="center")                                                     #Forteller at kolonnen skal være 100px bred og midtstilt
        
        data = self.db.call_procedure("hent_alle_kunder")                                                               #Henter data fra databasen med følgende store procedures: "SELECT * FROM varehusdb.kunde;"
        for i in data:                                                                                                  #Henter dataene som ligger i variablen data
            self.kunde_tree.insert("", "end", values=i) 

    @sikkerhetsSjekk
    def slettKunde(self):                                                                                               #Funksjon for å se kundedb med stored procedures
        if messagebox.askyesnocancel("Slette kunde", "Er du sikker på at du vil slette kunden?"):                       #Oppretter messagebox
            self.db.update_one("UPDATE kunde SET is_active = '0' WHERE KNr = %s;", (self.kundenummer_box.get(),))       #Oppdaterer databasen med slettingen av kundenummeret som er valgt i treeviewen.
            self.kunde_tree.delete(*self.kunde_tree.get_children())                                                     #Tømmer kunde_tree før oppdatering
            # Henter kunder
            self.kunde_tree["columns"] = ("Kundenummer", "Fornavn", "Etternavn", "Adresse", "Post Nummer")              #Setter inn kolonner
            for col in self.kunde_tree["columns"]:                                                                      #for loop som den kjører gjennom
                self.kunde_tree.heading(col, text=col)                                                                  #Setter overskrift
                self.kunde_tree.column(col, width=100, anchor="center")                                                 #Forteller at kolonnen skal være 100px bred og midtstilt
            
            data = self.db.call_procedure("hent_alle_kunder")                                                           #Henter data fra databasen med følgende store procedures: "SELECT * FROM varehusdb.kunde;"
            for i in data:                                                                                              #Henter dataene som ligger i variablen data
                self.kunde_tree.insert("", "end", values=i)  
            self.kunde_window.destroy()

GUI()  #Starter GUI
