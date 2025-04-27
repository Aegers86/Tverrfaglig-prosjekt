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

    felter, is_active_var = _lag_kundefelter(main_window.innhold_frame, kunde_data)

    def lagre_endringer():
        verdier = {k: v.get().strip() for k, v in felter.items()}
        is_active = bool(is_active_var.get())

        feil = valider_kundefelter(verdier)
        if feil:
            vis_advarsel("Valideringsfeil", "\n".join(feil))
            return
        try:
            main_window.db.oppdater_kunde(
                knr,
                verdier["fornavn"],
                verdier["etternavn"],
                verdier["adresse"],
                verdier["postnr"],
                None,
                None,
                is_active=is_active
            )
            logging.info(f"Kunde {knr} oppdatert.")

            # --- Vis status etter lagring ---
            status = main_window.db.hent_en(
                "SELECT is_active FROM kunde WHERE KNr = %s;",
                (knr,)
            )
            if status:
                aktiv = status.get("is_active")
                print(f"Etter oppdatering: Kunde {knr} aktiv status i databasen er: {aktiv}")
            else:
                print(f"⚠️ Klarte ikke hente status for kunde {knr} etter oppdatering.")

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

    # Avkrysningsboks for Aktiv/Passiv status
    is_active_var = tk.IntVar(value=1)
    if data and len(data) > 5:
        is_active_var.set(1 if str(data[5]) in ("1", "True", "true") else 0)

    chk = tk.Checkbutton(container, text="Aktiv kunde", variable=is_active_var)
    chk.grid(row=len(felt_definisjoner), column=0, columnspan=2, sticky="w", padx=5, pady=5)

    container.columnconfigure(1, weight=1)
    return entries, is_active_var

def _tilbake_til_kunder(main_window):
    from gui.kunde_vindu import vis_kunder
    vis_kunder(main_window)
