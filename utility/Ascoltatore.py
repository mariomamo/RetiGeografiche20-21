from abc import ABCMeta, abstractmethod


class Listener:
    __metaclass__ = ABCMeta

    @abstractmethod
    def update(self, operation: str,  *info):
        raise Exception("NotImplementedException")