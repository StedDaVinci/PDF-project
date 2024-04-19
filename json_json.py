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
    with open(file_path, "r", encoding="utf-8") as file:
        order_data = json.load(file)
    return order_data

def calculate_subtotal(items):
    subtotal = 0
    for item in items:
        subtotal += item["aantal"] * item["prijs_per_stuk_excl_btw"]
    return subtotal

def calculate_total(subtotal, tax_rate):
    return subtotal * (1 + tax_rate)

def generate_invoice(order_data, tax_rate):
    order_number = order_data["factuur"]["factuurnummer"]
    pdf_file_path = os.path.join("INVOICE", f"{order_number}.pdf")
    json_file_path = os.path.join("INVOICE", f"{order_number}.json")
    c = canvas.Canvas(pdf_file_path, pagesize=letter)
    width, height = letter

    # JSON factuurdata
    json_data = {
        "factuurnummer": order_data["factuur"]["factuurnummer"],
        "factuurdatum": order_data["factuur"]["factuurdatum"],
        "betaaltermijn": order_data["factuur"]["betaaltermijn"],
        "klant": order_data["factuur"]["klant"],
        "producten": order_data["factuur"]["producten"]
    }

    with open(json_file_path, "w") as json_file:
        json.dump(json_data, json_file, indent=4)

    # Hieronder blijft de PDF-generatie zoals het was

def process_json_files():
    json_files = os.listdir("/Volumes/School/PDF-project/JSON_IN")
    for json_file in json_files:
        json_file_path = os.path.join("/Volumes/School/PDF-project/JSON_IN", json_file)
        order_data = load_order_from_json(json_file_path)
        tax_rate = 0.21  
        generate_invoice(order_data, tax_rate)
        processed_json_path = os.path.join("JSON_PROCESSED", json_file)
        shutil.move(json_file_path, processed_json_path)

if __name__ == "__main__":
    for folder in ["JSON_IN", "JSON_PROCESSED", "INVOICE"]:
        if not os.path.exists(folder):
            os.makedirs(folder)
    
    process_json_files()
