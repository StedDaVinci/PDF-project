from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import sys
from datetime import datetime

def generate_invoice(address, invoice_number, invoice_date, items, total_amount):
    c = canvas.Canvas("invoice.pdf", pagesize=letter)
    width, height = letter
    
    # Adresveld
    address_x = 50
    address_y = height - 100
    if address:
        address_lines = address.split("\n")
        line_height = 15
        for line in address_lines:
            c.drawString(address_x, address_y, line.strip())
            address_y -= line_height
    
    # Factuurinformatie
    c.setFont("Helvetica-Bold", 12)
    c.drawString(width - 150, height - 50, "Factuurnummer:")
    c.drawString(width - 150, height - 70, "Factuurdatum:")
    c.setFont("Helvetica", 12)
    c.drawString(width - 50, height - 50, invoice_number)
    c.drawString(width - 50, height - 70, invoice_date)
    
    # Factuurregels
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 150, "Omschrijving")
    c.drawString(width - 200, height - 150, "Bedrag")
    c.line(50, height - 160, width - 50, height - 160)
    
    line_height = 20
    item_y = height - 180
    for item in items:
        c.drawString(50, item_y, item["description"])
        c.drawString(width - 200, item_y, str(item["amount"]))
        item_y -= line_height
    
    # Totaalbedrag
    c.line(width - 200, 50, width - 200, item_y)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(width - 150, item_y - 20, "Totaal:")
    c.drawString(width - 50, item_y - 20, str(total_amount))
    
    c.save()
    print("Factuur gegenereerd als 'invoice.pdf'")

if __name__ == "__main__":
    if len(sys.argv) < 6:
        print("Gebruik: python programma.py 'Adres' 'Factuurnummer' 'Factuurdatum' 'Omschrijving:Bedrag' 'Totaalbedrag'")
        sys.exit(1)
    
    address = sys.argv[1]
    invoice_number = sys.argv[2]
    invoice_date = sys.argv[3]
    items = []
    for item_str in sys.argv[4].split(";"):
        description, amount = item_str.split(":")
        items.append({"description": description, "amount": amount})
    total_amount = sys.argv[5]
    
    generate_invoice(address, invoice_number, invoice_date, items, total_amount)
