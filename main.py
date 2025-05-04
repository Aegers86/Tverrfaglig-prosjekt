# main.py
import logging # Legg til logging import
from gui.hoved_vindu import MainWindow

# Konfigurer logging for GUI-appen (valgfritt men lurt)
# Du kan justere filnavn og nivå
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s",
                    filename="gui_app.log") # Egen loggfil for GUI?

def main():
    logging.info("Starter GUI-applikasjon...") # Logg oppstart
    try: # Legg til try/except rundt GUI-start også
        app = MainWindow()
        app.run()
        logging.info("GUI-applikasjon avsluttet normalt.") # Logg avslutning
    except Exception as gui_err:
        logging.critical(f"KRITISK FEIL under kjøring av GUI: {gui_err}", exc_info=True)
        # Vis feilmelding til brukeren hvis mulig
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw() # Skjul tomt rotvindu
            messagebox.showerror("Applikasjonsfeil", f"En kritisk feil oppstod:\n{gui_err}\n\nSjekk gui_app.log for detaljer.")
            root.destroy()
        except:
            print(f"KRITISK FEIL under kjøring av GUI: {gui_err}")


if __name__ == "__main__":
    main()