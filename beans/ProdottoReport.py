import inspect


class ProdottoReport:

    def __init__(self, nome: str, prezzo_bf: float, prezzo_dopo: float, percentuale_sconto: float,
                 differenza_prezzo: float, is_sconto_fake: bool):
        self.__nome = nome
        self.__prezzo_bf = prezzo_bf
        self.__prezzo_dopo = prezzo_dopo
        self.__percentuale_sconto = percentuale_sconto
        self.__differenza_prezzo = differenza_prezzo
        self.__is_sconto_fake = is_sconto_fake

    @property
    def nome(self):
        return self.__nome

    @nome.setter
    def nome(self, nome):
        self.__nome = nome

    @property
    def prezzo_bf(self):
        return self.__prezzo_bf

    @prezzo_bf.setter
    def prezzo_bf(self, value):
        self.__prezzo_bf = value

    @property
    def prezzo_dopo(self):
        return self.__prezzo_dopo

    @prezzo_dopo.setter
    def prezzo_dopo(self, value):
        self.__prezzo_dopo = value

    @property
    def percentuale_sconto(self):
        return self.__percentuale_sconto

    @percentuale_sconto.setter
    def percentuale_sconto(self, value):
        self.__percentuale_sconto = value

    @property
    def differenza_prezzo(self):
        return self.__differenza_prezzo

    @differenza_prezzo.setter
    def differenza_prezzo(self, value):
        self.__differenza_prezzo = value

    @property
    def is_sconto_fake(self):
        return self.__is_sconto_fake

    @is_sconto_fake.setter
    def is_sconto_fake(self, value):
        self.__is_sconto_fake = value

    def __str__(self):
        result = "{"

        # Ottiene tutti i nomi delle properties
        properties = [name for (name, value) in inspect.getmembers(ProdottoReport) if isinstance(value, property)]

        for name in properties:
            valore = self.__getattribute__(name)
            result += f"\"{name}\""

            if isinstance(valore, str):
                result += f": \"{valore}\", "
            else:
                result += f": {valore}, "

        result = result[0:result.__len__() - 2]
        result += "}"

        return result