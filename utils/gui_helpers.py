# gui/gui_helpers.py
# Hjelpefunksjon for sortering av ttk.Treeview
# Plasser denne f.eks. øverst i hver av filene kunde_vindu.py, order_view.py, vare_vindu.py
# eller i en egen utils/gui_helpers.py og importer den.
import tkinter as tk
from tkinter import ttk
import logging
from decimal import Decimal, InvalidOperation

def sort_treeview_column(tree, col, reverse):
    """ Sorterer en ttk.Treeview-kolonne når headingen klikkes. """
    try:
        # Hent data fra alle rader for den aktuelle kolonnen
        # Må konvertere til riktig type for sammenligning
        data_list = []
        # Få kolonne-IDene slik de er definert i tree["columns"]
        column_ids = tree["columns"]
        try:
            # Finn indeksen til kolonnen som ble klikket (basert på ID)
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
                    # Prøv int først
                    numeric_value = int(value)
                    data_list.append((numeric_value, child_id))
                except (ValueError, TypeError):
                    try:
                         # Prøv Decimal (f.eks. for pris)
                         numeric_value = Decimal(value.replace(',', '.')) # Håndter komma som desimalseparator?
                         data_list.append((numeric_value, child_id))
                    except (InvalidOperation, ValueError, TypeError):
                         # Sorter som lav-case streng hvis ikke numerisk
                         data_list.append((str(value).lower(), child_id))
            except IndexError:
                 logging.warning(f"Indeksfeil ved henting av verdi for kolonne '{col}' (indeks {col_index}) for item {child_id}")
                 data_list.append(("", child_id)) # Legg til tom streng for å unngå krasj

        # Sorter listen
        # Bruker try/except rundt sortering i tilfelle blandede typer som ikke kan sammenlignes
        try:
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
        # Vis feilmelding til bruker? Vurderes.