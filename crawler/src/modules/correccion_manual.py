# Librerías
import pandas as pd

# Cargar archivos
df_empresas = pd.read_csv("empresas_limpias_corregidas_final.csv", encoding="utf-8-sig")
df_diccionario = pd.read_csv("diccionario_nombres_corregidos.csv", encoding="utf-8-sig")

# Crear diccionario manual: ADJUDICATARIO → NOMBRE_CORREGIDO_FINAL
diccionario = dict(zip(df_diccionario["NOMBRE_ORIGINAL"], df_diccionario["NOMBRE_CORREGIDO_FINAL"]))

# Guardar versión previa
df_empresas["ANTES_CORRECCIÓN"] = df_empresas["CORREGIDO_FINAL"]

# Aplicar corrección manual si el nombre original está en el diccionario
df_empresas["CORREGIDO_FINAL"] = df_empresas.apply(
    lambda row: diccionario[row["ADJUDICATARIO"]] if row["ADJUDICATARIO"] in diccionario else row["CORREGIDO_FINAL"],
    axis=1
)

# Registrar si hubo cambio
df_empresas["STATUS_CORRECCIÓN"] = df_empresas.apply(
    lambda row: "Corregido manual" if row["ANTES_CORRECCIÓN"] != row["CORREGIDO_FINAL"] else row["STATUS_CORRECCIÓN"],
    axis=1
)

# Filtrar correcciones aplicadas
corregidos = df_empresas[df_empresas["STATUS_CORRECCIÓN"] == "Corregido manual"]
print(f"Se aplicaron {len(corregidos)} correcciones manuales.")
print(corregidos[["ADJUDICATARIO", "ANTES_CORRECCIÓN", "CORREGIDO_FINAL"]])

# Exportar log de correcciones
corregidos.to_csv("log_correcciones_aplicadas.csv", index=False, encoding="utf-8-sig")

# Exportar archivo final corregido
df_empresas.to_csv("empresas_corregidas_final.csv", index=False, encoding="utf-8-sig")

# Crear nuevo DataFrame con columnas seleccionadas desde df_empresas
columnas_seleccionadas = ['Nº', 'CORREGIDO_FINAL', 'CIF']
df_nombres_scraping = df_empresas[columnas_seleccionadas]

# Guardar como CSV limpio y final
df_nombres_scraping.to_csv("nombres_scraping.csv", index=False, encoding="utf-8-sig")

df_nombres_scraping.head()