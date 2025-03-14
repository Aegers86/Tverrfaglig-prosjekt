# gui.py
import tkinter as tk
from tkinter import messagebox, ttk
from database import Database
from pdf_generator import PDFGenerator
from config import COLUMN_WIDTHS

class GUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry("960x600")
        self.root.resizable(False, False)
        self.root.title("Tverrfaglig prosjekt")

        self.db = Database()
        self.pdf_generator = PDFGenerator()
        self.navigation_status = tk.StringVar()
        self.navigation_status.set("Hjem")
        self.dark_mode = False

        self.sidebar = None
        self.nav_label = None
        self.content_frame = None
        self.table_frame = None
        self.tree = None
        self.vsb = None

        self.setup_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.terminate)

    def setup_ui(self):
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True)

        self.sidebar = tk.Frame(main_frame, width=200, bg="#EAEAEA", relief="raised", borderwidth=2)
        self.sidebar.pack(side="left", fill="y")

        self.content_frame = tk.Frame(main_frame)
        self.content_frame.pack(side="right", fill="both", expand=True)

        self.nav_label = tk.Label(self.content_frame, textvariable=self.navigation_status, font=("Arial", 12), anchor="w")
        self.nav_label.pack(fill="x", padx=10, pady=2)

        self.home_frame = tk.Frame(self.content_frame)
        self.home_frame.pack(padx=10, pady=10, expand=True, fill="both")
        self.display_home()

        self.table_frame = tk.Frame(self.content_frame, width=680, height=400)
        self.table_frame.pack(padx=10, pady=10, expand=True, fill="both")
        self.table_frame.pack_forget()

        self.create_treeview()

        menu_items = [
            ("🏠 Hjem", self.goto_home),
            ("📦 Varer på lager", self.hent_varer_pa_lager),
            ("📜 Ordrer", self.hent_alle_ordrer),
            ("👥 Kunder", self.hent_alle_kunder),
            ("🌙 Dark Mode", self.toggle_theme)
        ]

        for text, command in menu_items:
            btn = tk.Button(self.sidebar, text=text, font=("Arial", 12), bg="#E0E0E0", relief="flat", command=command)
            btn.pack(fill="x", padx=5, pady=5)

        tk.Button(self.sidebar, text="📄 Generer faktura", font=("Arial", 12), bg="#FFD700", command=self.generer_faktura).pack(fill="x", padx=5, pady=10)
        tk.Button(self.sidebar, text="❌ Avslutt", font=("Arial", 12), bg="#FF6347", command=self.terminate).pack(fill="x", padx=5, pady=10)

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        bg_color = "#333333" if self.dark_mode else "#EAEAEA"
        fg_color = "#FFFFFF" if self.dark_mode else "#000000"
        self.sidebar.config(bg=bg_color)
        self.nav_label.config(bg=bg_color, fg=fg_color)
        self.root.config(bg=bg_color)

    def display_home(self):
        for widget in self.home_frame.winfo_children():
            widget.destroy()

        stats = self.db.fetch_one(
            """
            SELECT 
                (SELECT COUNT(*) FROM kunde),
                (SELECT COUNT(*) FROM ordre),
                (SELECT COUNT(*) FROM vare),
                (SELECT COUNT(*) FROM ordre WHERE betalt_dato IS NOT NULL),
                (SELECT COUNT(*) FROM ordre WHERE betalt_dato IS NULL)
            """
        )

        labels = [
            "Totalt antall kunder", "Totalt antall ordrer", "Totalt antall varer", "Betalte fakturaer", "Ubetalte fakturaer"
        ]

        stats_frame = tk.Frame(self.home_frame)
        stats_frame.pack()
        for i, (label, value) in enumerate(zip(labels, stats)):
            tk.Label(stats_frame, text=label, font=("Arial", 10)).grid(row=i, column=0, sticky="w", padx=10, pady=2)
            tk.Label(stats_frame, text=str(value), font=("Arial", 10, "bold")).grid(row=i, column=1, sticky="w", padx=10, pady=2)

    def create_treeview(self):
        self.tree = ttk.Treeview(self.table_frame, show="headings")
        self.tree.pack(expand=True, fill="both")

        self.vsb = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        self.vsb.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=self.vsb.set)

    def goto_home(self):
        self.navigation_status.set("Hjem")
        self.table_frame.pack_forget()
        self.home_frame.pack()
        self.display_home()

    def hent_alle_kunder(self):
        self.display_data(
            "SELECT knr AS KundeNr, fornavn, etternavn, adresse, postnummer AS PostNr, epost FROM kunde;",
            ("KundeNr", "Fornavn", "Etternavn", "Adresse", "PostNr", "Epost"),
            "Hjem > Kunder"
        )

if __name__ == "__main__":
    gui = GUI()
    gui.run()
