from . import mods


def acc_calc(misses, count50, count100, count300):
    accuracy = str((50*count50+100*count100+300*count300)*100/(300*(misses+count50+count100+count300)))
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
    if m & mods.PERFECT > 0:
        r += "PF"
    if m & mods.SCOREV2 > 0:
        r += "V2"
    return r

def scoreFormat(
    username: str, title: str, m: int, accuracy: float, 
    combo: int, max_combo: int, misses:int, _pp: float, beatmap_id: int, pp_if_fc: float):
    if misses == 0: 
        misses = "" 
    else:
        misses = str(misses)+"xMiss"
    accuracy = str(round(float(accuracy), 2))
    mods = "" if m == 0 else "+" + readableMods(m)
    if _pp is not None:
        pp = str(_pp) + 'pp'
        if _pp != pp_if_fc:
            pp += " ({}pp if FC)".format(pp_if_fc)
    else:
        pp = "" 
    if int(combo) == int(max_combo):
        combo = ""
    else:
        combo = str(combo) + '/' + str(max_combo)
    text = '{} | {} {} ({}%) {} {} | {}\nhttps://osu.ppy.sh/b/{}'.format(
        username, title,mods,accuracy,combo,misses,pp, beatmap_id)
    return text