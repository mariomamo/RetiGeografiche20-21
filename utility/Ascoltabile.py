from abc import ABCMeta, abstractmethod
from utility.Listener import Listener


class Ascoltatore:
    __metaclass__ = ABCMeta

    @abstractmethod
    def addListeners(self, listeners: list = Listener):
        raise Exception("NotImplementedException")

    @abstractmethod
    def removeListener(self, listener: Listener):
        raise Exception("NotImplementedException")

    @abstractmethod
    def notify(self, operation, *args):
        raise Exception("NotImplementedException")