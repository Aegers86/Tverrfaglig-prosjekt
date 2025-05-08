# 🏆 Tverrfaglig Prosjekt – Gruppe 1  
 
**Respons på PROG/DB Tverrfaglig prosjekt Start oppgave**
 
📅 **Innleveringsfrist:** 25. mai 23:59

📌 **Fag:** Programmering (PROG) og Database (DB)
  
---



## 📝 Prosjektbeskrivelse  
 
Dette prosjektet er en løsning på den tverrfaglige startoppgaven i PROG/DB.
Vi har utviklet en GUI-basert applikasjon i Python som kobler seg til en MySQL-database for håndtering av handel og lager.
Applikasjonen muliggjør visning, søk, og enkel administrasjon av varelager, ordrer og kunder.

 
### **Prosjektet inkluderer:**  
 
✔️ **GUI:** Utviklet med **Tkinter** for et brukervennlig grensesnitt.

✔️ **Databasekommunikasjon:** Bruker **MySQL Connector/Python** for å samhandle med databasen ved hjelp av SQL-spørringer.

✔️ **Stored Procedures:** Implementert for spesifikke databaseoperasjoner, som f.eks. henting av kunder.

✔️ **SQL-injection beskyttelse:** Parametriserte spørringer benyttes for å forhindre SQL-injection angrep.

✔️ **Feilhåndtering og Input-validering:** Robust koding med `try...except` blokker og enkel validering av brukerinput for å hindre utilsiktede stopp og sikre dataintegritet.

✔️ **API-integrasjon:** En enkel web-API er laget med **Flask** for å vise varelageret i en nettleser.

✔️ **PDF-generering:** Funksjonalitet for å generere fakturaer i PDF-format er implementert (valgfritt krav).

---

  
## 📂 Installasjon og oppsett  
 
Følg disse trinnene for å sette opp og kjøre applikasjonen lokalt:

### **1. Klon repositoriet**
  
```bash
git clone [https://github.com/Aegers86/Tverrfaglig-prosjekt](https://github.com/Aegers86/Tverrfaglig-prosjekt)
cd Tverrfaglig-prosjekt
 ```

 
### **2. Installer nødvendige pakker**

```bash
pip install -r requirements.txt
 ```


### **3. Konfigurer miljøvariabler**  
 
Opprett en .env-fil i prosjektets rotmappe og legg inn din databaseinformasjon:

```ini
 
DB_USER=ditt_brukernavn
 
DB_PASSWORD=ditt_passord
 
DB_HOST=127.0.0.1
 
DB_PORT=3306
 
DB_NAME=varehusdb
 
```

 
### **4. Sett opp databasen**  
Opprett databasen ved hjelp av .sql-filen fra skoleoppgaven i din MySQL-server.
Kjør deretter Python-skriptet database/update_db_faktura.py for å legge til nødvendige tabeller (faktura) og kolonnen is_active i kunde-tabellen, samt oppdatere stored procedure for kunder.

```bash
python database/update_db_faktura.py
 ```

  
### **5. Start applikasjonen**  
Applikasjonen består av to deler: GUI og en valgfri web-API.

Start GUI-applikasjonen: Åpne en terminal i PyCharm (eller ditt foretrukne miljø med virtuelt miljø aktivert) og kjør:

```bash
 python Program.py
```

Start Web-API'en (valgfritt): Hvis du ønsker å se varelageret i en nettleser, åpne en ny terminal i samme virtuelle miljø og kjør:

```bash
 
python app.py
 
```
API-en vil da være tilgjengelig (standard: http://127.0.0.1:5000/).
 
---
 

## 📌 Funksjonalitet i applikasjonen (GUI) 
Tilbyr følgende funksjoner via GUI-grensesnittet:

### 🔹 **Varelager**  
 
- Viser en liste over alle varer på lager, inkludert varenummer, navn, antall og pris.
  Varelageret kan også vises i en nettleser via den medfølgende web-APIen (/ endepunktet), med automatisk oppdatering hvert 60. sekund.  

### 🔹 **Ordrer**  
 
- Viser en liste over alle ordrer i databasen.
- Ved å dobbeltklikke på en spesifikk ordre, vises detaljer om varene i ordren (varenummer, beskrivelse, pris per enhet, antall, sum for varelinjen), samt informasjon om kunden (navn, adresse) og ordrens totalpris.

### 🔹 **Kunder**  
 
- Viser en liste over alle aktive kunder registrert i databasen ved hjelp av en "Stored Procedure".
- Applikasjonen har også funksjonalitet for å legge til nye kunder og for å "fjerne" (deaktivere) eksisterende kunder.
  
### 🔹 **Generer faktura**  
 
- For en valgt ordre kan det genereres en faktura i PDF-format.
- En unik faktura-ID genereres og lagres i databasen for hver faktura.
- Fakturaen inkluderer en spesifisert MVA-sats (25%).
 
 
---
 
 
## 🛠 **Teknologi og bibliotek brukt**  
 
- **Python 3.11+**  
 
- **Tkinter:** (GUI)  
 
- **mysql-connector-python:** (Databaseforbindelse)  
 
- **python-dotenv:** For lasting av miljøvariabler fra en .env fil.  
 
- **reportlab:** (For PDF-generering av fakturaer)  
 
- **Flask:** Mikro-rammeverk for web (brukt til API).

- **flask-mysqldb:** Integrasjon mellom Flask og MySQL.
 
---
 

 
## 📊 **Databaseoppsett**  
 

 
### **Tabeller i databasen:**  
 
- **`kunde`** (kunderegister, utvidet med is_active kolonne)  
 
- **`vare`** (produktlager)  
 
- **`ordre`** (ordrehistorikk)  
 
- **`ordrelinje`** (varer i hver ordre)  
 
- **`faktura `** (lagrer genererte faktura-ID'er knyttet til ordrer og kunder)  
 
### **Eksempel på Stored Procedure brukt (hent_alle_kunder):**  
 
```sql
 
DELIMITER $$
CREATE PROCEDURE hent_alle_kunder()
BEGIN
    SELECT KNr, Fornavn, Etternavn, Adresse, Postnr FROM varehusdb.kunde WHERE is_active = 1;
END$$
DELIMITER ;
 
```
