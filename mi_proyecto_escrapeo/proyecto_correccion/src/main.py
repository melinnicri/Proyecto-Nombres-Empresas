# Librerías de main
import pandas as pd
from normalizacion import normalizar_nombre
from correccion import crear_diccionario_mejorado, corregir_nombre_con_score, correccion_por_partes, pipeline_correccion
from validacion import (
    generar_revision_manual,
    exportar_casos_sospechosos,
    aplicar_correcciones_manual,
    generar_log_correcciones
)

# Generación de log de correcciones:
def ejecutar_pipeline(nombre_archivo_entrada="100empresas.csv"):
    df_empresas = pd.read_csv(nombre_archivo_entrada, encoding="utf-8")
    df_corregido = pipeline_correccion(df_empresas, "ADJUDICATARIO")

    generar_revision_manual(df_corregido)
    exportar_casos_sospechosos(df_corregido)

    df_corregido.to_csv("empresas_limpias_corregidas_mejorado.csv", index=False, encoding="utf-8-sig")
    print("Corrección automática exportada.")

    df_corregido = aplicar_correcciones_manual(df_corregido)
    df_corregido.to_csv("empresas_limpias_corregidas_final.csv", index=False, encoding="utf-8-sig")
    print("Corrección final con revisión manual exportada.")

    generar_log_correcciones(df_corregido)
    print("Log de correcciones generado.")

if __name__ == "__main__":
    ejecutar_pipeline()
