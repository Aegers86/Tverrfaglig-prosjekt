# gui/kunde_vindu.py
import tkinter as tk
from tkinter import ttk, messagebox
import logging
from decimal import Decimal, InvalidOperation

# Sørg for at disse utils-filene finnes og er korrekte
try:
    from utils.validators import valider_kundefelter
    from utils.feedback import vis_feil, vis_advarsel
except ImportError:
    def valider_kundefelter(verdier): return []
    def vis_feil(tittel, melding): messagebox.showerror(tittel, melding)
    def vis_advarsel(tittel, melding): messagebox.showwarning(tittel, melding)

# --- START PÅ sorteringsfunksjon ---
def sort_treeview_column(tree, col, reverse):
    try:
        data_list = []
        column_ids = tree["columns"]
        col_index = column_ids.index(col)

        for child_id in tree.get_children(''):
            value = tree.item(child_id, 'values')[col_index]
            try:
                numeric_value = int(value)
            except (ValueError, TypeError):
                try:
                    numeric_value = Decimal(value.replace(',', '.'))
                except (InvalidOperation, ValueError, TypeError):
                    numeric_value = str(value).lower()
            data_list.append((numeric_value, child_id))

        data_list.sort(key=lambda item: item[0], reverse=reverse)
        for index, (val, child_id) in enumerate(data_list):
            tree.move(child_id, '', index)

        tree.heading(col, command=lambda _col=col: sort_treeview_column(tree, _col, not reverse))
    except Exception as e:
        logging.error(f"Feil under sortering av kolonne '{col}': {e}", exc_info=True)

# --- Søker og laster kunder ---
def _perform_customer_search(main_window, search_entry, tree):
    search_term = search_entry.get().strip()
    try:
        for i in tree.get_children(): tree.delete(i)
    except tk.TclError: pass

    try:
        if not search_term:
            data = main_window.db.kall_prosedyre("hent_alle_kunder")
            status_text_suffix = "kunder lastet."
        else:
            query = """
                SELECT KNr, Fornavn, Etternavn, Adresse, PostNr FROM kunde
                WHERE CAST(KNr AS CHAR) LIKE %s OR Fornavn LIKE %s OR Etternavn LIKE %s
                   OR CONCAT(Fornavn, ' ', Etternavn) LIKE %s
                ORDER BY Etternavn ASC, Fornavn ASC;
            """
            pattern = f"%{search_term}%"
            data = main_window.db.hent_alle(query, (pattern, pattern, pattern, pattern))
            status_text_suffix = f"kunder funnet for '{search_term}'."

        # ✅ Her mapper vi dictionary til tuple for Treeview
        data_length = 0
        for row in data:
            if isinstance(row, dict):
                values = (row.get('KNr'), row.get('Fornavn'), row.get('Etternavn'), row.get('Adresse'), row.get('PostNr'))
                tree.insert("", "end", values=values)
                data_length += 1

        main_window.status_label.config(text=f"{data_length} {status_text_suffix}")

    except Exception as e:
        logging.error(f"Feil under kundesøk: {e}", exc_info=True)
        vis_feil("Databasefeil", f"Feil under henting/søk etter kunder: {e}")
        main_window.status_label.config(text="Feil under kundelasting")

# --- Viser kundeoversikten ---
def vis_kunder(main_window):
    main_window.oppdater_navigasjon(["Hoved", "Kunder"])
    main_window.status_label.config(text="Laster kundevisning...")
    main_window.rydd_innhold()

    search_frame = tk.Frame(main_window.innhold_frame)
    search_frame.pack(fill="x", padx=10, pady=(5,0))
    tk.Label(search_frame, text="Søk (Kundenr, Navn):").pack(side="left", padx=(0,5))
    search_entry = tk.Entry(search_frame)
    search_entry.pack(side="left", fill="x", expand=True, padx=5)
    search_button = tk.Button(search_frame, text="Søk",
                              command=lambda: _perform_customer_search(main_window, search_entry, tree))
    search_button.pack(side="left", padx=(5,0))
    search_entry.bind("<Return>", lambda event: _perform_customer_search(main_window, search_entry, tree))

    tree = ttk.Treeview(main_window.innhold_frame, show="headings")
    tree_columns = ("KNr", "Fornavn", "Etternavn", "Adresse", "PostNr")
    tree["columns"] = tree_columns

    for col in tree_columns:
        tree.heading(col, text=col, command=lambda c=col: sort_treeview_column(tree, c, False))
        tree.column(col, width=120, anchor="w")

    tree.column("KNr", width=60, anchor="center")
    tree.column("PostNr", width=80, anchor="center")
    tree.pack(fill="both", expand=True, padx=10, pady=10)

    knapp_frame = tk.Frame(main_window.innhold_frame)
    knapp_frame.pack(pady=5)
    tk.Button(knapp_frame, text="Legg til kunde", command=lambda: nytt_kundevindu(main_window)).pack(side="left", padx=5)
    tk.Button(knapp_frame, text="Rediger valgt", command=lambda: rediger_kunde(main_window, tree)).pack(side="left", padx=5)

    _perform_customer_search(main_window, search_entry, tree)

# --- nytt_kundevindu ---
def nytt_kundevindu(main_window):
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
            logging.info("Ny kunde lagret.")
            vis_kunder(main_window)
        except Exception as e:
            logging.error(f"Feil ved lagring av kunde: {e}", exc_info=True)
            vis_feil("Feil", f"Klarte ikke å lagre kunde: {e}")

    knapp_frame = tk.Frame(main_window.innhold_frame)
    knapp_frame.pack(pady=10)

    tk.Button(knapp_frame, text="Lagre", command=lagre).pack(side="left", padx=5)
    tk.Button(knapp_frame, text="Tilbake", command=lambda: vis_kunder(main_window)).pack(side="left", padx=5)

# --- rediger_kunde ---
def rediger_kunde(main_window, tree):
    selected = tree.selection()
    if not selected:
        vis_advarsel("Ingen valgt", "Velg en kunde du vil redigere.")
        return

    data = tree.item(selected[0], "values")
    if not data:
        vis_feil("Feil", "Ingen data å redigere.")
        return

    knr = int(data[0])

    main_window.oppdater_navigasjon(["Hoved", "Kunder", f"Rediger kunde {knr}"])
    main_window.rydd_innhold()
    main_window.status_label.config(text=f"Redigerer kunde {knr}")

    felter = lag_kundefelter(main_window.innhold_frame, data)

    def lagre():
        verdier = {k: v.get().strip() for k, v in felter.items()}
        feil = valider_kundefelter(verdier)
        if feil:
            vis_advarsel("Valideringsfeil", "\n".join(feil))
            return
        try:
            main_window.db.oppdater_kunde(
                knr,
                verdier["fornavn"], verdier["etternavn"],
                verdier["adresse"], verdier["postnr"],
                verdier.get("telefon"), verdier.get("epost")
            )
            logging.info(f"Kunde {knr} oppdatert.")
            vis_kunder(main_window)
        except Exception as e:
            logging.error(f"Feil ved oppdatering av kunde: {e}", exc_info=True)
            vis_feil("Feil", f"Klarte ikke å oppdatere kunde: {e}")

    knapp_frame = tk.Frame(main_window.innhold_frame)
    knapp_frame.pack(pady=10)

    tk.Button(knapp_frame, text="Lagre endringer", command=lagre).pack(side="left", padx=5)
    tk.Button(knapp_frame, text="Tilbake", command=lambda: vis_kunder(main_window)).pack(side="left", padx=5)

# --- lag_kundefelter ---
def lag_kundefelter(master, data=None):
    felt_definisjoner = [
        ("Fornavn", "fornavn"),
        ("Etternavn", "etternavn"),
        ("Adresse", "adresse"),
        ("Postnummer", "postnr"),
        # ("Telefon", "telefon"), # Hvis du vil utvide
        # ("E-post", "epost")
    ]

    entries = {}
    container = tk.Frame(master)
    container.pack(fill="x", padx=10, pady=5)

    for i, (label, key) in enumerate(felt_definisjoner):
        lbl = tk.Label(container, text=label + ":")
        lbl.grid(row=i, column=0, sticky="w", padx=5, pady=2)
        entry = tk.Entry(container)
        entry.grid(row=i, column=1, sticky="ew", padx=5, pady=2)

        if data and i+1 < len(data) and data[i+1]:
            entry.insert(0, data[i+1])

        entries[key] = entry

    container.columnconfigure(1, weight=1)
    return entries