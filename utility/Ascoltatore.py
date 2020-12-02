from abc import ABCMeta, abstractmethod


class Ascoltatore:
    __metaclass__ = ABCMeta

    @abstractmethod
    def update(self, operation: str,  *info):
        raise Exception("NotImplementedException")