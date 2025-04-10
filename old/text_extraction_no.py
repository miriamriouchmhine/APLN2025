import os
import cv2
import pytesseract
from pdf2image import convert_from_path
import numpy as np
from PIL import Image
import re

# --- PREPROCESAMIENTO DE IMAGEN ---
def preprocess_image(image):
    # Convertir a escala de grises
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)

    # Eliminar ruido y mejorar contraste
    gray = cv2.bilateralFilter(gray, 9, 75, 75)

    # Binarización para optimizar OCR
    binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY, 11, 2)
    return Image.fromarray(binary)

# --- EXTRACCIÓN DE TEXTO CON OCR MEJORADO ---
def extract_text_with_ocr(pdf_path):
    pages = convert_from_path(pdf_path)
    text = ""
    for page in pages:
        processed_page = preprocess_image(page)
        text += pytesseract.image_to_string(processed_page, lang='spa', config='--psm 3')
    return text.strip()

# --- POSTPROCESAMIENTO DEL TEXTO ---
def clean_text(text):
    # Eliminar encabezados, pie de página y caracteres extraños
    text = re.sub(r'CSV:.*', '', text)  # Eliminar líneas tipo "CSV:GEN-..."
    text = re.sub(r'^\W{1,3}$', '', text, flags=re.MULTILINE)  # Eliminar caracteres sueltos
    text = re.sub(r'^\d{1,3}$', '', text, flags=re.MULTILINE)  # Eliminar números de página

    # Corregir palabras partidas
    text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)

    # Eliminar líneas muy cortas que suelen ser ruido
    text = '\n'.join([line for line in text.split('\n') if len(line.strip()) > 10])

    return text.strip()

# --- FLUJO PRINCIPAL ---
PDF_FOLDER = "corpus"
PDFS_A_PROCESAR = [
    "ayudas_21-22.pdf",
    "ayudas_22-23.pdf",
    "ayudas_23-24.pdf",
    "ayudas_24-25.pdf"
]

for pdf_file in PDFS_A_PROCESAR:
    pdf_path = os.path.join(PDF_FOLDER, pdf_file)
    text = extract_text_with_ocr(pdf_path)
    cleaned_text = clean_text(text)

    # Guardar texto limpio en un archivo
    output_file = os.path.join(PDF_FOLDER, pdf_file.replace('.pdf', '_limpio.txt'))
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(cleaned_text)

    print(f"[EXITO] Texto limpio guardado en '{output_file}'")
