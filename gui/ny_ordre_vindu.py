# gui/ny_ordre_vindu.py
# -*- coding: utf-8 -*-
# Vindu for å registrere en ny ordre

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from decimal import Decimal
from datetime import date

# Importer hjelpefunksjoner og feilmeldinger
try:
    from utils.feedback import vis_feil, vis_advarsel
except ImportError:
    logging.error("Kunne ikke importere feedback-modul. Bruker messagebox direkte.")
    def vis_feil(tittel, melding): messagebox.showerror(tittel, melding)
    def vis_advarsel(tittel, melding): messagebox.showwarning(tittel, melding)

try:
    # Antar at gui_helpers.py finnes i gui-mappen
    from gui.gui_helpers import formater_tall_norsk
except ImportError:
    logging.error("Kunne ikke importere gui_helpers. Tallformatering vil mangle.")
    # Fallback - enkel formatering uten tusenskille
    def formater_tall_norsk(verdi, desimaler=2):
        try: return f"{float(str(verdi).replace(',', '.')):.{desimaler}f}".replace('.', ',')
        except: return str(verdi)

def vis_ny_ordre_form(main_window):
    """ Åpner et Toplevel-vindu for å registrere en ny ordre. """

    win_ny_ordre = tk.Toplevel(main_window.root)
    win_ny_ordre.title("Registrer ny ordre")
    win_ny_ordre.geometry("850x650")
    win_ny_ordre.transient(main_window.root)
    win_ny_ordre.grab_set()
    win_ny_ordre.focus_set()

    db = main_window.db # Snarvei

    # --- Data-lagring for dette vinduet ---
    midlertidige_ordrelinjer = [] # Liste av dicts for linjer
    kunde_map = {} # Map: "KNr: Etternavn, Fornavn" -> KNr
    vare_map = {} # Map: "VNr: Betegnelse (pris kr)" -> {'vnr': VNr, 'navn': Betegnelse, 'pris': Pris(Decimal)}

    # --- Hent data for Comboboxes ---
    try:
        logging.info("Henter kunde- og vareliste for ny ordre-skjema...")
        kunde_liste_raadata = db.hent_kunde_liste()
        vare_liste_raadata = db.hent_vare_liste()

        if not kunde_liste_raadata: raise ValueError("Fant ingen kunder.")
        if not vare_liste_raadata: raise ValueError("Fant ingen varer.")

        kunde_display_list = []
        for knr, navn in kunde_liste_raadata:
            display = f"{knr}: {navn}"
            kunde_display_list.append(display)
            kunde_map[display] = int(knr)

        vare_display_list = []
        for vnr, betegnelse, pris in vare_liste_raadata:
            pris_decimal = Decimal(pris) if pris is not None else Decimal('0.00')
            display = f"{vnr}: {betegnelse} ({formater_tall_norsk(pris_decimal)} kr)"
            vare_display_list.append(display)
            vare_map[display] = {'vnr': vnr, 'navn': betegnelse, 'pris': pris_decimal}
        logging.info("Kunde- og vareliste lastet OK.")

    except Exception as e:
        logging.exception("Klarte ikke hente kunde/vare-data for ny ordre-skjema.")
        vis_feil("Feil ved lasting", f"Kunne ikke laste nødvendig data:\n{e}")
        win_ny_ordre.destroy()
        return

    # --- Hjelpefunksjoner for dette vinduet ---

    def _oppdater_total_sum_label():
        total = sum(linje['linjesum'] for linje in midlertidige_ordrelinjer)
        total_sum_label.config(text=f"Totalsum: {formater_tall_norsk(total)} kr")

    def _legg_til_linje():
        valgt_vare_display = vare_combo.get()
        antall_str = antall_entry.get().strip()

        if not valgt_vare_display: vis_advarsel("Mangler valg", "Vennligst velg en vare."); return
        if not antall_str: vis_advarsel("Mangler antall", "Vennligst skriv inn antall."); return

        try:
            antall = int(antall_str)
            if antall <= 0: raise ValueError()
        except ValueError: vis_advarsel("Ugyldig antall", "Antall må være et positivt heltall."); return

        if valgt_vare_display not in vare_map: vis_feil("Feil", "Ugyldig vare valgt."); return

        vare_info = vare_map[valgt_vare_display]
        vnr, navn, pris = vare_info['vnr'], vare_info['navn'], vare_info['pris']
        linjesum = pris * Decimal(antall)

        # Sjekk om varen finnes, oppdater antall hvis ja
        for i, eksisterende_linje in enumerate(midlertidige_ordrelinjer):
            if eksisterende_linje['vnr'] == vnr:
                 if messagebox.askyesno("Vare finnes", f"{navn} er allerede lagt til.\nVil du øke antallet med {antall}?"):
                      nytt_antall = eksisterende_linje['antall'] + antall
                      ny_linjesum = pris * Decimal(nytt_antall)
                      midlertidige_ordrelinjer[i].update({'antall': nytt_antall, 'linjesum': ny_linjesum})
                      tree_item_id = linje_tree.get_children()[i]
                      linje_tree.item(tree_item_id, values=(vnr, navn, nytt_antall, formater_tall_norsk(pris), formater_tall_norsk(ny_linjesum)))
                      _oppdater_total_sum_label()
                      vare_combo.set(''); antall_entry.delete(0, tk.END); antall_entry.insert(0,"1")
                 return

        # Legg til ny linje
        ny_linje_data = {'vnr': vnr, 'navn': navn, 'antall': antall, 'pris': pris, 'linjesum': linjesum}
        midlertidige_ordrelinjer.append(ny_linje_data)
        linje_tree.insert("", tk.END, values=(vnr, navn, antall, formater_tall_norsk(pris), formater_tall_norsk(linjesum)))
        _oppdater_total_sum_label()
        vare_combo.set(''); antall_entry.delete(0, tk.END); antall_entry.insert(0,"1")
        vare_combo.focus_set()

    def _fjern_linje():
        selected_items = linje_tree.selection()
        if not selected_items: vis_advarsel("Ingen valgt", "Velg linje(r) for å fjerne."); return
        if not messagebox.askyesno("Bekreft fjerning", f"Fjerne {len(selected_items)} valgt(e) linje(r)?"): return

        items_to_process = list(selected_items) # Lag kopi for å iterere trygt
        vnrs_removed = set()
        for item_id in items_to_process:
            try:
                values = linje_tree.item(item_id, 'values')
                if values: vnrs_removed.add(values[0]) # VNr er på indeks 0
                linje_tree.delete(item_id)
            except tk.TclError: # Item finnes kanskje ikke lenger hvis multi-select
                 pass

        # Oppdater datastrukturen ved å fjerne basert på VNr
        nonlocal midlertidige_ordrelinjer # Nødvendig for å modifisere listen i ytre scope
        midlertidige_ordrelinjer = [linje for linje in midlertidige_ordrelinjer if linje['vnr'] not in vnrs_removed]

        _oppdater_total_sum_label()
        logging.info(f"Fjernet {len(items_to_process)} ordrelinje(r).")

    def _lagre_ordre():
        valgt_kunde_display = kunde_combo.get()
        ordre_dato_str = dato_entry.get().strip()

        if not valgt_kunde_display or valgt_kunde_display not in kunde_map: vis_advarsel("Mangler kunde", "Velg en kunde."); return
        if not ordre_dato_str: vis_advarsel("Mangler dato", "Skriv inn ordredato (YYYY-MM-DD)."); return
        # Legg til bedre dato-validering her?
        try: date.fromisoformat(ordre_dato_str)
        except ValueError: vis_advarsel("Ugyldig dato", "Bruk format YYYY-MM-DD."); return
        if not midlertidige_ordrelinjer: vis_advarsel("Tom ordre", "Legg til minst én varelinje."); return

        kunde_nr = kunde_map[valgt_kunde_display]
        ordre_linjer_for_db = [(linje['vnr'], linje['antall'], linje['pris']) for linje in midlertidige_ordrelinjer]

        if not messagebox.askyesno("Bekreft Lagring", f"Lagre ordre for {valgt_kunde_display.split(': ')[1]} med {len(ordre_linjer_for_db)} linje(r)?"): return

        try:
            logging.info(f"Forsøker å lagre ny ordre for kunde {kunde_nr}...")
            nytt_ordre_nr = db.lagre_ny_ordre(kunde_nr, ordre_dato_str, ordre_linjer_for_db)

            if nytt_ordre_nr:
                logging.info(f"Ordre {nytt_ordre_nr} lagret successfully.")
                messagebox.showinfo("Ordre lagret", f"Ordre med nummer {nytt_ordre_nr} ble lagret.")
                win_ny_ordre.destroy()
                from gui.order_view import vis_ordrer # Sen import
                vis_ordrer(main_window) # Oppdater hovedvisning
            else:
                vis_feil("Lagringsfeil", "Klarte ikke å lagre ordren (ukjent feil).")
        except Exception as e:
            logging.exception(f"Feil ved lagring av ny ordre for kunde {kunde_nr}")
            vis_feil("Lagringsfeil", f"En feil oppstod under lagring:\n{e}")

    def _avbryt():
        if not midlertidige_ordrelinjer or \
           messagebox.askyesno("Avbryt", "Er du sikker på at du vil avbryte?\nAlle ulagrede linjer vil gå tapt."):
            win_ny_ordre.destroy()

    # --- START PÅ GUI-LAYOUT ---
    main_frame = tk.Frame(win_ny_ordre, padx=10, pady=10)
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Toppramme for kunde og dato
    top_frame = tk.Frame(main_frame)
    top_frame.pack(fill=tk.X, pady=(0, 10))

    tk.Label(top_frame, text="Kunde:").grid(row=0, column=0, padx=(0, 5), pady=5, sticky="w")
    kunde_combo = ttk.Combobox(top_frame, values=kunde_display_list, width=40, state="readonly")
    kunde_combo.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    tk.Label(top_frame, text="Ordredato:").grid(row=0, column=2, padx=(10, 5), pady=5, sticky="w")
    dato_var = tk.StringVar(value=date.today().strftime('%Y-%m-%d'))
    dato_entry = tk.Entry(top_frame, textvariable=dato_var, width=12)
    dato_entry.grid(row=0, column=3, padx=5, pady=5, sticky="w")
    top_frame.columnconfigure(1, weight=1) # La kunde-combo vokse

    # Ramme for å legge til linjer
    add_line_frame = tk.LabelFrame(main_frame, text="Legg til varelinje", padx=10, pady=10)
    add_line_frame.pack(fill=tk.X, pady=10)

    tk.Label(add_line_frame, text="Vare:").grid(row=0, column=0, padx=(0, 5), pady=5, sticky="w")
    vare_combo = ttk.Combobox(add_line_frame, values=vare_display_list, width=50, state="readonly")
    vare_combo.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    tk.Label(add_line_frame, text="Antall:").grid(row=0, column=2, padx=(10, 5), pady=5, sticky="w")
    antall_var = tk.StringVar(value="1")
    antall_entry = tk.Entry(add_line_frame, textvariable=antall_var, width=5)
    antall_entry.grid(row=0, column=3, padx=5, pady=5, sticky="w")
    # Bind Enter til å legge til linje
    antall_entry.bind("<Return>", lambda event: _legg_til_linje())

    add_button = tk.Button(add_line_frame, text="Legg til linje", command=_legg_til_linje)
    add_button.grid(row=0, column=4, padx=(10, 0), pady=5)
    add_line_frame.columnconfigure(1, weight=1)

    # Treeview for ordrelinjer
    tree_frame = tk.Frame(main_frame)
    tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

    linje_tree = ttk.Treeview(tree_frame, show="headings", height=10)
    linje_tree_cols = ("VNr", "Navn", "Antall", "Enhetspris", "Linjesum")
    linje_tree["columns"] = linje_tree_cols

    linje_tree.heading("VNr", text="VNr"); linje_tree.column("VNr", width=60, anchor="w")
    linje_tree.heading("Navn", text="Varenavn"); linje_tree.column("Navn", width=250, anchor="w")
    linje_tree.heading("Antall", text="Antall"); linje_tree.column("Antall", width=60, anchor="center")
    linje_tree.heading("Enhetspris", text="Pris"); linje_tree.column("Enhetspris", width=80, anchor="e")
    linje_tree.heading("Linjesum", text="Sum"); linje_tree.column("Linjesum", width=90, anchor="e")

    vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=linje_tree.yview)
    linje_tree.configure(yscrollcommand=vsb.set)
    vsb.pack(side='right', fill='y')
    linje_tree.pack(side='left', fill='both', expand=True)

    # Knapper for ordrelinjer + totalsum
    line_action_frame = tk.Frame(main_frame)
    line_action_frame.pack(fill=tk.X)

    remove_button = tk.Button(line_action_frame, text="Fjern valgt linje", command=_fjern_linje)
    remove_button.pack(side=tk.LEFT, padx=(0, 10))

    total_sum_label = tk.Label(line_action_frame, text="Totalsum: 0,00 kr", font=("Arial", 11, "bold"))
    total_sum_label.pack(side=tk.RIGHT)

    # Knapper for Lagre/Avbryt
    action_frame = tk.Frame(main_frame)
    action_frame.pack(pady=(15, 0))

    save_button = tk.Button(action_frame, text="Lagre Ordre", width=15, command=_lagre_ordre, bg="#D0F0D0") # Lys grønn
    save_button.pack(side=tk.LEFT, padx=10)

    cancel_button = tk.Button(action_frame, text="Avbryt", width=15, command=_avbryt)
    cancel_button.pack(side=tk.LEFT, padx=10)

    # Initial oppdatering av totalsum
    _oppdater_total_sum_label()

    # Sett fokus på kunde-comboboxen ved start
    kunde_combo.focus_set()

    # Håndter lukking av vinduet med Avbryt-logikken
    win_ny_ordre.protocol("WM_DELETE_WINDOW", _avbryt)