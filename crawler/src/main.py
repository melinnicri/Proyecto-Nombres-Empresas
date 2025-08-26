# Librerías:
import pandas as pd
from normalizacion import normalizar_nombre
from correccion import (
    crear_diccionario_empresas,
    corregir_nombre_con_score,
    correccion_por_partes,
    pipeline_correccion
)
from validacion import (
    generar_revision_manual,
    exportar_casos_sospechosos,
    aplicar_correcciones_manual,
    generar_log_correcciones
)

def ejecutar_pipeline(nombre_archivo_entrada="100empresas.csv"):
    
    # Cargar datos originales
    try:
        df_empresas = pd.read_csv(nombre_archivo_entrada, encoding="utf-8")
        print(f"Archivo cargado: {nombre_archivo_entrada}")
    except Exception as e:
        print(f"Error al cargar archivo: {e}")
        return

    # Validar columna clave
    if "ADJUDICATARIO" not in df_empresas.columns:
        print("La columna 'ADJUDICATARIO' no está presente en el archivo.")
        return

    # Respaldo del original
    df_empresas.to_csv("empresas_original.csv", index=False, encoding="utf-8-sig")

    # Corrección automática
    df_corregido = pipeline_correccion(df_empresas, "ADJUDICATARIO")
    df_corregido.to_csv("empresas_limpias_corregidas_mejorado.csv", index=False, encoding="utf-8-sig")
    print("Corrección automática exportada.")

    # Revisión manual y casos sospechosos
    generar_revision_manual(df_corregido)
    exportar_casos_sospechosos(df_corregido)

    # Aplicar correcciones manuales (si existen)
    df_corregido = aplicar_correcciones_manual(df_corregido)
    df_corregido.to_csv("empresas_limpias_corregidas_final.csv", index=False, encoding="utf-8-sig")
    print("Corrección final con revisión manual exportada.")

    # Log final de correcciones
    generar_log_correcciones(df_corregido)
    print("Log de correcciones generado.")

    # Checklist final
    print("\n Pipeline completado con éxito.")
    print("Archivos generados:")
    print("- empresas_original.csv")
    print("- empresas_limpias_corregidas_mejorado.csv")
    print("- revision_manual.csv")
    print("- correcciones_sospechosas.csv")
    print("- empresas_limpias_corregidas_final.csv")
    print("- log_de_correcciones.csv")

# Para ver las correcciones en la DF (fueron 10 correcciones manuales)
df_corregido = pd.read_csv("empresas_limpias_corregidas_final.csv", encoding="utf-8-sig")

correcciones_automaticas = df_corregido[df_corregido["STATUS_CORRECCIÓN"] == "Corregido"]
print(f"Correcciones automáticas aplicadas: {len(correcciones_automaticas)}")



if __name__ == "__main__":
    ejecutar_pipeline()
