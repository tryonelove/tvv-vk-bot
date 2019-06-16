import re

sig_colors = ['black', 'red', 'orange', 'yellow', 'green', 'blue', 'purple', 'pink', 'hex2255ee']

modToInt = {
    "": 1 >> 1,
    "NF": 1 << 0,
    "EZ": 1 << 1,
    "TD": 1 << 2,
    "HD": 1 << 3,
    "HR": 1 << 4,
    "SD": 1 << 5,
    "DT": 1 << 6,
    "RX": 1 << 7,
    "HT": 1 << 8,
    "NC": 1 << 6 | 1 << 9,  # DT is always set along with NC.
    "FL": 1 << 10,
    "AT": 1 << 11,
    "SO": 1 << 12,
    "AP": 1 << 13,
    "PF": 1 << 5 | 1 << 14,  # SD is always set along with PF.
    "V2": 1 << 29,
    # TODO: Unranked Mania mods, maybe.
}

intToMod = { v: k for k, v in modToInt.items() }

# osu! regex
beatmap_id_re = re.compile(".*\/b/(\d+)")
title_re = re.compile(".+[\|丨].+-.+\[.+\]")
mods_re = re.compile("\+[^\s]+")
screenshots_re = re.compile(".*.jpg")