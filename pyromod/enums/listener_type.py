from enum import auto

from .auto_name import AutoName


class ListenerType(AutoName):
    MESSAGE = auto()
    CALLBACK_QUERY = auto()
