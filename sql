CREATE TABLE klanten (
    klant_id INTEGER PRIMARY KEY,
    naam TEXT,
    adres TEXT,
    postcode TEXT,
    stad TEXT,
    KVK_nummer TEXT
);

CREATE TABLE facturen (
    factuur_id INTEGER PRIMARY KEY,
    ordernummer TEXT,
    orderdatum DATE,
    betaaltermijn TEXT,
    klant_id INTEGER,
    FOREIGN KEY (klant_id) REFERENCES klanten(klant_id)
);

CREATE TABLE factuurregels (
    regel_id INTEGER PRIMARY KEY,
    factuur_id INTEGER,
    productnaam TEXT,
    aantal INTEGER,
    prijs_per_stuk_excl_btw REAL,
    btw_percentage REAL,
    FOREIGN KEY (factuur_id) REFERENCES facturen(factuur_id)
);




