from . import mods


def acc_calc(misses, count50, count100, count300):
    accuracy = str(round(((50*count50+100*count100+300*count300)*100/(300*(misses+count50+count100+count300))),2))
    return accuracy

def readableMods(m):
    r = ""
    if m == 0:
        r += "NOMOD"
    if m & mods.NOFAIL > 0:
        r += "NF"
    if m & mods.EASY > 0:
        r += "EZ"
    if m & mods.HIDDEN > 0:
        r += "HD"
    if m & mods.HARDROCK > 0:
        r += "HR"
    if m & mods.DOUBLETIME > 0:
        r += "DT"
    if m & mods.HALFTIME > 0:
        r += "HT"
    if m & mods.FLASHLIGHT > 0:
        r += "FL"
    if m & mods.SPUNOUT > 0:
        r += "SO"
    if m & mods.TOUCHSCREEN > 0:
        r += "TD"
    if m & mods.RELAX > 0:
        r += "RX"
    if m & mods.RELAX2 > 0:
        r += "AP"	
    if m & mods.SCOREV2 > 0:
        r += "V2"
    return r
