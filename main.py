import requests
import json
from pagina import Pagina
from bs4 import BeautifulSoup
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd

# pip install beautifulsoup4

# DEPURACION
# Si DEBUG es True, se imprimen mensajes de depuración
DEBUG = False

# Data to be written
list_to_json = []

# Guardar lista de tuplas de paginas conectadas
conexiones = []

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

# Guardar las paginas iniciales para analizarlas al ultimo
paginas_iniciales = list(paginas)

# Para evitar recorrer una pagina dos veces, se crea otra lista
# que aloja las paginas que ya fueron recorridas
paginas_recorridas = []

# Se arman las capas
for x in range(6):

    # Se almacenan las paginas recien encontradas
    nuevas_paginas = []

    # Se crea un contador para avisar si no se encuentran mas referencias
    contador = 0

    for pagina in paginas:

        response = requests.get(f"{pagina_base}{pagina.Href}")
        soup = BeautifulSoup(response.text, "html.parser")

        if pagina.Titulo == "":
            # Si no tiene titulo, se busca el primero
            # que tenga un h1
            h1 = soup.find("h1")
            if h1 is not None:
                pagina.Titulo = h1.get_text().strip()
            else:
                MsgDg(f"{"*"*15}No se encontro titulo para {pagina.Href}...{"*"*15}")
                continue

        # Si la pagina ya fue recorrida, no se vuelve a recorrer
        if pagina in paginas_recorridas:
            MsgDg(f"{"*"*15}Ignorando por ya recorrida{pagina.Titulo}...{"*"*15}")
            continue

        print(f"{"*"*15}Leyendo {pagina.Titulo}...{"*"*15}")

        # Primero por los recomendados
        for noticia in soup.find_all("h2", "most-read-card-headline"):
            enlace = noticia.find_parent("a")
            nueva_pagina = Pagina(noticia.get_text().strip(), enlace["href"])

            # Si la noticia no es de deportes, no se agrega
            if not es_deportes(nueva_pagina.Href):
                MsgDg(f"{"*"*15}Ignorando por no ser de deportes{nueva_pagina.Titulo}...{"*"*15}")
                continue

            MsgDg(f"{"*"*15}Guardando {nueva_pagina.Titulo}...{"*"*15}")
            
            pagina.Paginas.append(nueva_pagina)
            nuevas_paginas.append(nueva_pagina)
            conexiones.append((pagina.Titulo, nueva_pagina.Titulo))
            contador += 1

        # Luego por ultimas noticias
        for noticia in soup.find_all("h2", "feed-list-card-headline-lean"):
            enlace = noticia.find_parent("div").find_parent("a")
            nueva_pagina = Pagina(noticia.get_text().strip(), enlace["href"])

            # Si la noticia no es de deportes, no se agrega
            if not es_deportes(nueva_pagina.Href):
                MsgDg(f"{"*"*15}Ignorando por no ser de deportes{nueva_pagina.Titulo}...{"*"*15}")
                continue

            MsgDg(f"{"*"*15}Guardando {nueva_pagina.Titulo}...{"*"*15}")

            pagina.Paginas.append(nueva_pagina)
            nuevas_paginas.append(nueva_pagina)
            conexiones.append((pagina.Titulo, nueva_pagina.Titulo))
            contador += 1

        # Analizar los enlaces en negrita
        for noticia in soup.find_all("b"):
            enlace = noticia.find_parent("a")
            if enlace is None:
                continue
            nuevo_enlace = enlace["href"].replace(pagina_base,"")
            nueva_pagina = Pagina("", nuevo_enlace)
            

            # Si la noticia no es de deportes, no se agrega
            if not es_deportes(nueva_pagina.Href):
                MsgDg(f"{"*"*15}Ignorando por no ser de deportes{nueva_pagina.Titulo}...{"*"*15}")
                continue

            MsgDg(f"{"*"*15}Guardando {nueva_pagina.Titulo}...{"*"*15}")

            pagina.Paginas.append(nueva_pagina)
            nuevas_paginas.append(nueva_pagina)
            conexiones.append((pagina.Titulo, nueva_pagina.Titulo))
            contador += 1

        paginas_recorridas.append(pagina)

        list_to_json.append(pagina.ToJson())
    
    # Se pone la nueva lista a usar
    paginas = nuevas_paginas

    if contador == 0:
        MsgDg("No se encontraron más páginas.")
        break

labels = {"Id" : [], "Label": []}

for x in range(len(paginas_recorridas)):
    print(f"{x+1} - {paginas_recorridas[x].Titulo}")
    print(paginas_recorridas[x].Href)
    print("=" * 50)

    # Agregar estas definiciones a un csv de labels
    labels["Id"].append(x+1)
    labels["Label"].append(paginas_recorridas[x].Titulo)

pd.DataFrame(labels).to_excel("labels.xlsx", index=False)

# Reemplazar los titulos en los enlaces por numeros para
# simplificar el grafo
for x in range(len(paginas_recorridas)):
    # Por cada pagina recorrida, se reemplaza este nombre en todas las tuplas
    for y in range(len(conexiones)):
        if conexiones[y][0] == paginas_recorridas[x].Titulo:
            conexiones[y] = (x+1, conexiones[y][1])
        if conexiones[y][1] == paginas_recorridas[x].Titulo:
            conexiones[y] = (conexiones[y][0], x+1)

# Crear un grafo dirigido
G = nx.DiGraph()

# Agregar nodos
G.add_nodes_from([x for x in range(1, len(paginas_recorridas)+1)])

edges = {"Source": [], "Target": [], "Weight": []}

# Agregar aristas dirigidas (incluyendo conexiones bidireccionales)
for x in range(len(conexiones)):
    
    # Solamente se usa los nodos que son enteros, o sea que fueron explorados.
    if isinstance(conexiones[x][0], str) or isinstance(conexiones[x][1], str):
        continue

    G.add_edge(conexiones[x][0], conexiones[x][1])  # Conexión de 1 -> 2

    # Agregar estas aristas a un csv de aristas
    edges["Source"].append(conexiones[x][0])
    edges["Target"].append(conexiones[x][1])
    edges["Weight"].append(1)

pd.DataFrame(edges).to_excel("edges.xlsx", index=False)
pos = nx.spring_layout(G, k=1) 

plt.figure(figsize=(8, 8))
nx.draw(G, pos, with_labels=True, node_color="lightblue", edge_color="gray", font_weight="bold")
plt.show()
 
# Serializing json
json_object = json.dumps(list_to_json, indent=4, ensure_ascii=False)
 
# Writing to sample.json
with open("sample.json", "w", encoding="utf-8") as outfile:
    outfile.write(json_object)