# gui/order_view.py
# -*- coding: utf-8 -*-

import tkinter as tk
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

import logging # Importer logging
from decimal import Decimal, InvalidOperation # Importer Decimal for nøyaktig summering

# Prøv å importere PDFGenerator, sett flagg
try:
    # Sørg for at pdf_generator.py ligger riktig til
    from pdf_generator import PDFGenerator
    PDF_GENERATOR_AVAILABLE = True
    logging.info("PDFGenerator importert OK.")
except ImportError as e:
    logging.warning(f"Kunne ikke importere PDFGenerator: {e}. Fakturagenerering vil være utilgjengelig.")
    PDF_GENERATOR_AVAILABLE = False
    # Definer en dummy klasse for å unngå NameError hvis linteren *krever* det
    class PDFGenerator: pass
except Exception as e:
    logging.error(f"Uventet feil ved import av PDFGenerator: {e}", exc_info=True)
    PDF_GENERATOR_AVAILABLE = False
    class PDFGenerator: pass

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
                         # Anta at priser/summer kan ha komma, erstatt før Decimal
                         numeric_value = Decimal(str(value).replace(',', '.'))
                         data_list.append((numeric_value, child_id))
                    except (InvalidOperation, ValueError, TypeError):
                         # Sorter datoer (YYYY-MM-DD) eller annen tekst som strenger
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


# --- Hjelpefunksjon for ordresøk ---
def _perform_order_search(main_window, search_entry, tree):
    """ Henter ordre basert på søketerm og oppdaterer Treeview. """
    search_term = search_entry.get().strip()
    status_msg = f"Søker etter '{search_term}'..." if search_term else "Laster alle ordre..."
    main_window.status_label.config(text=status_msg)
    logging.info(status_msg)

    try:
        for i in tree.get_children(): tree.delete(i)
    except tk.TclError as e: logging.warning(f"Feil ved tømming av Treeview (ignorerer): {e}")

    try:
        base_query = """
            SELECT o.OrdreNr, o.OrdreDato, o.SendtDato, o.BetaltDato, o.KNr,
                   CONCAT(k.Fornavn, ' ', k.Etternavn) AS Kundenavn
            FROM ordre o JOIN kunde k ON o.KNr = k.KNr """
        where_clause = "" ; params = []
        if search_term:
            search_pattern = f"%{search_term}%"
            where_clause = """
                WHERE CAST(o.OrdreNr AS CHAR) LIKE %s OR CAST(o.KNr AS CHAR) LIKE %s
                   OR k.Fornavn LIKE %s OR k.Etternavn LIKE %s
                   OR CONCAT(k.Fornavn, ' ', k.Etternavn) LIKE %s """
            params = [search_pattern] * 5
        # Default sortering når man søker/laster inn på nytt
        final_query = base_query + where_clause + " ORDER BY o.OrdreDato DESC;"
        data = main_window.db.hent_alle(final_query, tuple(params))

        data_length = 0
        if data:
            for row in data:
                formatted_row = list(row)
                for i in [1, 2, 3]: # Datoindekser
                     if formatted_row[i] is not None and not isinstance(formatted_row[i], str):
                         try: formatted_row[i] = formatted_row[i].strftime('%Y-%m-%d')
                         except AttributeError: pass
                tree.insert("", "end", values=tuple(formatted_row))
                data_length += 1
        if search_term: status_text = f"Søkeresultat for '{search_term}': {data_length} treff. Dobbelklikk for detaljer."
        else: status_text = f"Alle ordre ({data_length} stk) lastet. Dobbelklikk for detaljer."
        main_window.status_label.config(text=status_text); logging.info(status_text)
    except Exception as e:
        logging.error(f"Feil under ordresøk etter '{search_term}': {e}", exc_info=True)
        vis_feil("Databasefeil", f"Feil under søk etter ordre: {e}")
        main_window.status_label.config(text="Feil under ordresøk")


# --- Start på komplett vis_ordrer (med sortering) ---
def vis_ordrer(main_window):
    """ Viser ordreoversikten med søkefunksjonalitet og kolonnesortering. """
    main_window.oppdater_navigasjon(["Hoved", "Ordre"])
    main_window.status_label.config(text="Laster inn ordrevisning...")
    main_window.rydd_innhold()

    search_frame = tk.Frame(main_window.innhold_frame)
    search_frame.pack(fill="x", padx=10, pady=(5, 0))
    tk.Label(search_frame, text="Søk (Ordrenr, Kundenr, Navn):").pack(side="left", padx=(0, 5))
    search_entry = tk.Entry(search_frame)
    search_entry.pack(side="left", fill="x", expand=True, padx=5)
    tree = ttk.Treeview(main_window.innhold_frame, show="headings")
    search_button = tk.Button(search_frame, text="Søk",
                              command=lambda: _perform_order_search(main_window, search_entry, tree))
    search_button.pack(side="left", padx=(5, 0))
    search_entry.bind("<Return>", lambda event: _perform_order_search(main_window, search_entry, tree))

    # Definer kolonne-IDer som sorteringsfunksjonen forventer
    tree_columns = ("OrdreNr", "OrdreDato", "SendtDato", "BetaltDato", "KNr", "Kundenavn")
    tree["columns"] = tree_columns

    # Legg til command for sortering på hver heading
    tree.heading("OrdreNr", text="Ordrenr", command=lambda c="OrdreNr": sort_treeview_column(tree, c, False))
    tree.column("OrdreNr", width=80, anchor="center")
    tree.heading("OrdreDato", text="Ordredato", command=lambda c="OrdreDato": sort_treeview_column(tree, c, False))
    tree.column("OrdreDato", width=100, anchor="center")
    tree.heading("SendtDato", text="Sendt dato", command=lambda c="SendtDato": sort_treeview_column(tree, c, False))
    tree.column("SendtDato", width=100, anchor="center")
    tree.heading("BetaltDato", text="Betalt dato", command=lambda c="BetaltDato": sort_treeview_column(tree, c, False))
    tree.column("BetaltDato", width=100, anchor="center")
    tree.heading("KNr", text="Kundenr", command=lambda c="KNr": sort_treeview_column(tree, c, False))
    tree.column("KNr", width=80, anchor="center")
    tree.heading("Kundenavn", text="Kundenavn", command=lambda c="Kundenavn": sort_treeview_column(tree, c, False))
    tree.column("Kundenavn", width=150, anchor="w")

    tree.pack(fill="both", expand=True, padx=10, pady=10)
    tree.bind("<Double-1>", lambda event: vis_ordredetaljer(main_window, tree))

    # Bunn-knapp er fjernet
    _perform_order_search(main_window, search_entry, tree) # Last inn alle initielt

# --- Slutt på komplett vis_ordrer ---


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

    # Treeview for ordrelinjer (INGEN sortering lagt til her - kan legges til om ønskelig)
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
            enhetspris_str = f"{Decimal(row[1]):.2f}" if row[1] is not None else "N/A"
            sum_str = f"{Decimal(row[3]):.2f}" if row[3] is not None else "N/A"
            formatted_row = (row[0], enhetspris_str, row[2], sum_str)
            tree_detaljer.insert("", "end", values=formatted_row)
            if row[3] is not None:
                try: total_sum += Decimal(row[3])
                except Exception as sum_err: logging.warning(f"Kunne ikke summere verdi {row[3]} for ordre {ordre_nr}: {sum_err}")

    tree_detaljer.pack(fill="both", expand=True, padx=10, pady=10)

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

            faktura_nummer = f"FA-{ordre_nr}"

            pdf_gen = PDFGenerator()
            pdf_gen.generate_invoice(ordre, ordrelinjer_pdf, kunde, faktura_nummer)

            messagebox.showinfo("Suksess", f"Faktura 'faktura_{ordre_nr}.pdf' er generert!")
            main_window.status_label.config(text=f"Faktura for ordre {ordre_nr} generert.")

        except FileNotFoundError as fnf_error:
             logging.error(f"Filafeil ved generering av faktura for ordre {ordre_nr}: {fnf_error}", exc_info=True)
             if 'static/logo.png' in str(fnf_error):
                 vis_feil("Feil", f"Finner ikke logo-filen 'static/logo.png'.")
             else:
                 vis_feil("Feil", f"Finner ikke fil ({fnf_error}).")
             main_window.status_label.config(text=f"Feil ved generering av faktura")
        except ValueError as val_err:
             logging.error(f"Datafeil ved generering av faktura for ordre {ordre_nr}: {val_err}", exc_info=True)
             vis_feil("Feil", f"Kunne ikke generere faktura: {val_err}")
             main_window.status_label.config(text=f"Feil: Manglende data for faktura")
        except Exception as e:
            logging.error(f"Generell feil ved generering av faktura for ordre {ordre_nr}: {e}", exc_info=True)
            error_msg = f"Kunne ikke generere faktura ({type(e).__name__}: {e})"
            vis_feil("Feil", error_msg)
            main_window.status_label.config(text=f"Feil ved generering av faktura")

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