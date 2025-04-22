# gui/hoved_vindu.py
import tkinter as tk
from tkinter import font # Importer font
from tkinter import messagebox
from gui.order_view import vis_ordrer
from gui.kunde_vindu import vis_kunder
from handlers.database_handler import DatabaseHandler
import logging

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry("1000x600")
        self.root.title("Tverrfaglig prosjekt")
        self.db = DatabaseHandler() # Antar denne fortsatt er gyldig

        # --- Start endring: Bytt ut Label med Text for breadcrumbs ---
        # Lag en font for lenkene
        self.link_font = font.Font(family="Arial", size=10, underline=True)

        # Opprett Text widget istedenfor Label
        self.breadcrumb_text = tk.Text(
            self.root,
            height=1,
            bd=0, # Ingen kantlinje
            relief="flat", # Flat utseende
            font=("Arial", 10, "italic"),
            cursor="arrow", # Standard pilmarkør
            takefocus=0, # Ikke la den få fokus
            background=self.root.cget('bg') # Samme bakgrunn som vinduet
        )
        self.breadcrumb_text.pack(fill="x", side="top", padx=10, pady=(5, 0))
        # Gjør teksten i utgangspunktet ikke-redigerbar
        self.breadcrumb_text.config(state="disabled")
        # --- Slutt endring ---

        self.innhold_frame = tk.Frame(self.root)
        self.innhold_frame.pack(fill="both", expand=True)

        self.status_label = tk.Label(self.root, text="Klar", anchor="w")
        self.status_label.pack(fill="x", side="bottom")

        # Kartlegging fra stinavn til funksjon som viser den visningen
        self.navigasjon_map = {
            "Hoved": self.vis_startside,
            "Ordre": lambda: vis_ordrer(self), # Bruk lambda for å passe signaturen
            "Kunder": lambda: vis_kunder(self) # Bruk lambda for å passe signaturen
            # Legg til flere her hvis du har flere hovednivåer
        }

        self.lag_meny()
        self.vis_startside() # Kaller oppdater_navigasjon internt

        self.root.protocol("WM_DELETE_WINDOW", self.avslutt)


    # --- Start endring: Omskrevet oppdater_navigasjon ---
    def oppdater_navigasjon(self, sti_liste):
        # Gjør widgeten redigerbar midlertidig
        self.breadcrumb_text.config(state="normal")
        self.breadcrumb_text.delete("1.0", "end") # Tøm gammel tekst

        for i, sti_del in enumerate(sti_liste):
            if i > 0:
                # Legg til separator (ikke klikkbar)
                self.breadcrumb_text.insert("end", " > ")

            # Lag en unik tag for denne delen
            tag_navn = f"nav_{sti_del}_{i}" # Inkluderer indeks for unikhet

            # Sett inn tekst for denne delen
            start_index = self.breadcrumb_text.index("end-1c") # Startposisjon for tag
            self.breadcrumb_text.insert("end", sti_del)
            end_index = self.breadcrumb_text.index("end-1c") # Sluttposisjon for tag

            # Gjør alle unntatt den siste delen klikkbar
            if i < len(sti_liste) - 1 and sti_del in self.navigasjon_map:
                self.breadcrumb_text.tag_add(tag_navn, start_index, end_index)
                # Konfigurer utseende og oppførsel for taggen (lenken)
                self.breadcrumb_text.tag_config(tag_navn, foreground="blue", font=self.link_font, underline=True)
                # Bind klikk-hendelse til en handler, send med funksjonen som skal kalles
                # Bruker lambda for å unngå problem med sen binding i loop
                nav_func = self.navigasjon_map[sti_del]
                self.breadcrumb_text.tag_bind(tag_navn, "<Button-1>", lambda e, func=nav_func: self._on_breadcrumb_click(func))
                self.breadcrumb_text.tag_bind(tag_navn, "<Enter>", lambda e: self.breadcrumb_text.config(cursor="hand2")) # Pekefinger-markør
                self.breadcrumb_text.tag_bind(tag_navn, "<Leave>", lambda e: self.breadcrumb_text.config(cursor="arrow")) # Tilbake til pil

        # Gjør widgeten ikke-redigerbar igjen
        self.breadcrumb_text.config(state="disabled")
    # --- Slutt endring ---

    # --- Start NY metode: Handler for klikk på breadcrumb ---
    def _on_breadcrumb_click(self, navigasjons_funksjon):
        # Kaller den lagrede funksjonen som ble sendt med fra tag_bind
        if navigasjons_funksjon:
            try:
                navigasjons_funksjon()
            except Exception as e:
                 logging.error(f"Feil ved navigering fra breadcrumb: {e}", exc_info=True)
                 messagebox.showerror("Navigasjonsfeil", f"Kunne ikke navigere: {e}")
        return "break" # Hindrer standard Text-widget klikk-oppførsel
    # --- Slutt NY metode ---

    def lag_meny(self):
        menylinje = tk.Menu(self.root)
        self.root.config(menu=menylinje)

        filmeny = tk.Menu(menylinje, tearoff=0)
        # Denne kaller allerede riktig funksjon
        filmeny.add_command(label="Startside", command=self.vis_startside)
        filmeny.add_command(label="Avslutt", command=self.avslutt)
        menylinje.add_cascade(label="Fil", menu=filmeny)

        hjelpmeny = tk.Menu(menylinje, tearoff=0)
        hjelpmeny.add_command(label="Om", command=self.vis_om)
        menylinje.add_cascade(label="Hjelp", menu=hjelpmeny)

    def rydd_innhold(self):
        for widget in self.innhold_frame.winfo_children():
            widget.destroy()

    # vis_startside, vis_om, avslutt, run er som før (men vis_startside
    # vil nå bruke den nye oppdater_navigasjon)
    def vis_startside(self):
        # Setter brødsmulestien for denne siden
        self.oppdater_navigasjon(["Hoved"]) # Denne kaller den nye metoden
        self.rydd_innhold() # Fjerner innhold fra forrige visning
        self.status_label.config(text="Henter oversikt...")

        # Hent data fra databasen
        try:
            # Bruk COUNT(*) for å telle kunder direkte i databasen
            antall_kunder_tuple = self.db.hent_en("SELECT COUNT(*) FROM kunde;")
            antall_kunder = antall_kunder_tuple[0] if antall_kunder_tuple else 0

            # Bruk COUNT(*) for å telle ordrer direkte
            antall_ordrer_tuple = self.db.hent_en("SELECT COUNT(*) FROM ordre;")
            antall_ordrer = antall_ordrer_tuple[0] if antall_ordrer_tuple else 0

            # Bruk riktig kolonnenavn fra varehusdb.sql ('PrisPrEnhet', 'Antall')
            total_sum_tuple = self.db.hent_en("SELECT SUM(PrisPrEnhet * Antall) FROM ordrelinje;")
            total_sum = total_sum_tuple[0] if total_sum_tuple and total_sum_tuple[0] is not None else 0.0

        except Exception as e:
            logging.error(f"Feil ved henting av oversikt for startside: {e}", exc_info=True)
            messagebox.showerror("Feil", f"Kunne ikke hente oversikt: {e}")
            self.status_label.config(text="Feil ved lasting av oversikt")
            return # Avslutt hvis data ikke kan hentes

        # --- Koden for å vise innholdet på startsiden (denne manglet sannsynligvis) ---
        tk.Label(self.innhold_frame, text="Velkommen!", font=("Arial", 18)).pack(pady=10)
        tk.Label(self.innhold_frame, text=f"Totalt antall kunder: {antall_kunder}").pack(pady=5)
        tk.Label(self.innhold_frame, text=f"Totalt antall ordre: {antall_ordrer}").pack(pady=5)
        tk.Label(self.innhold_frame, text=f"Total ordreverdi: {total_sum:.2f} kr").pack(pady=5)

        knapp_frame = tk.Frame(self.innhold_frame)
        knapp_frame.pack(pady=20)

        # Knapper for navigasjon
        knapper = [
            ("Gå til ordre", lambda: vis_ordrer(self)), # Bruker importert funksjon
            ("Gå til kunder", lambda: vis_kunder(self)) # Bruker importert funksjon
        ]
        for tekst, kommando in knapper:
            btn = tk.Button(knapp_frame, text=tekst, command=kommando, width=20)
            btn.pack(side="left", padx=10)
        # --- Slutt på koden som viser innhold ---

        self.status_label.config(text="Oversikt lastet")

    def vis_om(self):
        messagebox.showinfo("Om", "Tverrfaglig prosjekt\nLaget av Gruppe 1")

    def avslutt(self):
        if messagebox.askyesno("Avslutt", "Er du sikker på at du vil avslutte?"):
            self.root.destroy()

    def run(self):
        self.root.mainloop()

__all__ = ["MainWindow"]