# main.py — Validación y corrección de nombres extraídos con Crawl4AI

import pandas as pd
import os

# Crear carpeta logs si no existe
os.makedirs("logs", exist_ok=True)

# Confirmación opcional para auditoría
if os.path.exists("logs"):
    print("Carpeta 'logs/' disponible para escritura.")
else:
    raise Exception("No se pudo crear la carpeta 'logs/'.")

# Corrección automática y por partes

from correccion_crawler import (
    crear_diccionario_mejorado,
    corregir_nombre_con_score,
    correccion_por_partes,
    pipeline_correccion
)

# Validación y revisión manual
from validacion_crawler import (
    exportar_casos_sospechosos,
    revisar_y_aplicar_correcciones_manual,
    generar_log_correcciones
)

# Diccionario manual con errores tipográficos conocidos
from diccionario_manual import diccionario_manual, agregar_correccion

# Corrección modular con trazabilidad
from gestor_correcciones import (
    cargar_diccionario_manual,
    corregir_nombre,
    guardar_diccionario
)

from normalizacion_crawler import normalizar_nombre as normalizar_basico  # si tienes esta función aparte

# Actualizar diccionario manual con casos conocidos
diccionario_manual.update({
    "ASOCIACION FAMILAIRES ENFERMOS ALZHEIMER Y OTRAS DEMENCIAS DE LANZAROTE":
    "ASOCIACION FAMILIARES ENFERMOS ALZHEIMER Y OTRAS DEMENCIAS DE LANZAROTE"
    # Puedes agregar más casos aquí
})

# Pipeline principal con validación y corrección
def ejecutar_pipeline(nombre_archivo_entrada="100empresas.csv"):
    df_empresas = pd.read_csv(nombre_archivo_entrada, encoding="utf-8")

    # Corrección automática con heurísticas
    df_corregido = pipeline_correccion(df_empresas, "ADJUDICATARIO")
    df_corregido.to_csv("empresas_limpias_corregidas_mejorado.csv", index=False, encoding="utf-8-sig")
    print("Corrección automática exportada.")


    # Revisión manual y sugerencias
    ejecutar_revision_manual(df_corregido, diccionario_manual)
    exportar_casos_sospechosos(df_corregido)

# Revisión manual y aplicación de correcciones
def ejecutar_revision_manual(df_original, diccionario_manual):
    df_revision = df_original[df_original["STATUS_CORRECCIÓN"] == "Sin cambio"].copy()
    df_revision["SUGERENCIA_MANUAL"] = df_revision["NOMBRE_LIMPIO"].apply(
        lambda x: diccionario_manual.get(x, "")
    )
    df_revision.to_csv("revision_manual.csv", index=False, encoding="utf-8-sig")
    print("Revisión manual exportada.")

    df_corregido = revisar_y_aplicar_correcciones_manual(df_original, diccionario_manual)
    df_corregido.to_csv("empresas_limpias_corregidas_final.csv", index=False, encoding="utf-8-sig")
    print("Corrección final con revisión manual exportada.")

    generar_log_correcciones(df_corregido)
    print("Log de correcciones generado.")

# Corrección alternativa con gestor_correcciones (si quieres comparar)
def ejecutar_pipeline_modular(nombre_archivo="datos_originales.csv"):
    df = pd.read_csv(nombre_archivo, encoding="utf-8-sig")
    diccionario = cargar_diccionario_manual("diccionario_manual.csv")

    df['NOMBRE_CORREGIDO'] = df['ADJUDICATARIO'].apply(
        lambda x: corregir_nombre(x, diccionario, normalizar_nombre)  # ← AQUÍ VA
    )

    df.to_csv("resultado_corregido.csv", index=False, encoding="utf-8-sig")
    guardar_diccionario(diccionario)
    print("Corrección modular exportada.")


# Punto de entrada
if __name__ == "__main__":
    ejecutar_pipeline()
    # Si quieres ejecutar el otro flujo:
    # ejecutar_pipeline_modular()
