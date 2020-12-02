from abc import ABCMeta, abstractmethod
from utility.Ascoltatore import Ascoltatore


class Ascoltabile:
    __metaclass__ = ABCMeta

    @abstractmethod
    def addListeners(self, listeners: list = Ascoltatore):
        raise Exception("NotImplementedException")

    @abstractmethod
    def removeListener(self, listener: Ascoltatore):
        raise Exception("NotImplementedException")

    @abstractmethod
    def notify(self, operation, *args):
        raise Exception("NotImplementedException")