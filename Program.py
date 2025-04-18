import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from database.database_program import Database
from pdf_generator import PDFGenerator

class GUI:
    def __init__(self):
        self.root = tk.Tk()  #Oppretter hovedvinduet
        self.root.geometry("800x1000")  #Setter størrelsen på vinduet
        self.root.title("Tverrfaglig prosjekt")  #Setter tittelen på vinduet
        self.root.columnconfigure(0, weight=1)  #Konfigurerer kolonne 0
        self.root.columnconfigure(1, weight=1)  #Konfigurerer kolonne 1
        self.root.columnconfigure(2, weight=1)  #Konfigurerer kolonne 2
        self.root.columnconfigure(3, weight=1)  #Konfigurerer kolonne 3
        self.root.columnconfigure(4, weight=0)  #Konfigurerer kolonne 4
        
        self.root.rowconfigure(1, weight=1)  #Konfigurerer rad 1

        #Oppretter knapper med tilhørende kommandoer
        buttons = {
            "Vis varer på lager": self.hentVarerPåLager,
            "Vis alle ordre": self.hentAlleOrdrer,
            "Vis alle kunder": self.hentAlleKunder,
            "Avslutt": self.terminate
        }
        for i, (text, command) in enumerate(buttons.items()):
            button = tk.Button(master=self.root, text=text, font=("Arial", 14), command=command)
            button.grid(row=0, column=i, sticky="ew")  #Plasserer knappene i grid

        #Oppretter tre for å vise data
        self.tree = ttk.Treeview(self.root, show="headings")
        self.tree.grid(row=1, column=0, columnspan=5, padx=10, pady=10, sticky="nsew")
        self.vsb = ttk.Scrollbar(self.root, orient="vertical", command=self.tree.yview)
        self.vsb.grid(row=1, column=5, sticky="ns", padx=(0, 10))
        self.tree.configure(yscrollcommand=self.vsb.set)
        self.tree.bind("<Double-1>", self.påTreKlikk)  #Binder dobbeltklikk til funksjonen påTreKlikk

        self.db = Database()  #Initialiserer databaseobjektet

        self.root.protocol("WM_DELETE_WINDOW", self.terminate)  #Håndterer lukking av vinduet
        self.root.mainloop()  #Starter hovedløkken

    def terminate(self):
        if messagebox.askyesno("Avslutt", "Er du sikker på at du vil avslutte?"): #Spør om brukeren er sikker
            self.root.destroy()  #Lukker vinduet

    def tømTre(self):
        for i in self.tree.get_children():
            self.tree.delete(i)  #Tømmer tre

    def oppdaterKolonner(self, kolonner):
        self.tree["columns"] = kolonner  #Oppdaterer kolonnene i tre
        for col in kolonner:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="center")

    def hentVarerPåLager(self):
        self.tømTre()  
        self.oppdaterKolonner(("varenummer", "Betegnelse", "Pris", "Antall"))  #Oppdaterer kolonnene
        data = self.db.fetch_all("SELECT * FROM vare WHERE antall > 0 ORDER BY antall DESC;")  # Henter data fra databasen
        for i in data:
            self.tree.insert("", "end", values=i)  #Setter inn data i tre

    def hentAlleOrdrer(self):
        self.tømTre()  
        self.oppdaterKolonner(("Ordrenummer", "Ordre dato", "Dato sendt", "Betalt Dato", "Kundenummer"))  #Oppdaterer kolonnene
        data = self.db.fetch_all("SELECT * FROM ordre;")  #Henter data fra databasen
        for i in data:
            self.tree.insert("", "end", values=i)  #Setter inn data i tre

    def visInfoOmOrdre(self, ordreNr):
        self.tømTre()  
        self.oppdaterKolonner(("Ordrenummer", "Varenummer", "Enhetspris", "Antall"))  #Oppdaterer kolonnene
        data = self.db.fetch_all("SELECT * FROM ordrelinje WHERE OrdreNr = %s;", (ordreNr,))  #Henter data fra databasen med beskyttet parameter for SQL-injeksjon.
        for i in data:
            self.tree.insert("", "end", values=i)  #Setter inn data i tre

    def påTreKlikk(self, _):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Ingen valgt", "Vennligst velg en ordre.")
            return

        ordreNr = self.tree.item(selected_item[0], "values")[0]

        # Lager nytt vindu for ordre detaljer
        details_window = tk.Toplevel(self.root)
        details_window.title(f"Ordre detaljer - OrdreNr: {ordreNr}")
        details_window.geometry("600x400")

        # Legger til en knapp for å generere faktura
        generate_invoice_button = tk.Button(details_window, text="Generer faktura", command=lambda: self.printPdf())
        generate_invoice_button.pack(pady=10)

        # Lager Treeview for å vise ordre detaljer
        details_tree = ttk.Treeview(details_window, show="headings")
        details_tree.pack(fill="both", expand=True, padx=10, pady=10, side="left")

        # Legger til scrollbar for Treeview
        details_vsb = ttk.Scrollbar(details_window, orient="vertical", command=details_tree.yview)
        details_vsb.pack(side="right", fill="y")
        details_tree.configure(yscrollcommand=details_vsb.set)

        # Henter data for ordre detaljer
        details_tree["columns"] = ("Ordrenummer", "Varenummer", "Enhetspris", "Antall")
        for col in details_tree["columns"]:
            details_tree.heading(col, text=col)
            details_tree.column(col, width=100, anchor="center")

        data = self.db.fetch_all("SELECT * FROM ordrelinje WHERE OrdreNr = %s;", (ordreNr,))
        for i in data:
            details_tree.insert("", "end", values=i)
 
    def printPdf(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Ingen valgt", "Vennligst velg en ordre å skrive ut.")
            return

        ordreNr = self.tree.item(selected_item[0], "values")[0]
        ordrelinjer = self.db.fetch_all("SELECT ordrelinje.*, vare.betegnelse FROM ordrelinje JOIN vare ON ordrelinje.VNr = vare.VNr WHERE ordrelinje.ordreNr = %s;", (ordreNr,))  #Henter ordrelinjer fra databasen med beskyttet parameter for SQL-injeksjon.
        ordre = self.db.fetch_one("SELECT * FROM ordre WHERE OrdreNr = %s;", (ordreNr,)) #Henter ordre data fra databasen med beskyttet parameter for SQL-injeksjon.
        kunde = self.db.fetch_one("SELECT * FROM kunde WHERE knr = %s;", (ordre[4],))  #Henter kunde data fra databasen med beskyttet parameter for SQL-injeksjon.
        #print(f"ordre {ordre},ordrelinje {ordrelinjer}, kunde {kunde}") #debugging print
        pdfgen = PDFGenerator() #Initialiserer PDF-generatoren
        pdfgen.generate_invoice(ordre,ordrelinjer,kunde)  #Genererer PDF
    
    def hentAlleKunder(self):
        self.tømTre() 
        self.oppdaterKolonner(("Kundenummer", "Fornavn", "Etternavn", "Adresse", "Post Nummer"))  #Oppdaterer kolonnene
        data = self.db.call_procedure("hent_alle_kunder")  #Henter data fra databasen
        for i in data:
            self.tree.insert("", "end", values=i)

GUI()  #Starter GUI
