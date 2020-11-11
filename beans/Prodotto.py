class Prodotto:

    def __init__(self, nome: str = None, prezzo: float = None, url: str = None, commenti: list = None):
        self.__nome = nome
        self.__prezzo = prezzo
        self.__url = url
        self.__commenti = commenti

    @property
    def nome(self): return self.__nome

    @nome.setter
    def nome(self, nome:str): self.__nome = nome

    @property
    def prezzo(self): return self.__prezzo

    @prezzo.setter
    def prezzo(self, prezzo: float): self.__prezzo = prezzo

    @property
    def url(self): return self.__url

    @url.setter
    def url(self, url: str): self.__url = url

    @property
    def commenti(self): return self.__commenti

    @commenti.setter
    def commenti(self, commenti: list): self.__commenti = commenti
