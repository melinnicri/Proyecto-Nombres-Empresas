
# Librerías de Validación
import pandas as pd

# 1. Revisión por score
def generar_revision_por_score(df, output_file="revision_manual_score.csv"):
    revision = df[(df["MATCH_SCORE"] > 60) & (df["MATCH_SCORE"] < 85)].copy()
    
    if not revision.empty:
        revision["CORRECCION_MANUAL"] = revision["NOMBRE_CORREGIDO_FINAL"]
        columnas_exportar = [
            "ADJUDICATARIO", "NOMBRE_LIMPIO", "NOMBRE_CORREGIDO", 
            "MATCH_SCORE", "NOMBRE_CORREGIDO_FINAL", "CORRECCION_MANUAL"
        ]
        revision[columnas_exportar].to_csv(output_file, index=False, encoding="utf-8-sig")
        print(f"Archivo '{output_file}' generado para revisión manual por score.")
    else:
        print("No se detectaron casos dudosos para revisión.")

# Combinación de revisión y aplicación de correcciones manuales:
def revisar_y_aplicar_correcciones_manual(df, diccionario_manual, archivo_revision="revision_manual.csv"):
    """
    Combina la generación de revisión manual y la aplicación de correcciones.
    Usa el diccionario como sugerencia y permite edición externa del CSV.
    """
    try:
        # Paso 1: Generar archivo de revisión con sugerencias
        df_revision = df[df["STATUS_CORRECCIÓN"] == "Sin cambio"].copy()
        df_revision["SUGERENCIA_MANUAL"] = df_revision["NOMBRE_LIMPIO"].apply(
            lambda x: diccionario_manual.get(x, "")
        )
        df_revision["CORRECCION_MANUAL"] = df_revision["SUGERENCIA_MANUAL"]  # editable por humanos
        df_revision.to_csv(archivo_revision, index=False, encoding="utf-8-sig")
        print(f"Archivo '{archivo_revision}' exportado para revisión manual.")

        # Paso 2: Leer correcciones desde el archivo (editado o no)
        revision = pd.read_csv(archivo_revision, encoding="utf-8-sig")
        correcciones = dict(zip(revision["NOMBRE_LIMPIO"], revision["CORRECCION_MANUAL"]))

        # Paso 3: Combinar con diccionario manual si se desea
        correcciones.update(diccionario_manual)

        # Paso 4: Aplicar correcciones
        df["NOMBRE_CORREGIDO_FINAL"] = df.apply(
            lambda row: correcciones.get(row["NOMBRE_LIMPIO"], row.get("NOMBRE_CORREGIDO_FINAL", row["NOMBRE_LIMPIO"])),
            axis=1
        )
        df["STATUS_CORRECCIÓN"] = df.apply(
            lambda row: "Corregido manual" if row["NOMBRE_LIMPIO"] != row["NOMBRE_CORREGIDO_FINAL"] else "Sin cambio",
            axis=1
        )

        print("Correcciones manuales aplicadas.")
        return df

    except Exception as e:
        print(f"Error en revisión/aplicación manual: {e}")
        return df


# 3. Exportar casos sospechosos
def exportar_casos_sospechosos(df, output_file="correcciones_sospechosas.csv"):
    # Detectar si el primer token del nombre limpio no aparece en el corregido
    df["sospechoso"] = df.apply(
        lambda row: (
            isinstance(row["NOMBRE_CORREGIDO_FINAL"], str) and
            isinstance(row["NOMBRE_LIMPIO"], str) and
            row["NOMBRE_LIMPIO"].split()[0] not in row["NOMBRE_CORREGIDO_FINAL"]
        ),
        axis=1
    )

    # También considerar casos donde el nombre corregido es mucho más largo
    casos_sospechosos = df[
        (df["MATCH_SCORE"] >= 85) &
        (df["sospechoso"] |
        ((df["NOMBRE_CORREGIDO_FINAL"].str.len() - df["NOMBRE_LIMPIO"].str.len()) > 20))
    ]

    if not casos_sospechosos.empty:
        casos_sospechosos.to_csv(output_file, index=False, encoding="utf-8-sig")
        print(f"Archivo '{output_file}' generado con correcciones sospechosas.")
    else:
        print("No se detectaron correcciones sospechosas.")


# 4. Aplicar correcciones manuales
def aplicar_correcciones_manual(df_original, archivo_revision="revision_manual.csv"):
    try:
        revision = pd.read_csv(archivo_revision, encoding="utf-8-sig")
        correcciones = dict(zip(revision["NOMBRE_LIMPIO"], revision["CORRECCION_MANUAL"]))
        
        df_original["NOMBRE_CORREGIDO_FINAL"] = df_original.apply(
            lambda row: correcciones.get(row["NOMBRE_LIMPIO"], row.get("NOMBRE_CORREGIDO_FINAL", row["NOMBRE_LIMPIO"])),
            axis=1
        )
        
        df_original["STATUS_CORRECCIÓN"] = df_original.apply(
            lambda row: "Corregido manual" if row["NOMBRE_LIMPIO"] != row["NOMBRE_CORREGIDO_FINAL"] else "Sin cambio",
            axis=1
        )
        
        print("Correcciones manuales aplicadas.")
        return df_original
    except Exception as e:
        print(f"Error al aplicar correcciones manuales: {e}")
        return df_original


# 5. Generar log de correcciones
def generar_log_correcciones(df, archivo_revision="revision_manual.csv", archivo_salida="log_de_correcciones.csv"):
    try:
        revision = pd.read_csv(archivo_revision, encoding="utf-8-sig")
        revision_dict = dict(zip(revision["NOMBRE_LIMPIO"], revision["CORRECCION_MANUAL"]))
        
        log = df.copy()
        log["CORREGIDO_AUTOMÁTICO"] = log.get("NOMBRE_CORREGIDO", log["NOMBRE_LIMPIO"])
        log["CORRECCION_MANUAL"] = log["NOMBRE_LIMPIO"].map(revision_dict)
        log["CORREGIDO_FINAL"] = log["NOMBRE_CORREGIDO_FINAL"]
        
        def tipo(row):
            if pd.notna(row["CORRECCION_MANUAL"]):
                return "Manual"
            elif row["NOMBRE_LIMPIO"] != row["CORREGIDO_AUTOMÁTICO"]:
                return "Automática"
            else:
                return "Sin cambio"
        
        log["TIPO_CORRECCIÓN"] = log.apply(tipo, axis=1)
        
        columnas_log = [
            "NOMBRE_LIMPIO", "CORREGIDO_AUTOMÁTICO", "CORRECCION_MANUAL",
            "CORREGIDO_FINAL", "TIPO_CORRECCIÓN"
        ]
        
        log[columnas_log].to_csv(archivo_salida, index=False, encoding="utf-8-sig")
        print(f"Log de correcciones guardado en {archivo_salida}")
    except Exception as e:
        print(f"Error al generar log de correcciones: {e}")
