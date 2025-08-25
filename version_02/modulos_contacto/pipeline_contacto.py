# pipeline_contacto.py
# Asincrónico con asyncio y Playwright
import asyncio
import csv
from playwright.async_api import async_playwright, TimeoutError
from extractor import extraer_contacto
from tqdm.asyncio import tqdm_asyncio
import aiohttp

# Constante para limitar las tareas concurrentes, 
# Limita el número de tareas simultáneas para evitar sobrecarga del sistema o bloqueo por parte de los servidores.
MAX_CONCURRENCY = 5

async def buscar_pagina_contacto(url_base):
    """
    Intenta encontrar una página de contacto en el mismo sitio web.
    """
    posibles_urls = [
        f"{url_base.rstrip('/')}/contacto",
        f"{url_base.rstrip('/')}/contact",
        f"{url_base.rstrip('/')}/about-us",
        f"{url_base.rstrip('/')}/sobre-nosotros"
    ]
    
    # Aumenta el tiempo de espera para aiohttp
    timeout = aiohttp.ClientTimeout(total=15)
    
    async with aiohttp.ClientSession(timeout=timeout) as session:
        for url_pagina in posibles_urls:
            try:
                # Usa una petición HEAD para ser más rápido (solo pide los encabezados)
                async with session.head(url_pagina, allow_redirects=True) as response:
                    if response.status == 200:
                        return url_pagina
            except aiohttp.ClientError:
                continue
    return url_base

async def procesar_url_con_semaforo(semaforo, page, row):
    async with semaforo:
        url_principal = row.get("URL_OFICIAL")
        empresa = row.get("CORREGIDO_FINAL")

        if not url_principal or url_principal in ["No encontrada", "Error"]:
            await page.close() # Asegúrate de cerrar la página aquí también
            return {
                "empresa": empresa, "url": url_principal, "email": "", 
                "telefono": "", "direccion": "", "error": "URL no válida"
            }

        url_a_scrapear = await buscar_pagina_contacto(url_principal)

        try:
            await page.goto(url_a_scrapear, timeout=30000, wait_until="load")
            html = await page.content()
            contacto = extraer_contacto(html)
            return {
                "empresa": empresa, "url": url_a_scrapear, 
                "email": contacto.get("email", ""), 
                "telefono": contacto.get("telefono", ""), 
                "direccion": contacto.get("direccion", ""), "error": ""
            }
        except PlaywrightTimeoutError:
            return {
                "empresa": empresa, "url": url_a_scrapear, "email": "", 
                "telefono": "", "direccion": "", "error": "TimeoutError"
            }
        except Exception as e:
            return {
                "empresa": empresa, "url": url_a_scrapear, "email": "", 
                "telefono": "", "direccion": "", "error": str(e)
            }
        finally:
            await page.close()


async def main():
    resultados = []
    semaforo = asyncio.Semaphore(MAX_CONCURRENCY)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        
        with open("urls.csv", newline='', encoding="utf-8") as f:
            reader = csv.DictReader(f)
            
            tareas = []
            for row in reader:
                page = await browser.new_page()
                tareas.append(procesar_url_con_semaforo(semaforo, page, row))
            
            resultados = await tqdm_asyncio.gather(*tareas, desc="Extrayendo contactos")
        
        await browser.close()
    
    with open("contacto.csv", "w", newline='', encoding="utf-8") as out:
        fieldnames = ["empresa", "url", "email", "telefono", "direccion", "error"]
        writer = csv.DictWriter(out, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(resultados)
        
    print("✅ Información de contacto guardada en 'contacto.csv'")

if __name__ == "__main__":
    asyncio.run(main())