# Librerías para Flujo asíncrono y lógica de auditoría
import asyncio
from bs4 import BeautifulSoup
from crawl4ai import CrawlerHub
from scraping_utils import (
    obtener_html_renderizado,
    buscar_por_palabra_clave,
    extraer_email,
    extraer_telefono,
    extraer_direccion
)

crawler = CrawlerHub()

async def extraer_contacto_async(url):
    try:
        html = await crawler.fetch(url)
        texto = crawler.extract_text(html)

        if len(texto.strip()) < 500:
            html = obtener_html_renderizado(url)
            soup = BeautifulSoup(html, "html.parser")
            texto = soup.get_text(separator=" ", strip=True)
            fuente = "Playwright"
        else:
            soup = BeautifulSoup(html, "html.parser")
            fuente = "CrawlerHub"

        direccion = buscar_por_palabra_clave(soup, "Dirección|Dónde estamos")
        telefono = buscar_por_palabra_clave(soup, "Teléfono|Llámanos")
        email = buscar_por_palabra_clave(soup, "Email|Correo")
        if email == " Error":
            email = extraer_email(texto)

        with open("logs_scraping.txt", "a", encoding="utf-8") as f:
            f.write(f"{url} | Fuente: {fuente} | Dirección: {direccion != ' Error'} | "
                    f"Teléfono: {telefono != ' Error'} | Email: {email != ' Error'}\n")

        return direccion, telefono, email

    except Exception:
        return " Error", " Error", " Error"
