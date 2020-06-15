from abc import ABC, abstractmethod
import requests
from helpers import message

class Command(ABC):
    def __init__(self):
        self.Message = message.Message

    @abstractmethod
    def execute(self):
        pass