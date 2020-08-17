from enum import IntFlag

class MessageTypes(IntFlag):
    CHAT = 0
    PRIVATE = 1,
    CREATOR = 2