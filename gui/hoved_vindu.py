# gui/hoved_vindu.py
# (Viser hele filen for enkel kopiering)
import tkinter as tk
from tkinter import font, messagebox
import logging
from decimal import Decimal

# --- Importer med fallback for linter ---
try:
    from gui.order_view import vis_ordrer
    from gui.kunde_vindu import vis_kunder
    from gui.vare_vindu import vis_varer
except ImportError as e:
    logging.error(f"Kunne ikke importere GUI-moduler: {e}. Funksjonalitet vil mangle.", exc_info=True)
    messagebox.showerror("Importfeil", f"Kunne ikke importere GUI-modul: {e}\nSjekk filstruktur.")
    def vis_ordrer(main_window): messagebox.showerror("Feil", "Ordre-modul ikke lastet.")
    def vis_kunder(main_window): messagebox.showerror("Feil", "Kunde-modul ikke lastet.")
    def vis_varer(main_window): messagebox.showerror("Feil", "Vare-modul ikke lastet.")

try:
    from handlers.database_handler import DatabaseHandler
except ImportError as e:
     logging.error(f"Kunne ikke importere DatabaseHandler: {e}.", exc_info=True)
     messagebox.showerror("Importfeil", f"Kunne ikke importere DatabaseHandler: {e}\nSjekk filstruktur.")
     class DatabaseHandler: # Dummy klasse
         def __init__(self): raise ImportError("DatabaseHandler ikke lastet")

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry("1000x600")
        self.root.title("Tverrfaglig prosjekt")
        try:
            self.db = DatabaseHandler()
        except Exception as init_db_err:
             logging.critical(f"KRITISK FEIL ved init av DatabaseHandler: {init_db_err}", exc_info=True)
             messagebox.showerror("Databasefeil", f"Kunne ikke koble til databasen ved oppstart: {init_db_err}\nApplikasjonen avsluttes.")
             self.root.destroy()
             return

        self.link_font = font.Font(family="Arial", size=10, underline=True)
        self.breadcrumb_text = tk.Text(
            self.root, height=1, bd=0, relief="flat", font=("Arial", 10, "italic"),
            cursor="arrow", takefocus=0, background=self.root.cget('bg')
        )
        self.breadcrumb_text.pack(fill="x", side="top", padx=10, pady=(5, 0))
        self.breadcrumb_text.config(state="disabled")
        self.innhold_frame = tk.Frame(self.root)
        self.innhold_frame.pack(fill="both", expand=True)
        self.status_label = tk.Label(self.root, text="Klar", anchor="w")
        self.status_label.pack(fill="x", side="bottom", padx=5)

        self.navigasjon_map = {
            "Hoved": self.vis_startside,
            "Ordre": lambda: vis_ordrer(self),
            "Kunder": lambda: vis_kunder(self),
            "Varelager": lambda: vis_varer(self)
        }
        self.lag_meny()
        try:
            self.vis_startside()
        except Exception as initial_load_err:
             logging.error(f"Feil ved første kall til vis_startside: {initial_load_err}", exc_info=True)
             messagebox.showerror("Oppstartsfeil", f"Kunne ikke laste startsiden: {initial_load_err}")
        self.root.protocol("WM_DELETE_WINDOW", self.avslutt)

    def oppdater_navigasjon(self, sti_liste):
        try:
            self.breadcrumb_text.config(state="normal")
            self.breadcrumb_text.delete("1.0", "end")
            for i, sti_del in enumerate(sti_liste):
                if i > 0: self.breadcrumb_text.insert("end", " > ")
                tag_navn = f"nav_{sti_del.replace(' ', '_')}_{i}"
                start_index = self.breadcrumb_text.index("end-1c")
                self.breadcrumb_text.insert("end", sti_del)
                end_index = self.breadcrumb_text.index("end-1c")
                if i < len(sti_liste) - 1 and sti_del in self.navigasjon_map:
                    self.breadcrumb_text.tag_add(tag_navn, start_index, end_index)
                    self.breadcrumb_text.tag_config(tag_navn, foreground="blue", font=self.link_font, underline=True)
                    nav_func = self.navigasjon_map[sti_del]
                    self.breadcrumb_text.tag_bind(tag_navn, "<Button-1>", lambda e, func=nav_func: MainWindow._on_breadcrumb_click(func))
                    self.breadcrumb_text.tag_bind(tag_navn, "<Enter>", lambda e: self.breadcrumb_text.config(cursor="hand2"))
                    self.breadcrumb_text.tag_bind(tag_navn, "<Leave>", lambda e: self.breadcrumb_text.config(cursor="arrow"))
                else:
                    self.breadcrumb_text.tag_add(tag_navn, start_index, end_index)
                    self.breadcrumb_text.tag_config(tag_navn, foreground="black", font=("Arial", 10, "italic"), underline=False)
            self.breadcrumb_text.config(state="disabled")
        except tk.TclError as tcl_err:
             logging.warning(f"TclError i oppdater_navigasjon (ignorerer): {tcl_err}")
        except Exception as nav_err:
             logging.error(f"Uventet feil i oppdater_navigasjon: {nav_err}", exc_info=True)

    @staticmethod
    def _on_breadcrumb_click(navigasjons_funksjon):
        if navigasjons_funksjon:
            try: navigasjons_funksjon()
            except Exception as e_nav:
                 logging.error(f"Feil ved navigering fra breadcrumb: {e_nav}", exc_info=True)
                 messagebox.showerror("Navigasjonsfeil", f"Kunne ikke navigere: {e_nav}")
        return "break"

    def lag_meny(self):
        menylinje = tk.Menu(self.root)
        self.root.config(menu=menylinje)
        filmeny = tk.Menu(menylinje, tearoff=0)
        filmeny.add_command(label="Startside", command=self.vis_startside)
        filmeny.add_separator()
        filmeny.add_command(label="Avslutt", command=self.avslutt)
        menylinje.add_cascade(label="Fil", menu=filmeny)
        vis_meny = tk.Menu(menylinje, tearoff=0)
        vis_meny.add_command(label="Kunder", command=lambda: vis_kunder(self))
        vis_meny.add_command(label="Ordrer", command=lambda: vis_ordrer(self))
        vis_meny.add_command(label="Varelager", command=lambda: vis_varer(self))
        menylinje.add_cascade(label="Vis", menu=vis_meny)
        hjelpmeny = tk.Menu(menylinje, tearoff=0)
        hjelpmeny.add_command(label="Om", command=MainWindow.vis_om) # Kall statisk metode
        menylinje.add_cascade(label="Hjelp", menu=hjelpmeny)

    def rydd_innhold(self):
        for widget in self.innhold_frame.winfo_children(): widget.destroy()

    def vis_startside(self):
        self.oppdater_navigasjon(["Hoved"])
        self.rydd_innhold()
        self.status_label.config(text="Henter oversikt...")
        try:
            # --- ENDRET HER: Fjernet WHERE is_active = 1 ---
            antall_kunder_tuple = self.db.hent_en("SELECT COUNT(*) FROM kunde;")
            antall_kunder = antall_kunder_tuple[0] if antall_kunder_tuple else 0
            # --- Slutt på endring ---

            antall_ordrer_tuple = self.db.hent_en("SELECT COUNT(*) FROM ordre;")
            antall_ordrer = antall_ordrer_tuple[0] if antall_ordrer_tuple else 0

            total_sum_tuple = self.db.hent_en("SELECT SUM(PrisPrEnhet * Antall) FROM ordrelinje;")
            total_sum = Decimal(total_sum_tuple[0]) if total_sum_tuple and total_sum_tuple[0] is not None else Decimal('0.00')

        except Exception as e_start:
            logging.error(f"Feil ved henting av oversikt for startside: {e_start}", exc_info=True)
            messagebox.showerror("Feil", f"Kunne ikke hente oversikt: {e_start}")
            self.status_label.config(text="Feil ved lasting av oversikt")
            return

        tk.Label(self.innhold_frame, text="Velkommen!", font=("Arial", 18)).pack(pady=10)
        # --- ENDRET HER: Fjernet "aktive" fra label ---
        tk.Label(self.innhold_frame, text=f"Antall kunder: {antall_kunder}").pack(pady=5)
        # --- Slutt på endring ---
        tk.Label(self.innhold_frame, text=f"Totalt antall ordre: {antall_ordrer}").pack(pady=5)
        tk.Label(self.innhold_frame, text=f"Total ordreverdi: {total_sum:.2f} kr").pack(pady=5)

        knapp_frame = tk.Frame(self.innhold_frame)
        knapp_frame.pack(pady=20)
        knapper = [
            ("Gå til Ordrer", lambda: vis_ordrer(self)),
            ("Gå til Kunder", lambda: vis_kunder(self)),
            ("Gå til Varelager", lambda: vis_varer(self))
        ]
        for tekst, kommando in knapper:
            btn = tk.Button(knapp_frame, text=tekst, command=kommando, width=20, height=2)
            btn.pack(side="left", padx=10, pady=5)
        self.status_label.config(text="Oversikt lastet")

    @staticmethod
    def vis_om():
        messagebox.showinfo("Om", "Tverrfaglig prosjekt - Varehus App\n\nLaget av Gruppe X\n(Rediger gjerne denne teksten)")

    def avslutt(self):
        if messagebox.askyesno("Avslutt", "Er du sikker på at du vil avslutte?"):
            logging.info("Applikasjon avsluttet av bruker.")
            self.root.destroy()

    def run(self):
        if hasattr(self, 'root') and self.root and self.root.winfo_exists():
             logging.info("Starter Tkinter mainloop.")
             try: self.root.mainloop()
             except Exception as mainloop_err:
                  logging.critical(f"Kritisk feil i Tkinter mainloop: {mainloop_err}", exc_info=True)
        else:
             logging.error("Kunne ikke starte Tkinter mainloop fordi root-vindu ikke finnes eller init feilet.")

__all__ = ["MainWindow"]