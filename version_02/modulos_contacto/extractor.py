# extractor.py
# Librerías del auxiliar
import re
import requests
from bs4 import BeautifulSoup

# Función de extracción de la información de contacto:
# Aquí debes eliminar el espacio o tabulación al principio de la línea
# Si la línea 52 es esta:
#     Extracción de la información de contacto (dirección, teléfono, email desde una url dada)
# Cámbiala por esta:
# Extracción de la información de contacto (dirección, teléfono, email desde una url dada)

def extraer_contacto(html_content):
    """
    Extracción de la información de contacto (dirección, teléfono, email desde una url dada)
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # Búsqueda en el pie de página y secciones de contacto
    posibles_secciones = soup.find_all(['footer', 'div', 'p', 'span'], class_=re.compile(r'contact|info|footer', re.I))
    textos_a_buscar = [sec.get_text() for sec in posibles_secciones]
    textos_a_buscar.append(soup.get_text()) # Por si no está en las secciones comunes

    texto_combinado = " ".join(textos_a_buscar)

    # Regex para los datos de contacto
    email_regex = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    telefono_regex = r"(?:\+34)?[\s.-]?[\d\s-]{9,15}"
    # Se ha simplificado la regex de dirección, es difícil encontrar una perfecta
    direccion_regex = r"(Calle|Avda|Avenida|Plaza|Paseo|Camino|Ctra\.)[\s\w.,#-ñÑáéíóúÁÉÍÓÚüÜ]+(?:\d{1,4}[A-Za-z]?\b)?"
    
    email = re.search(email_regex, texto_combinado)
    telefono = re.search(telefono_regex, texto_combinado)
    direccion = re.search(direccion_regex, texto_combinado, re.IGNORECASE)

    return {
        "direccion": direccion.group(0) if direccion else "No encontrado",
        "telefono": telefono.group(0) if telefono else "No encontrado",
        "email": email.group(0) if email else "No encontrado"
    }

if __name__ == "__main__":
    html_ejemplo = """
    <html><body>
    <footer>
    <p>Dirección: Calle Falsa 123, 28001 Madrid. Teléfono: +34 91 123 4567. Email: info@ejemplo.com</p>
    </footer>
    </body></html>
    """
    contacto = extraer_contacto(html_ejemplo)
    print(contacto)



"""
# Función de extracción de la información de contacto:
def extraer_contacto(html_content):
"""
"""Extracción de la información de contacto (dirección, teléfono, email desde una url dada)
"""
"""    try:
        # Aquí ya recibes el contenido HTML, no necesitas hacer una nueva petición.
        soup = BeautifulSoup(html_content, 'html.parser')
        text_content = soup.get_text()

        # Regular Expressions (Regex):
        email_regex = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
        telefono_regex = r"(?:\+34|0034)?[\s.-]?[679]\d{8}"
        
        # Una regex más robusta para extraer información de direcciones españolas:
        direccion_regex = r"(?:Calle|Avda|Avenida|Plaza|Paseo|Camino|Ctra\.)[\s\w.,#-ñÑáéíóúÁÉÍÓÚüÜ]+\b\d{1,4}"

        # Find all matches
        emails = re.findall(email_regex, text_content)
        telefonos = re.findall(telefono_regex, text_content)
        direcciones = re.findall(direccion_regex, text_content, re.IGNORECASE)

        # Return the first found match for each type in the new desired order
        return {
            "direccion": direcciones[0] if direcciones else "",
            "telefono": telefonos[0] if telefonos else "",
            "email": emails[0] if emails else ""
        }
    
    except Exception as e:
        print(f"Un error inesperado ha ocurrido: {e}")
        return {
            "direccion": "Error",
            "telefono": "Error",
            "email": "Error"
        }
"""

"""
# Ejemplo de cómo se usa la función (con un fragmento de HTML de ejemplo)
if __name__ == "__main__":
    html_ejemplo =
    <html>
    <body>
    <p>Dirección: Calle Falsa 123, 28001 Madrid. Teléfono: +34 91 123 4567. Email: info@ejemplo.com</p>
    </body>
    </html>
    contacto = extraer_contacto(html_ejemplo)
    print(contacto)
"""