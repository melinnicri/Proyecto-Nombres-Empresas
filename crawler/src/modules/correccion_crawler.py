import pandas as pd
from rapidfuzz import process, fuzz
from diccionario_manual import diccionario_manual

    
# Corrección manual explícita
def aplicar_diccionario_manual(nombre, diccionario):
    return diccionario.get(nombre, nombre)

# Diccionario mejorado desde nombres únicos
def crear_diccionario_mejorado(df, columna):
    nombres_unicos = df[columna].dropna().unique()
    return {nombre: nombre for nombre in nombres_unicos}

# Corrección fonética con score y umbral
def corregir_nombre_con_score(nombre, diccionario, umbral=75):
    if not nombre or pd.isna(nombre):
        return nombre, 0

    mejor_match, score, _ = process.extractOne(nombre, diccionario, scorer=fuzz.token_sort_ratio)
    return (mejor_match, score) if score >= umbral else (nombre, score)

# Corrección por partes con validación de longitud
def correccion_por_partes(nombre, diccionario, umbral=80):
    partes = nombre.split()
    corregidas = []

    for p in partes:
        if len(p) <= 3:
            corregidas.append(p)
            continue
        match, score, _ = process.extractOne(p, diccionario.keys(), scorer=fuzz.token_sort_ratio)
        corregidas.append(match if score >= umbral else p)

    return " ".join(corregidas)

# Pipeline completo con trazabilidad
def pipeline_correccion(df, columna_original):
    df["NOMBRE_LIMPIO"] = df[columna_original].str.upper().str.strip()
    diccionario_empresas = crear_diccionario_mejorado(df, "NOMBRE_LIMPIO")

    # Corrección fonética principal
    df[["NOMBRE_CORREGIDO", "MATCH_SCORE"]] = df["NOMBRE_LIMPIO"].apply(
        lambda x: pd.Series(corregir_nombre_con_score(x, diccionario_empresas, umbral=75))
    )

    # Corrección por partes si el score es bajo
    df["NOMBRE_CORREGIDO_FINAL"] = df.apply(
        lambda row: correccion_por_partes(row["NOMBRE_CORREGIDO"], diccionario_empresas)
        if row["MATCH_SCORE"] < 75 else row["NOMBRE_CORREGIDO"],
        axis=1
    )

    # Corrección manual final
    df["NOMBRE_CORREGIDO_FINAL"] = df["NOMBRE_CORREGIDO_FINAL"].apply(
        lambda x: aplicar_diccionario_manual(x, diccionario_manual)
    )

    # Estado de corrección
    df["STATUS_CORRECCIÓN"] = df.apply(
        lambda row: "Corregido" if row["NOMBRE_LIMPIO"] != row["NOMBRE_CORREGIDO_FINAL"] else "Sin cambio",
        axis=1
    )

    return df
