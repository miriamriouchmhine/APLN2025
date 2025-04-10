import os
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from rouge_score import rouge_scorer
from bert_score import score as bert_score
from nltk.translate.bleu_score import sentence_bleu
from tqdm import tqdm  # Para barra de progreso

# Configuración
METRICAS = ["ROUGE-L", "BLEU", "BERTScore"]
TIPOS_INFORME = ["Comparativa", "ultimoAño"]
MODELOS = ["neural-chat", "granite3.2", "gemma3", "gemma3-12b", "llama3.2", "llama3.1", "deepseek-r1-8b", "deepseek-r1-14b", "phi4", "orca2-13b"]

# --- Funciones principales ---
def cargar_informes():
    """Carga todos los informes en un diccionario (modelo, tipo) -> contenido"""
    informes = {}
    for archivo in os.listdir("output"):
        if archivo.startswith("Informe_") and archivo.endswith(".txt"):
            partes = archivo.split("_")
            modelo, tipo = partes[1], partes[2].replace(".txt", "")
            with open(f"./output/{archivo}", "r", encoding="utf-8") as f:
                informes[(modelo, tipo)] = f.read()
    return informes

def calcular_metricas(texto1, texto2):
    """Calcula todas las métricas entre dos textos"""
    # ROUGE-L
    scorer = rouge_scorer.RougeScorer(["rougeL"])
    rouge = scorer.score(texto1, texto2)["rougeL"].fmeasure
    
    # BLEU
    bleu = sentence_bleu([texto1.split()], texto2.split())
    
    # BERTScore (usamos F1)
    _, _, bert_f1 = bert_score([texto1], [texto2], lang="es")
    bert_f1 = bert_f1.mean().item()
    
    return {
        "ROUGE-L": rouge,
        "BLEU": bleu,
        "BERTScore": bert_f1
    }

def generar_matrices_completas(informes):
    """Genera matrices 10x10 para cada métrica y tipo de informe"""
    resultados = {}
    
    for tipo in TIPOS_INFORME:
        matrices = {metrica: pd.DataFrame(index=MODELOS, columns=MODELOS) for metrica in METRICAS}
        
        # Comparar todos los modelos entre sí (combinaciones)
        modelos_tipo = [m for m in MODELOS if (m, tipo) in informes]
        for modelo1 in tqdm(modelos_tipo, desc=f"Procesando {tipo}"):
            for modelo2 in modelos_tipo:
                metricas = calcular_metricas(
                    informes[(modelo1, tipo)],
                    informes[(modelo2, tipo)]
                )
                for metrica in METRICAS:
                    matrices[metrica].loc[modelo1, modelo2] = metricas[metrica]
        
        resultados[tipo] = matrices
    
    return resultados

def guardar_y_visualizar(resultados):
    """Guarda CSV y genera heatmaps para todas las matrices"""
    os.makedirs("resultados", exist_ok=True)
    
    for tipo, matrices in resultados.items():
        for metrica, df in matrices.items():
            # Guardar CSV
            df.to_csv(f"resultados/Matriz_{metrica}_{tipo}.csv")
            
            # Heatmap
            plt.figure(figsize=(12, 10))
            sns.heatmap(
                df.astype(float),
                annot=True,
                fmt=".2f",
                cmap="YlGnBu",
                vmin=0,
                vmax=1,
                linewidths=0.5,
                cbar_kws={"label": metrica}
            )
            plt.title(f"{metrica} - {tipo}", fontsize=14)
            plt.xticks(rotation=45, ha="right")
            plt.yticks(rotation=0)
            plt.tight_layout()
            plt.savefig(f"resultados/Heatmap_{metrica}_{tipo}.png", dpi=300)
            plt.close()

# --- Ejecución ---
def main():
    print("Cargando informes...")
    informes = cargar_informes()
    
    print("\nGenerando matrices 10x10...")
    resultados = generar_matrices_completas(informes)
    
    print("\nGuardando resultados y generando visualizaciones...")
    guardar_y_visualizar(resultados)
    
    print("\n¡Proceso completado! Resultados guardados en /resultados")
    
   

if __name__ == "__main__":
    main()