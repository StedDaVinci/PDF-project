import os
import shutil
import json
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from os.path import isfile, join

def read_files_in_folder(folder_path):
    file_contents = {}
    onlyfiles = [f for f in os.listdir(folder_path) if isfile(join(folder_path, f))]
    for filename in onlyfiles:
        file_path = join(folder_path, filename)
        with open(file_path, "r") as file:
            file_contents[filename] = file.read()
    return file_contents

def load_order_from_json(file_path):
    with open(file_path, "r") as file:
        order_data = json.load(file)
        print(order_data)
        print(file)
    return order_data

def calculate_subtotal(items):
    subtotal = 0
    for item in items:
        subtotal += item["aantal"] * item["prijs_per_stuk_excl_btw"]
    return subtotal

def calculate_total(subtotal, tax_rate):
    return subtotal * (1 + tax_rate)

def generate_invoice(order_data, tax_rate):
    # Aannemen dat het bestandsnaam hetzelfde is als de ordernummer
    print(order_data)
    order_number = order_data["factuur"]["factuurnummer"]
    pdf_file_path = os.path.join("INVOICE", f"{order_number}.pdf")
    c = canvas.Canvas(pdf_file_path, pagesize=letter)
    width, height = letter

    # Factuurinformatie
    c.setFont("Helvetica-Bold", 12)
    c.drawString(width - 150, height - 50, "Ordernummer:")
    c.drawString(width - 150, height - 70, "Orderdatum:")
    c.drawString(width - 150, height - 90, "Betaaltermijn:")
    c.setFont("Helvetica", 12)
    c.drawString(width - 50, height - 50, order_data["factuur"]["factuurnummer"])
    c.drawString(width - 50, height - 70, order_data["factuur"]["factuurdatum"])
    c.drawString(width - 50, height - 90, order_data["factuur"]["betaaltermijn"])

    # Klantinformatie
    klant = order_data["factuur"]["klant"]
    klant_naam = klant["naam"]
    klant_adres = klant["adres"]
    klant_postcode = klant["postcode"]
    klant_stad = klant["stad"]
    klant_kvknr = klant["KVK-nummer"]

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 130, "Klantgegevens:")
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 150, klant_naam)
    c.drawString(50, height - 170, klant_adres)
    c.drawString(50, height - 190, klant_postcode + " " + klant_stad)
    c.drawString(50, height - 210, "KVK-nummer: " + klant_kvknr)

    # Factuurregels
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 250, "Product")
    c.drawString(width - 200, height - 250, "Aantal")
    c.drawString(width - 150, height - 250, "Prijs per stuk (excl. btw)")
    c.drawString(width - 50, height - 250, "Totaal (excl. btw)")
    c.line(50, height - 260, width - 50, height - 260)

    line_height = 20
    items = order_data["factuur"]["producten"]
    item_y = height - 280
    for item in items:
        c.drawString(50, item_y, item["productnaam"])
        c.drawString(width - 200, item_y, str(item["aantal"]))
        c.drawString(width - 150, item_y, "{:.2f}".format(item["prijs_per_stuk_excl_btw"]))
        total_price = item["aantal"] * item["prijs_per_stuk_excl_btw"]
        c.drawString(width - 50, item_y, "{:.2f}".format(total_price))
        item_y -= line_height

    # Subtotaal
    subtotal = calculate_subtotal(items)
    c.drawString(width - 150, item_y - 20, "Subtotaal (excl. btw):")
    c.drawString(width - 50, item_y - 20, "{:.2f}".format(subtotal))

    # Btw-bedrag
    c.setFont("Helvetica-Bold", 12)
    c.drawString(width - 150, item_y - 40, "Btw:")
    btw_total = 0
    for item in items:
        btw_amount = item["aantal"] * item["prijs_per_stuk_excl_btw"] * tax_rate 
        btw_total += btw_amount
    c.drawString(width - 50, item_y - 40, "{:.2f}".format(btw_total))

    # Totaalbedrag
    total_amount = calculate_total(subtotal + btw_total, tax_rate)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(width - 150, item_y - 60, "Totaal:")
    c.drawString(width - 50, item_y - 60, "{:.2f}".format(total_amount))

    c.save()
    print("Factuur gegenereerd als '{}'".format(pdf_file_path))

    return pdf_file_path

def process_json_files():
    json_files = os.listdir("JSON_IN")
    for json_file in json_files:
        json_file_path = os.path.join("JSON_IN", json_file)
        order_data = load_order_from_json(json_file_path)
        tax_rate = 0.21  
        pdf_file_path = generate_invoice(order_data, tax_rate)
        processed_json_path = os.path.join("JSON_PROCESSED", json_file)
        shutil.move(json_file_path, processed_json_path)

if __name__ == "__main__":
    for folder in ["JSON_IN", "JSON_PROCESSED", "INVOICE"]:
        if not os.path.exists(folder):
            os.makedirs(folder)
    
    process_json_files()
