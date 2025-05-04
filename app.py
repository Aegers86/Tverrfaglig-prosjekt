from flask_mysqldb import MySQL
from flask import Flask, render_template_string
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Configure your MySQL connection
app.config['MYSQL_USER'] = os.getenv('DB_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('DB_PASSWORD')
app.config['MYSQL_HOST'] = os.getenv('DB_HOST')
app.config['MYSQL_PORT'] = int(os.getenv('DB_PORT', 3306))  # Default to 3306 if not found
app.config['MYSQL_DB'] = os.getenv('DB_NAME')
mysql = MySQL(app)

# HTML-mal som inneholder en enkel tabell
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Varelager</title>
    <style>
        table { border-collapse: collapse; width: 70%; margin: 20px auto; }
        th, td { border: 1px solid #888; padding: 8px 12px; text-align: left; }
        th { background-color: #f2f2f2; }
        h1 { text-align: center; font-family: sans-serif; }
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
        </thead>
        <tbody>
            {% for vare in varer %}
            <tr>
                <td>{{ vare.Vnr }}</td>
                <td>{{ vare.Betegnelse }}</td>
                <td>{{ vare.Antall }}</td>
                <td>{{ vare.Pris }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</body>
</html>
"""

@app.route('/')
def vis_varer_html():
    cur = mysql.connection.cursor()
    cur.execute("SELECT Vnr, Betegnelse, Antall, Pris FROM vare")
    varer_data = cur.fetchall()
    cur.close()

    # Konverter til liste av ordbøker
    varer = [
        {'Vnr': row[0], 'Betegnelse': row[1], 'Antall': row[2], 'Pris': float(row[3])}
        for row in varer_data
    ]

    return render_template_string(HTML_TEMPLATE, varer=varer)

if __name__ == '__main__':
    app.run(debug=False)