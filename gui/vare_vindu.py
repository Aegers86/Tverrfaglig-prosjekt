# gui/vare_vindu.py
# -*- coding: utf-8 -*-
# Importer nødvendige moduler
import tkinter as tk
from tkinter import ttk, messagebox
import logging
from decimal import Decimal, InvalidOperation

# Importer egen scrollbar-funksjon
try:
    from utils.treeview_scroll import legg_til_scrollbar
except ImportError:
    def legg_til_scrollbar(parent, tree): pass

# Sørg for at disse utils-filene finnes og er korrekte
try:
    from utils.feedback import vis_feil, vis_advarsel
except ImportError:
    # Fallback hvis utils ikke finnes
    import logging
    logging.error("Kunne ikke importere feedback-modul. Bruker messagebox direkte.")
    def vis_feil(tittel, melding): messagebox.showerror(tittel, melding)
    def vis_advarsel(tittel, melding): messagebox.showwarning(tittel, melding)

import logging
from decimal import Decimal, InvalidOperation # Importer Decimal for nøyaktig summering/formatering

# --- START PÅ INKLUDERT sorteringsfunksjon ---
def sort_treeview_column(tree, col, reverse):
    """ Sorterer en ttk.Treeview-kolonne når headingen klikkes. """
    try:
        data_list = []
        column_ids = tree["columns"]
        try:
            col_index = column_ids.index(col)
        except ValueError:
            logging.error(f"Sortering feilet: Kolonne-ID '{col}' ikke funnet i {column_ids}")
            return # Kan ikke sortere ukjent kolonne

        for child_id in tree.get_children(''):
            # Hent verdien fra riktig indeks
            try:
                value = tree.item(child_id, 'values')[col_index]
                # Prøv å konvertere til numerisk type hvis mulig for bedre sortering
                try:
                    # Prøv int først (for Antall)
                    numeric_value = int(value)
                    data_list.append((numeric_value, child_id))
                except (ValueError, TypeError):
                    try:
                         # Prøv Decimal (for Pris) - Håndterer formatert streng "x.xx"
                         numeric_value = Decimal(str(value).replace(',', '.')) # Håndterer evt. komma
                         data_list.append((numeric_value, child_id))
                    except (InvalidOperation, ValueError, TypeError):
                         # Sorter VNr eller Betegnelse som streng
                         data_list.append((str(value).lower(), child_id))
            except IndexError:
                 logging.warning(f"Indeksfeil ved henting av verdi for kolonne '{col}' (indeks {col_index}) for item {child_id}")
                 data_list.append(("", child_id)) # Legg til tom streng for å unngå krasj
        try:
            # Sorter listen basert på den konverterte verdien
            data_list.sort(key=lambda item: item[0], reverse=reverse)
        except TypeError as sort_err:
             logging.error(f"TypeError under sortering av kolonne '{col}': {sort_err}. Sorterer som streng.")
             # Fallback: Sorter alt som strenger hvis typesammenligning feiler
             data_list = [(str(item[0]).lower(), item[1]) for item in data_list]
             data_list.sort(key=lambda item: item[0], reverse=reverse)


        # Omorganiser elementene i Treeview
        for index, (val, child_id) in enumerate(data_list):
            tree.move(child_id, '', index)

        # Oppdater heading-kommandoen for å bytte sorteringsretning neste gang
        tree.heading(col, command=lambda _col=col: sort_treeview_column(tree, _col, not reverse))

    except Exception as e:
        logging.error(f"Uventet feil under sortering av kolonne '{col}': {e}", exc_info=True)
# --- SLUTT PÅ INKLUDERT sorteringsfunksjon ---

# --- vis_varer (OPPDATERT med søkefelt og scrollbar) ---
def vis_varer(main_window):
    main_window.oppdater_navigasjon(["Hoved", "Varelager"])
    main_window.status_label.config(text="Laster varelager...")
    main_window.rydd_innhold()

    # --- Søkefelt øverst ---
    search_frame = tk.Frame(main_window.innhold_frame)
    search_frame.pack(fill="x", padx=10, pady=(5, 0))

    tk.Label(search_frame, text="Søk (Varenr, Navn):").pack(side="left", padx=(0, 5))
    search_entry = tk.Entry(search_frame)
    search_entry.pack(side="left", fill="x", expand=True, padx=5)

    # --- Container for Treeview og Scrollbar ---
    tree_frame = tk.Frame(main_window.innhold_frame)
    tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

    tree = ttk.Treeview(tree_frame, show="headings")
    tree_columns = ("VNr", "Betegnelse", "Antall", "Pris")
    tree["columns"] = tree_columns

    for col in tree_columns:
        tree.heading(col, text=col, command=lambda c=col: sort_treeview_column(tree, c, False))
        tree.column(col, width=100, anchor="w")
    tree.column("Betegnelse", width=250, anchor="w")
    tree.column("Antall", width=100, anchor="center")
    tree.column("Pris", width=100, anchor="e")

    legg_til_scrollbar(tree_frame, tree)
    tree.pack(side="left", fill="both", expand=True)

    # --- Funksjon for å søke varer ---
    def perform_item_search():
        search_term = search_entry.get().strip()
        try:
            for i in tree.get_children():
                tree.delete(i)
        except tk.TclError:
            pass

        try:
            base_query = "SELECT VNr, Betegnelse, Antall, Pris FROM vare"
            where_clause = ""
            params = []

            if search_term:
                pattern = f"%{search_term}%"
                where_clause = """
                    WHERE CAST(VNr AS CHAR) LIKE %s
                       OR Betegnelse LIKE %s
                """
                params = [pattern, pattern]

            final_query = base_query + (" " + where_clause if where_clause else "") + " ORDER BY Betegnelse ASC;"
            data = main_window.db.hent_alle(final_query, tuple(params))

            data_length = 0
            if data:
                for row in data:
                    try:
                        pris_decimal = Decimal(row["Pris"]) if row["Pris"] is not None else Decimal('0.00')
                        pris_str = f"{pris_decimal:.2f}"
                    except (InvalidOperation, TypeError, KeyError):
                        pris_str = "Ugyldig"

                    formatted_row = (row.get("VNr"), row.get("Betegnelse"), row.get("Antall"), pris_str)
                    tree.insert("", "end", values=formatted_row)
                    data_length += 1

            if search_term:
                main_window.status_label.config(text=f"Søkeresultat for '{search_term}': {data_length} treff.")
            else:
                main_window.status_label.config(text=f"Varelager lastet ({data_length} varer).")

        except Exception as e:
            logging.error(f"Feil ved søk i varelager: {e}", exc_info=True)
            vis_feil("Databasefeil", f"Feil ved søk i varelager: {e}")
            main_window.status_label.config(text="Feil under søk i varelager")

    # --- Søkeknapp ---
    search_button = tk.Button(search_frame, text="Søk", command=perform_item_search)
    search_button.pack(side="left", padx=(5, 0))

    search_entry.bind("<Return>", lambda event: perform_item_search())

    # --- Laster varer ved første åpning ---
    perform_item_search()
