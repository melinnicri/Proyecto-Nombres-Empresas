# extractor.py
# Librerías del auxiliar
import re                           # para aplicar expresiones regulares (regex)
from bs4 import BeautifulSoup       # para parsear y navegar el contenido HTML


# Función de extracción de la información de contacto:
def extraer_contacto(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    posibles_secciones = soup.find_all(['footer', 'div', 'p', 'span'], class_=re.compile(r'contact|info|footer', re.I))
    textos_a_buscar = [sec.get_text() for sec in posibles_secciones]
    textos_a_buscar.append(soup.get_text())

    texto_combinado = " ".join(textos_a_buscar)
    texto_limpio = re.sub(r'\s+', ' ', texto_combinado).strip()

    email_regex = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    telefono_regex = r"(?:\+34)?[\s.-]?\d{2,3}[\s.-]?\d{2,3}[\s.-]?\d{2,3}"
    direccion_regex = r"(?:Calle|Avda|Avenida|Plaza|Paseo|Camino|Ctra\.|Carrer)[\s\w.,º#-]+?\d{1,4}[A-Za-z]?(?:\s+\d{5})?\s+[A-ZÁÉÍÓÚÑa-záéíóúñüÜ]+"

    email = re.search(email_regex, texto_limpio)
    telefono = re.search(telefono_regex, texto_limpio)
    direcciones = [match.group(0).strip() for match in re.finditer(direccion_regex, texto_limpio)]

    # Validación semántica por localidad
    def validar_localidad(direccion):
        localidades = ["Madrid", "Albacete", "Palma", "Málaga"]
        return any(loc in direccion for loc in localidades)

    direcciones_filtradas = [d for d in direcciones if validar_localidad(d)]
    direccion_final = "; ".join(direcciones_filtradas) if direcciones_filtradas else "No encontrado"

    return {
        "direccion": direccion_final,
        "telefono": telefono.group(0).strip() if telefono else "No encontrado",
        "email": email.group(0).strip() if email else "No encontrado"
    }
    
if __name__ == "__main__": 
    html_ejemplo = """ 
    <footer> 
    <p>Calle Falsa 123, 28001 Madrid</p> 
    <p>Teléfono: +34 91 123 4567</p> 
    <p>Email: info@ejemplo.com</p> 
    </footer> 
    """ 
    contacto = extraer_contacto(html_ejemplo) 
    print(contacto)