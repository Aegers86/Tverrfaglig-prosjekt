# main.py
from gui.hoved_vindu import MainWindow
from database.database_checker import sjekk_og_opprett_is_active, sjekk_og_opprett_faktura_tabell

def main():
    try:
        sjekk_og_opprett_is_active()
        sjekk_og_opprett_faktura_tabell()  # 👈 utvidet sjekk
    except Exception as e:
        print(f"Feil ved databasetilpasning: {e}")
        return  # Stopper programmet hvis det er kritiske feil

    app = MainWindow()
    app.run()

if __name__ == "__main__":
    main()
