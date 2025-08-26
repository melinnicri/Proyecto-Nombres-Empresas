# Librerías para corrección:
import pandas as pd
from rapidfuzz import process, fuzz
from normalizacion import normalizar_nombre

# Construcción del diccionario limpio
def crear_diccionario_empresas(df, columna, min_freq=2, variantes_extra=None):
    nombres = df[columna].value_counts()
    base = nombres[nombres >= min_freq].index.tolist()

    if variantes_extra:
        for variante in variantes_extra:
            if variante not in base:
                base.append(variante)

    return sorted(set(base), key=lambda x: -len(x))  # Prioriza nombres largos

# Corrección con score y heurística
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

        if score >= umbral and (intersección or nombre[:4] in mejor_match):
            return mejor_match, score

    return nombre, 0

# Corrección por partes (fallback)
def correccion_por_partes(nombre, diccionario, umbral=85):
    palabras = nombre.split()
    if len(palabras) <= 1:
        return nombre

    corregidas = []
    for palabra in palabras:
        if len(palabra) <= 3:
            corregidas.append(palabra)
            continue
        match, score = corregir_nombre_con_score(palabra, diccionario, umbral)
        corregidas.append(match if score > umbral else palabra)

    return " ".join(corregidas)

# Pipeline completo de corrección
def pipeline_correccion(df, columna_original, variantes_extra=None):
    # 1. Normalización previa
    df["NOMBRE_NORMALIZADO"] = df[columna_original].apply(normalizar_nombre)

    # 2. Diccionario limpio
    diccionario = crear_diccionario_empresas(df, "NOMBRE_NORMALIZADO", variantes_extra=variantes_extra)

    # 3. Corrección con score
    df[["MATCH_CORREGIDO", "MATCH_SCORE"]] = df["NOMBRE_NORMALIZADO"].apply(
        lambda x: pd.Series(corregir_nombre_con_score(x, diccionario, umbral=80))
    )

    # 4. Fallback por partes si el score es bajo
    df["CORREGIDO_FINAL"] = df.apply(
        lambda row: correccion_por_partes(row["MATCH_CORREGIDO"], diccionario)
        if row["MATCH_SCORE"] < 70 else row["MATCH_CORREGIDO"],
        axis=1
    )

    # 5. Estado de corrección
    df["STATUS_CORRECCIÓN"] = df.apply(
        lambda row: "Corregido" if row["NOMBRE_NORMALIZADO"] != row["CORREGIDO_FINAL"] else "Sin cambio",
        axis=1
    )

    return df
