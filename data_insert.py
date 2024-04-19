import os
import json
import sqlite3

# Verbinding maken met de SQLite-database
conn = sqlite3.connect('database.db')
c = conn.cursor()

# Functie om JSON-gegevens naar de database te schrijven
def insert_data(json_data, c, conn):
    factuur = json_data['factuur']
    klant = factuur['klant']

    # Klantgegevens invoeren
    c.execute("INSERT INTO klanten (naam, adres, postcode, stad, KVK-nummer) VALUES (?, ?, ?, ?, ?)",
              (klant['naam'], klant['adres'], klant['postcode'], klant['stad'], klant['KVK-nummer']))
    conn.commit()

    klant_id = c.lastrowid  # Het ID van de net ingevoerde klant

    # Factuurgegevens invoeren
    c.execute("INSERT INTO facturen (ordernummer, orderdatum, betaaltermijn, klant_id) VALUES (?, ?, ?, ?)",
              (factuur['ordernummer'], factuur['orderdatum'], factuur['betaaltermijn'], klant_id))
    conn.commit()

    factuur_id = c.lastrowid  # Het ID van de net ingevoerde factuur

    # Factuurregels invoeren
    for product in factuur['producten']:
        c.execute("INSERT INTO factuurregels (factuur_id, productnaam, aantal, prijs_per_stuk_excl_btw, btw_percentage) VALUES (?, ?, ?, ?, ?)",
                  (factuur_id, product['productnaam'], product['aantal'], product['prijs_per_stuk_excl_btw'], product['btw_percentage']))
        conn.commit()

# Loop door alle JSON-bestanden in de map
json_folder = 'JSON_IN'
for filename in os.listdir(json_folder):
    if filename.endswith('.json'):
        with open(os.path.join(json_folder, filename), 'r') as file:
            json_data = json.load(file)
            insert_data(json_data, c, conn)  # Passing 'c' and 'conn' as arguments

# Database-verbinding sluiten
conn.close()
