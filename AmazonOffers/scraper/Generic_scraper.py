from abc import ABCMeta, abstractmethod


class Generic_scraper:
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_offers(self, link: list, slector: str) -> dict: raise Exception("NotImplementedException")
