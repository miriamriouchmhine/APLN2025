import pandas as pd
import ast
import ollama
from typing import Dict, List

# --- Versión Fija (para CSVs con estructura conocida) ---
def procesar_csv_fijo(ruta: str) -> str:
    """Procesamiento para CSVs con campos predecibles (como tu ejemplo de becas)"""
    df = pd.read_csv(ruta)
    
    # Convertir columnas complejas
    df['excelencia_tramos'] = df['excelencia_tramos'].apply(ast.literal_eval)
    df['ensenanzas'] = df['ensenanzas'].apply(ast.literal_eval)
    
    resumen = []
    for _, row in df.iterrows():
        tramos_excelencia = "\n".join(
            [f"- Nota {t['nota_min']}-{t['nota_max']}: {t['cuantia']}€" 
             for t in row['excelencia_tramos']]
        )
        
        resumen.append(
            f"Año {row['curso']}:\n"
            f"- Cuantía fija (renta): {row['cuantia_fija_renta']}€\n"
            f"- Cuantía fija (residencia): {row['cuantia_fija_residencia']}€\n"
            f"- Beca básica: {row['beca_basica']}€\n"
            f"- Excelencia académica:\n{tramos_excelencia}\n"
            f"- Enseñanzas cubiertas: {len(row['ensenanzas'])} categorías\n"
        )
    
    return "\n".join(resumen)

# --- Versión Dinámica (para CSVs genéricos) ---
def procesar_csv_dinamico(ruta: str) -> str:
    """Procesamiento automático para CSVs con estructura desconocida"""
    df = pd.read_csv(ruta)
    resumen = []
    
    for _, row in df.iterrows():
        fila_resumen = []
        for col, valor in row.items():
            # Manejo especial para listas/diccionarios
            if isinstance(valor, str) and valor.startswith(('[', '{')):
                try:
                    valor = ast.literal_eval(valor)
                    if isinstance(valor, list):
                        fila_resumen.append(f"- {col}: {(valor)}")
                    elif isinstance(valor, dict):
                        fila_resumen.append(f"- {col}: Claves -> {', '.join(valor.keys())}")
                except:
                    fila_resumen.append(f"- {col}: {valor}")
            else:
                fila_resumen.append(f"- {col}: {valor}")
        
        resumen.append(f"Beca {_ + 1}:\n" + "\n".join(fila_resumen))
    
    return "\n\n".join(resumen)

# --- Generador de Prompt (compartido) ---
def generar_resumen_ollama(datos_procesados: str, modo: str = "resumen") -> str:
    """Genera el prompt adaptándose al modo de procesamiento"""
    if modo == "resumen":
        prompt = f"""

{datos_procesados}

Analiza y compara los datos de becas educativas y genera un informe en español(sin recomendaciones) que incluya comparaciones entre todos los años, resaltando únicamente las diferencias entre ellos.
Algunos puntos a considerar:
1. Tendencias temporales: Cambios en cuantías entre años.
2. Estructura de ayudas: Desglose de componentes (fijas/variables).
3. Datos destacados: Máximos, mínimos y peculiaridades.
4. Excelencia académica: Rango de notas y recompensas, desglosa toda la información por año, notas y ramas.
"""
    else:
        prompt = f"""

{datos_procesados}

Haz un resumen no estructurado(prosa) de los datos de la beca 5 (curso: 2025-2026), para que alguien pueda leerlos.
Incluye cuantías(valor numérico en euros) por año, tramos de excelencia, enseñanzas cubiertas(resumido) y otra información que consideres relevante de forma resumida sacando tus conclusiones de que es lo más importante.
""" 
    
    response = ollama.generate(
        model="deepseek-r1:14b",#gemma3
        prompt=prompt,
        #options={"temperature": 0.5} 
        options={"temperature": 0.1, "max_tokens": 10000, "top_p": 0.95, "frequency_penalty": 0.5, "presence_penalty": 0.5} 
        # Los valores indican: 
        # temperature: controla la aleatoriedad de la respuesta (0.2 es más conservador)
        # max_tokens: límite de tokens en la respuesta (8000 es un límite alto)
        # top_p: controla la diversidad de las respuestas (0.95 permite más variedad)
        # frequency_penalty: penaliza palabras repetidas (0.5 es un valor moderado)
        # presence_penalty: penaliza la aparición de nuevas palabras (0.5 es un valor moderado)
    )
    return response['response']



# --- Ejecución ---
def main(ruta_csv: str, modo_procesamiento: str = "resumen"):
    """Ejecuta el procesamiento según el modo seleccionado"""
    if modo_procesamiento == "resumen":
        #datos = procesar_csv_fijo(ruta_csv)
        datos = procesar_csv_dinamico(ruta_csv)
        print("=== COMPARACIÓN ENTRE AÑOS GENERADO ===")

    else:
        datos = procesar_csv_dinamico(ruta_csv)
        print("=== INFORME 2025-2026 GENERADO ===")
    
    informe = generar_resumen_ollama(datos, modo_procesamiento)
    print(informe)   



main("./dataIn/becas_structurado_3.csv", modo_procesamiento="ultimo") 
main("./dataIn/becas_structurado_3.csv", modo_procesamiento="resumen") 


'''
[Neural Chat] (intel)->7B	4.1GB	ollama run neural-chat
[Granite-3.2] (IBM) ->	8B	4.9GB	ollama run granite3.2

[gemma3] (google)-> 	4B	3.3GB	ollama run gemma3
[gemma3] (google)->     12B 8.1GB   ollama run gemma3:12b

[Llama 3.2] (meta) -> 	3B	2.0GB	ollama run llama3.2
[Llama 3.1] (meta)-> 	8B	4.7GB	ollama run llama3.1

[deepseek-r1:8b] -> 8B 4.9GB ollama run deepseek-r1:8b
[deepseek-r1:14b] -> 14B 9GB ollama run deepseek-r1:14b

[phi4] (microsoft) ->   14B  9.1GB ollama run phi4
[orca] (microsoft) -> 13B 7.4GB ollama run orca2:13b
'''