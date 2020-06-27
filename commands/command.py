from abc import ABC, abstractmethod
import requests
from objects import message

class Command(ABC):
    def __init__(self):
        self.Message = message.MessageObject

    @abstractmethod
    def execute(self):
        pass