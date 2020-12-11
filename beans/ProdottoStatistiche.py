class ProdottoStatistiche():

    def __init__(self, nome: str, prezzo_minimo: int, prezzo_massimo: int, media_prezzo: int):
        self.__nome = nome
        self.__prezzo_minimo = prezzo_minimo
        self.__prezzo_massimo = prezzo_massimo
        self.__media_prezzo = media_prezzo
        self.__is_scontato = False

    @property
    def nome(self):
        return self.__nome

    @nome.setter
    def nome(self, nome: str):
        self.__nome = nome

    @property
    def prezzo_minimo(self):
        return self.__prezzo_minimo

    @prezzo_minimo.setter
    def prezzo_minimo(self, prezzo_minimo: int):
        self.__prezzo_minimo = prezzo_minimo

    @property
    def prezzo_massimo(self):
        return self.__prezzo_massimo

    @prezzo_massimo.setter
    def prezzo_massimo(self, prezzo_massimo: int):
        self.__prezzo_massimo = prezzo_massimo

    @property
    def media_prezzo(self):
        return self.__media_prezzo

    @media_prezzo.setter
    def media_prezzo(self, media_prezzo: int):
        self.__media_prezzo = media_prezzo

    @property
    def is_fake_sconto(self):
        return self.__is_scontato

    @is_fake_sconto.setter
    def is_fake_sconto(self, isScontato: bool):
        self.__is_scontato = isScontato

    def __str__(self):
        string = f"{{\"nome\":\"{self.__nome}\""
        string += f", \"prezzo_minimo\":{self.__prezzo_minimo}"
        string += f", \"prezzo_massimo\":{self.__prezzo_massimo}"
        string += f", \"media_prezzo\":{self.__media_prezzo}"
        string += f", \"is_scontato\":\"{self.__is_scontato}\""
        string += "}"

        return string
