# 🏆 Tverrfaglig Prosjekt – Gruppe 1  
 
**Database- og programmeringsprosjekt**  
 

 

📅 **Innleveringsfrist:** 25. mai 23:59  
 

📌 **Fag:** Programmering (PROG) og Database (DB)  
 


 
---
 

 
## 📝 Prosjektbeskrivelse  
 
Dette prosjektet består av en GUI-basert applikasjon for håndtering av handel og lager.  
 
Applikasjonen kobler seg til en MySQL-database og gir brukerne mulighet til å vise,  
 
legge til og administrere kunder, ordrer og varelager.  
 

 
### **Prosjektet inkluderer:**  
 
- ✔️ GUI laget med **Tkinter**  
 
- ✔️ Databaseforbindelse med **MySQL**  
 
- ✔️ **Stored Procedures** for databaseoperasjoner  
 
- ✔️ **SQL-injection beskyttelse**  
 
- ✔️ **Feilhåndtering og input-validering**  
 
- ✔️ **API-integrasjon** for visning av varelager i en nettleser  
 
- ✔️ **PDF-generering** for fakturaer (valgfritt)  
 
- ✔️ Flask er brukt som rammeverk for webside/API
 
---
 

 
## 📂 Installasjon og oppsett  
 

 
### **1. Installer nødvendige pakker**  
 
Kjør følgende kommando for å installere alle avhengigheter:  
 

 
```bash
 
pip install -r requirements.txt
 
```
 

 
### **2. Konfigurer miljøvariabler**  
 
Opprett en `.env`-fil i rotmappen og legg inn følgende (juster verdier etter din database):  
 

 
```ini
 
DB_USER=ditt_brukernavn
 
DB_PASSWORD=ditt_passord
 
DB_HOST=127.0.0.1
 
DB_PORT=3306
 
DB_NAME=varehusdb
 
```
 

 
### **3. Sett opp databasen**  
 
Bruk .sql fil fra skole oppgava  
  
### **4. Start applikasjonen**  
 

 
```bash
 
python app.py
 
```
 

 
---
 

 
## 📌 Funksjonalitet i applikasjonen  
 

 
### 🔹 **Hjemmeside**  
 
- Viser nøkkeltall: Antall kunder, ordrer, varer, betalte og ubetalte fakturaer.  
 

 
### 🔹 **Varelager**  
 
- Viser en liste over varer med varenummer, navn, pris og antall.  
 

 
### 🔹 **Ordrer**  
 
- Viser alle ordrer med detaljer om dato, status og kunde.  
 
- Mulighet for å velge en ordre og se detaljer om varer, priser og totalbeløp.  
 

 
### 🔹 **Kunder**  
 
- Viser alle kunder registrert i databasen.  
 
- Bruker **Stored Procedure** for å hente kundelisten.  
 

 
### 🔹 **Generer faktura (valgfritt)**  
 
- Genererer en faktura i PDF-format for en valgt ordre.  
 

 
### 🔹 **Dark Mode**  
 
- Brukeren kan velge mellom lys og mørk modus.  
 

 
---
 

 
## 🛠 **Teknologi og bibliotek brukt**  
 
- **Python 3.11**  
 
- **Tkinter** (GUI)  
 
- **mysql-connector-python** (Databaseforbindelse)  
 
- **python-dotenv** (Miljøvariabler)  
 
- **pdfkit** (For PDF-generering av fakturaer)  
 

 
---
 

 
## 📊 **Databaseoppsett**  
 

 
### **Tabeller i databasen:**  
 
- **`kunde`** (kunderegister)  
 
- **`vare`** (produktlager)  
 
- **`ordre`** (ordrehistorikk)  
 
- **`ordrelinje`** (varer i hver ordre)  
 

 
### **Stored Procedure brukt:**  
 
```sql
 
CREATE PROCEDURE hent_alle_kunder()
 
SELECT * FROM varehusdb.kunde;
 
```
