import inspect
import math


class ProdottoStatistiche():

    def __init__(self, nome: str=None, prezzo_minimo_bf: float=None, prezzo_minimo_dopo: float=None,
                 percentuale_sconto: str=None, differenza: str=None, media_prezzo: float=None, is_scontato: bool=None,
                 prezzo_minimo: float=None, prezzo_massimo: float=None, media: float=None,):

        if nome is not None: self.__nome = str(nome)
        else: self.__nome = ""
        if prezzo_minimo_bf is not None: self.__prezzo_minimo_bf = str(prezzo_minimo_bf)
        else: self.__prezzo_minimo_bf = 1
        if prezzo_minimo_dopo is not None: self.__prezzo_minimo_dopo = str(prezzo_minimo_dopo)
        else: self.__prezzo_minimo_dopo = 1
        if percentuale_sconto is not None: self.__percentuale_sconto = str(percentuale_sconto)
        else: self.__percentuale_sconto = ""
        if differenza is not None: self.__differenza = str(differenza)
        else: self.__differenza = ""
        if media_prezzo is not None: self.__media_prezzo = str(media_prezzo)
        else: self.__media_prezzo = ""
        if is_scontato is not None: self.__is_scontato = str(is_scontato)
        else: self.__is_scontato = ""
        if prezzo_minimo is not None: self.__prezzo_minimo = int(prezzo_minimo)
        else: self.__prezzo_minimo = 1
        if prezzo_massimo is not None: self.__prezzo_massimo = int(prezzo_massimo)
        else: self.__prezzo_massimo = 1
        if media_prezzo is not None: self.__media_prezzo = int(media)
        else: self.__media_prezzo = 1

    @property
    def nome(self):
        return self.__nome

    @nome.setter
    def nome(self, nome: str):
        self.__nome = nome

    @property
    def prezzo_minimo_bf(self) -> float:
        return self.__prezzo_minimo_bf

    @prezzo_minimo_bf.setter
    def prezzo_minimo_bf(self, prezzo_minimo_bf: float):
        self.__prezzo_minimo_bf = prezzo_minimo_bf

    @property
    def prezzo_minimo_dopo(self) -> float:
        return self.__prezzo_minimo_dopo

    @prezzo_minimo_dopo.setter
    def prezzo_minimo_dopo(self, prezzo_minimo_dopo: float):
        self.__prezzo_minimo_dopo = prezzo_minimo_dopo

    @property
    def percentuale_sconto(self):
        return self.__percentuale_sconto

    @percentuale_sconto.setter
    def percentuale_sconto(self, percentuale_sconto):
        self.__percentuale_sconto = percentuale_sconto

    @property
    def differenza(self):
        return self.__differenza

    @differenza.setter
    def differenza(self, differenza):
        self.__differenza = differenza

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

    @property
    def prezzo_minimo(self):
        return self.__prezzo_minimo

    @prezzo_minimo.setter
    def prezzo_minimo(self, prezzo_minimo):
        self.__prezzo_minimo = prezzo_minimo

    @property
    def prezzo_massimo(self):
        return self.__prezzo_massimo

    @prezzo_massimo.setter
    def prezzo_massimo(self, prezzo_massimo):
        self.__prezzo_massimo = prezzo_massimo

    @property
    def media(self):
        return self.__media_prezzo

    @media.setter
    def media(self, media_prezzo):
        self.__media_prezzo = media_prezzo

    def __str__(self):
        result = "{"

        # Ottiene tutti i nomi delle properties
        properties = [name for (name, value) in inspect.getmembers(ProdottoStatistiche) if isinstance(value, property)]

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
