from abc import ABC, abstractmethod
import requests
from helpers import messageObject

class Command(ABC):
    def __init__(self):
        self.Message = messageObject.MessageObject

    @abstractmethod
    def execute(self):
        pass