Tverrfaglig prosjekt for Gruppe 1 i database og programmering

1.
installer python-dotenv, mysql database connector og pdfkit.
pip install python-dotenv
pip install mysql.connector
pip install pdfkit

2.
lag en fil som heter .env, info i denne filen blir ikke synkronisert til github så du trenger ikke dele din info
i denne legger du inn 

De skal stå på egne linjer, vet ikke hvorfor github viser de slik, klikk edit eller raw for å kopiere.
DB_USER=din bruker
DB_PASSWORD=ditt passord
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=varehusdb

3.
pdf

https://wkhtmltopdf.org/downloads.html

4.
Lag en prosedyre for å hente alle kunder, dette gjøres i mysql workbench

create procedure hent_alle_kunder()
SELECT * 
FROM varehusdb.kunde;
