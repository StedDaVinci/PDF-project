from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import sys

def generate_pdf(text):
    c = canvas.Canvas("output.pdf", pagesize=letter)
    width, height = letter

    text_width = c.stringWidth(text)
    x = (width - text_width) / 2
    y = height / 2
    c.drawString(x, y, text)

    c.save()
    print("PDF gegenereerd als 'output.pdf'")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Gebruik: python programma.py 'Tekst voor PDF'")
        sys.exit(1)
    
    text = sys.argv[1]
    generate_pdf(text)
