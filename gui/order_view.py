# gui/order_view.py
# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
import logging
from decimal import Decimal

# --- Import av hjelpefunksjoner ---
try:
    from utils.feedback import vis_feil, vis_advarsel
    from gui.gui_helpers import sort_treeview_column, formater_dato_norsk
except ImportError:
    def vis_feil(tittel, melding): messagebox.showerror(tittel, melding)
    def vis_advarsel(tittel, melding): messagebox.showwarning(tittel, melding)
    def sort_treeview_column(tree, col, reverse): pass
    def formater_dato_norsk(dato_str): return dato_str

# --- Import av PDFGenerator ---
try:
    from utils.pdf_generator import PDFGenerator
    PDF_GENERATOR_AVAILABLE = True
except ImportError:
    PDF_GENERATOR_AVAILABLE = False
    class PDFGenerator: pass

# --- Søker og laster ordrer ---
def _perform_order_search(main_window, search_entry, tree):
    search_term = search_entry.get().strip()
    try:
        for i in tree.get_children(): tree.delete(i)
    except tk.TclError: pass

    try:
        base_query = """
            SELECT o.OrdreNr, o.OrdreDato, o.SendtDato, o.BetaltDato, o.KNr,
                   CONCAT(k.Fornavn, ' ', k.Etternavn) AS Kundenavn
            FROM ordre o JOIN kunde k ON o.KNr = k.KNr
        """
        where_clause = ""
        params = []
        if search_term:
            pattern = f"%{search_term}%"
            where_clause = """
                WHERE CAST(o.OrdreNr AS CHAR) LIKE %s
                   OR CAST(o.KNr AS CHAR) LIKE %s
                   OR k.Fornavn LIKE %s
                   OR k.Etternavn LIKE %s
                   OR CONCAT(k.Fornavn, ' ', k.Etternavn) LIKE %s
            """
            params = [pattern] * 5

        final_query = base_query + where_clause + " ORDER BY o.OrdreDato DESC;"
        data = main_window.db.hent_alle(final_query, tuple(params))

        data_length = 0
        for row in data:
            if isinstance(row, dict):
                values = (
                    row.get('OrdreNr'),
                    formater_dato_norsk(row.get('OrdreDato')),
                    formater_dato_norsk(row.get('SendtDato')),
                    formater_dato_norsk(row.get('BetaltDato')),
                    row.get('KNr'),
                    row.get('Kundenavn')
                )
                tree.insert("", "end", values=values)
                data_length += 1

        if search_term:
            status_text = f"Søkeresultat for '{search_term}': {data_length} treff."
        else:
            status_text = f"Alle ordre ({data_length} stk) lastet."
        main_window.status_label.config(text=status_text)

    except Exception as e:
        logging.error(f"Feil under henting av ordre: {e}", exc_info=True)
        vis_feil("Databasefeil", f"Feil under henting av ordre: {e}")

# --- Placeholder-funksjon for "Legg til ordre" ---
def _vis_ny_ordre_form(main_window):
    """ Placeholder: Viser en melding om at funksjonen ikke er implementert. """
    logging.info("Bruker trykket 'Legg til ordre' - funksjon ikke implementert ennå.")
    messagebox.showinfo("Kommer snart", "Funksjonalitet for å legge til ny ordre er ikke implementert ennå.\nDette krever et nytt skjema og database-logikk.")
    # Neste steg: Implementer gui/ny_ordre_vindu.py og kall den herfra.

# --- Viser ordreoversikten ---
def vis_ordrer(main_window):
    from gui.vis_ordredetaljer_vindu import åpne_ordredetaljer_vindu  # Import her for å unngå sirkulær import

    main_window.oppdater_navigasjon(["Hoved", "Ordre"])
    main_window.status_label.config(text="Laster ordrevisning...")
    main_window.rydd_innhold()

    # Søkefelt
    search_frame = tk.Frame(main_window.innhold_frame)
    search_frame.pack(fill="x", padx=10, pady=(5, 0))
    tk.Label(search_frame, text="Søk (Ordrenr, Kundenr, Navn):").pack(side="left", padx=(0, 5))
    search_entry = tk.Entry(search_frame)
    search_entry.pack(side="left", fill="x", expand=True, padx=5)

    # Tabell
    tree = ttk.Treeview(main_window.innhold_frame, show="headings")
    tree_columns = ("OrdreNr", "OrdreDato", "SendtDato", "BetaltDato", "KNr", "Kundenavn")
    tree["columns"] = tree_columns

    for col in tree_columns:
        tree.heading(col, text=col, command=lambda c=col: sort_treeview_column(tree, c, False))
        tree.column(col, width=100, anchor="w")
    tree.column("OrdreNr", width=80, anchor="center")
    tree.column("KNr", width=60, anchor="center")
    tree.pack(fill="both", expand=True, padx=10, pady=10)

    # 🎯 Legg til dobbeltklikk-binding på treet
    tree.bind("<Double-1>", lambda event: åpne_ordredetaljer_vindu(main_window, tree))

    # Søke-knapp
    search_button = tk.Button(search_frame, text="Søk",
                              command=lambda: _perform_order_search(main_window, search_entry, tree))
    search_button.pack(side="left", padx=(5, 0))
    search_entry.bind("<Return>", lambda event: _perform_order_search(main_window, search_entry, tree))

    # Legg til ordre-knapp
    tk.Button(main_window.innhold_frame, text="Legg til ordre",
              command=lambda: vis_feil("Kommer", "Funksjonen Legg til ordre er ikke ferdig."))\
        .pack(pady=5)

    # Laster inn initiale ordrer
    _perform_order_search(main_window, search_entry, tree)

# --- Start på komplett vis_ordredetaljer ---
def vis_ordredetaljer(main_window, tree):
    """ Viser detaljer for en valgt ordre og mulighet for fakturagenerering. """
    selected = tree.selection()
    if not selected:
        vis_advarsel("Ingen valgt", "Velg en ordre for detaljer.")
        return

    ordre_data_display = tree.item(selected[0], "values")
    if not ordre_data_display or len(ordre_data_display) < 1:
        vis_feil("Feil", "Kunne ikke hente data for valgt ordre.")
        return

    try:
        ordre_nr = int(ordre_data_display[0])
    except (ValueError, TypeError, IndexError):
         vis_feil("Feil", "Kunne ikke identifisere valgt ordrenummer.")
         return

    main_window.oppdater_navigasjon(["Hoved", "Ordre", f"Ordre {ordre_nr}"])
    main_window.status_label.config(text=f"Laster detaljer for ordre {ordre_nr}...")
    main_window.rydd_innhold()

    try:
        # Henter ordrelinjer for visning
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

    # Treeview for ordrelinjer
    tree_detaljer = ttk.Treeview(main_window.innhold_frame, show="headings")
    tree_detaljer_columns = ("VNr", "Enhetspris", "Antall", "Sum")
    tree_detaljer["columns"] = tree_detaljer_columns

    tree_detaljer.heading("VNr", text="Varenr"); tree_detaljer.column("VNr", width=80, anchor="center")
    tree_detaljer.heading("Enhetspris", text="Enhetspris"); tree_detaljer.column("Enhetspris", width=100, anchor="e")
    tree_detaljer.heading("Antall", text="Antall"); tree_detaljer.column("Antall", width=80, anchor="center")
    tree_detaljer.heading("Sum", text="Sum"); tree_detaljer.column("Sum", width=100, anchor="e")

    total_sum = Decimal('0.00')
    if detaljer_display:
        for row in detaljer_display:
            # Formaterer tall for visning
            enhetspris_str = f"{Decimal(row[1]):.2f}" if row[1] is not None else "N/A"
            sum_str = f"{Decimal(row[3]):.2f}" if row[3] is not None else "N/A"
            formatted_row = (row[0], enhetspris_str, row[2], sum_str)
            tree_detaljer.insert("", "end", values=formatted_row)
            # Summerer med Decimal
            if row[3] is not None:
                try: total_sum += Decimal(row[3])
                except Exception as sum_err: logging.warning(f"Kunne ikke summere verdi {row[3]} for ordre {ordre_nr}: {sum_err}")

    tree_detaljer.pack(fill="both", expand=True, padx=10, pady=10)

    # Viser totalsum
    label_sum = tk.Label(main_window.innhold_frame, text=f"Totalsum: {total_sum:.2f} kr", font=("Arial", 12, "bold"))
    label_sum.pack(pady=5)

    # --- Funksjon for fakturaknapp ---
    def _generer_faktura_pdf():
        if not PDF_GENERATOR_AVAILABLE:
             vis_feil("Feil", "PDFGenerator-modulen er ikke tilgjengelig.")
             main_window.status_label.config(text="Feil: PDFGenerator mangler")
             return

        main_window.status_label.config(text=f"Genererer faktura for ordre {ordre_nr}...")
        try:
            # Hent data for faktura
            ordre_query = "SELECT OrdreNr, OrdreDato, SendtDato, BetaltDato, KNr FROM ordre WHERE OrdreNr = %s"
            ordre = main_window.db.hent_en(ordre_query, (ordre_nr,))
            if not ordre: raise ValueError(f"Fant ikke ordredata for ordre {ordre_nr}")

            kunde_nr = ordre[4]
            kunde_query = "SELECT KNr, Fornavn, Etternavn, Adresse, PostNr FROM kunde WHERE KNr = %s"
            kunde = main_window.db.hent_en(kunde_query, (kunde_nr,))
            if not kunde: raise ValueError(f"Fant ikke kundedata for kunde {kunde_nr}")

            query_pdf_linjer = """
                SELECT ol.VNr, ol.OrdreNr, ol.PrisPrEnhet, ol.Antall, v.Betegnelse
                FROM ordrelinje ol JOIN vare v ON ol.VNr = v.VNr WHERE ol.OrdreNr = %s;
                """
            ordrelinjer_pdf = main_window.db.hent_alle(query_pdf_linjer, (ordre_nr,))
            if not ordrelinjer_pdf: raise ValueError(f"Fant ingen ordrelinjer for ordre {ordre_nr}")

            faktura_nummer = f"FA-{ordre_nr}" # Enkel løsning

            pdf_gen = PDFGenerator()
            pdf_gen.generate_invoice(ordre, ordrelinjer_pdf, kunde, faktura_nummer)

            messagebox.showinfo("Suksess", f"Faktura 'faktura_{ordre_nr}.pdf' er generert!")
            main_window.status_label.config(text=f"Faktura for ordre {ordre_nr} generert.")

        except FileNotFoundError as fnf_error:
             logging.error(f"Filafeil: {fnf_error}", exc_info=True)
             if 'static/logo.png' in str(fnf_error): vis_feil("Feil", "Finner ikke logo-filen 'static/logo.png'.")
             else: vis_feil("Feil", f"Finner ikke fil ({fnf_error}).")
             main_window.status_label.config(text=f"Feil ved generering")
        except ValueError as val_err:
             logging.error(f"Datafeil: {val_err}", exc_info=True)
             vis_feil("Feil", f"Kunne ikke generere faktura: {val_err}")
             main_window.status_label.config(text=f"Feil: Manglende data")
        except Exception as e:
            logging.error(f"Generell feil: {e}", exc_info=True)
            error_msg = f"Kunne ikke generere faktura ({type(e).__name__}: {e})"
            vis_feil("Feil", error_msg)
            main_window.status_label.config(text=f"Feil ved generering")

    # Ramme for knapper under detaljvisningen
    knapp_frame_detaljer = tk.Frame(main_window.innhold_frame)
    knapp_frame_detaljer.pack(pady=10)

    tilbake_btn = tk.Button(knapp_frame_detaljer, text="Tilbake til ordreoversikt", command=lambda: vis_ordrer(main_window))
    tilbake_btn.pack(side="left", padx=10)

    faktura_btn_state = tk.NORMAL if PDF_GENERATOR_AVAILABLE else tk.DISABLED
    faktura_btn = tk.Button(knapp_frame_detaljer, text="Generer Faktura", command=_generer_faktura_pdf, state=faktura_btn_state)
    faktura_btn.pack(side="left", padx=10)
    if not PDF_GENERATOR_AVAILABLE:
         tk.Label(knapp_frame_detaljer, text="(PDF-modul mangler)", fg="grey").pack(side="left")

    main_window.status_label.config(text=f"Detaljer for ordre {ordre_nr} lastet.")
# --- Slutt på komplett vis_ordredetaljer ---