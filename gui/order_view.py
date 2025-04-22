# gui/order_view.py
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, messagebox # Importer messagebox
from utils.feedback import vis_feil, vis_advarsel # Antar disse finnes
import logging # Importer logging
from decimal import Decimal # Importer Decimal for nøyaktig summering
from pdf_generator import PDFGenerator # Importer PDFGenerator

# --- Start på komplett vis_ordrer ---
def vis_ordrer(main_window):
    # Setter brødsmulesti
    main_window.oppdater_navigasjon(["Hoved", "Ordre"])
    main_window.status_label.config(text="Laster ordre...")
    main_window.rydd_innhold()

    try:
        # Henter ordre med korrekte kolonnenavn fra varehusdb.sql
        query = "SELECT OrdreNr, OrdreDato, SendtDato, BetaltDato, KNr FROM ordre ORDER BY OrdreDato DESC;"
        data = main_window.db.hent_alle(query)
    except Exception as e:
        logging.error(f"Feil ved henting av ordreliste: {e}", exc_info=True)
        vis_feil("Databasefeil", f"Feil ved henting av ordre: {e}")
        main_window.status_label.config(text="Feil ved lasting av ordre")
        return

    # Setter opp Treeview for ordrelisten
    tree = ttk.Treeview(main_window.innhold_frame, show="headings")
    # Kolonnenavn som matcher SELECT-spørringen og varehusdb.sql
    tree_columns = ("OrdreNr", "OrdreDato", "SendtDato", "BetaltDato", "KNr")
    tree["columns"] = tree_columns

    # Definerer kolonneoverskrifter og -bredder
    tree.heading("OrdreNr", text="Ordrenr")
    tree.column("OrdreNr", width=80, anchor="center")
    tree.heading("OrdreDato", text="Ordredato")
    tree.column("OrdreDato", width=100, anchor="center")
    tree.heading("SendtDato", text="Sendt dato")
    tree.column("SendtDato", width=100, anchor="center")
    tree.heading("BetaltDato", text="Betalt dato")
    tree.column("BetaltDato", width=100, anchor="center")
    tree.heading("KNr", text="Kundenr")
    tree.column("KNr", width=80, anchor="center")

    # Fyller Treeview med data
    data_length = 0 # Holder styr på antall rader
    if data:
        for row in data:
            # Formater datoer for penere visning (hvis de ikke allerede er strenger)
            formatted_row = list(row) # Konverter tuple til liste for å endre
            # Anta datoer er på indeks 1, 2, 3
            for i in [1, 2, 3]:
                 if formatted_row[i] is not None and not isinstance(formatted_row[i], str):
                     try:
                        formatted_row[i] = formatted_row[i].strftime('%Y-%m-%d') # Eksempelformat
                     except AttributeError:
                         pass # La den være hvis den ikke har strftime (f.eks. allerede streng)
            tree.insert("", "end", values=tuple(formatted_row)) # Konverter tilbake til tuple
            data_length += 1
    else:
        # Ingen data funnet
        pass

    tree.pack(fill="both", expand=True, padx=10, pady=10)
    # Binder dobbelklikk til å vise ordredetaljer
    tree.bind("<Double-1>", lambda event: vis_ordredetaljer(main_window, tree))

    # Ramme for knapper under listen
    knapp_frame_ordre = tk.Frame(main_window.innhold_frame)
    knapp_frame_ordre.pack(pady=5)
    # Knappen for å gå tilbake til hovedmenyen
    tk.Button(knapp_frame_ordre, text="Til Hovedmeny", command=main_window.vis_startside).pack(pady=5)

    # Oppdaterer statuslabel
    status_text = f"Ordre lastet ({data_length} stk). Dobbelklikk for detaljer." if data else "Ingen ordre funnet."
    main_window.status_label.config(text=status_text)
# --- Slutt på komplett vis_ordrer ---


# --- Start på komplett vis_ordredetaljer (med Decimal-fiks og faktura-knapp) ---
def vis_ordredetaljer(main_window, tree):
    selected = tree.selection()
    if not selected:
        vis_advarsel("Ingen valgt", "Velg en ordre for detaljer.")
        return

    ordre_data_display = tree.item(selected[0], "values") # Data fra ordrelisten
    if not ordre_data_display:
        vis_feil("Feil", "Kunne ikke hente data for valgt ordre.")
        return

    ordre_nr = ordre_data_display[0] # OrdreNr er første kolonne
    # Setter brødsmulesti for detaljsiden
    main_window.oppdater_navigasjon(["Hoved", "Ordre", f"Ordre {ordre_nr}"])
    main_window.status_label.config(text=f"Laster detaljer for ordre {ordre_nr}...")
    main_window.rydd_innhold()

    # Hent data for visning i Treeview
    try:
        query_detaljer_display = """
            SELECT VNr, PrisPrEnhet, Antall, (PrisPrEnhet * Antall) as Sum
            FROM ordrelinje
            WHERE OrdreNr = %s;
            """
        detaljer_display = main_window.db.hent_alle(query_detaljer_display, (ordre_nr,))
    except Exception as e:
        logging.error(f"Feil ved henting av ordrelinjer for visning for ordre {ordre_nr}: {e}", exc_info=True)
        vis_feil("Databasefeil", f"Kunne ikke hente ordrelinjer for visning: {e}")
        main_window.status_label.config(text=f"Feil ved lasting av detaljer for ordre {ordre_nr}")
        return

    # Sett opp Treeview for ordrelinjer
    tree_detaljer = ttk.Treeview(main_window.innhold_frame, show="headings")
    tree_detaljer_columns = ("VNr", "Enhetspris", "Antall", "Sum")
    tree_detaljer["columns"] = tree_detaljer_columns

    # Definerer kolonneoverskrifter og -bredder
    tree_detaljer.heading("VNr", text="Varenr")
    tree_detaljer.column("VNr", width=80, anchor="center")
    tree_detaljer.heading("Enhetspris", text="Enhetspris")
    tree_detaljer.column("Enhetspris", width=100, anchor="e")
    tree_detaljer.heading("Antall", text="Antall")
    tree_detaljer.column("Antall", width=80, anchor="center")
    tree_detaljer.heading("Sum", text="Sum")
    tree_detaljer.column("Sum", width=100, anchor="e")

    # Summerer totalbeløp og fyller Treeview
    total_sum = Decimal('0.00') # Initialiserer som Decimal
    if detaljer_display:
        for row in detaljer_display:
            # Konverterer Decimal til formatert streng for visning
            # Sjekker for None før formatering
            enhetspris_str = f"{Decimal(row[1]):.2f}" if row[1] is not None else "N/A"
            sum_str = f"{Decimal(row[3]):.2f}" if row[3] is not None else "N/A"

            formatted_row = (
                row[0], # VNr
                enhetspris_str,
                row[2], # Antall
                sum_str
            )
            tree_detaljer.insert("", "end", values=formatted_row)
            # Summerer med Decimal-objekter
            if row[3] is not None:
                try:
                    total_sum += Decimal(row[3]) # Sikrer at vi summerer Decimal
                except Exception as sum_err:
                     logging.warning(f"Kunne ikke summere verdi {row[3]} for ordre {ordre_nr}: {sum_err}")


    tree_detaljer.pack(fill="both", expand=True, padx=10, pady=10)

    # Viser totalsummen
    label_sum = tk.Label(main_window.innhold_frame, text=f"Totalsum: {total_sum:.2f} kr", font=("Arial", 12, "bold"))
    label_sum.pack(pady=5)

    # --- Funksjon for fakturaknapp ---
    def _generer_faktura_pdf():
        main_window.status_label.config(text=f"Genererer faktura for ordre {ordre_nr}...")
        try:
            # Hent nødvendig data for fakturaen
            # a) Ordre-hode (hent relevante kolonner)
            ordre_query = "SELECT OrdreNr, OrdreDato, SendtDato, BetaltDato, KNr FROM ordre WHERE OrdreNr = %s"
            ordre = main_window.db.hent_en(ordre_query, (ordre_nr,))
            if not ordre:
                vis_feil("Feil", f"Fant ikke ordredata for ordre {ordre_nr}")
                main_window.status_label.config(text=f"Feil: Fant ikke ordre {ordre_nr}")
                return

            # b) Kundeinfo (hent relevante kolonner)
            kunde_nr = ordre[4] # Antar KNr er 5. element (indeks 4)
            kunde_query = "SELECT KNr, Fornavn, Etternavn, Adresse, PostNr FROM kunde WHERE KNr = %s"
            kunde = main_window.db.hent_en(kunde_query, (kunde_nr,))
            if not kunde:
                vis_feil("Feil", f"Fant ikke kundedata for kunde {kunde_nr}")
                main_window.status_label.config(text=f"Feil: Fant ikke kunde {kunde_nr}")
                return

            # c) Ordrelinjer (med varenavn for beskrivelse)
            query_pdf_linjer = """
                SELECT ol.VNr, ol.OrdreNr, ol.PrisPrEnhet, ol.Antall, v.Betegnelse
                FROM ordrelinje ol
                JOIN vare v ON ol.VNr = v.VNr
                WHERE ol.OrdreNr = %s;
                """
            ordrelinjer_pdf = main_window.db.hent_alle(query_pdf_linjer, (ordre_nr,))
            if not ordrelinjer_pdf:
                vis_feil("Feil", f"Fant ingen ordrelinjer for ordre {ordre_nr}")
                main_window.status_label.config(text=f"Feil: Fant ingen ordrelinjer for {ordre_nr}")
                return

            # d) Fakturanummer (enkel løsning)
            faktura_nummer = f"FA-{ordre_nr}"

            # Generer PDF
            pdf_gen = PDFGenerator()
            pdf_gen.generate_invoice(ordre, ordrelinjer_pdf, kunde, faktura_nummer)

            messagebox.showinfo("Suksess", f"Faktura 'faktura_{ordre_nr}.pdf' er generert!")
            main_window.status_label.config(text=f"Faktura for ordre {ordre_nr} generert.")

        except FileNotFoundError as fnf_error:
             logging.error(f"Filafeil ved generering av faktura for ordre {ordre_nr}: {fnf_error}", exc_info=True)
             # Spesifikk feilmelding for manglende logo
             if 'static/logo.png' in str(fnf_error):
                 vis_feil("Feil", f"Kunne ikke generere faktura: Finner ikke logo-filen 'static/logo.png'. Sørg for at filen finnes.")
             else:
                 vis_feil("Feil", f"Kunne ikke generere faktura: Finner ikke en nødvendig fil ({fnf_error}).")
             main_window.status_label.config(text=f"Feil ved generering av faktura for ordre {ordre_nr}")

        except ImportError as imp_error:
             logging.error(f"Importfeil ved generering av faktura: {imp_error}", exc_info=True)
             vis_feil("Feil", f"Kunne ikke generere faktura: Mangler nødvendig bibliotek ({imp_error}). Kjør 'pip install reportlab'?")
             main_window.status_label.config(text=f"Feil: Mangler bibliotek for fakturagenerering")

        except Exception as e:
            logging.error(f"Generell feil ved generering av faktura for ordre {ordre_nr}: {e}", exc_info=True)
            vis_feil("Feil", f"Kunne ikke generere faktura: {e}")
            main_window.status_label.config(text=f"Feil ved generering av faktura for ordre {ordre_nr}")

    # Ramme for knapper under detaljvisningen
    knapp_frame_detaljer = tk.Frame(main_window.innhold_frame)
    knapp_frame_detaljer.pack(pady=10)

    # Knapp for å gå tilbake til ordrelisten
    tilbake_btn = tk.Button(knapp_frame_detaljer, text="Tilbake til ordreoversikt", command=lambda: vis_ordrer(main_window))
    tilbake_btn.pack(side="left", padx=10)

    # Knapp for å generere faktura
    faktura_btn = tk.Button(knapp_frame_detaljer, text="Generer Faktura", command=_generer_faktura_pdf)
    faktura_btn.pack(side="left", padx=10)

    # Oppdaterer statuslabel
    main_window.status_label.config(text=f"Detaljer for ordre {ordre_nr} lastet.")
# --- Slutt på komplett vis_ordredetaljer ---