# gui.py
import tkinter as tk
from tkinter import messagebox, ttk
from database import Database
from pdf_generator import PDFGenerator
from strings import TEXTS  # Importer tekstene

class GUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry("960x600")
        self.root.resizable(False, False)
        self.root.title(TEXTS["title"])

        self.db = Database()
        self.pdf_generator = PDFGenerator()
        self.navigation_status = tk.StringVar()
        self.navigation_status.set(TEXTS["home_title"])
        self.dark_mode = False

        self.sidebar = None
        self.nav_label = None
        self.content_frame = None
        self.table_frame = None
        self.tree_frame = None  # Defineres her
        self.tree = None
        self.vsb = None
        self.hsb = None  # Defineres her
        self.home_frame = None

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
            (TEXTS["home"], self.goto_home),
            (TEXTS["inventory"], self.hent_varer_pa_lager),
            (TEXTS["orders"], self.hent_alle_ordrer),
            (TEXTS["customers"], self.hent_alle_kunder),
            (TEXTS["dark_mode"], self.toggle_theme)
        ]

        for text, command in menu_items:
            btn = tk.Button(self.sidebar, text=text, font=("Arial", 12), bg="#E0E0E0", relief="flat", command=command)
            btn.pack(fill="x", padx=5, pady=5)

        tk.Button(self.sidebar, text=TEXTS["generate_invoice"], font=("Arial", 12), bg="#FFD700", command=self.generer_faktura).pack(fill="x", padx=5, pady=10)
        tk.Button(self.sidebar, text=TEXTS["exit"], font=("Arial", 12), bg="#FF6347", command=self.terminate).pack(fill="x", padx=5, pady=10)

    def toggle_theme(self):
        """Bytter mellom mørk og lys modus og oppdaterer UI."""
        self.dark_mode = not self.dark_mode

        # Farger for mørk og lys modus
        bg_color = "#333333" if self.dark_mode else "#EAEAEA"
        fg_color = "#FFFFFF" if self.dark_mode else "#000000"
        btn_color = "#555555" if self.dark_mode else "#E0E0E0"
        table_bg = "#2E2E2E" if self.dark_mode else "#FFFFFF"
        table_fg = "#FFFFFF" if self.dark_mode else "#000000"
        header_bg = "#444444" if self.dark_mode else "#F0F0F0"  # Bakgrunn for kolonne-headeren
        header_fg = "#FFFFFF" if self.dark_mode else "#000000"

        # Oppdater hovedkomponenter
        self.sidebar.config(bg=bg_color)
        self.nav_label.config(bg=bg_color, fg=fg_color)
        self.root.config(bg=bg_color)

        # Oppdater knappene i sidemenyen
        for widget in self.sidebar.winfo_children():
            if isinstance(widget, tk.Button):
                widget.config(bg=btn_color, fg=fg_color)

        # **Sørg for at "Generer faktura" og "Avslutt" beholder sine farger**
        self.sidebar.winfo_children()[-2].config(bg="#FFD700", fg="#000000")  # Generer faktura
        self.sidebar.winfo_children()[-1].config(bg="#FF6347", fg="#FFFFFF")  # Avslutt-knappen

        # **Oppdater Treeview (tabell)**
        style = ttk.Style()
        style.theme_use("alt")  # Bruk et alternativt tema for å gi bedre kontroll

        style.configure("Treeview",
                        background=table_bg, foreground=table_fg, fieldbackground=table_bg,
                        rowheight=25, font=("Arial", 10))

        style.configure("Treeview.Heading",
                        background=header_bg, foreground=header_fg, font=("Arial", 10, "bold"),
                        relief="flat")

        style.map("Treeview.Heading",
                  background=[("active", header_bg)],
                  foreground=[("active", header_fg)])

    def clear_tree(self):
        """Fjerner alle rader fra tabellen."""
        for item in self.tree.get_children():
            self.tree.delete(item)

    def update_columns(self, columns):
        """Oppdaterer kolonnene i tabellen og sørger for at scrollbarene fungerer."""
        self.tree["columns"] = columns

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor="center", stretch=True)  # Gir nok plass til scrollbarene

        # **Tving scrollbarene til å vises ved behov**
        self.tree.update_idletasks()  # Sikrer at layouten oppdateres umiddelbart
        self.vsb.update_idletasks()
        self.hsb.update_idletasks()

    def display_home(self):
        """Viser nøkkeltall på hjemmesiden."""
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

        stats_frame = tk.Frame(self.home_frame)
        stats_frame.pack()
        for i, (label, value) in enumerate(zip(TEXTS["key_metrics"], stats)):
            tk.Label(stats_frame, text=label, font=("Arial", 10)).grid(row=i, column=0, sticky="w", padx=10, pady=2)
            tk.Label(stats_frame, text=str(value), font=("Arial", 10, "bold")).grid(row=i, column=1, sticky="w", padx=10, pady=2)

    def display_data(self, query, columns, nav_text):
        """Generisk funksjon for å vise data i tabellen uten å ødelegge GUI."""
        self.navigation_status.set(nav_text)

        # Vis tabellen og skjul home-skjermen
        self.home_frame.pack_forget()
        self.table_frame.pack(padx=10, pady=10, expand=True, fill="both")

        self.clear_tree()
        self.update_columns(columns)
        data = self.db.fetch_all(query)

        for row in data:
            self.tree.insert("", "end", values=row)

        # **Tving scrollbarene til å vises ved behov**
        self.tree.update_idletasks()

    def goto_home(self):
        self.navigation_status.set(TEXTS["home_title"])
        self.table_frame.pack_forget()
        self.home_frame.pack()
        self.display_home()

    def hent_varer_pa_lager(self):
        """Viser varer på lager."""
        self.display_data(
            "SELECT varenummer, betegnelse, pris, antall FROM vare WHERE antall > 0 ORDER BY antall DESC;",
            ("Varenummer", "Betegnelse", "Pris", "Antall"),
            TEXTS["inventory_title"]
        )

    def hent_alle_ordrer(self):
        """Viser alle ordrer."""
        self.display_data(
            """
            SELECT o.ordrenummer, o.ordre_dato, o.dato_sendt, o.betalt_dato, CONCAT(k.fornavn, ' ', k.etternavn)
            FROM ordre o JOIN kunde k ON o.kundenummer = k.knr;
            """,
            ("Ordrenummer", "Ordre dato", "Dato sendt", "Betalt Dato", "Kundenavn"),
            TEXTS["orders_title"]
        )

    def hent_alle_kunder(self):
        """Viser alle kunder."""
        self.display_data(
            "SELECT knr AS KundeNr, fornavn, etternavn, adresse, postnummer AS PostNr, epost FROM kunde;",
            ("KundeNr", "Fornavn", "Etternavn", "Adresse", "PostNr", "Epost"),
            TEXTS["customers_title"]
        )

    def generer_faktura(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning(TEXTS["no_selection"], TEXTS["select_order_warning"])
            return

        ordre_nr = self.tree.item(selected_item[0], "values")[0]
        ordrelinjer = self.db.fetch_all("SELECT * FROM ordrelinje WHERE ordreNr = %s;", (ordre_nr,))
        ordre = self.db.fetch_one("SELECT * FROM ordre WHERE ordrenummer = %s;", (ordre_nr,))

        if not ordre:
            messagebox.showerror(TEXTS["error"], TEXTS["order_not_found"])
            return

        kunde = self.db.fetch_one(
            "SELECT knr, fornavn, etternavn, adresse, postnummer, epost FROM kunde WHERE knr = %s;",
            (ordre[4],)
        )

        if not kunde:
            messagebox.showerror(TEXTS["error"], TEXTS["customer_not_found"])
            return

        self.pdf_generator.generate_invoice(ordre, ordrelinjer, kunde)
        messagebox.showinfo(TEXTS["success"], TEXTS["invoice_generated"])

    def terminate(self):
        if messagebox.askyesno(TEXTS["exit"], TEXTS["confirm_exit"]):
            self.root.destroy()

    def create_treeview(self):
        """Oppretter én Treeview-widget med fungerende horisontal og vertikal scrollbar."""
        self.tree_frame = tk.Frame(self.table_frame)
        self.tree_frame.pack(expand=True, fill="both")

        # Opprett Treeview med scrollbars
        self.tree = ttk.Treeview(self.tree_frame, show="headings")

        # Vertikal scrollbar
        self.vsb = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.vsb.set)

        # Horisontal scrollbar
        self.hsb = ttk.Scrollbar(self.tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(xscrollcommand=self.hsb.set)

        # Plasser scrollbars riktig
        self.vsb.pack(side="right", fill="y")
        self.hsb.pack(side="bottom", fill="x")

        # Plasser Treeview på riktig måte
        self.tree.pack(expand=True, fill="both")

        # **Sikre at Treeview fyller plassen riktig**
        self.tree_frame.pack_propagate(False)

    def run(self):
        """Starter GUI."""
        self.root.mainloop()


if __name__ == "__main__":
    gui = GUI()
    gui.run()
