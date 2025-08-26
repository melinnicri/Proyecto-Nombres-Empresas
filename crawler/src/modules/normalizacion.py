# Librerías para normalizar los nombres de las empresas del archivo .csv
import re
import unicodedata

def normalizar_nombre(nombre):
    if not isinstance(nombre, str):
        return ""

    # 1. Eliminar contenido entre paréntesis
    nombre = re.sub(r'\(.*?\)', '', nombre)

    # 2. Convertir a mayúsculas
    nombre = nombre.upper()

    # 3. Eliminar acentos y caracteres no ASCII (incluye ñ → n)
    nombre = unicodedata.normalize("NFKD", nombre).encode("ASCII", "ignore").decode("utf-8")

    # 4. Sustituciones legales y comerciales
    sustituciones = [
        (r'\bS\.?A\.?U\.?\b', 'SAU'),
        (r'\bS\.?L\.?U\.?\b', 'SLU'),
        (r'\bS\.?A\.?\b', 'SA'),
        (r'\bS\.?L\.?\b', 'SL'),
        (r'\bC\.?V\.?\b', 'CV'),
        (r'\bCOOP\.?\b', 'COOP'),
        (r'\bINC\.?\b', 'INC'),
        (r'\bLTDA\.?\b', 'LTDA'),
        (r'\bEIRL\.?\b', 'EIRL')
    ]

    # 5. Reemplazo especial si contiene "UNIPERSONAL"
    if "UNIPERSONAL" in nombre:
        nombre = re.sub(r'\bS\.?A\.?\b', 'SAU', nombre)

    # 6. Aplicar todas las sustituciones
    for patron, reemplazo in sustituciones:
        nombre = re.sub(patron, reemplazo, nombre, flags=re.IGNORECASE)

    # 7. Eliminar cualquier carácter que no sea letra, número, espacio, &, /
    nombre = re.sub(r"[^A-Z0-9&/ ]", " ", nombre)

    # 8. Reemplazar múltiples espacios por uno solo
    nombre = re.sub(r"\s+", " ", nombre).strip()

    return nombre
