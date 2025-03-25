import os
import cv2
import pytesseract
from pdf2image import convert_from_path
import numpy as np
from PIL import Image
import re

# --- PREPROCESAMIENTO DE IMAGEN MEJORADO ---
def preprocess_image(image):
    # Convertir a escala de grises
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)

    # Filtro bilateral para reducir ruido y mejorar bordes
    gray = cv2.bilateralFilter(gray, 9, 75, 75)

    # Proyección horizontal para detectar columnas principales
    horizontal_projection = np.sum(gray, axis=1)
    
    # Detectar líneas del contenido eliminando bordes laterales
    top = np.argmax(horizontal_projection > 0)
    bottom = len(horizontal_projection) - np.argmax(horizontal_projection[::-1] > 0)

    # Recorte del contenido sin cortar el texto principal
    cropped_image = gray[top:bottom, 50:-50]

    # Binarización adaptativa para optimizar el OCR
    binary = cv2.adaptiveThreshold(cropped_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
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
    # Corregir palabras partidas
    text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)
    # Eliminar texto repetitivo o ruidos
    text = re.sub(r'Código Seguro de Verificación.*\n?', '', text, flags=re.IGNORECASE)
    text = re.sub(r'DIRECCIÓN DE VALIDACIÓN.*\n?', '', text, flags=re.IGNORECASE)
    # Eliminar líneas muy cortas que no aportan valor
    text = '\n'.join([line for line in text.split('\n') if len(line.strip()) > 20])
    return text

# --- FLUJO PRINCIPAL ---
PDF_FOLDER = "corpus"
pdf_path = os.path.join(PDF_FOLDER, "ayudas_20-21.pdf")

text = extract_text_with_ocr(pdf_path)
cleaned_text = clean_text(text)

# Guardar texto limpio en un archivo
output_file = os.path.join(PDF_FOLDER, "ayudas_20-21_limpio_sinlat.txt")
with open(output_file, "w", encoding="utf-8") as f:
    f.write(cleaned_text)

print(f"[EXITO] Texto limpio guardado en '{output_file}'")


# --- FUNCIÓN PARA LIMPIAR EL TXT FINAL ---
def clean_footer_in_txt(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as file:
        text = file.read()

    # Detectar todas las líneas que coinciden con el patrón del pie de página
    footers = re.findall(r'(CSV : GEN-.*?ALEJANDRO TIANA FERRER.*?)\n', text, re.DOTALL)

    # Guardar solo la última aparición del pie de página
    footer_text = footers[-1] if footers else ""

    # Eliminar todas las repeticiones anteriores del pie de página en el texto
    text_cleaned = re.sub(r'(CSV : GEN-.*?ALEJANDRO TIANA FERRER.*?)\n', '', text, flags=re.DOTALL)

    # Agregar el pie de página solo una vez al final del texto
    final_text = text_cleaned.strip() + "\n\n=== PIE DE PÁGINA ===\n" + footer_text

    # Guardar el resultado limpio
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(final_text)

    print(f"[EXITO] Texto limpio guardado en '{output_file}'")

# --- FLUJO PRINCIPAL ---
input_file = "corpus/ayudas_20-21_limpio_sinlat.txt"
output_file = "corpus/ayudas_20-21_final.txt"

clean_footer_in_txt(input_file, output_file)