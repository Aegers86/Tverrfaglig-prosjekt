# gui/ny_kunde_vindu.py
import tkinter as tk
from tkinter import messagebox
import logging

try:
    from utils.validators import valider_kundefelter
    from utils.feedback import vis_feil, vis_advarsel
except ImportError:
    def valider_kundefelter(verdier): return []
    def vis_feil(tittel, melding): messagebox.showerror(tittel, melding)
    def vis_advarsel(tittel, melding): messagebox.showwarning(tittel, melding)

def vis_ny_kunde_vindu(main_window):
    main_window.oppdater_navigasjon(["Hoved", "Kunder", "Ny kunde"])
    main_window.rydd_innhold()
    main_window.status_label.config(text="Legg til ny kunde")

    felter, is_active_var = _lag_kundefelter(main_window.innhold_frame)

    def lagre_kunde():
        verdier = {k: v.get().strip() for k, v in felter.items()}
        is_active = bool(is_active_var.get())  # ✅ Hent ut som bool separat
        feil = valider_kundefelter(verdier)
        if feil:
            vis_advarsel("Valideringsfeil", "\n".join(feil))
            return
        try:
            main_window.db.sett_inn_kunde(
                verdier["fornavn"],
                verdier["etternavn"],
                verdier["adresse"],
                verdier["postnr"],
                None,  # telefon
                None,  # epost
                is_active=is_active
            )
            logging.info("Ny kunde lagret.")
            from gui.kunde_vindu import vis_kunder
            vis_kunder(main_window)
        except Exception as e:
            logging.error(f"Feil ved lagring av kunde: {e}", exc_info=True)
            vis_feil("Feil", f"Klarte ikke å lagre kunde: {e}")

    knapp_frame = tk.Frame(main_window.innhold_frame)
    knapp_frame.pack(pady=10)

    tk.Button(knapp_frame, text="Lagre", command=lagre_kunde).pack(side="left", padx=5)
    tk.Button(knapp_frame, text="Tilbake", command=lambda: _tilbake_til_kunder(main_window)).pack(side="left", padx=5)

def _lag_kundefelter(master, data=None):
    felt_definisjoner = [
        ("Fornavn", "fornavn"),
        ("Etternavn", "etternavn"),
        ("Adresse", "adresse"),
        ("Postnummer", "postnr"),
    ]

    entries = {}
    container = tk.Frame(master)
    container.pack(fill="x", padx=10, pady=5)

    for i, (label, key) in enumerate(felt_definisjoner):
        lbl = tk.Label(container, text=label + ":")
        lbl.grid(row=i, column=0, sticky="w", padx=5, pady=2)
        entry = tk.Entry(container)
        entry.grid(row=i, column=1, sticky="ew", padx=5, pady=2)
        entries[key] = entry

    # Avkrysningsboks for aktiv kunde
    is_active_var = tk.IntVar(value=1)
    chk = tk.Checkbutton(container, text="Aktiv kunde", variable=is_active_var)
    chk.grid(row=len(felt_definisjoner), column=0, columnspan=2, sticky="w", padx=5, pady=5)

    container.columnconfigure(1, weight=1)
    return entries, is_active_var

def _tilbake_til_kunder(main_window):
    from gui.kunde_vindu import vis_kunder
    vis_kunder(main_window)
