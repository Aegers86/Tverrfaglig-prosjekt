from flask import Flask, render_template_string                                                                         #Importerer Flask og benytter HTML fra en streng og ikke en  ekstern fil.
from flask_mysqldb import MySQL                                                                                         #Importerer MySQL klassen fra FLASK
import os                                                                                                               #Importerer os for å kunne aksessere .env parameter.
from dotenv import load_dotenv                                                                                          #Benyttes for å laste variablene i .env filen inn i app.py

load_dotenv()                                                                                                           #Benyttes for å laste variablene i .env filen og benytte senere i koden.
app = Flask(__name__)                                                                                                   #Lager en Flask applikasjon.

app.config["MYSQL_USER"] = os.getenv("DB_USER")                                                                         #Henter info fra .env filen for å angi brukernavn knyttet mot database.
app.config["MYSQL_PASSWORD"] = os.getenv("DB_Password")                                                                 #Henter info fra .env filen for å angi passord knyttet mot database.
app.config["MYSQL_HOST"] = os.getenv("DB_HOST")                                                                         #Henter info fra .env filen for å angi host knyttet mot database.
app.config["MYSQL_PORT"] = int(os.getenv("DB_PORT"))                                                                    #Henter info fra .env filen for å angi nettverks knyttet mot database, må være i integer ellers feiler applikasjonen.
app.config["MYSQL_DB"] = os.getenv("DB_NAME")                                                                           #Henter info fra .env filen for å angi databasen som skal benyttes.
mysql = MySQL(app)                                                                                                      #Starter MySQL og knytter det mot Flask applikasjonen.

#HTML kode for hjemmesiden til varelageret, er satt opp til å oppdateres hvert minutt.
HTML_TEMPLATE = """
<!DOCTYPE html>                                                                                                         
<html>
<head>
    <title>Varelager</title>                                                                                            
    <meta http-equiv="refresh" content="60">                                                                            
    <style>                                                                                                             
        table {border-collapse: collapse; width: 90%; margin: 20px auto;}                                               
        th, td {border: 1px solid #888; padding: 10px 14px; text-align: left;}
        th {background-color: #33ffdd;}
        h1 {text-align: center; font-family: calibri;} 
     </style>
</head>
<body>
    <h1>Varelager</h1>
    <table>
        <thead>
            <tr>
                <th>Varenummer</th>
                <th>Betegnelse</th>
                <th>Antall</th>
                <th>Pris</th>
            </tr>
        <thead>
        <tbodyZ
            {% for vare in varer %}
            <tr>
                <td>{{vare.Vnr}}</td>
                <td>{{vare.Betegnelse}}</td>
                <td>{{vare.Antall}}</td>
                <td>{{vare.Pris}}</td>
            <tr>
            {%endfor%}
        </tbody>
    </table>
</body>
</html>
"""

@app.route("/")                                                                                                         #Angir hjemmesiden sin path i dette tilfellet eksempelvis 127.0.0.1:5000/
def varerlager_html():                                                                                                  #Funksjon som angir websiden.
    cur = mysql.connection.cursor()                                                                                     #Benyttes for å sende forespørsel til databasen for å kjøre en SQL forespørsel.
    cur.execute("SELECT Vnr, Betegnelse, Antall, Pris FROM vare")                                                       #Benyttes for å hente data fra tabellen vare i databasen
    varelager_data = cur.fetchall()                                                                                     #Lager dataforespørselen fra databasen som en tuple liste.
    cur.close()                                                                                                         #Lukker databaseforbindelsen
    varer = [{"Vnr": row[0], "Betegnelse": row[1], "Antall": row[2], "Pris": float(row[3])}for row in varelager_data]   #Benyttes for å konvertere dataene til en dictionary.
    return render_template_string(HTML_TEMPLATE, varer=varer)                                                           #Flask funksjon for å lage HTML siden og returnere den til klienten.

if __name__ == "__main__":                                                                                              #Kjører koden når man starter applikasjonen.
    app.run(debug=False)                                                                                                #Kjører applikasjonen, debug er satt til False da dette er i produksjon.
