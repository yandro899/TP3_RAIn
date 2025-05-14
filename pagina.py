class Pagina:
    def __init__(self, titulo: str, href: str):
        self.titulo = titulo
        self.href = href
        self.paginas = []

    def __str__(self):
        return f"Titulo: {self.titulo}\nEnlace: {self.href}"
    
    def __eq__(self, value):
        """Es verdadero si el título y el enlace son iguales."""
        if not isinstance(value, Pagina):
            return False
        return self.titulo == value.titulo and self.href == value.href
    
    def __hash__(self):
        """Devuelve el hash del objeto."""
        return hash((self.titulo, self.href))
    
    @property
    def Titulo(self) -> str:
        """Devuelve el título de la página."""
        return self.titulo
    
    @Titulo.setter
    def Titulo(self, titulo: str):
        """Establece el título de la página."""
        self.titulo = titulo
    
    @property
    def Href(self) -> str:
        """Devuelve el enlace de la página."""
        return self.href
    
    @Href.setter
    def Href(self, href: str):
        """Establece el enlace de la página."""
        self.href = href

    @property
    def Paginas(self) -> list:
        """Devuelve la lista de páginas."""
        return self.paginas
    
    @Paginas.setter
    def Paginas(self, paginas: list):
        """Establece la lista de páginas."""
        self.paginas = paginas

    def ToJson(self) -> dict:
        """Devuelve un diccionario con los datos de la página."""
        return {
            "titulo": self.titulo,
            "href": self.href,
            "paginas": [pagina.ToJson() for pagina in self.paginas]
        }