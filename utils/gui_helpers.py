# gui/gui_helpers.py
# Hjelpefunksjoner for GUI-elementer

import logging
from decimal import Decimal, InvalidOperation

# --- Sorteringsfunksjon ---
def sort_treeview_column(tree, col, reverse):
    """ Sorterer en ttk.Treeview-kolonne når headingen klikkes. """
    try:
        data_list = []
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
                         # Håndterer formatert streng (med .) og evt. komma som des.tegn
                         numeric_value = Decimal(str(value).replace(',', '.'))
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
        # Vurder å vise feilmelding til bruker:
        # from tkinter import messagebox
        # messagebox.showerror("Sorteringsfeil", f"En feil oppstod under sortering av {col}.")

# --- Datoformateringsfunksjon ---
def formater_dato_norsk(dato_str):
    """ Konverterer dato fra 'YYYY-MM-DD' til 'DD.MM.YYYY' """
    try:
        if not dato_str:
            return ""
        deler = str(dato_str).split("-")
        if len(deler) == 3:
            yyyy, mm, dd = deler
            return f"{dd}.{mm}.{yyyy}"
        else:
            return dato_str
    except Exception as e:
        logging.warning(f"Feil ved datoformatering: {e}")
        return dato_str

# --- Formateringsfunksjon ---
def formater_tall_norsk(verdi, desimaler=2):
    """ Formaterer et tall (int, float, Decimal) til norsk format.
        Bruker mellomrom som tusenskille og komma som desimalskille.
    """
    try:
        # Sikrer at vi jobber med Decimal for nøyaktighet med desimaler
        if verdi is None:
            return "N/A" # Eller en tom streng?
        if not isinstance(verdi, Decimal):
            # Håndterer komma som desimaltegn ved konvertering
            verdi_decimal = Decimal(str(verdi).replace(',', '.'))
        else:
            verdi_decimal = verdi

        # Bruk Pythons innebygde formatering med komma som tusenskille og punktum som desimal
        # Dette er et mellomsteg før vi bytter tegnene
        formatert_punktum = f"{verdi_decimal:,.{desimaler}f}"

        # Bytt ut komma med en midlertidig markør (for å unngå konflikt med desimalkomma)
        # Bytt deretter punktum til komma (desimalskille)
        # Bytt til slutt markøren til non-breaking space (tusenskille)
        temp_marker = "§TEMP§"
        formatert_norsk = formatert_punktum.replace(",", temp_marker)
        formatert_norsk = formatert_norsk.replace(".", ",")
        formatert_norsk = formatert_norsk.replace(temp_marker, "\u00A0") # Non-breaking space

        return formatert_norsk

    except (ValueError, TypeError, InvalidOperation) as e:
        logging.warning(f"Kunne ikke formatere tallverdi '{verdi}': {e}")
        return str(verdi) # Returner opprinnelig verdi (som streng) ved feil
    except Exception as e_global:
         logging.error(f"Uventet feil i formater_tall_norsk for verdi '{verdi}': {e_global}", exc_info=True)
         return "Feil"