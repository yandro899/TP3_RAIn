import requests
from pagina import Pagina
from bs4 import BeautifulSoup

# pip install beautifulsoup4

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

# Imprimimos los títulos y enlaces
for pagina in paginas:
    print(pagina)
    print("=" * 50)

# Se arma la segunda capa
for pagina in paginas:

    print(f"{"*"*15}Leyendo {pagina.Titulo}...{"*"*15}")
    response = requests.get(f"{pagina_base}{pagina.Href}")
    soup = BeautifulSoup(response.text, "html.parser")

    # Extraemos los enlaces

    # Primero por los recomendados
    for noticia in soup.find_all("h2", "most-read-card-headline"):
        enlace = noticia.find_parent("a")
        pagina.Paginas.append(Pagina(noticia.get_text(), enlace["href"]))

    # Luego por ultimas noticias
    for noticia in soup.find_all("h2", "feed-list-card-headline-lean"):
        enlace = noticia.find_parent("div").find_parent("a")
        pagina.Paginas.append(Pagina(noticia.get_text(), enlace["href"]))

    # Imprimimos los títulos y enlaces
    for pagina_sec in pagina.paginas:
        print(pagina_sec)
        print("=" * 50)