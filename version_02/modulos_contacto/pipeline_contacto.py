# pipeline_contacto.py
# Scraping asincrónico con Playwright para extraer contacto desde URLs oficiales

import asyncio
import csv
import aiohttp
from tqdm import tqdm

# Manejo de errores específicos de Playwright
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from playwright._impl._errors import TargetClosedError

# Función de extracción personalizada
from extractor import extraer_contacto

MAX_CONCURRENCY = 5  # Número máximo de tareas concurrentes

# Buscar página de contacto dentro del sitio
async def buscar_pagina_contacto(url_base):
    posibles_urls = [
        f"{url_base.rstrip('/')}/contacto",
        f"{url_base.rstrip('/')}/contact",
        f"{url_base.rstrip('/')}/about-us",
        f"{url_base.rstrip('/')}/sobre-nosotros"
    ]
    timeout = aiohttp.ClientTimeout(total=15)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        for url_pagina in posibles_urls:
            try:
                async with session.head(url_pagina, allow_redirects=True) as response:
                    if response.status == 200:
                        return url_pagina
            except aiohttp.ClientError:
                continue
    return url_base  # Fallback si no se encuentra página específica

# Procesar cada empresa con semáforo de concurrencia
async def procesar_url_con_semaforo(semaforo, page, row):
    async with semaforo:
        url_principal = row.get("URL_OFICIAL")
        empresa = row.get("CORREGIDO_FINAL")

        if not url_principal or url_principal in ["No encontrada", "Error"]:
            try:
                await page.close()
            except Exception:
                pass
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
        except TargetClosedError:
            return {
                "empresa": empresa, "url": url_a_scrapear, "email": "", 
                "telefono": "", "direccion": "", "error": "TargetClosedError"
            }
        except Exception as e:
            return {
                "empresa": empresa, "url": url_a_scrapear, "email": "", 
                "telefono": "", "direccion": "", "error": str(e)
            }
        finally:
            try:
                await page.close()
            except Exception:
                pass

# Función principal del pipeline
async def main():
    resultados_raw = []
    semaforo = asyncio.Semaphore(MAX_CONCURRENCY)

    async with async_playwright() as p:
        browser = await p.chromium.launch()

        try:
            with open("urls.csv", newline='', encoding="utf-8") as f:
                reader = list(csv.DictReader(f))
                tareas = []
                for row in reader:
                    page = await browser.new_page()
                    tareas.append(procesar_url_con_semaforo(semaforo, page, row))

                for coro in tqdm(asyncio.as_completed(tareas), total=len(tareas), desc="Extrayendo contactos"):
                    try:
                        resultado = await coro
                    except Exception as e:
                        resultado = {
                            "empresa": "", "url": "", "email": "", 
                            "telefono": "", "direccion": "", "error": str(e)
                        }
                    resultados_raw.append(resultado)

        except FileNotFoundError:
            print("No se encontró el archivo 'urls.csv'. Verifica la ruta.")
            return

        await browser.close()

    # Guardar resultados
    with open("contacto.csv", "w", newline='', encoding="utf-8") as out:
        fieldnames = ["empresa", "url", "email", "telefono", "direccion", "error"]
        writer = csv.DictWriter(out, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(resultados_raw)

# Disparador de ejecución
if __name__ == "__main__":
    print("Iniciando pipeline de contacto...")
    asyncio.run(main())
    print("Pipeline finalizado. Revisa contacto.csv para resultados.")