import re
import json
import pandas as pd
import os

# Leemos y normalizamos el contenido de todos los archivos .txt
corpus_folder = "corpus"
txt_files = [
    "ayudas_20-21_docling.txt",
    "ayudas_21-22_docling.txt",
    "ayudas_22-23_docling.txt",
    "ayudas_23-24_docling.txt",
    "ayudas_24-25_docling.txt",
    "ayudas_25-26_docling.txt"
]

csv_json_folder = "SummaryGeneration/dataIn"

def extract_structured_info(text):
    text = re.sub(r'\s+', ' ', text)  # Quitar saltos de línea y espacios extra

    data = {}

    # Curso académico
    curso = re.search(r"curso académico (\d{4}-\d{4})", text, re.IGNORECASE)
    data["curso"] = curso.group(1) if curso else None

    # Cuantías fijas
    fija_renta = re.search(r"Cuantía fija ligada a la renta.*?(\d+[\..]\d+[\.,]\d+)\s*euros", text, re.IGNORECASE)
    fija_residencia = re.search(r"Cuantía fija ligada a la residencia del solicitante durante el curso:.*?(\d+[\..]\d+[\.,]\d+)\s*euros", text, re.IGNORECASE)
    beca_basica = re.search(r"Beca básica:.*?(\d+[.,]?\d*)\s*euros", text)
    beca_basica_ciclo_formativo = re.search(r"Grado Básico esta cuantía será de.*?(\d+[.,]?\d*)\s*euros", text)
    cuantia_variable_min = re.search(r"(importe mínimo|mínimo será de)\s*(\d+[.,]?\d*)\s*euros", text)

    data["cuantia_fija_renta"] = float(fija_renta.group(1).replace(".", "").replace(",", ".")) if fija_renta else None
    data["cuantia_fija_residencia"] = float(fija_residencia.group(1).replace(".", "").replace(",", ".")) if fija_residencia else None
    data["beca_basica"] = float(beca_basica.group(1).replace(",", ".")) if beca_basica else None
    data["beca_basica_ciclo_formativo"] = float(beca_basica_ciclo_formativo.group(1).replace(",", ".")) if beca_basica_ciclo_formativo else None
    data["cuantia_variable_min"] = float(cuantia_variable_min.group(2).replace(",", ".")) if cuantia_variable_min else None

    # Excelencia académica
    excelencia = re.findall(r"Entre\s*(\d+[.,]?\d*)\s*y\s*(\d+[.,]?\d*).*?(\d+)\s*euros", text)
    ultimo_tramo = re.search(r"(\d+[.,]?\d*)\s*puntos\s*o más\s*\|\s*(\d+)\s*euros", text)
    tramos = []
    for n1, n2, euros in excelencia:
        tramos.append({
            "nota_min": float(n1.replace(",", ".")),
            "nota_max": float(n2.replace(",", ".")),
            "cuantia": int(euros)
        })

    if ultimo_tramo:
        tramos.append({
            "nota_min": float(ultimo_tramo.group(1).replace(",", ".")),
            "nota_max": 10.00,
            "cuantia": int(ultimo_tramo.group(2))
        })

    if tramos:
        data["excelencia_tramos"] = tramos

    # Enseñanzas
    ensenanzas_section = re.search(r"Artículo 3\. Enseñanzas comprendidas.*?Artículo 4", text, re.IGNORECASE | re.DOTALL)
    if ensenanzas_section:
        ensenanzas = re.findall(r"[a-z]\)\s*(.*?)(?:\.|,)", ensenanzas_section.group(0))
        data["ensenanzas"] = [e.strip() for e in ensenanzas if len(e.strip()) > 3]

    #return data
# Requisitos académicos mínimos

    requisitos = []
    if re.search(r"matriculados.*?curso 2025-2026.*?60 créditos", text, re.IGNORECASE):
        requisitos.append("Matriculación mínima: 60 créditos")
    if re.search(r"no se concederá beca a quienes repitan curso", text, re.IGNORECASE):
        requisitos.append("No repetir curso total o parcialmente")
    if re.search(r"nota media de\s*5[.,]00\s*puntos", text):
        requisitos.append("Nota mínima de acceso: 5,00 puntos")
    data["requisitos"] = requisitos

    fechas = re.search(r"extenderá desde el día (\d{1,2} de \w+ de \d{4}).*? hasta el (\d{1,2} de \w+ de \d{4})", text, re.IGNORECASE)
    if fechas:
        data["plazo_presentacion"] = {
            "inicio": fechas.group(1),
            "fin": fechas.group(2)
        }

    return data

# Procesar todos los archivos y guardar en lista
resultados = []
for file in txt_files:
    with open(os.path.join(corpus_folder, file), encoding="utf-8") as f:
        txt = f.read()
        info = extract_structured_info(txt)
        info["archivo"] = file
        resultados.append(info)

# Convertir a DataFrame plano (para CSV)
df = pd.json_normalize(resultados)

# Guardar CSV y JSON
csv_path = os.path.join(csv_json_folder, "becas_structurado.csv")
json_path = os.path.join(csv_json_folder, "becas_structurado.json")
df.to_csv(csv_path, index=False)
with open(json_path, "w", encoding="utf-8") as jf:
    json.dump(resultados, jf, indent=2, ensure_ascii=False)

csv_path, json_path
