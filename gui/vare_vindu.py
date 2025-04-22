# gui/vare_vindu.py
from tkinter import ttk, messagebox
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
            return

        for child_id in tree.get_children(''):
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


# --- vis_varer (OPPDATERT med sortering) ---
def vis_varer(main_window):
    """ Viser en liste over varer på lager med kolonnesortering. """
    main_window.oppdater_navigasjon(["Hoved", "Varelager"])
    main_window.status_label.config(text="Laster varelager...")
    main_window.rydd_innhold()

    try:
        # Hent data fra vare-tabellen, bruk korrekte kolonnenavn
        query = "SELECT VNr, Betegnelse, Antall, Pris FROM vare ORDER BY Betegnelse ASC;" # Default sort
        data = main_window.db.hent_alle(query)
    except Exception as e:
        logging.error(f"Feil ved henting av varelager: {e}", exc_info=True)
        vis_feil("Databasefeil", f"Feil ved henting av varelager: {e}")
        main_window.status_label.config(text="Feil ved lasting av varelager")
        return

    # Sett opp Treeview for varelageret
    tree = ttk.Treeview(main_window.innhold_frame, show="headings")
    # Definer kolonne-IDer som skal brukes i heading command
    tree_columns = ("VNr", "Betegnelse", "Antall", "Pris")
    tree["columns"] = tree_columns

    # Definerer kolonneoverskrifter, bredder OG command for sortering
    tree.heading("VNr", text="Varenr", command=lambda c="VNr": sort_treeview_column(tree, c, False))
    tree.column("VNr", width=100, anchor="w")
    tree.heading("Betegnelse", text="Navn", command=lambda c="Betegnelse": sort_treeview_column(tree, c, False))
    tree.column("Betegnelse", width=250, anchor="w")
    tree.heading("Antall", text="Antall på lager", command=lambda c="Antall": sort_treeview_column(tree, c, False))
    tree.column("Antall", width=100, anchor="center")
    tree.heading("Pris", text="Pris (NOK)", command=lambda c="Pris": sort_treeview_column(tree, c, False))
    tree.column("Pris", width=100, anchor="e") # 'e' for høyrejustert

    # Fyller Treeview med data
    data_length = 0
    if data:
        for row in data:
            # Formater pris FØR innsetting, slik at sorteringsfunksjonen
            # mottar den formaterte strengen (f.eks. "123.45")
            try:
                pris_decimal = Decimal(row[3]) if row[3] is not None else Decimal('0.00')
                pris_str = f"{pris_decimal:.2f}"
            except (InvalidOperation, TypeError) as price_err:
                logging.warning(f"Kunne ikke formatere pris for vare {row[0]}: {row[3]} ({price_err})")
                pris_str = "Ugyldig"

            # Bruk den formaterte pris-strengen ved innsetting
            formatted_row = (row[0], row[1], row[2], pris_str)
            tree.insert("", "end", values=formatted_row)
            data_length += 1

    tree.pack(fill="both", expand=True, padx=10, pady=10)

    # Ingen ekstra knapper under varelagerlisten

    # Oppdaterer statuslabel
    status_text = f"Varelager lastet ({data_length} varer)." if data else "Varelageret er tomt."
    main_window.status_label.config(text=status_text)
    logging.info(status_text)