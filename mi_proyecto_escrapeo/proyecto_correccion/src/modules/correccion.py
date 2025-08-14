# Librerías corrección de nombres:
import pandas as pd
from rapidfuzz import process, fuzz

def crear_diccionario_mejorado(df, columna, min_freq=2):
    nombres_frecuentes = df[columna].value_counts()
    diccionario = nombres_frecuentes[nombres_frecuentes >= min_freq].index.tolist()
    
    variantes_comunes = [
        "FAMILIARES", "TELEFONICA", "BANCO SANTANDER", "INDRA", 
        "ACCIONA AGUA SAU", "FERROVIAL", "IBERDROLA", "REPSOL", "ENDESA"
    ]
    
    for variante in variantes_comunes:
        if variante not in diccionario:
            diccionario.append(variante)
    
    return sorted(list(set(diccionario)), key=lambda x: -len(x))

def corregir_nombre_con_score(nombre, diccionario, umbral=80):
    if not nombre or pd.isna(nombre):
        return nombre, 0

    resultado = process.extractOne(nombre, diccionario, scorer=fuzz.WRatio)
    if resultado and resultado[1] < umbral:
        resultado = process.extractOne(nombre, diccionario, scorer=fuzz.token_set_ratio)

    if resultado:
        mejor_match, score, _ = resultado
        tokens_original = set(nombre.split())
        tokens_match = set(mejor_match.split())
        intersección = tokens_original & tokens_match

        if score >= umbral and (intersección or nombre[:4] in mejor_match) and abs(len(mejor_match) - len(nombre)) < 20:
            return mejor_match, score
        else:
            return nombre, score

    return nombre, 0

def correccion_por_partes(nombre, diccionario):
    palabras = nombre.split()
    if len(palabras) <= 1:
        return nombre

    palabras_corregidas = []
    for palabra in palabras:
        if len(palabra) <= 3:
            palabras_corregidas.append(palabra)
            continue
        corregida, score = corregir_nombre_con_score(palabra, diccionario, umbral=85)
        palabras_corregidas.append(corregida if score > 85 else palabra)

    return " ".join(palabras_corregidas)

# Confirmación de la corrección de nombres:
def pipeline_correccion(df, columna_original):
    df["NOMBRE_LIMPIO"] = df[columna_original].str.upper().str.strip()
    diccionario_empresas = crear_diccionario_mejorado(df, "NOMBRE_LIMPIO")

    df[["NOMBRE_CORREGIDO", "MATCH_SCORE"]] = df["NOMBRE_LIMPIO"].apply(
        lambda x: pd.Series(corregir_nombre_con_score(x, diccionario_empresas, umbral=75))
    )

    df["NOMBRE_CORREGIDO_FINAL"] = df.apply(
        lambda row: correccion_por_partes(row["NOMBRE_CORREGIDO"], diccionario_empresas)
        if row["MATCH_SCORE"] < 75 else row["NOMBRE_CORREGIDO"],
        axis=1
    )

    df["STATUS_CORRECCIÓN"] = df.apply(
        lambda row: "Corregido" if row["NOMBRE_LIMPIO"] != row["NOMBRE_CORREGIDO_FINAL"] else "Sin cambio",
        axis=1
    )

    return df
