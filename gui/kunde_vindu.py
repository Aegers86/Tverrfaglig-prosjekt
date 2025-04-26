# gui/kunde_vindu.py

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from decimal import Decimal, InvalidOperation

# Importer de riktige vinduene
from gui.ny_kunde_vindu import vis_ny_kunde_vindu
from gui.rediger_kunde_vindu import vis_rediger_kunde_vindu

try:
    from utils.validators import valider_kundefelter
    from utils.feedback import vis_feil, vis_advarsel
except ImportError:
    def valider_kundefelter(verdier): return []
    def vis_feil(tittel, melding): messagebox.showerror(tittel, melding)
    def vis_advarsel(tittel, melding): messagebox.showwarning(tittel, melding)

# --- Sorteringsfunksjon ---
def sort_treeview_column(tree, col, reverse):
    try:
        data_list = []
        column_ids = tree["columns"]
        col_index = column_ids.index(col)

        for child_id in tree.get_children(''):
            value = tree.item(child_id, 'values')[col_index]
            try:
                numeric_value = int(value)
            except (ValueError, TypeError):
                try:
                    numeric_value = Decimal(value.replace(',', '.'))
                except (InvalidOperation, ValueError, TypeError):
                    numeric_value = str(value).lower()
            data_list.append((numeric_value, child_id))

        data_list.sort(key=lambda item: item[0], reverse=reverse)

        for index, (val, child_id) in enumerate(data_list):
            tree.move(child_id, '', index)

        tree.heading(col, command=lambda _col=col: sort_treeview_column(tree, _col, not reverse))
    except Exception as e:
        logging.error(f"Feil under sortering av kolonne '{col}': {e}", exc_info=True)

# --- Hjelpefunksjon for kundesøk ---
def _perform_customer_search(main_window, search_entry, tree):
    search_term = search_entry.get().strip()
    try:
        for i in tree.get_children():
            tree.delete(i)
    except tk.TclError:
        pass

    try:
        if not search_term:
            data = main_window.db.kall_prosedyre("hent_alle_kunder")
            status_suffix = "kunder lastet."
        else:
            query = """
                SELECT KNr, Fornavn, Etternavn, Adresse, PostNr FROM kunde
                WHERE CAST(KNr AS CHAR) LIKE %s OR Fornavn LIKE %s OR Etternavn LIKE %s
                   OR CONCAT(Fornavn, ' ', Etternavn) LIKE %s
                ORDER BY Etternavn ASC, Fornavn ASC;
            """
            pattern = f"%{search_term}%"
            data = main_window.db.hent_alle(query, (pattern, pattern, pattern, pattern))
            status_suffix = f"kunder funnet for '{search_term}'."

        data_length = 0
        for row in data:
            if isinstance(row, dict):
                values = (
                    row.get('KNr'),
                    row.get('Fornavn'),
                    row.get('Etternavn'),
                    row.get('Adresse'),
                    row.get('PostNr')
                )
                tree.insert("", "end", values=values)
                data_length += 1

        main_window.status_label.config(text=f"{data_length} {status_suffix}")

    except Exception as e:
        logging.error(f"Feil under kundesøk: {e}", exc_info=True)
        vis_feil("Databasefeil", f"Feil under henting/søk etter kunder: {e}")
        main_window.status_label.config(text="Feil under kundelasting")

# --- Viser kundeoversikten ---
def vis_kunder(main_window):
    main_window.oppdater_navigasjon(["Hoved", "Kunder"])
    main_window.status_label.config(text="Laster kundevisning...")
    main_window.rydd_innhold()

    search_frame = tk.Frame(main_window.innhold_frame)
    search_frame.pack(fill="x", padx=10, pady=(5, 0))

    tk.Label(search_frame, text="Søk (Kundenr, Navn):").pack(side="left", padx=(0, 5))
    search_entry = tk.Entry(search_frame)
    search_entry.pack(side="left", fill="x", expand=True, padx=5)

    tree = ttk.Treeview(main_window.innhold_frame, show="headings")
    tree_columns = ("KNr", "Fornavn", "Etternavn", "Adresse", "PostNr")
    tree["columns"] = tree_columns

    for col in tree_columns:
        tree.heading(col, text=col, command=lambda c=col: sort_treeview_column(tree, c, False))
        tree.column(col, width=120, anchor="w")

    tree.column("KNr", width=60, anchor="center")
    tree.column("PostNr", width=80, anchor="center")

    tree.pack(fill="both", expand=True, padx=10, pady=10)

    search_button = tk.Button(search_frame, text="Søk",
                              command=lambda: _perform_customer_search(main_window, search_entry, tree))
    search_button.pack(side="left", padx=(5, 0))

    search_entry.bind("<Return>", lambda event: _perform_customer_search(main_window, search_entry, tree))

    knapp_frame = tk.Frame(main_window.innhold_frame)
    knapp_frame.pack(pady=5)

    def åpne_ny_kunde():
        vis_ny_kunde_vindu(main_window)

    def åpne_rediger_kunde():
        selected = tree.selection()
        if not selected:
            vis_advarsel("Ingen valgt", "Velg en kunde du vil redigere.")
            return
        kunde_data = tree.item(selected[0], "values")
        if not kunde_data:
            vis_feil("Feil", "Ingen data å redigere.")
            return
        vis_rediger_kunde_vindu(main_window, kunde_data)

    tk.Button(knapp_frame, text="Legg til kunde", command=åpne_ny_kunde).pack(side="left", padx=5)
    tk.Button(knapp_frame, text="Rediger valgt", command=åpne_rediger_kunde).pack(side="left", padx=5)

    _perform_customer_search(main_window, search_entry, tree)