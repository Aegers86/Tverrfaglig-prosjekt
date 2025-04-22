# gui/kunde_vindu.py
import tkinter as tk
from tkinter import ttk
from utils.validators import valider_kundefelter # Antar denne finnes og er korrekt
from utils.feedback import vis_feil, vis_advarsel # Antar denne finnes og er korrekt
import logging # Importer logging

# --- Start på korrigert funksjon ---
def vis_kunder(main_window):
    main_window.oppdater_navigasjon(["Hoved", "Kunder"])
    main_window.status_label.config(text="Laster kunder...")
    main_window.rydd_innhold()

    try:
        # ENDRET: Erstatter prosedyrekall med direkte SQL-spørring
        # Henter kolonner som matcher Treeview (juster hvis Telefon/Epost finnes/ikke finnes)
        # Bruker kolonnenavn fra varehusdb.sql
        query = """
            SELECT KNr, Fornavn, Etternavn, Adresse, PostNr
            FROM kunde
            ORDER BY Etternavn ASC, Fornavn ASC;
            """
        # Bruker nå hent_alle i stedet for kall_prosedyre
        data = main_window.db.hent_alle(query)

    except Exception as e:
        # Logg feilen
        logging.error(f"Feil ved henting av kunder for GUI: {e}", exc_info=True)
        vis_feil("Databasefeil", f"Feil ved henting av kunder: {e}")
        main_window.status_label.config(text="Feil ved lasting av kunder")
        return # Avslutt hvis data ikke kan hentes

    # Sett opp Treeview
    tree = ttk.Treeview(main_window.innhold_frame, show="headings")

    # Definer kolonner BASERT PÅ SPØRRINGEN over (og det som finnes i db)
    # Hvis du *har* Telefon og Epost i din faktiske kunde-tabell, legg dem til her
    # og i SELECT-spørringen over. Hvis ikke, fjern dem herfra.
    tree_columns = ("Kundenummer", "Fornavn", "Etternavn", "Adresse", "Postnummer") # Fjernet Telefon, E-post
    tree["columns"] = tree_columns

    # Sett kolonneoverskrifter og bredde
    tree.heading("Kundenummer", text="KNr") # Bruk KNr som i databasen
    tree.column("Kundenummer", width=80, anchor="center")
    tree.heading("Fornavn", text="Fornavn")
    tree.column("Fornavn", width=120, anchor="w")
    tree.heading("Etternavn", text="Etternavn")
    tree.column("Etternavn", width=120, anchor="w")
    tree.heading("Adresse", text="Adresse")
    tree.column("Adresse", width=200, anchor="w")
    tree.heading("Postnummer", text="PostNr")
    tree.column("Postnummer", width=80, anchor="center")
    # Hvis du legger til Telefon/Epost, legg til heading/column her også

    # Fyll inn data
    if data: # Sjekk om data faktisk ble hentet
        for row in data:
            # Pass på at values har like mange elementer som tree["columns"]
            tree.insert("", "end", values=row)
    else:
        # Vis en melding hvis ingen data ble funnet?
        pass # Eller tk.Label(...)

    tree.pack(fill="both", expand=True, padx=10, pady=10)

    # Knapper
    knapp_frame = tk.Frame(main_window.innhold_frame)
    knapp_frame.pack(pady=5)
    tk.Button(knapp_frame, text="Legg til kunde", command=lambda: nytt_kundevindu(main_window)).pack(side="left", padx=5)
    # TODO: Funksjonaliteten til rediger_kunde må også tilpasses hvis Telefon/Epost er fjernet/endret
    tk.Button(knapp_frame, text="Rediger valgt", command=lambda: rediger_kunde(main_window, tree)).pack(side="left", padx=5)

    main_window.status_label.config(text="Kunder lastet.")
# --- Slutt på korrigert funksjon ---


# --- Resten av filen (inkludert nytt_kundevindu, rediger_kunde, lag_kundefelter) ---
# Disse må kanskje også justeres hvis Telefon/Epost mangler i databasen
# eller hvis kolonneindeksene i 'data' har endret seg i rediger_kunde.

def nytt_kundevindu(main_window):
    main_window.oppdater_navigasjon(["Hoved", "Kunder", "Ny kunde"])
    main_window.rydd_innhold()

    # VIKTIG: Pass på at felter her matcher det sett_inn_kunde forventer
    # og det som finnes i databasen.
    felter = lag_kundefelter(main_window.innhold_frame)

    def lagre():
        verdier = {k: v.get() for k, v in felter.items()}
        # VIKTIG: valider_kundefelter må kanskje justeres hvis Telefon/Epost ikke er obligatorisk/finnes
        feil = valider_kundefelter(verdier)
        if feil:
            vis_advarsel("Valideringsfeil", "\n".join(feil))
            return
        try:
            # Pass på at argumentene her matcher sett_inn_kunde i database_handler
            # og kolonnene i databasen (f.eks., mangler Telefon/Epost?)
            main_window.db.sett_inn_kunde(
                verdier["fornavn"],
                verdier["etternavn"],
                verdier["adresse"],
                verdier["postnr"],
                verdier.get("telefon", None), # Bruk .get med default hvis de kan mangle
                verdier.get("epost", None)
            )
            vis_kunder(main_window) # Gå tilbake til kundeoversikten
        except Exception as e:
            logging.error(f"Feil ved lagring av ny kunde: {e}", exc_info=True)
            vis_feil("Feil", f"Klarte ikke å lagre kunde: {e}")

    tk.Button(main_window.innhold_frame, text="Lagre", command=lagre).pack(pady=10)
    tk.Button(main_window.innhold_frame, text="Tilbake", command=lambda: vis_kunder(main_window)).pack(pady=5)

def rediger_kunde(main_window, tree):
    valgt = tree.selection()
    if not valgt:
        vis_advarsel("Ingen valgt", "Velg en kunde først.")
        return
    # Henter data fra den valgte raden i Treeview
    data = tree.item(valgt[0], "values")

    # VIKTIG: Indeksene i 'data' her må matche rekkefølgen i SELECT-spørringen
    # og kolonnene i Treeview i vis_kunder. data[0] er KNr.
    if not data:
        vis_feil("Feil", "Kunne ikke hente data for valgt kunde.")
        return

    knr_for_redigering = data[0]
    main_window.oppdater_navigasjon(["Hoved", "Kunder", f"Rediger kunde {knr_for_redigering}"])
    main_window.rydd_innhold()

    # Sender data til felt-oppretteren. Pass på rekkefølgen!
    # Hvis Telefon/Epost ble fjernet fra vis_kunder, må 'data' her justeres.
    felter = lag_kundefelter(main_window.innhold_frame, data) # data sendes med

    def lagre():
        verdier = {k: v.get() for k, v in felter.items()}
        # VIKTIG: valider_kundefelter må kanskje justeres
        feil = valider_kundefelter(verdier)
        if feil:
            vis_advarsel("Valideringsfeil", "\n".join(feil))
            return
        try:
            # Pass på at argumentene matcher oppdater_kunde i database_handler
            # og kolonnene i databasen.
            main_window.db.oppdater_kunde(
                knr_for_redigering, # Send med kundenummeret
                verdier["fornavn"],
                verdier["etternavn"],
                verdier["adresse"],
                verdier["postnr"],
                verdier.get("telefon", None), # Bruk .get med default hvis de kan mangle
                verdier.get("epost", None)
            )
            vis_kunder(main_window) # Gå tilbake til kundeoversikten
        except Exception as e:
            logging.error(f"Feil ved oppdatering av kunde {knr_for_redigering}: {e}", exc_info=True)
            vis_feil("Feil", f"Klarte ikke å oppdatere kunde: {e}")

    tk.Button(main_window.innhold_frame, text="Lagre", command=lagre).pack(pady=10)
    tk.Button(main_window.innhold_frame, text="Tilbake", command=lambda: vis_kunder(main_window)).pack(pady=5)

def lag_kundefelter(master, data=None):
    # VIKTIG: Sørg for at etiketter og keys matcher kolonnene i databasen
    # og det du forventer i sett_inn/oppdater_kunde.
    # Fjernet Telefon, E-post fra standardfeltene her, basert på varehusdb.sql.
    etiketter = ["Fornavn", "Etternavn", "Adresse", "Postnummer"]
    keys = ["fornavn", "etternavn", "adresse", "postnr"]
    # Hvis du *har* Telefon/Epost, legg dem til i listene over.

    entries = {}
    for i, label in enumerate(etiketter):
        tk.Label(master, text=label + ":").pack(anchor="w", padx=10)
        entry = tk.Entry(master)
        entry.pack(fill="x", padx=10, pady=2)
        if data:
            # data[0] er KNr, så vi starter indeksering fra data[1]
            if i + 1 < len(data): # Sjekk at indeksen finnes
                 entry.insert(0, data[i + 1])
        entries[keys[i]] = entry

    # Legg til Telefon og Epost manuelt hvis de skal være med,
    # siden de ikke var i standard etiketter/keys lenger.
    # Eksempel (hvis de finnes):
    # tk.Label(master, text="Telefon:").pack(anchor="w", padx=10)
    # telefon_entry = tk.Entry(master)
    # telefon_entry.pack(fill="x", padx=10, pady=2)
    # if data and len(data) > 5: telefon_entry.insert(0, data[5]) # Juster indeks ved behov
    # entries["telefon"] = telefon_entry
    #
    # tk.Label(master, text="E-post:").pack(anchor="w", padx=10)
    # epost_entry = tk.Entry(master)
    # epost_entry.pack(fill="x", padx=10, pady=2)
    # if data and len(data) > 6: epost_entry.insert(0, data[6]) # Juster indeks ved behov
    # entries["epost"] = epost_entry

    return entries