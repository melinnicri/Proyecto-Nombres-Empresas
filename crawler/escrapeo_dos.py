# ─── Librerías ────────────── Se realizó un escraping híbrido, asincrónico, con fallback dinámico y validación semántica.
import pandas as pd # Manejo de CSV y DataFrames
import re    # Expresiones regulares para patrones
import asyncio # Manejo de tareas asíncronas
from crawl4ai import CrawlerHub # Crawler para scraping rápido
from googlesearch import search  # Búsqueda de URLs oficiales
from tqdm.asyncio import tqdm_asyncio # Barra de progreso en tareas asíncronas
import aiohttp # Manejo de solicitudes HTTP asíncronas

from playwright.sync_api import sync_playwright # Renderizado de páginas con JavaScript
from bs4 import BeautifulSoup # Parsing de HTML

# Advertencia para ignorar SyntaxWarnings (no afecta al funcionamiento, pero limpia la salida)
# Esto es útil si se usan versiones de librerías que generan estas advertencias.
import warnings    # Limpieza de salida en consola
warnings.filterwarnings("ignore", category=SyntaxWarning)

# ─── Configuración inicial ─────────────────────────────────────────────────────
def obtener_html_renderizado(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_timeout(3000)  # espera carga JS
        html = page.content()
        browser.close()
        return html
    
# ─── Obtener HTML renderizado ────────────────────────────────────────────────
html = obtener_html_renderizado("https://www.acciona.com/es/soluciones/agua")  # usa playwright
soup = BeautifulSoup(html, "html.parser")  # ahora sí, con contenido dinámico
texto = soup.get_text(separator=" ", strip=True)



# ─── Headers ────────────────────────────────────────────────────────────────── 
# Evitar bloqueos automáticos por parte del servidor, 
# que podrían ocurrir si detecta peticiones provenientes de bots o scripts.
# Acceder a contenido completo, ya que algunos sitios sirven versiones distintas 
# según el tipo de cliente (por ejemplo, móvil vs escritorio).
# Mantener una práctica ética, sin ocultar la intención de acceso, pero respetando las reglas de presentación del sitio.
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.203"
    )
}

# ─── Cargar CSV ───────────────────────────────────────────────────────────────
RUTA_CSV = "nombres_normalizados_para_scraping.csv"
df = pd.read_csv(RUTA_CSV)

# ─── Validar columnas ────────────────────────────────────────────────────────
REQUIRED_COLS = {"NOMBRE_CORREGIDO_FINAL_MANUAL_NORMALIZADO", "CIF"}
if not REQUIRED_COLS.issubset(df.columns):
    raise ValueError(f"Faltan columnas requeridas: {REQUIRED_COLS - set(df.columns)}")

# ─── Buscar URL oficial ───────────────────────────────────────────────────────
def buscar_url(nombre_empresa):
    query = f"{nombre_empresa} sitio oficial España"
    try:
        resultados = list(search(query, num_results=5))
        return resultados[0] if resultados else "No encontrada"
    except Exception:
        return " Error en búsqueda"

# ─── Inicializar crawler ──────────────────────────────────────────────────────
crawler = CrawlerHub()

# ─── Función para buscar por palabra clave ──────────────────────────────────
# con playwright
def buscar_por_palabra_clave(soup, clave):
    etiquetas = soup.find_all(string=re.compile(clave, re.IGNORECASE))

    for etiqueta in etiquetas:
        padre = etiqueta.find_parent()
        if padre:
            texto = padre.get_text(strip=True)
            if len(texto) > 5 and len(texto) < 150:
                return texto
    return " Error"

# ─── Funciones de extracción ──────────────────────────────────────────────────
def extraer_direccion(texto):
    # Patrón ampliado con variantes comunes en español
    patron = r"""
        (?:
            C\/|Calle|Avda\.?|Avenida|Plaza|Polígono|Camino|Carretera|
            Urbanización|Edificio|Piso|Local|Oficina|Sector|Pasaje|Manzana|Bloque|Depto\.?
        )
        [^\n]{5,150}
    """
    match = re.search(patron, texto, re.IGNORECASE | re.VERBOSE)
    return match.group(0).strip() if match else " No encontrada"

def extraer_telefono(texto):
    # Permite formatos con espacios, guiones, paréntesis, y prefijos internacionales
    patron = r"(?:\+?\d{1,3}[\s\-()]*)?(?:\d{2,4}[\s\-()]*){2,3}\d{2,4}"
    telefonos = re.findall(patron, texto)

    # Filtrar por longitud mínima y evitar secuencias triviales
    telefonos_filtrados = [t.strip() for t in telefonos if len(re.sub(r"\D", "", t)) >= 9]

    return telefonos_filtrados[0] if telefonos_filtrados else " No encontrado"

def extraer_email(texto):
    # Patrón clásico
    patron_clasico = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.(?:com|es|org|net|info|biz)"
    match_clasico = re.search(patron_clasico, texto)

    if match_clasico:
        return match_clasico.group(0).strip()

    # Patrón obfuscado
    patron_obfuscado = r"[a-zA-Z0-9_.+-]+\s?\[?@\(at\)?\]?\s?[a-zA-Z0-9-]+\s?\[?\.(dot)?\]?\s?[a-zA-Z]{2,}"
    match_obfuscado = re.search(patron_obfuscado, texto)

    if match_obfuscado:  # Se corrigen formatos como juan [at] empresa [dot] com.
        email_obfuscado = match_obfuscado.group(0)
        # Normalizar el formato
        email_normalizado = (
            email_obfuscado.replace("[at]", "@")
            .replace("(at)", "@")
            .replace(" at ", "@")
            .replace("[dot]", ".")
            .replace("(dot)", ".")
            .replace(" dot ", ".")
            .replace(" ", "")
        )
        return email_normalizado.strip()

    return " No encontrado"

# ─── Función asíncrona principal ──────────────────────────────────────────────
async def extraer_contacto_async(url):
    try:
        html = await crawler.fetch(url)
        texto = crawler.extract_text(html)

        # Si el texto es muy corto, usar playwright como fallback, solo si el contenido extraído es insuficiente (<500 caracteres).
        if len(texto.strip()) < 500:
            html = obtener_html_renderizado(url)
            soup = BeautifulSoup(html, "html.parser")
            texto = soup.get_text(separator=" ", strip=True)
        else:
            soup = BeautifulSoup(html, "html.parser")

        direccion = buscar_por_palabra_clave(soup, "Dirección|Dónde estamos")
        telefono = buscar_por_palabra_clave(soup, "Teléfono|Llámanos")
        email = buscar_por_palabra_clave(soup, "Email|Correo")
        if email == " Error":
            email = buscar_email_regex(texto)

        with open("logs_errores_scraping.txt", "a", encoding="utf-8") as f:
            f.write(f"{url} → Dirección: {direccion != ' Error'}, "
                    f"Teléfono: {telefono != ' Error'}, "
                    f"Email: {email != ' Error'}\n")

        return direccion, telefono, email

    except Exception:
        return " Error", " Error", " Error"

# ─── Procesamiento asíncrono ──────────────────────────────────────────────────
async def procesar_empresas_async(df):
    async def procesar_fila(row):
        nombre = row["NOMBRE_CORREGIDO_FINAL_MANUAL_NORMALIZADO"]
        cif = row["CIF"]
        url = buscar_url(nombre)

        if url not in [" No encontrada", " Error en búsqueda"]:
            direccion, telefono, email = await extraer_contacto_async(url)
        else:
            direccion, telefono, email = " No disponible", " No disponible", " No disponible"

        return {
            "Empresa": nombre,
            "CIF": cif,
            "URL": url,
            "Dirección": direccion,
            "Teléfono": telefono,
            "Email": email
        }

    tareas = [procesar_fila(row) for _, row in df.iterrows()]
    resultados = await tqdm_asyncio.gather(*tareas, desc="Procesando empresas")
    return resultados


def buscar_email_regex(texto):
    match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", texto)
    return match.group(0) if match else " Error"

# Ejemplo de uso
direccion = buscar_por_palabra_clave(soup, "Dirección|Dónde estamos")
telefono = buscar_por_palabra_clave(soup, "Teléfono|Llámanos")
email = buscar_por_palabra_clave(soup, "Email|Correo")
if email == " Error":
    email = buscar_email_regex(texto)


# ─── Ejecutar flujo principal ─────────────────────────────────────────────────
if __name__ == "__main__":
    resultados = asyncio.run(procesar_empresas_async(df))
    df_resultado = pd.DataFrame(resultados)
    df_resultado.to_csv("contacto_empresas_es_2.csv", index=False)
    print("Datos guardados en contacto_empresas_es_2.csv")
