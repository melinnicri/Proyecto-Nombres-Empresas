import re

def auditar_texto_extraido(ruta_log="debug_texto_extraido.txt", umbral_caracteres=200):
    with open(ruta_log, "r", encoding="utf-8") as f:
        contenido = f.read()

    bloques = re.split(r"\n{2,}--- (https?://[^\s]+) ---\n", contenido)
    resumen = []
    urls_con_texto = 0
    urls_sin_texto = 0

    # bloques[0] es basura antes del primer "--- URL ---"
    for i in range(1, len(bloques), 2):
        url = bloques[i]
        texto = bloques[i+1].strip()
        largo = len(texto)

        if largo >= umbral_caracteres:
            urls_con_texto += 1
            estado = "Texto suficiente"
        elif largo > 0:
            urls_sin_texto += 1
            estado = f"Texto escaso ({largo} caracteres)"
        else:
            urls_sin_texto += 1
            estado = "Sin texto"

        resumen.append(f"{estado} → {url}")

    # Resumen final
    print(f"\n Auditoría de texto extraído:")
    print(f"Total URLs auditadas: {urls_con_texto + urls_sin_texto}")
    print(f"Con texto suficiente: {urls_con_texto}")
    print(f"Sin texto o escaso: {urls_sin_texto}\n")

    # Detalle por URL
    for linea in resumen:
        print(linea)

if __name__ == "__main__":
    auditar_texto_extraido()
