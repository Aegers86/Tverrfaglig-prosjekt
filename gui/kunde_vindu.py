# gui/kunde_vindu.py
import tkinter as tk
from tkinter import ttk, messagebox
# Sørg for at disse utils-filene finnes og er korrekte
try:
    from utils.validators import valider_kundefelter
    from utils.feedback import vis_feil, vis_advarsel
except ImportError:
    # Fallback hvis utils ikke finnes
    import logging
    logging.error("Kunne ikke importere utils-moduler. Bruker messagebox direkte.")
    # Definer dummy-funksjoner eller bruk messagebox direkte
    def valider_kundefelter(verdier): return []
    def vis_feil(tittel, melding): messagebox.showerror(tittel, melding)
    def vis_advarsel(tittel, melding): messagebox.showwarning(tittel, melding)

import logging
from decimal import Decimal, InvalidOperation # Trengs for sorteringsfunksjon

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
                try:
                    numeric_value = int(value)
                    data_list.append((numeric_value, child_id))
                except (ValueError, TypeError):
                    try:
                         numeric_value = Decimal(value.replace(',', '.'))
                         data_list.append((numeric_value, child_id))
                    except (InvalidOperation, ValueError, TypeError):
                         data_list.append((str(value).lower(), child_id))
            except IndexError:
                 logging.warning(f"Indeksfeil ved henting av verdi for kolonne '{col}' (indeks {col_index}) for item {child_id}")
                 data_list.append(("", child_id))
        try:
            data_list.sort(key=lambda item: item[0], reverse=reverse)
        except TypeError as sort_err:
             logging.error(f"TypeError under sortering av kolonne '{col}': {sort_err}. Sorterer som streng.")
             data_list = [(str(item[0]).lower(), item[1]) for item in data_list]
             data_list.sort(key=lambda item: item[0], reverse=reverse)

        for index, (val, child_id) in enumerate(data_list):
            tree.move(child_id, '', index)

        tree.heading(col, command=lambda _col=col: sort_treeview_column(tree, _col, not reverse))

    except Exception as e:
        logging.error(f"Uventet feil under sortering av kolonne '{col}': {e}", exc_info=True)
# --- SLUTT PÅ INKLUDERT sorteringsfunksjon ---


# --- Hjelpefunksjon for kundesøk (Inkluderer Stored Procedure logikk, uten is_active) ---
def _perform_customer_search(main_window, search_entry, tree):
    """ Henter kunder basert på søketerm (direkte SQL)
        eller alle kunder (Stored Procedure) og oppdaterer Treeview. """
    search_term = search_entry.get().strip()
    data = None

    try:
        for i in tree.get_children(): tree.delete(i)
    except tk.TclError as e: logging.warning(f"Feil ved tømming av Kunde-Treeview (ignorerer): {e}")

    try:
        if not search_term:
            # Bruk Stored Procedure (som nå henter ALLE kunder)
            status_msg = "Laster alle kunder (via Stored Procedure)..."
            main_window.status_label.config(text=status_msg); logging.info(status_msg)
            data = main_window.db.kall_prosedyre("hent_alle_kunder")
            status_text_suffix = "kunder lastet."
        else:
            # Bruk direkte SQL med LIKE (uten is_active filter)
            status_msg = f"Søker etter kunde '{search_term}' (via direkte SQL)..."
            main_window.status_label.config(text=status_msg); logging.info(status_msg)
            base_query = "SELECT KNr, Fornavn, Etternavn, Adresse, PostNr FROM kunde"
            where_clause = """
                WHERE CAST(KNr AS CHAR) LIKE %s OR Fornavn LIKE %s OR Etternavn LIKE %s
                   OR CONCAT(Fornavn, ' ', Etternavn) LIKE %s """
            search_pattern = f"%{search_term}%"
            params = [search_pattern] * 4
            final_query = base_query + where_clause + " ORDER BY Etternavn ASC, Fornavn ASC;"
            data = main_window.db.hent_alle(final_query, tuple(params))
            status_text_suffix = f"kunder funnet for '{search_term}'."

        # Fyll treet med resultater
        data_length = 0
        if data:
            for row in data: tree.insert("", "end", values=row); data_length += 1
        status_text = f"{data_length} {status_text_suffix}"
        main_window.status_label.config(text=status_text); logging.info(status_text)

    except Exception as e:
        proc_error_msg = ""
        if not search_term and ("hent_alle_kunder" in str(e) or "1305" in str(e)):
             proc_error_msg = " Sjekk at Stored Procedure 'hent_alle_kunder' eksisterer."
        logging.error(f"Feil under henting/søk av kunder ('{search_term}'): {e}{proc_error_msg}", exc_info=True)
        vis_feil("Databasefeil", f"Feil under henting/søk etter kunder: {e}{proc_error_msg}")
        main_window.status_label.config(text="Feil under kundelasting/-søk")


# --- Start på komplett vis_kunder ---
def vis_kunder(main_window):
    """ Viser kundeoversikten med søkefunksjonalitet og kolonnesortering. """
    main_window.oppdater_navigasjon(["Hoved", "Kunder"])
    main_window.status_label.config(text="Laster inn kundevisning...")
    main_window.rydd_innhold()

    # Ramme for søk
    search_frame = tk.Frame(main_window.innhold_frame)
    search_frame.pack(fill="x", padx=10, pady=(5, 0))
    tk.Label(search_frame, text="Søk (Kundenr, Navn):").pack(side="left", padx=(0, 5))
    search_entry = tk.Entry(search_frame)
    search_entry.pack(side="left", fill="x", expand=True, padx=5)
    tree = ttk.Treeview(main_window.innhold_frame, show="headings")
    search_button = tk.Button(search_frame, text="Søk",
                              command=lambda: _perform_customer_search(main_window, search_entry, tree))
    search_button.pack(side="left", padx=(5, 0))
    search_entry.bind("<Return>", lambda event: _perform_customer_search(main_window, search_entry, tree))

    # Definer kolonne-IDer
    tree_columns = ("KNr", "Fornavn", "Etternavn", "Adresse", "PostNr")
    tree["columns"] = tree_columns

    # Sett kolonneoverskrifter, bredde OG LEGG TIL command for sortering
    tree.heading("KNr", text="KNr", command=lambda c="KNr": sort_treeview_column(tree, c, False))
    tree.column("KNr", width=80, anchor="center")
    tree.heading("Fornavn", text="Fornavn", command=lambda c="Fornavn": sort_treeview_column(tree, c, False))
    tree.column("Fornavn", width=120, anchor="w")
    tree.heading("Etternavn", text="Etternavn", command=lambda c="Etternavn": sort_treeview_column(tree, c, False))
    tree.column("Etternavn", width=120, anchor="w")
    tree.heading("Adresse", text="Adresse", command=lambda c="Adresse": sort_treeview_column(tree, c, False))
    tree.column("Adresse", width=200, anchor="w")
    tree.heading("PostNr", text="PostNr", command=lambda c="PostNr": sort_treeview_column(tree, c, False))
    tree.column("PostNr", width=80, anchor="center")

    tree.pack(fill="both", expand=True, padx=10, pady=10)

    # Knapper under Treeview
    knapp_frame = tk.Frame(main_window.innhold_frame)
    knapp_frame.pack(pady=5)
    tk.Button(knapp_frame, text="Legg til kunde", command=lambda: nytt_kundevindu(main_window)).pack(side="left", padx=5)
    tk.Button(knapp_frame, text="Rediger valgt", command=lambda: rediger_kunde(main_window, tree)).pack(side="left", padx=5)
    # Deaktiver/Hovedmeny-knapper er fjernet

    # Last inn alle kunder initielt
    _perform_customer_search(main_window, search_entry, tree)

# --- Slutt på komplett vis_kunder ---


# --- Start på komplett nytt_kundevindu ---
def nytt_kundevindu(main_window):
    """ Viser vindu for å legge til ny kunde. """
    main_window.oppdater_navigasjon(["Hoved", "Kunder", "Ny kunde"])
    main_window.rydd_innhold()
    main_window.status_label.config(text="Legg til ny kunde")

    # Oppretter felter for input
    felter = lag_kundefelter(main_window.innhold_frame)

    def lagre():
        verdier = {k: v.get().strip() for k, v in felter.items()} # Hent verdier
        # Valider input (sørg for at valider_kundefelter er korrekt ift. dine krav)
        feil = valider_kundefelter(verdier)
        if feil:
            vis_advarsel("Valideringsfeil", "\n".join(feil))
            return
        try:
            # Kall databasehandler for å sette inn (uten is_active)
            # Pass på at sett_inn_kunde i handler er oppdatert!
            # KNr må håndteres - enten ved at DB genererer det, eller at det hentes/legges inn her.
            # Gitt schema, må KNr sannsynligvis spesifiseres. Dette krever et ekstra felt
            # eller en metode for å finne neste ledige KNr.
            # Forenkling: Anta at bruker MÅ skrive inn et unikt KNr selv i feltdefinisjonen under.
            # (Dette bør forbedres i en ekte applikasjon)

            # VIKTIG: Sjekk om `sett_inn_kunde` forventer KNr som argument!
            # Hvis ja, legg til KNr-felt i lag_kundefelter og hent verdien her.
            # Eksempel (hvis KNr trengs):
            # main_window.db.sett_inn_kunde(
            #     verdier["knr"], # Antatt at du legger til 'knr' i lag_kundefelter
            #     verdier["fornavn"], verdier["etternavn"], verdier["adresse"],
            #     verdier["postnr"], verdier.get("telefon"), verdier.get("epost")
            # )

            # Hvis sett_inn_kunde *ikke* tar KNr (og DB håndterer det, f.eks. AUTO_INCREMENT)
            main_window.db.sett_inn_kunde(
                 verdier["fornavn"], verdier["etternavn"], verdier["adresse"],
                 verdier["postnr"], verdier.get("telefon"), verdier.get("epost")
            )

            logging.info(f"Ny kunde lagret: {verdier.get('fornavn')} {verdier.get('etternavn')}")
            vis_kunder(main_window) # Gå tilbake for å se den nye kunden
        except Exception as e:
            logging.error(f"Feil ved lagring av ny kunde: {e}", exc_info=True)
            vis_feil("Feil", f"Klarte ikke å lagre kunde: {e}")

    # Knapper for Lagre og Tilbake
    knapp_frame_ny = tk.Frame(main_window.innhold_frame)
    knapp_frame_ny.pack(pady=10)
    tk.Button(knapp_frame_ny, text="Lagre", command=lagre).pack(side="left", padx=5)
    tk.Button(knapp_frame_ny, text="Tilbake", command=lambda: vis_kunder(main_window)).pack(side="left", padx=5)
# --- Slutt på komplett nytt_kundevindu ---


# --- Start på komplett rediger_kunde ---
def rediger_kunde(main_window, tree):
    """ Viser vindu for å redigere valgt kunde. """
    selected_item = tree.selection()
    if not selected_item:
        vis_advarsel("Ingen valgt", "Velg en kunde fra listen for å redigere.")
        return

    try:
        data = tree.item(selected_item[0], "values")
        if not data or len(data) < 1: raise ValueError("Mangler data i valgt rad")
        knr_for_redigering = int(data[0])
    except (ValueError, TypeError, IndexError) as e:
        logging.error(f"Kunne ikke hente KNr for redigering fra Treeview: {e}", exc_info=True)
        vis_feil("Feil", "Kunne ikke identifisere kundenummer for valgt kunde.")
        return

    main_window.oppdater_navigasjon(["Hoved", "Kunder", f"Rediger kunde {knr_for_redigering}"])
    main_window.rydd_innhold()
    main_window.status_label.config(text=f"Redigerer kunde {knr_for_redigering}")

    # Oppretter felter med eksisterende data
    felter = lag_kundefelter(main_window.innhold_frame, data) # Send med 'data'

    def lagre():
        verdier = {k: v.get().strip() for k, v in felter.items()}
        feil = valider_kundefelter(verdier)
        if feil:
            vis_advarsel("Valideringsfeil", "\n".join(feil))
            return
        try:
            # Kall databasehandler for å oppdatere
            main_window.db.oppdater_kunde(
                knr_for_redigering, # Viktig å sende med riktig KNr
                verdier["fornavn"], verdier["etternavn"],
                verdier["adresse"], verdier["postnr"],
                verdier.get("telefon"), verdier.get("epost")
            )
            logging.info(f"Kunde {knr_for_redigering} oppdatert.")
            vis_kunder(main_window) # Gå tilbake til oppdatert liste
        except Exception as e:
            logging.error(f"Feil ved oppdatering av kunde {knr_for_redigering}: {e}", exc_info=True)
            vis_feil("Feil", f"Klarte ikke å oppdatere kunde: {e}")

    knapp_frame_edit = tk.Frame(main_window.innhold_frame)
    knapp_frame_edit.pack(pady=10)
    tk.Button(knapp_frame_edit, text="Lagre endringer", command=lagre).pack(side="left", padx=5)
    tk.Button(knapp_frame_edit, text="Tilbake", command=lambda: vis_kunder(main_window)).pack(side="left", padx=5)
# --- Slutt på komplett rediger_kunde ---


# --- Start på komplett lag_kundefelter ---
def lag_kundefelter(master, data=None):
    """ Oppretter input-felter for kundeinformasjon.
        'data' er en tuple med eksisterende verdier (fra Treeview) hvis vi redigerer.
    """
    # Feltdefinisjoner - KNr må kanskje legges til hvis det skal settes manuelt ved 'Ny kunde'
    felt_definisjoner = [
        # ("Kundenummer", "knr"), # Uncomment hvis KNr skal legges inn manuelt
        ("Fornavn", "fornavn"),
        ("Etternavn", "etternavn"),
        ("Adresse", "adresse"),
        ("Postnummer", "postnr")
        # ("Telefon", "telefon"), # Uncomment hvis relevant
        # ("E-post", "epost")     # Uncomment hvis relevant
    ]

    entries = {}
    container = tk.Frame(master)
    container.pack(fill='x', padx=10, pady=5)

    for i, (label_tekst, key) in enumerate(felt_definisjoner):
        lbl = tk.Label(container, text=label_tekst + ":", anchor="w", width=12)
        lbl.grid(row=i, column=0, padx=2, pady=3, sticky="w")
        entry = tk.Entry(container, width=40)
        entry.grid(row=i, column=1, padx=2, pady=3, sticky="ew")

        if data:
            # Juster indeksen basert på om KNr er med i felt_definisjoner
            data_index = i + 1 # Hvis KNr IKKE er med i felt_definisjoner
            # data_index = i # Hvis KNr ER med i felt_definisjoner

            if data_index < len(data) and data[data_index] is not None:
                 entry.insert(0, data[data_index])
            else:
                 logging.warning(f"Mangler data på indeks {data_index} for kunde {data[0] if data else 'UKJENT'}.")

        # Hvis vi redigerer, deaktiver KNr-feltet (hvis det vises)
        # if key == "knr" and data:
        #    entry.config(state="readonly")

        entries[key] = entry

    container.columnconfigure(1, weight=1)

    return entries
# --- Slutt på komplett lag_kundefelter ---