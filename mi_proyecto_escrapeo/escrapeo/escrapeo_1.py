# Entorno virtual carpeta escrapeo ligada al entorno virtual de la otra carpeta proyecto_correccion 
# se liga lo siguiente en la terminal: & "C:..\trabajo_nuevo\proyecto_correccion\.venv_limpio\Scripts\Activate.ps1"

# Activación del entorno virtual `.venv_limpio`

## Contexto del proyecto

# Este entorno virtual forma parte del módulo de limpieza y corrección de nombres empresariales dentro del proyecto `proyecto_correccion`. 
# Se prioriza la trazabilidad, modularidad y reproducibilidad en cada etapa del flujo.

#--- Incidente detectado:

# **Fecha:** 13 de agosto de 2025  
# **Descripción:** Al intentar activar el entorno virtual desde PowerShell, el script `Activate.ps1` no se ejecutaba correctamente.

#**Comando inicial usado:**
#```powershell
#& "C:..\trabajo_nuevo\proyecto_correccion\.venv_limpio\Scripts\Activate.ps1"

# Librerías necesarias para escrapeo de páginas web (sincrónico):
import pandas as pd  # Para cargar y guardar CSVs
import requests  # Para obtener el HTML de las páginas
from bs4 import BeautifulSoup  # Para extraer texto del HTML
import lxml  # Parser rápido y robusto (usado por BeautifulSoup)
from fake_useragent import UserAgent  # Para simular navegadores reales
from googlesearch import search  # Para obtener URLs oficiales
import re  # Para extraer dirección, teléfono y email
from tqdm import tqdm  # Para mostrar barra de progreso
import os
print("Librerías cargadas correctamente.")

# Advertencia para ignorar SyntaxWarnings (no afecta al funcionamiento, pero limpia la salida)
# Esto es útil si se usan versiones de librerías que generan estas advertencias.
import warnings
warnings.filterwarnings("ignore", category=SyntaxWarning)

# Buscar URL oficial en Google (sin cambios, sigue siendo sincrónica)
def buscar_url(nombre_empresa):
    query = f"{nombre_empresa} sitio oficial España"
    try:
        resultados = list(search(query, num_results=5))
        return resultados[0] if resultados else "No encontrada"
    except Exception:
        return "Error en búsqueda"

# Extraer contacto de forma sincrónica
def extraer_contacto(url):
    try:
        ua = UserAgent()
        headers = {"User-Agent": ua.random}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "lxml")
        texto = soup.get_text(separator=" ", strip=True)

        direccion = re.search(r"(Calle|Avda\.?|Avenida|Polígono|Plaza)[^\n,]{10,100}", texto)
        direccion = direccion.group(0) if direccion else "No encontrada"

        telefono = re.search(r"(?:\+34\s?)?(?:\d{2,3}[\s\-]?){3,4}", texto)
        telefono = telefono.group(0) if telefono else "No encontrado"

        email = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", texto)
        email = email.group(0) if email else "No encontrado"

        return direccion, telefono, email

    except Exception:
        return "Error", "Error", "Error"

# Abrir archivo CSV con nombres de empresas:
# Ruta relativa al archivo CSV desde el script actual
ruta_csv = r"../proyecto_correccion/empresas_limpias_corregidas_final.csv"

# Verificación de existencia
if not os.path.exists(ruta_csv):
    raise FileNotFoundError(f"No se encontró el archivo en: {os.path.abspath(ruta_csv)}")

# Cargar el archivo CSV
df = pd.read_csv(ruta_csv)
print("Archivo cargado correctamente.")
print("Ruta completa:", os.path.abspath(ruta_csv))

# Validar columnas requeridas
print(df.info())
print(df.head())


# Procesar empresas sincrónicamente
def procesar_empresas(df):
    resultados = []

    for _, row in tqdm(df.iterrows(), total=len(df), desc="Procesando empresas"):
        nombre = row["NOMBRE_CORREGIDO_FINAL"]
        cif = row["CIF"]
        url = buscar_url(nombre)

        if url not in ["No encontrada", "Error en búsqueda"]:
            direccion, telefono, email = extraer_contacto(url)
        else:
            direccion, telefono, email = "No disponible", "No disponible", "No disponible"

        resultados.append({
            "Empresa": nombre,
            "CIF": cif,
            "URL": url,
            "Dirección": direccion,
            "Teléfono": telefono,
            "Email": email
        })

    return resultados


# Validar columnas
required_cols = {"NOMBRE_CORREGIDO_FINAL", "CIF"}
if not required_cols.issubset(df.columns):
    raise ValueError(f"Faltan columnas requeridas: {required_cols - set(df.columns)}")

# Ejecutar flujo sincrónico
resultados = procesar_empresas(df)

# Exportar resultados
df_resultado = pd.DataFrame(resultados)
df_resultado.to_csv("contacto_empresas_es.csv", index=False)
print("Datos guardados en contacto_empresas_es.csv")

