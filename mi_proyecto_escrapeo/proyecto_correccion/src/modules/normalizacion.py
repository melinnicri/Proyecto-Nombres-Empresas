# Librerías para Normalización
import re
import unicodedata

def normalizar_nombre(nombre):
    if not isinstance(nombre, str):
        return ""
    
    nombre = re.sub(r'\(.*?\)', '', nombre)
    nombre = nombre.upper()
    nombre = unicodedata.normalize("NFKD", nombre).encode("ASCII", "ignore").decode("utf-8")
    
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
    
    if "UNIPERSONAL" in nombre:
        nombre = re.sub(r'\bS\.?A\.?\b', 'SAU', nombre)
    
    for patron, reemplazo in sustituciones:
        nombre = re.sub(patron, reemplazo, nombre, flags=re.IGNORECASE)
    
    nombre = re.sub(r"[^a-zA-Z0-9&/ ]", " ", nombre)
    nombre = re.sub(r"\s+", " ", nombre).strip()
    
    return nombre


