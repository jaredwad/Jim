from abc import ABCMeta, abstractmethod


class IDataHandler(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def on_receive_data(self, data):
        raise NotImplementedError("Should implement on_receive_data()")
