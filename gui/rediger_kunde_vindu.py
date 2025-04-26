# gui/rediger_kunde_vindu.py

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

def vis_rediger_kunde_vindu(main_window, kunde_data):
    """ Åpner vindu for å redigere valgt kunde. """
    if not kunde_data:
        vis_feil("Feil", "Ingen data for valgt kunde.")
        return

    knr = int(kunde_data[0])

    main_window.oppdater_navigasjon(["Hoved", "Kunder", f"Rediger kunde {knr}"])
    main_window.rydd_innhold()
    main_window.status_label.config(text=f"Redigerer kunde {knr}")

    felter = _lag_kundefelter(main_window.innhold_frame, kunde_data)

    def lagre_endringer():
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
            from gui.kunde_vindu import vis_kunder
            vis_kunder(main_window)
        except Exception as e:
            logging.error(f"Feil ved oppdatering av kunde: {e}", exc_info=True)
            vis_feil("Feil", f"Klarte ikke å oppdatere kunde: {e}")

    knapp_frame = tk.Frame(main_window.innhold_frame)
    knapp_frame.pack(pady=10)

    tk.Button(knapp_frame, text="Lagre endringer", command=lagre_endringer).pack(side="left", padx=5)
    tk.Button(knapp_frame, text="Tilbake", command=lambda: _tilbake_til_kunder(main_window)).pack(side="left", padx=5)

def _lag_kundefelter(master, data=None):
    """ Lager feltene for kundeinfo med eksisterende data. """
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

        if data and i + 1 < len(data) and data[i + 1]:
            entry.insert(0, data[i + 1])

        entries[key] = entry

    container.columnconfigure(1, weight=1)
    return entries

def _tilbake_til_kunder(main_window):
    from gui.kunde_vindu import vis_kunder
    vis_kunder(main_window)
