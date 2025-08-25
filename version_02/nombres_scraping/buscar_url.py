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
        # Limitar a 5 resultados para reducir tiempo de espera
        resultados = await loop.run_in_executor(None, lambda: list(search(query, num_results=5)))

        for url in resultados:
            # Filtrar dominios no deseados
            if "google.com" not in url and "youtube.com" not in url:
                if modo_estricto:
                    if contiene_nombre_empresa(url, nombre_empresa):
                        return url, "Validada por contenido"
                else:
                    return url, "Dominio válido"

        return "No encontrada", "Sin resultados"

    except Exception as e:
        return f"Error: {e}", "Error en la búsqueda"

# ─── Función principal para procesar el DataFrame CORREGIDA ──────────────────
async def procesar_dataframe(df):
    tasks = [buscar_url_oficial_async(row['CORREGIDO_FINAL']) for _, row in df.iterrows()]
    resultados = await tqdm_asyncio.gather(*tasks, desc="Buscando URLs")

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
        
        # --- CAMBIO AQUÍ ---
        # El archivo de salida para este script será la entrada para el siguiente
        df_resultado.to_csv("urls.csv", index=False)
        # --- FIN DEL CAMBIO ---
        
        print("✅ URLs oficiales guardadas en urls.csv")
    except FileNotFoundError:
        print("Error: El archivo 'nombres_scraping.csv' no se encuentra.")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")