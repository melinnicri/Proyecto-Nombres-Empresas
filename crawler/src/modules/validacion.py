# Librerías para validación:
import pandas as pd

def generar_revision_manual(df, output_file="revision_manual.csv", min_score=60, max_score=85):
    """
    Exporta casos con score intermedio para revisión humana.
    """
    revision = df[(df["MATCH_SCORE"] > min_score) & (df["MATCH_SCORE"] < max_score)].copy()
    
    if not revision.empty:
        revision["CORRECCION_MANUAL"] = revision["CORREGIDO_FINAL"]
        columnas = [
            "ADJUDICATARIO", "NOMBRE_LIMPIO", "NOMBRE_CORREGIDO", 
            "MATCH_SCORE", "CORREGIDO_FINAL", "CORRECCION_MANUAL"
        ]
        revision[columnas].to_csv(output_file, index=False, encoding="utf-8-sig")
        print(f"Revisión manual exportada a: {output_file}")
    else:
        print("No hay casos intermedios para revisión.")

def exportar_casos_sospechosos(df, output_file="correcciones_sospechosas.csv", delta_longitud=20):
    """
    Detecta correcciones sospechosas por divergencia semántica o longitud excesiva.
    """
    df["sospechoso"] = df.apply(
        lambda row: (
            isinstance(row["CORREGIDO_FINAL"], str) and
            isinstance(row["NOMBRE_NORMALIZADO"], str) and
            row["NOMBRE_NORMALIZADO"].split()[0] not in row["CORREGIDO_FINAL"]
        ),
        axis=1
    )
    
    casos = df[
    (df["MATCH_SCORE"] >= 85) &
    (
        df["sospechoso"] |
        ((df["CORREGIDO_FINAL"].str.len() - df["NOMBRE_NORMALIZADO"].str.len()) > delta_longitud)
    )
]

    if not casos.empty:
        casos.to_csv(output_file, index=False, encoding="utf-8-sig")
        print(f"Correcciones sospechosas exportadas a: {output_file}")
    else:
        print("No se detectaron correcciones sospechosas.")

def aplicar_correcciones_manual(df, archivo_revision="revision_manual.csv"):
    """
    Aplica correcciones manuales al DataFrame original.
    """
    try:
        revision = pd.read_csv(archivo_revision, encoding="utf-8-sig")
        correcciones = dict(zip(revision["NOMBRE_LIMPIO"], revision["CORRECCION_MANUAL"]))
        
        df["NOMBRE_CORREGIDO_PREVIO"] = df["CORREGIDO_FINAL"]
        df["CORREGIDO_FINAL"] = df.apply(
            lambda row: correcciones.get(row["NOMBRE_LIMPIO"], row["CORREGIDO_FINAL"]),
            axis=1
        )
        
        df["STATUS_CORRECCIÓN"] = df.apply(
            lambda row: "Corregido manual" if row["NOMBRE_CORREGIDO_PREVIO"] != row["CORREGIDO_FINAL"] else "Sin cambio",
            axis=1
        )
        
        print("🔧 Correcciones manuales aplicadas.")
        return df
    except Exception as e:
        print(f"Error al aplicar correcciones: {e}")
        return df

def generar_log_correcciones(df, archivo_revision="revision_manual.csv", archivo_salida="log_de_correcciones.csv"):
    """
    Genera log final con tipo de corrección aplicada.
    """
    try:
        revision = pd.read_csv(archivo_revision, encoding="utf-8-sig")
        revision_dict = dict(zip(revision["NOMBRE_LIMPIO"], revision["CORRECCION_MANUAL"]))
        
        log = df.copy()
        log["CORREGIDO_AUTOMÁTICO"] = log.get("NOMBRE_CORREGIDO", log["NOMBRE_LIMPIO"])
        log["CORRECCION_MANUAL"] = log["NOMBRE_LIMPIO"].map(revision_dict)
        log["CORREGIDO_FINAL"] = log["CORREGIDO_FINAL"]
        
        def tipo(row):
            if pd.notna(row["CORRECCION_MANUAL"]):
                return "Manual"
            elif row["NOMBRE_LIMPIO"] != row["CORREGIDO_AUTOMÁTICO"]:
                return "Automática"
            else:
                return "Sin cambio"
        
        log["TIPO_CORRECCIÓN"] = log.apply(tipo, axis=1)
        
        columnas = [
            "NOMBRE_LIMPIO", "CORREGIDO_AUTOMÁTICO", "CORRECCION_MANUAL",
            "CORREGIDO_FINAL", "TIPO_CORRECCIÓN"
        ]
        
        log[columnas].to_csv(archivo_salida, index=False, encoding="utf-8-sig")
        print(f"Log de correcciones guardado en: {archivo_salida}")
    except Exception as e:
        print(f"Error al generar log: {e}")
