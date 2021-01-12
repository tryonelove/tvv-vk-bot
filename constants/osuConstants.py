from enum import Enum

class Mods(Enum):
    NOMOD   = 1 >> 1
    NF      = 1 << 0
    EZ      = 1 << 1
    TD      = 1 << 2
    HD      = 1 << 3
    HR      = 1 << 4
    SD      = 1 << 5
    DT      = 1 << 6
    RX      = 1 << 7
    HT      = 1 << 8
    NC      = 1 << 6 | 1 << 9  # DT is always set along with NC.
    FL      = 1 << 10
    AT      = 1 << 11
    SO      = 1 << 12
    AP      = 1 << 13
    PF      = 1 << 5 | 1 << 14  # SD is always set along with PF.
    SCOREV2 = 1 << 29


class Mode(Enum):
    OSU     = 0
    TAIKO   = 1
    CATCH   = 2
    MANIA   = 3


INT_TO_MOD = { data.name: data.value for data in Mods }

MOD_ORDER = [
    "EZ", "HD", "HT", "DT", "NC", "HR", "FL", "NF",
    "SD", "PF", "RX", "AP", "SO", "AT", "V2", "TD",
]

SERVER_ACRONYMS = {
    "bancho": ["bancho", "b", "банчо", "б"],
    "gatari": ["gatari", "g", "гатари", "г"]
}