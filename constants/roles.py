from enum import IntFlag

class Roles(IntFlag):
    RESTRICTED = 0,
    USER = 1,
    DONATOR = 2,
    ADMIN = 4