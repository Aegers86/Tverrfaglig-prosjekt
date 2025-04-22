# gui/kunde_vindu.py
import tkinter as tk
from tkinter import ttk, messagebox # Importer messagebox
# Sørg for at disse utils-filene finnes og er korrekte
try:
    from utils.validators import valider_kundefelter
    from utils.feedback import vis_feil, vis_advarsel
except ImportError:
    # Fallback hvis utils ikke finnes
    import logging
    logging.error("Kunne ikke importere utils-moduler. Bruker messagebox direkte.")
    def valider_kundefelter(verdier): return [] # Returner ingen feil som standard
    def vis_feil(tittel, melding): messagebox.showerror(tittel, melding)
    def vis_advarsel(tittel, melding): messagebox.showwarning(tittel, melding)

import logging # Importer logging

# --- Hjelpefunksjon for kundesøk ---
def _perform_customer_search(main_window, search_entry, tree):
    """ Henter kunder basert på søketerm og oppdaterer Treeview. """
    search_term = search_entry.get().strip()
    status_msg = f"Søker etter kunde '{search_term}'..." if search_term else "Laster alle kunder..."
    main_window.status_label.config(text=status_msg)
    logging.info(status_msg)

    # Tømmer treet før nytt søk/oppdatering
    try:
        for i in tree.get_children():
            tree.delete(i)
    except tk.TclError as e:
        logging.warning(f"Feil ved tømming av Kunde-Treeview (ignorerer): {e}")

    try:
        # Basis-spørring - hent kolonner som trengs for visning
        base_query = "SELECT KNr, Fornavn, Etternavn, Adresse, PostNr FROM kunde"
        where_clause = ""
        params = []

        if search_term:
            search_pattern = f"%{search_term}%"
            # Søker i KNr (som tekst), Fornavn, Etternavn, og fullt navn
            where_clause = """
                WHERE CAST(KNr AS CHAR) LIKE %s
                   OR Fornavn LIKE %s
                   OR Etternavn LIKE %s
                   OR CONCAT(Fornavn, ' ', Etternavn) LIKE %s
            """
            params = [search_pattern] * 4

        final_query = base_query + where_clause + " ORDER BY Etternavn ASC, Fornavn ASC;"

        data = main_window.db.hent_alle(final_query, tuple(params))

        data_length = 0
        if data:
            for row in data:
                tree.insert("", "end", values=row)
                data_length += 1

        if search_term:
             status_text = f"Søkeresultat for '{search_term}': {data_length} kunder funnet."
        else:
             status_text = f"Alle kunder ({data_length} stk) lastet."
        main_window.status_label.config(text=status_text)
        logging.info(status_text)

    except Exception as e:
        logging.error(f"Feil under kundesøk etter '{search_term}': {e}", exc_info=True)
        vis_feil("Databasefeil", f"Feil under søk etter kunder: {e}")
        main_window.status_label.config(text="Feil under kundesøk")


# --- Start på komplett vis_kunder (med søkefelt og UTEN bunn-knapp) ---
def vis_kunder(main_window):
    """ Viser kundeoversikten med søkefunksjonalitet. """
    main_window.oppdater_navigasjon(["Hoved", "Kunder"])
    main_window.status_label.config(text="Laster inn kundevisning...")
    main_window.rydd_innhold()

    # --- Ramme for søkefunksjonalitet ---
    search_frame = tk.Frame(main_window.innhold_frame)
    search_frame.pack(fill="x", padx=10, pady=(5, 0))

    tk.Label(search_frame, text="Søk (Kundenr, Navn):").pack(side="left", padx=(0, 5))
    search_entry = tk.Entry(search_frame)
    search_entry.pack(side="left", fill="x", expand=True, padx=5)

    # Treeview må defineres FØR knappen som bruker den i command
    tree = ttk.Treeview(main_window.innhold_frame, show="headings")

    search_button = tk.Button(search_frame, text="Søk",
                              command=lambda: _perform_customer_search(main_window, search_entry, tree))
    search_button.pack(side="left", padx=(5, 0))
    search_entry.bind("<Return>", lambda event: _perform_customer_search(main_window, search_entry, tree))
    # --- Slutt på søkeramme ---


    # --- Sett opp Treeview ---
    tree_columns = ("Kundenummer", "Fornavn", "Etternavn", "Adresse", "Postnummer")
    tree["columns"] = tree_columns

    tree.heading("Kundenummer", text="KNr"); tree.column("Kundenummer", width=80, anchor="center")
    tree.heading("Fornavn", text="Fornavn"); tree.column("Fornavn", width=120, anchor="w")
    tree.heading("Etternavn", text="Etternavn"); tree.column("Etternavn", width=120, anchor="w")
    tree.heading("Adresse", text="Adresse"); tree.column("Adresse", width=200, anchor="w")
    tree.heading("Postnummer", text="PostNr"); tree.column("Postnummer", width=80, anchor="center")

    tree.pack(fill="both", expand=True, padx=10, pady=10)

    # --- Knapper under Treeview ---
    knapp_frame = tk.Frame(main_window.innhold_frame)
    knapp_frame.pack(pady=5)

    tk.Button(knapp_frame, text="Legg til kunde", command=lambda: nytt_kundevindu(main_window)).pack(side="left", padx=5)
    tk.Button(knapp_frame, text="Rediger valgt", command=lambda: rediger_kunde(main_window, tree)).pack(side="left", padx=5)

    # --- FJERNET KNAPP HER ---
    # tk.Button(knapp_frame, text="Til Hovedmeny", command=main_window.vis_startside).pack(side="left", padx=5)

    # --- Last inn alle kunder initielt ---
    _perform_customer_search(main_window, search_entry, tree)

# --- Slutt på komplett vis_kunder ---


# --- nytt_kundevindu, rediger_kunde, lag_kundefelter (som før, husk Telefon/Epost justeringer) ---
# Disse funksjonene er uendret fra forrige versjon
def nytt_kundevindu(main_window):
    """ Viser vindu for å legge til ny kunde. """
    main_window.oppdater_navigasjon(["Hoved", "Kunder", "Ny kunde"])
    main_window.rydd_innhold()
    main_window.status_label.config(text="Legg til ny kunde")
    felter = lag_kundefelter(main_window.innhold_frame)
    def lagre():
        verdier = {k: v.get().strip() for k, v in felter.items()}
        feil = valider_kundefelter(verdier)
        if feil:
            vis_advarsel("Valideringsfeil", "\n".join(feil))
            return
        try:
            main_window.db.sett_inn_kunde(
                verdier["fornavn"], verdier["etternavn"], verdier["adresse"],
                verdier["postnr"], verdier.get("telefon"), verdier.get("epost")
            )
            logging.info(f"Ny kunde lagret: {verdier.get('fornavn')} {verdier.get('etternavn')}")
            vis_kunder(main_window)
        except Exception as e:
            logging.error(f"Feil ved lagring av ny kunde: {e}", exc_info=True)
            vis_feil("Feil", f"Klarte ikke å lagre kunde: {e}")
    knapp_frame_ny = tk.Frame(main_window.innhold_frame)
    knapp_frame_ny.pack(pady=10)
    tk.Button(knapp_frame_ny, text="Lagre", command=lagre).pack(side="left", padx=5)
    tk.Button(knapp_frame_ny, text="Tilbake", command=lambda: vis_kunder(main_window)).pack(side="left", padx=5)

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
        logging.error(f"Kunne ikke hente data for redigering fra Treeview: {e}", exc_info=True)
        vis_feil("Feil", "Kunne ikke hente data for valgt kunde fra listen.")
        return
    main_window.oppdater_navigasjon(["Hoved", "Kunder", f"Rediger kunde {knr_for_redigering}"])
    main_window.rydd_innhold()
    main_window.status_label.config(text=f"Redigerer kunde {knr_for_redigering}")
    felter = lag_kundefelter(main_window.innhold_frame, data)
    def lagre():
        verdier = {k: v.get().strip() for k, v in felter.items()}
        feil = valider_kundefelter(verdier)
        if feil:
            vis_advarsel("Valideringsfeil", "\n".join(feil))
            return
        try:
            main_window.db.oppdater_kunde(
                knr_for_redigering, verdier["fornavn"], verdier["etternavn"],
                verdier["adresse"], verdier["postnr"], verdier.get("telefon"),
                verdier.get("epost")
            )
            logging.info(f"Kunde {knr_for_redigering} oppdatert.")
            vis_kunder(main_window)
        except Exception as e:
            logging.error(f"Feil ved oppdatering av kunde {knr_for_redigering}: {e}", exc_info=True)
            vis_feil("Feil", f"Klarte ikke å oppdatere kunde: {e}")
    knapp_frame_edit = tk.Frame(main_window.innhold_frame)
    knapp_frame_edit.pack(pady=10)
    tk.Button(knapp_frame_edit, text="Lagre endringer", command=lagre).pack(side="left", padx=5)
    tk.Button(knapp_frame_edit, text="Tilbake", command=lambda: vis_kunder(main_window)).pack(side="left", padx=5)

def lag_kundefelter(master, data=None):
    """ Oppretter input-felter for kundeinformasjon. """
    felt_definisjoner = [
        ("Fornavn", "fornavn"), ("Etternavn", "etternavn"),
        ("Adresse", "adresse"), ("Postnummer", "postnr")
        # ("Telefon", "telefon"), # Uncomment hvis relevant
        # ("E-post", "epost")     # Uncomment hvis relevant
    ]
    entries = {}
    for i, (label_tekst, key) in enumerate(felt_definisjoner):
        frame = tk.Frame(master)
        frame.pack(fill="x", padx=10, pady=2)
        tk.Label(frame, text=label_tekst + ":", width=12, anchor="w").pack(side="left")
        entry = tk.Entry(frame)
        entry.pack(side="left", fill="x", expand=True)
        if data:
            if i + 1 < len(data): entry.insert(0, data[i + 1])
            else: logging.warning(f"Mangler data på indeks {i+1} for kunde {data[0]} ved redigering.")
        entries[key] = entry
    return entries