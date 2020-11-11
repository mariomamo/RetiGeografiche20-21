from abc import ABCMeta, abstractmethod


class GenericScraper:
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_offers(self) -> dict: raise Exception("NotImplementedException")
