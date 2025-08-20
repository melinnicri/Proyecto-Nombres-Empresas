# gestor_correcciones.py
#Librerías asociadas a la gestión de correcciones manuales en nombres propios.
import pandas as pd
import csv
from datetime import datetime


# Cargar diccionario manual desde CSV
def cargar_diccionario_manual(path):
    df_dicc = pd.read_csv(path, encoding="utf-8-sig")
    return dict(zip(df_dicc['original'], df_dicc['corregido']))

# Aplicar corrección prioritaria
def corregir_nombre(nombre_original, diccionario_manual, funcion_normalizacion):
    nombre_normalizado = funcion_normalizacion(nombre_original)

    # Buscar en el diccionario manual
    if nombre_normalizado in diccionario_manual:
        return diccionario_manual[nombre_normalizado]
    
    # Si no está, devolver el nombre normalizado como fallback
    return nombre_normalizado


# Agregar corrección manual con log ético
def agregar_correccion(nombre_errado, nombre_corregido, diccionario_manual, motivo=""):
    if nombre_errado in diccionario_manual:
        print(f"'{nombre_errado}' ya tiene una corrección registrada: '{diccionario_manual[nombre_errado]}'")
    else:
        print(f"Corrección agregada: '{nombre_errado}' → '{nombre_corregido}'")
    
    diccionario_manual[nombre_errado] = nombre_corregido

    with open("log_diccionario_manual.csv", mode="a", encoding="utf-8-sig", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now(), nombre_errado, nombre_corregido, motivo])

# Exportar diccionario actualizado (opcional para versionado)
def guardar_diccionario(diccionario_manual, path="diccionario_manual_actualizado.csv"):
    df_dicc = pd.DataFrame(diccionario_manual.items(), columns=["original", "corregido"])
    df_dicc.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"Diccionario guardado en: {path}")
