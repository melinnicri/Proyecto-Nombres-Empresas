# Sistema asincrónico para búsqueda de URLs oficiales de empresas
# Librerías
import pandas as pd                                         # Manipulación y análisis de datos en Python
import requests                                             # Para hacer peticiones HTTP
import asyncio                                              # Soporte para programación asíncrona, varias tareas al mismo tiempo
import warnings                                             # Manejo de advertencias
from googlesearch import search                             # Búsqueda en Google
from tqdm.asyncio import tqdm_asyncio                       # Barra de progreso para tareas asíncronas
from bs4 import BeautifulSoup                               # Análisis de documentos HTML y XML

warnings.filterwarnings("ignore", category=SyntaxWarning)   # Ignorar advertencias de sintaxis
from tqdm import tqdm

# ─── Configuración ──────────────────────────────────────────────────────────
# Definición de los headers para las peticiones HTTP, simula visita a la página web
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.203"
    )
}

# ─── Extracción de localidad ─────────────────────────────────────────────────
# Esta función es un marcador de posición:
def contiene_nombre_empresa(url, nombre_empresa):
    try:
        response = requests.get(url, headers=HEADERS, timeout=5)
        return nombre_empresa.lower() in response.text.lower()
    except requests.exceptions.RequestException:
        return False
    
# ─── Extracción de localidad desde el nombre ────────────────────────────────
def contiene_localidad(url, nombre_empresa):
    return True # 

# ─── Búsqueda asincrónica CORREGIDA ─────────────────────────────────────────
async def buscar_url_oficial_async(nombre_empresa, modo_estricto=False):
    loop = asyncio.get_event_loop()
    try:
        query = f"{nombre_empresa} sitio oficial empresa España"
        resultados = await loop.run_in_executor(None, lambda: list(search(query, num_results=5)))

        for url in resultados:
            # Validación de URL sospechosa
            if not url.startswith("http"):
                print(f"[LOG] URL inválida para {nombre_empresa}: {url}")
                continue

            # Filtrar dominios no deseados
            if "google.com" in url or "youtube.com" in url or url.startswith("/search"):
                continue

            # Validación por contenido si modo_estricto está activado
            if modo_estricto:
                if contiene_nombre_empresa(url, nombre_empresa):
                    return url, "Validada por contenido"
                else:
                    continue  # Si no contiene el nombre, sigue buscando
            else:
                return url, "Dominio válido"

        return "No encontrada", "Sin resultados"

    except Exception as e:
        return f"Error: {e}", "Error en la búsqueda"

# ─── Función principal para procesar el DataFrame CORREGIDA ──────────────────
async def procesar_dataframe(df):
    tareas = [
        (i, buscar_url_oficial_async(row['CORREGIDO_FINAL'])) 
        for i, row in df.iterrows()
    ]

    resultados = [None] * len(df)  # Prepara lista vacía con mismo largo

    for i, coro in tqdm(tareas, desc="Buscando URLs"):
        try:
            resultado = await coro
        except Exception as e:
            resultado = ("Error: " + str(e), "Error en la búsqueda")
        resultados[i] = resultado  # Asigna en la posición correcta

    df['URL_OFICIAL'], df['ESTADO'] = zip(*resultados)
    return df

# ─── Carga y validación del CSV ───────────────────────────────────────────────
if __name__ == "__main__":
    try:
        RUTA_CSV = "nombres_scraping.csv"
        df = pd.read_csv(RUTA_CSV)

        REQUIRED_COLS = {"CORREGIDO_FINAL", "CIF"}
        if not REQUIRED_COLS.issubset(df.columns):
            raise ValueError(f"Faltan columnas requeridas: {REQUIRED_COLS - set(df.columns)}")
        
        df_resultado = asyncio.run(procesar_dataframe(df))
        
        # El archivo de salida para este script será la entrada para el siguiente
        df_resultado.to_csv("urls.csv", index=False)
        
        print("✅ URLs oficiales guardadas en urls.csv")
    except FileNotFoundError:
        print("Error: El archivo 'nombres_scraping.csv' no se encuentra.")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")