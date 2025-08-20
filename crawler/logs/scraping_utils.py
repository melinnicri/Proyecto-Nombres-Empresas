# Librerías para Funciones de scraping y extracción
import re
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

def obtener_html_renderizado(url, espera_ms=3000):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_timeout(espera_ms)
        html = page.content()
        browser.close()
        return html

def buscar_por_palabra_clave(soup, clave):
    etiquetas = soup.find_all(text=re.compile(clave, re.IGNORECASE))
    for etiqueta in etiquetas:
        padre = etiqueta.find_parent()
        if padre:
            texto = padre.get_text(strip=True)
            if 5 < len(texto) < 150:
                return texto
    return " Error"

def extraer_email(texto):
    patron_clasico = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.(com|es|org|net|info|biz)"
    match = re.search(patron_clasico, texto)
    if match:
        return match.group(0).strip()

    patron_obfuscado = r"[a-zA-Z0-9_.+-]+\s?\[?@\(at\)?\]?\s?[a-zA-Z0-9-]+\s?\[?\.(dot)?\]?\s?[a-zA-Z]{2,}"
    match = re.search(patron_obfuscado, texto)
    if match:
        email = match.group(0)
        return (
            email.replace("[at]", "@").replace("(at)", "@").replace(" at ", "@")
                .replace("[dot]", ".").replace("(dot)", ".").replace(" dot ", ".")
                .replace(" ", "").strip()
        )
    return " No encontrado"

def extraer_telefono(texto):
    patron = r"(?:\+?\d{1,3}[\s\-()]*)?(?:\d{2,4}[\s\-()]*){2,3}\d{2,4}"
    telefonos = re.findall(patron, texto)
    filtrados = [t.strip() for t in telefonos if len(re.sub(r"\D", "", t)) >= 9]
    return filtrados[0] if filtrados else " No encontrado"

def extraer_direccion(texto):
    patron = r"(C\/|Calle|Avda\.?|Avenida|Plaza|Polígono|Camino|Carretera|Urbanización)[^\n]{5,150}"
    match = re.search(patron, texto, re.IGNORECASE)
    return match.group(0).strip() if match else " No encontrada"
