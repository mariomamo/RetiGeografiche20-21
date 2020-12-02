from abc import ABCMeta, abstractmethod


class Listener:
    __metaclass__ = ABCMeta

    @abstractmethod
    def update(self, info):
        raise Exception("NotImplementedException")