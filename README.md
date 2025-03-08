Tverrfaglig prosjekt for Gruppe 1 i database og programmering

1.
installer python-dotenv og mysql database connector.
pip install python-dotenv
pip install mysql.connector

2.
lag en fil som heter .env, info i denne filen blir ikke synkronisert til github så du trenger ikke dele din info
i denne legger du inn 

De skal stå på egne linjer, vet ikke hvorfor github viser de slik, klikk edit eller raw for å kopiere.
DB_USER=din bruker
DB_PASSWORD=ditt passord
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=varehusdb
