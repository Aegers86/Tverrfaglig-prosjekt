# gui/vis_ordredetaljer_vindu.py

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from decimal import Decimal

try:
    from utils.pdf_generator import PDFGenerator
    PDF_GENERATOR_AVAILABLE = True
except ImportError:
    PDF_GENERATOR_AVAILABLE = False
    class PDFGenerator: pass

try:
    from utils.feedback import vis_feil, vis_advarsel
except ImportError:
    def vis_feil(tittel, melding): messagebox.showerror(tittel, melding)
    def vis_advarsel(tittel, melding): messagebox.showwarning(tittel, melding)

def åpne_ordredetaljer_vindu(main_window, tree):
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

    detaljer_vindu = tk.Toplevel(main_window.root)
    detaljer_vindu.title(f"Ordredetaljer - Ordre {ordre_nr}")
    detaljer_vindu.geometry("600x500")
    detaljer_vindu.transient(main_window.root)
    detaljer_vindu.grab_set()

    try:
        query = """
            SELECT VNr, PrisPrEnhet, Antall, (PrisPrEnhet * Antall) as Sum
            FROM ordrelinje
            WHERE OrdreNr = %s;
        """
        detaljer = main_window.db.hent_alle(query, (ordre_nr,))
    except Exception as e:
        logging.error(f"Feil ved henting av ordrelinjer: {e}", exc_info=True)
        vis_feil("Databasefeil", f"Feil ved henting av ordrelinjer: {e}")
        detaljer_vindu.destroy()
        return

    tree_detaljer = ttk.Treeview(detaljer_vindu, show="headings")
    tree_detaljer["columns"] = ("VNr", "Enhetspris", "Antall", "Sum")

    for col in tree_detaljer["columns"]:
        tree_detaljer.heading(col, text=col)
        tree_detaljer.column(col, width=100, anchor="center")

    total_sum = Decimal('0.00')
    if detaljer:
        for row in detaljer:
            enhetspris = row.get('PrisPrEnhet')
            summen = row.get('Sum')

            enhetspris_str = f"{Decimal(enhetspris):.2f}" if enhetspris is not None else "N/A"
            sum_str = f"{Decimal(summen):.2f}" if summen is not None else "N/A"

            tree_detaljer.insert("", "end", values=(
                row.get('VNr', 'N/A'), enhetspris_str, row.get('Antall', 'N/A'), sum_str
            ))

            if summen is not None:
                try:
                    total_sum += Decimal(summen)
                except Exception as e:
                    logging.warning(f"Summasjon feil: {summen}: {e}")

    tree_detaljer.pack(fill="both", expand=True, padx=10, pady=10)

    label_sum = tk.Label(detaljer_vindu, text=f"Totalsum: {total_sum:.2f} kr", font=("Arial", 12, "bold"))
    label_sum.pack(pady=5)

    def generer_faktura():
        if not PDF_GENERATOR_AVAILABLE:
            vis_feil("Feil", "PDFGenerator-modulen er ikke tilgjengelig.")
            return

        try:
            ordre_query = "SELECT OrdreNr, OrdreDato, SendtDato, BetaltDato, KNr FROM ordre WHERE OrdreNr = %s"
            ordre = main_window.db.hent_en(ordre_query, (ordre_nr,))
            if not ordre:
                vis_feil("Feil", "Fant ikke ordredata.")
                return

            kunde_nr = ordre.get('KNr')
            kunde_query = "SELECT KNr, Fornavn, Etternavn, Adresse, PostNr FROM kunde WHERE KNr = %s"
            kunde = main_window.db.hent_en(kunde_query, (kunde_nr,))
            if not kunde:
                vis_feil("Feil", "Fant ikke kundedata.")
                return

            faktura_id = main_window.db.insert_faktura(ordre_nr, kunde_nr)
            if not faktura_id or faktura_id == 0:
                vis_feil("Feil", "Kunne ikke opprette faktura.")
                return

            query_pdf_linjer = """
                SELECT ol.VNr, ol.OrdreNr, ol.PrisPrEnhet, ol.Antall, v.Betegnelse
                FROM ordrelinje ol JOIN vare v ON ol.VNr = v.VNr
                WHERE ol.OrdreNr = %s;
            """
            ordrelinjer_pdf = main_window.db.hent_alle(query_pdf_linjer, (ordre_nr,))
            if not ordrelinjer_pdf:
                vis_feil("Feil", "Fant ingen ordrelinjer.")
                return

            faktura_nummer = f"FA-{faktura_id}"
            pdf_gen = PDFGenerator()
            pdf_gen.generate_invoice(ordre, ordrelinjer_pdf, kunde, faktura_nummer)

            messagebox.showinfo("Suksess", f"Faktura '{faktura_nummer}.pdf' er generert!")
        except Exception as e:
            logging.error(f"Feil ved fakturagenerering: {e}", exc_info=True)
            vis_feil("Feil", f"Kunne ikke generere faktura: {e}")

    knapp_frame = tk.Frame(detaljer_vindu)
    knapp_frame.pack(pady=10)

    faktura_btn_state = tk.NORMAL if PDF_GENERATOR_AVAILABLE else tk.DISABLED
    tk.Button(knapp_frame, text="Generer Faktura", command=generer_faktura, state=faktura_btn_state).pack(side="left", padx=10)
    tk.Button(knapp_frame, text="Lukk", command=detaljer_vindu.destroy).pack(side="left", padx=10)

    detaljer_vindu.mainloop()
