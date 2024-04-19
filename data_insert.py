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

    c.execute('CREATE TABLE if not exists klanten (klant_id INTEGER PRIMARY KEY,naam TEXT,adres TEXT,postcode TEXT,stad TEXT,KVK_nummer TEXT);')
    c.execute('CREATE TABLE if not exists facturen (factuur_id INTEGER PRIMARY KEY,factuurnummer TEXT,factuurdatum DATE,betaaltermijn TEXT,klant_id INTEGER,FOREIGN KEY (klant_id) REFERENCES klanten(klant_id));')
    c.execute('CREATE TABLE if not exists factuurregels (regel_id INTEGER PRIMARY KEY,factuur_id INTEGER,productnaam TEXT,aantal INTEGER,prijs_per_stuk_excl_btw REAL,FOREIGN KEY (factuur_id) REFERENCES facturen(factuur_id));')
    
    
    # Klantgegevens invoeren
    c.execute("INSERT INTO klanten (naam, adres, postcode, stad, KVK_nummer) VALUES (?, ?, ?, ?, ?)",
              (klant['naam'], klant['adres'], klant['postcode'], klant['stad'], klant['KVK-nummer']))
    conn.commit()

    klant_id = c.lastrowid  # Het ID van de net ingevoerde klant

    # Factuurgegevens invoeren
    c.execute("INSERT INTO facturen (factuurnummer, factuurdatum, betaaltermijn, klant_id) VALUES (?, ?, ?, ?)",
              (factuur['factuurnummer'], factuur['factuurdatum'], factuur['betaaltermijn'], klant_id))
    conn.commit()

    factuur_id = c.lastrowid  # Het ID van de net ingevoerde factuur

    # Factuurregels invoeren
    for product in factuur['producten']:
        c.execute("INSERT INTO factuurregels (factuur_id, productnaam, aantal, prijs_per_stuk_excl_btw ) VALUES (?, ?, ?, ?)",
                  (factuur_id, product['productnaam'], product['aantal'], product['prijs_per_stuk_excl_btw']))
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
