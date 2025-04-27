# gui/hoved_vindu.py

import os
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import font, messagebox
import logging
from decimal import Decimal
from datetime import datetime

# Importer de riktige modulene
try:
    from gui.order_view import vis_ordrer
    from gui.kunde_vindu import vis_kunder
    from gui.vare_vindu import vis_varer
    from gui.meny import lag_menylinje
except ImportError as e:
    logging.error(f"Kunne ikke importere GUI-moduler: {e}", exc_info=True)
    def vis_ordrer(main_window): messagebox.showerror("Feil", "Ordre-modul ikke lastet.")
    def vis_kunder(main_window): messagebox.showerror("Feil", "Kunde-modul ikke lastet.")
    def vis_varer(main_window): messagebox.showerror("Feil", "Vare-modul ikke lastet.")
    def lag_menylinje(root, main_window): pass

try:
    from handlers.database_handler import DatabaseHandler
except ImportError as e:
    logging.error(f"Kunne ikke importere DatabaseHandler: {e}", exc_info=True)
    class DatabaseHandler:
        def __init__(self): raise ImportError("DatabaseHandler ikke lastet")

try:
    from utils.gui_helpers import formater_tall_norsk
except ImportError:
    def formater_tall_norsk(verdi, desimaler=2):
        try: return f"{float(str(verdi).replace(',', '.')):.{desimaler}f}".replace('.', ',')
        except: return str(verdi)

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.minsize(width=800, height=500)
        self.root.geometry("1100x650")
        self.root.title("Tverrfaglig prosjekt - Varehus App")

        try:
            self.db = DatabaseHandler()
        except Exception as init_db_err:
            logging.critical(f"KRITISK FEIL ved init av DatabaseHandler: {init_db_err}", exc_info=True)
            messagebox.showerror("Databasefeil", f"Kunne ikke koble til databasen ved oppstart: {init_db_err}\nApplikasjonen avsluttes.")
            self.root.destroy()
            return

        self.link_font = font.Font(family="Arial", size=10, underline=True)
        self._lag_layout()
        self._lag_navigasjonsknapper()
        lag_menylinje(self.root, self)

        try:
            self.vis_startside()
        except Exception as initial_load_err:
            logging.error(f"Feil ved første kall til vis_startside: {initial_load_err}", exc_info=True)
            messagebox.showerror("Oppstartsfeil", f"Kunne ikke laste startsiden: {initial_load_err}")

        self.root.protocol("WM_DELETE_WINDOW", self.avslutt)

    def _lag_layout(self):
        self.top_frame = tk.Frame(self.root)
        self.top_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=(5,0))

        self.bottom_frame = tk.Frame(self.root)
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=(0,5))

        self.nav_frame = tk.Frame(self.root, width=180, bg="#ECECEC", relief=tk.SUNKEN, bd=1)
        self.nav_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(5,0), pady=5)
        self.nav_frame.pack_propagate(False)

        self.innhold_frame = tk.Frame(self.root)
        self.innhold_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.breadcrumb_text = tk.Text(self.top_frame, height=1, bd=0, relief="flat",
                                       font=("Arial", 10, "italic"), cursor="arrow",
                                       takefocus=0, background=self.root.cget('bg'))
        self.breadcrumb_text.pack(fill=tk.X, padx=5)
        self.breadcrumb_text.config(state="disabled")

        self.status_label = tk.Label(self.bottom_frame, text="Klar", anchor="w")
        self.status_label.pack(fill=tk.X)

        self.navigasjon_map = {
            "Hoved": self.vis_startside,
            "Ordre": lambda: vis_ordrer(self),
            "Kunder": lambda: vis_kunder(self),
            "Varelager": lambda: vis_varer(self)
        }

    def _lag_navigasjonsknapp(self, tekst, kommando):
        tk.Button(self.nav_frame, text=tekst, command=kommando, anchor="w",
                  relief=tk.FLAT, font=("Arial", 11), padx=10, bg="#ECECEC",
                  activebackground="#d9d9d9").pack(fill=tk.X, pady=2, padx=5)

    def _lag_navigasjonsknapper(self):
        tk.Label(self.nav_frame, text="Navigasjon", font=("Arial", 12, "bold"), bg="#ECECEC").pack(pady=(10,5))
        tk.Frame(self.nav_frame, height=1, bg="grey").pack(fill=tk.X, padx=5, pady=(0,10))
        for tekst, kommando in self.navigasjon_map.items():
            self._lag_navigasjonsknapp(tekst, kommando)

    def vis_startside(self):
        self.oppdater_navigasjon(["Hoved"])
        self.rydd_innhold()
        self.status_label.config(text="Henter oversikt...")

        try:
            oversikt_frame = tk.Frame(self.innhold_frame)
            oversikt_frame.pack(fill="both", expand=True, padx=10, pady=10)

            antall_kunder = self.db.hent_en("SELECT COUNT(*) FROM kunde;").get("COUNT(*)", 0)
            antall_ordrer = self.db.hent_en("SELECT COUNT(*) FROM ordre;").get("COUNT(*)", 0)
            total_sum_result = self.db.hent_en("SELECT SUM(PrisPrEnhet * Antall) FROM ordrelinje;")
            total_sum = Decimal(total_sum_result.get("SUM(PrisPrEnhet * Antall)", 0)) if total_sum_result else Decimal("0.00")
            verdi_ubetalte = self.db.hent_verdi_ubetalte_ordrer()

            nå = datetime.now()
            antall_ordrer_i_år = self.db.hent_antall_ordrer_per_aar(nå.year)
            antall_ordrer_fjorår = self.db.hent_antall_ordrer_per_aar(nå.year - 1)

            labels = [
                f"Antall kunder: {antall_kunder}",
                f"Antall ordrer: {antall_ordrer}",
                f"Total omsetning: {formater_tall_norsk(total_sum)} kr",
                f"Verdi ubetalte fakturaer: {formater_tall_norsk(verdi_ubetalte)} kr",
                f"Ordrer i år: {antall_ordrer_i_år}",
                f"Ordrer i fjor: {antall_ordrer_fjorår}"
            ]

            for tekst in labels:
                lbl = tk.Label(oversikt_frame, text=tekst, font=("Arial", 12), anchor="w")
                lbl.pack(fill="x", pady=2)

            # --- Tegn salgsgraf ---
            self.vis_salgsgraf(oversikt_frame)

            self.status_label.config(text="Oversikt lastet")

        except Exception as e:
            logging.error(f"Feil ved henting av data for startside: {e}", exc_info=True)
            messagebox.showerror("Feil", f"Kunne ikke hente data for startsiden: {e}")
            self.status_label.config(text="Feil ved lasting av oversikt")

    def vis_salgsgraf(self, parent_frame):
        """ Viser graf over salg siste 7 år som stolpediagram, lagrer i static/ """
        try:
            nå = datetime.now()
            start_år = nå.year - 6
            årstall = list(range(start_år, nå.year + 1))
            salgstall = []

            for år in årstall:
                result = self.db.hent_en(
                    "SELECT SUM(PrisPrEnhet * Antall) as total FROM ordrelinje JOIN ordre ON ordrelinje.OrdreNr = ordre.OrdreNr WHERE YEAR(ordre.OrdreDato) = %s;",
                    (år,)
                )
                total = result.get('total', 0) if result else 0
                salgstall.append(float(total or 0))

            fig = Figure(figsize=(7, 4), dpi=100)
            ax = fig.add_subplot(111)

            # Stolpediagram (ikke linje)
            ax.bar(årstall, salgstall, color='steelblue', width=0.5)

            ax.set_title("Salg siste 7 år")
            ax.set_xlabel("År")
            ax.set_ylabel("Omsetning (kr)")
            ax.grid(axis='y', linestyle='--', alpha=0.7)

            # Formater y-aksen til å vise kr med tusenskilletegn
            from matplotlib.ticker import FuncFormatter
            def tusen_format(x, pos):
                return f"{int(x):,}".replace(",", " ") + " kr"

            ax.yaxis.set_major_formatter(FuncFormatter(tusen_format))

            canvas = FigureCanvasTkAgg(fig, master=parent_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, pady=10)

            os.makedirs("static", exist_ok=True)
            fig.savefig(os.path.join("static", "salg_siste_7_år.png"))
            logging.info("Salgsgraf lagret til static/salg_siste_7_år.png")

        except Exception as e:
            logging.error(f"Feil under generering av salgsgraf: {e}", exc_info=True)
            tk.Label(parent_frame, text="Kunne ikke laste salgsgraf", fg="red").pack(pady=10)

    def oppdater_navigasjon(self, sti_liste):
        try:
            self.breadcrumb_text.config(state="normal")
            self.breadcrumb_text.delete("1.0", "end")
            for i, sti_del in enumerate(sti_liste):
                if i > 0: self.breadcrumb_text.insert("end", " > ")
                tag_navn = f"nav_{i}"
                self.breadcrumb_text.insert("end", sti_del, tag_navn)
            self.breadcrumb_text.config(state="disabled")
        except Exception as e:
            logging.warning(f"Feil i oppdater_navigasjon: {e}", exc_info=True)

    def rydd_innhold(self):
        for widget in self.innhold_frame.winfo_children():
            widget.destroy()

    def avslutt(self):
        if messagebox.askyesno("Avslutt", "Er du sikker på at du vil avslutte?"):
            logging.info("Applikasjon avsluttet av bruker.")
            self.root.destroy()

    def run(self):
        if hasattr(self, 'root') and self.root and self.root.winfo_exists():
            logging.info("Starter Tkinter mainloop.")
            try:
                self.root.mainloop()
            except Exception as mainloop_err:
                logging.critical(f"Kritisk feil i Tkinter mainloop: {mainloop_err}", exc_info=True)
        else:
            logging.error("Kunne ikke starte Tkinter mainloop fordi root-vindu ikke finnes eller init feilet.")
