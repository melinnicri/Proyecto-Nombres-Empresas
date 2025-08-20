# Librerías para Normalización
# Scraping asincrónico
import asyncio
from crawl4ai import CrawlerHub


# Normalización
import re
import unicodedata

# Normalización de nombres de empresas
def normalizar_nombre(nombre):
    if not isinstance(nombre, str):
        return ""
    
    nombre = re.sub(r'\(.*?\)', '', nombre)
    nombre = nombre.upper()
    nombre = unicodedata.normalize("NFKD", nombre).encode("ASCII", "ignore").decode("utf-8")

    sustituciones = [
        (r'S\.?A\.?U\.?', 'SAU'),
        (r'S\.?L\.?U\.?', 'SLU'),
        (r'S\.?A\.?', 'SA'),
        (r'S\.?L\.?', 'SL'),
        (r'C\.?V\.?', 'CV'),
        (r'COOP\.?', 'COOP'),
        (r'INC\.?', 'INC'),
        (r'LTDA\.?', 'LTDA'),
        (r'EIRL\.?', 'EIRL')
    ]

    for patron, reemplazo in sustituciones:
        nombre = re.sub(patron, reemplazo, nombre, flags=re.IGNORECASE)

    nombre = re.sub(r"[^a-zA-Z0-9&/ ]", " ", nombre)
    nombre = re.sub(r"\s+", " ", nombre).strip()

    return nombre


