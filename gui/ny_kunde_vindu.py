# gui/ny_kunde_vindu.py

import tkinter as tk
from tkinter import messagebox
import logging

# Importer validering og feilmeldingsfunksjoner
try:
    from utils.validators import valider_kundefelter
    from utils.feedback import vis_feil, vis_advarsel
except ImportError:
    def valider_kundefelter(verdier): return []
    def vis_feil(tittel, melding): messagebox.showerror(tittel, melding)
    def vis_advarsel(tittel, melding): messagebox.showwarning(tittel, melding)

def vis_ny_kunde_vindu(main_window):
    """ Viser vindu for å legge til ny kunde. """
    main_window.oppdater_navigasjon(["Hoved", "Kunder", "Ny kunde"])
    main_window.rydd_innhold()
    main_window.status_label.config(text="Legg til ny kunde")

    felter = _lag_kundefelter(main_window.innhold_frame)

    def lagre_kunde():
        verdier = {k: v.get().strip() for k, v in felter.items()}
        feil = valider_kundefelter(verdier)
        if feil:
            vis_advarsel("Valideringsfeil", "\n".join(feil))
            return
        try:
            main_window.db.sett_inn_kunde(
                verdier["fornavn"], verdier["etternavn"],
                verdier["adresse"], verdier["postnr"],
                verdier.get("telefon"), verdier.get("epost")
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
    """ Lager feltene for kundeinfo. """
    felt_definisjoner = [
        ("Fornavn", "fornavn"),
        ("Etternavn", "etternavn"),
        ("Adresse", "adresse"),
        ("Postnummer", "postnr"),
        # ("Telefon", "telefon"), # Legg til hvis ønskelig
        # ("E-post", "epost"),
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

    container.columnconfigure(1, weight=1)
    return entries

def _tilbake_til_kunder(main_window):
    """ Går tilbake til kundeoversikten. """
    from gui.kunde_vindu import vis_kunder
    vis_kunder(main_window)
