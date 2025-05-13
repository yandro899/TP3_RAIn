import requests
from bs4 import BeautifulSoup

# pip install beautifulsoup4

# URL de la página que queremos analizar
url = "https://www.infobae.com/deportes/"
response = requests.get(url)

# Parseamos el contenido HTML
soup = BeautifulSoup(response.text, "html.parser")

# Extraemos títulos de noticias
for noticia in soup.find_all("h2", "story-card-hl"):
    print("Título:", noticia.get_text())
    enlace = noticia.find_parent("a")
    print("Enlace:", enlace["href"])
    print("=" * 50)
