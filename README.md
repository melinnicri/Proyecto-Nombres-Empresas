# Prueba Técnica: Scraping de Información en Página Web

**Extracción automatizada de datos de contacto empresarial desde fuentes públicas**  
**Autora:** Amelia Cristina Herrera Briceño  
**Rol:** Data Analyst & Scientist en transición hacia BI y automatización  
**Entorno de trabajo:** Python · Pandas · BeautifulSoup · Regex · CSV · Exploración reproducible  
**Fecha de entrega:** 15 Agosto 2025  

<p align="center"><img src="https://github.com/melinnicri/Proyecto-Nombres-Empresas/blob/main/image/scrapeo.png"></p>

---

## 1. Problema

Se cuenta con listados de empresas (nombre y CIF), pero se carece de sus datos de contacto directo 
(emails corporativos, teléfonos, direcciones). Para establecer comunicación comercial, es necesario 
localizar y extraer automáticamente esta información desde sus sitios web oficiales u otras fuentes 
públicas disponibles en internet.

---

## 2. Solución Técnica

Desarrollar un proceso de scraping web que permita obtener datos de contacto empresariales de forma 
automatizada a partir de los nombres de las empresas.

---

## 3. Alcance de la Prueba

- **Dataset:** Muestra de 50–100 empresas españolas (nombre + CIF)
- **Proceso esperado:**
  1. Localizar la web corporativa oficial de cada empresa
  2. Extraer datos de contacto mediante scraping web
- **Datos objetivo:**
  - URL oficial
  - Email corporativo principal (info@, contacto@, comercial@)
  - Teléfono de contacto
  - Dirección postal completa
- **Entregables:**
  - Archivo CSV/Excel con los datos obtenidos
  - Documentación técnica del proceso
  - Registro de limitaciones (robots.txt, captchas, etc.)
  - Tiempo estimado de procesamiento por empresa
  - Coste estimado del proceso
  - Video explicativo del flujo técnico

---

## 4. Implementación Técnica

- Scraping sincrónico reproducible: `requests` + `BeautifulSoup` + `regex`
- Limpieza post-scraping: DataFrames exportables, validación de encoding y estructura
- Exportación: Archivos CSV listos para análisis y visualización

---

## 5. Métricas y Evaluación

- **Tasa de éxito:** porcentaje de empresas con datos completos
- **Limitaciones encontradas:** robots.txt, captchas, páginas sin datos visibles
- **Tiempo estimado por empresa:** medido con barra de progreso
- **Coste estimado:** bajo en entorno local; escalable con APIs

---

## 6. Video Explicativo

🎥 Se graba un video mostrando el flujo, explicando el código y los resultados obtenidos.  
_Pendiente de edición y subida._

---

## 7. Escalabilidad

Para flujos masivos, se propone una versión asincrónica con `aiohttp` o `crawl4ai`, que mejora el 
rendimiento y permite scraping concurrente.

---

## 8. Comparativa de Métodos de Búsqueda de URLs Oficiales


| Método                    | Gratuito | Límite         | Costo estimado | Ventajas                            | Desventajas                           |
|---------------------------|----------|----------------|----------------|-------------------------------------|---------------------------------------|
| googlesearch (scraping)   | Sí       | No oficial     | $0             | Sin registro, ideal para pruebas    | Bloqueos, resultados no estructurados |
| SerpAPI                   | Sí (250) | Pago desde $50 | ~$50           | JSON limpio, sin bloqueo            | Requiere API Key, coste mensual       |
| Zenserp                   | Sí (50)  | Pago desde $29 | ~$29           | Fácil de usar, resultados precisos  | Menor volumen gratuito                |
| Google Custom Search API  | Sí (100) | $5/1000        | ~$5            | Oficial, configurable               | Requiere configuración previa         |
| Bing Search API           | Sí (1000)| Pago desde $3  | ~$3            | Económica, buena cobertura          | Menor precisión en empresas locales   |

---

## 9. Recomendación Final

Para esta prueba técnica (50–100 empresas), se recomienda utilizar `googlesearch` por su simplicidad 
y coste cero. Para escalar el proceso, se sugiere evaluar APIs comerciales como `SerpAPI` y adoptar 
scraping asincrónico con `aiohttp` o `crawl4ai`.

---

## 10. Corrección Fonética y Semántica de Nombres Empresariales

Objetivo: corregir nombres empresariales con validación fonética (`rapidfuzz`) y semántica (`unidecode`), 
asegurando trazabilidad y limpieza formal.

### Ejemplo de corrección fonética

```python
import re
from unidecode import unidecode

def normalizar_nombre(nombre):
    nombre = unidecode(nombre)
    nombre = re.sub(r'[^\w\s]', '', nombre)
    nombre = nombre.strip().upper()
    return nombre

nombre_1 = "Compañía ABC S.A."
nombre_2 = "Compania - ABC, SA"

print(normalizar_nombre(nombre_1))  # COMPANIA ABC SA
print(normalizar_nombre(nombre_2))  # COMPANIA ABC SA
```

---

## 11. Flujo de Corrección y Validación

Este módulo se encarga de limpiar, corregir y validar los nombres empresariales antes del scraping,
asegurando trazabilidad y coherencia semántica.

| Archivo           | Propósito principal                                                         |
|-------------------|-----------------------------------------------------------------------------|
| `normalizacion.py`| Funciones para limpiar y normalizar nombres (acentos, símbolos, mayúsculas) |
| `correccion.py`   | Corrección fonética con `RapidFuzz` y validación semántica con `unidecode`  |
| `validacion.py`   | Detección de correcciones sospechosas y generación de revisión manual       |
| `main.py`         | Orquestación del flujo completo: carga, limpieza, corrección y exportación  |

> Cada paso del flujo está documentado y modularizado, permitiendo auditoría, mejora continua y enseñanza técnica.

---

## 12. Archivos CSV y Logs Funcionales

| Archivo CSV                                | Rol en el flujo                            | Contenido esperado                             | Sugerencias de mejora                              |
|--------------------------------------------|--------------------------------------------|------------------------------------------------|----------------------------------------------------|
| `empresas_limpias_corregidas_mejorado.csv` | Post-normalización y corrección automática | Nombres limpios + correcciones automáticas     | Agregar columna `ORIGEN_CORRECCIÓN` y `FECHA_PROCESO`       |
| `revision_manual.csv`                      | Correcciones manuales aplicadas            | Casos límite revisados por uno mismo           | Agregar columna `OBSERVACIONES` y `VALIDACIÓN_MANUAL`   |
| `correcciones_sospechosas.csv`             | Casos con ambigüedad o errores detectados  | Correcciones dudosas, posibles sobreajustes    | Agregar columna `TIPO_ERROR` y `RECOMENDACIÓN`                            |
| `empresas_limpias_corregidas_final.csv`    | Resultado final validado                   | Nombres corregidos y validados                 | Agregar columna `VALIDACIÓN_FINAL` y `FUENTE_CORRECCIÓN`   |
| `log_de_correcciones.csv`                  | Registro trazable de cada corrección       | Entradas, salidas, tipo de corrección          | Ya bien estructurado, solo falta `ID` y `TIMESTAMP`                       |

---

## 13. Informe de Cobertura y Limitaciones del Scraping

- **Empresas procesadas:** 100  
- **Con datos completos:** 19  
- **Con datos parciales:** 81  
- **Sin datos encontrados:** 0  
- **Costo estimado por empresa útil:** 1.89 horas  

---

### Hallazgos clave

1. Datos incompletos en la página principal  
2. Carga asincrónica de contenido  
3. URLs inválidas o redireccionadas  
4. Datos mezclados o mal formateados  

---

## 14. Mejoras Sugeridas

- Ajustar patrones de `regex`  
- Filtrar URLs sin `http`  
- Documentar casos sin datos  
- Explorar subpáginas automáticamente  
- Usar `Selenium` o `Playwright`  
- Consultar APIs internas  
- Registrar logs por empresa  

---

## 15. Reflexión Final

Este ejercicio permitió identificar las limitaciones del scraping tradicional y la necesidad de
modularizar el flujo. Se documentaron errores como evidencia de aprendizaje y se dejaron mejoras
futuras para auditoría y enseñanza.

---

## 16. Tiempo y Esfuerzo Invertido

**Tareas realizadas:**

- Preparación del entorno virtual  
- Limpieza y validación de nombres  
- Gestión de asincronía y subpáginas  
- Documentación de incidentes  
- Comparación de flujos  
- Generación de evidencia  

**Tiempo total invertido:** ~36 horas distribuidas en 3 días intensivos

---

## 17. Tabla de Incidentes Técnicos y Validaciones

| Tipo de incidente         | Descripción breve                                      | Ejemplo o patrón detectado                          | Mejora futura sugerida                                 |
|---------------------------|--------------------------------------------------------|-----------------------------------------------------|--------------------------------------------------------|
| `#asincronía`             | Carga de datos depende de JavaScript o peticiones dinámicas | Páginas sin datos en HTML estático              | Usar `Selenium` o capturas manuales                    |
| `#estructura_inaccesible` | Datos embebidos en imágenes o banners                  | Contacto solo en PDF o banners                      | Documentar como “no extraíble automáticamente”         |
| `#subpágina_oculta`       | Datos en subpáginas no enlazadas desde el home         | Sección “Contacto” sin enlace directo               | Detectar enlaces internos relevantes                   |
| `#validación_manual`      | Requiere criterio humano para interpretar ambigüedades | Nombres genéricos o duplicados                      | Crear diccionario personalizado y registrar ejemplos   |
| `#datos_incompletos`      | Se extrae solo parte del contacto                      | Formularios sin email visible                       | Marcar como “parcial” y registrar en log               |
| `#estructura_inconsistente`| HTML varía entre empresas, dificultando selectores únicos | Plantillas distintas o CMS personalizado         | Modularizar el scraping por tipo de estructura         |
| `#bloqueo_scraping`       | El sitio detecta scraping y bloquea o redirige         | Cloudflare, captcha o redirección forzada           | Documentar como “requiere intervención manual”         |
| `#errores_de_entorno`     | Problemas con librerías, rutas o entornos virtuales    | Conflictos entre kernels o rutas relativas          | Registrar en README y limpiar entornos obsoletos       |

---

## Extras:

---

```

# Diagrama del proyecto:
Proyecto-Nombres-Empresas/
├── image/
│   └── scrapeo/
├── mi_proyecto_escrapeo/
│   ├── escrapeo/
│   │   ├── data/                                                    # Archivos CSV de entrada y salida
│   │   │   ├── processed/
│   │   │   │   ├── contacto_empresas_es.csv
│   │   │   │   └── empresas_completas.csv
│   │   │   └── raw/
│   │   │       └── comparados.csv
│   │   ├── src/                                                      # Scripts del flujo técnico
│   │   │   └── comparativa.ipynb
│   │   ├── escrapeo_1.py
│   │   └── requirements.txt                                          # Librerías necesarias para reproducir el entorno para escrapeo
│   └── proyecto_correccion/
│       ├── __pycache__/
│       │   ├── correccion.cpython-312.pyc
│       │   ├── normalizacion.cpython-312.pyc
│       │   └── validacion.cpython-312.pyc
│       ├── data/                                                      # Archivos CSV de entrada y salida
│       │   ├── processed/
│       │   │   ├── empresas_limpias_corregidas_final.csv
│       │   │   └── empresas_limpias_corregidas_mejorado.csv
│       │   └── raw/
│       │       └── 100empresas.csv
│       ├── logs/                                                       # Logs funcionales de la correción de los nombres de empresas
│       │   ├── correcciones_sospechosas.csv
│       │   ├── log_de_correcciones.csv
│       │   └── revision_manual.csv
│       ├── src/                                                        # Scripts del flujo técnico
│       │   ├── modules/
│       │   │   ├── correccion.py
│       │   │   ├── normalizacion.py
│       │   │   └── validacion.py
│       │   └── main.py
│       └── requirements.txt                                            # Librerías necesarias para reproducir el entorno para corrección
├── README.md                                                           # Informe técnico en formato Markdown


```

---

```
## Diagrama de flujo funcional del proyecto

Inicio
  ↓
📁 Carga de datos iniciales (100empresas.csv)
  ↓
🧹 Corrección fonética y semántica
  ├─> correccion.py
  ├─> normalizacion.py
  └─> validacion.py
  ↓
📊 Generación de empresas_limpias_corregidas_final.csv
  ↓
📝 Registro de correcciones en logs/*.csv
  ↓
🌐 Scrapeo de nombres corregidos
  ├─> escrapeo_1.py
  └─> comparativa.ipynb
  ↓
📁 Almacenamiento en contacto_empresas_es.csv y empresas_completas.csv
  ↓
📚 Documentación en README.md
  ↓
Fin

```
---



```
## Diagrama de la carpeta "crawler" (escrapeo híbrido, asincrónico, con fallback dinámico y validadción semántica, realizado con Crawl4ai).

crawler/
├── __pycache__/                     # Archivos compilados automáticamente por Python
│   ├── contact_extractor.cpython-313.pyc
│   ├── correccion_crawler.cpython-313.pyc
│   ├── diccionario_manual.cpython-313.pyc
│   ├── gestor_correcciones.cpython-313.pyc
│   ├── normalizacion_crawler.cpython-313.pyc
│   ├── scraping_utils.cpython-313.pyc
│   └── validacion_crawler.cpython-313.pyc

├── data/                            # Ecosistema de datos
│   ├── raw/                         # Datos originales sin procesar
│   │   └── 100empresas.csv
│   ├── processed/                   # Datos corregidos, validados y listos para análisis
│   │   ├── contacto_empresas_es_2.csv*
│   │   ├── correcciones_sospechosas.csv
│   │   ├── diccionario_nombres_corregidos.csv
│   │   ├── empresas_limpias_corregidas_final.csv
│   │   ├── empresas_limpias_corregidas_mejorado.csv
│   │   ├── nombres_normalizados_para_scraping.csv
│   │   └── revision_manual.csv
│   └── diccionario_manual.py        # Correcciones manuales y mapeos heurísticos

├── logs/                            # Auditoría del proceso y scripts auxiliares
│   ├── auditoria_texto_extraido.py
│   ├── contact_extractor.py
│   ├── gestor_correcciones.py
│   ├── log_de_correcciones.csv
│   ├── main_async.py
│   └── scraping_utils.py

├── src/                             # Código principal y módulos reutilizables
│   ├── modules/                     # Funciones compartidas y componentes técnicos
│   └── main.py                      # Script principal de ejecución

├── compar2.ipynb                    # Notebook de comparación o análisis exploratorio
├── escrapeo_dos.py                  # Script de scraping híbrido con fallback dinámico
└── requirements.txt                 # Lista de dependencias del proyecto

Resultado: extrae los urls con pocos errores, pero dirección, teléfono y email no los alcanza a extraer. En 36 segundos.
```


```
Agregué otra versión mejorada del sistema asíncrona de scraping de información de empresas españolas: version_02
Versión_02/
├── nombres_scraping/                  # Punto de partida del proceso
│   └── buscar_url.py                  # Sistema asincrónico que busca URLs
│   └── urls.csv                       # Resultado exitoso (¡por fin!)
│
├── módulos_contacto/                 # Extracción y validación de contacto
│   └── extractor.py                  # Auxiliar para extracción
│   └── pipeline_contacto.py          # Pipeline principal
│   └── contacto.csv                  # Resultado con datos de contacto
│
├── análisis/                         # Estadísticas y validaciones
│   └── estadística.ipynb             # Notebook con análisis de urls y contacto
├── requirements.txt                  # Requerimientos del entorno virtual para trabajarlo
```
