import requests
from pagina import Pagina
from bs4 import BeautifulSoup

# pip install beautifulsoup4

# DEPURACION
# Si DEBUG es True, se imprimen mensajes de depuración
DEBUG = False

def MsgDg(msg: str):
    """Imprime un mensaje de depuración si DEBUG es True."""
    if DEBUG:
        print(msg)

def es_deportes(titulo: str) -> bool:
    """Devuelve True si el título contiene la palabra 'deportes'."""
    return "deportes" in titulo.lower()

# URL de la página que queremos analizar
pagina_base = "https://www.infobae.com"
url = f"{pagina_base}/deportes/"
response = requests.get(url)
paginas = list[Pagina]()

# Parseamos el contenido HTML
soup = BeautifulSoup(response.text, "html.parser")

# Extraemos títulos de noticias y guardamos los enlaces
# en una lista de objetos Pagina
# Esto es el punto de inicio
# de la extracción de datos
for noticia in soup.find_all("h2", "story-card-hl"):
    enlace = noticia.find_parent("a")
    paginas.append(Pagina(noticia.get_text(), enlace["href"]))

# Para evitar recorrer una pagina dos veces, se crea otra lista
# que aloja las paginas que ya fueron recorridas
paginas_recorridas = paginas.copy()

# Imprimimos los títulos y enlaces
for pagina in paginas:
    print(pagina)
    print("=" * 50)

# Se arman las capas
while True:

    # Se almacenan las paginas recien encontradas
    nuevas_paginas = []

    # Se crea un contador para avisar si no se encuentran mas referencias
    contador = 0

    for pagina in paginas:

        response = requests.get(f"{pagina_base}{pagina.Href}")
        soup = BeautifulSoup(response.text, "html.parser")

        # Primero por los recomendados
        for noticia in soup.find_all("h2", "most-read-card-headline"):
            enlace = noticia.find_parent("a")
            nueva_pagina = Pagina(noticia.get_text(), enlace["href"])

            # Si la pagina ya fue recorrida, no se agrega
            if nueva_pagina in paginas_recorridas:
                MsgDg(f"{"*"*15}Ignorando por estar explorada{pagina.Titulo}...{"*"*15}")
                continue

            # Si la noticia no es de deportes, no se agrega
            if not es_deportes(nueva_pagina.Href):
                MsgDg(f"{"*"*15}Ignorando por no ser de deportes{pagina.Titulo}...{"*"*15}")
                continue

            pagina.Paginas.append(nueva_pagina)
            nuevas_paginas.append(nueva_pagina)
            paginas_recorridas.append(nueva_pagina)
            contador += 1

        # Luego por ultimas noticias
        for noticia in soup.find_all("h2", "feed-list-card-headline-lean"):
            enlace = noticia.find_parent("div").find_parent("a")
            nueva_pagina = Pagina(noticia.get_text(), enlace["href"])

            # Si la pagina ya fue recorrida, no se agrega
            if nueva_pagina in paginas_recorridas:
                MsgDg(f"{"*"*15}Ignorando por estar explorada{pagina.Titulo}...{"*"*15}")
                continue

            # Si la noticia no es de deportes, no se agrega
            if not es_deportes(nueva_pagina.Href):
                MsgDg(f"{"*"*15}Ignorando por no ser de deportes{pagina.Titulo}...{"*"*15}")
                continue

            pagina.Paginas.append(nueva_pagina)
            nuevas_paginas.append(nueva_pagina)
            paginas_recorridas.append(nueva_pagina)
            contador += 1

        # Imprimimos los títulos y enlaces
        for pagina_sec in pagina.paginas:
            print(pagina_sec)
            print("=" * 50)
    
    # Se pone la nueva lista a usar
    paginas = nuevas_paginas

    if contador == 0:
        print("No se encontraron más páginas.")
        break
