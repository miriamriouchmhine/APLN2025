import subprocess
import os
import sys

def run_script(script_name):
    print(f"\n Ejecutando: {script_name}")
    script_path = os.path.join(os.getcwd(), script_name)
    result = subprocess.run([sys.executable, script_path])
    if result.returncode != 0:
        print(f"Error ejecutando {script_path}")
        exit(1)
    print(f"Finalizado: {script_path}")


def main():
    # Paso 1: Preprocesamiento con Docling
    run_script("preprocess_docling.py")

    # Paso 2: Extracción de texto estructurado
    run_script("structured_text_extraction.py")

    # Paso 3:  Generación de resúmenes con Ollama
    run_script(os.path.join("SummaryGeneration", "OllamaSummaryGen.py"))

if __name__ == "__main__":
    main()