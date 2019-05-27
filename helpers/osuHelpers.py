from constants.osuConst import intToMod, modToInt

def acc_calc(misses, count50, count100, count300):
    accuracy = str((50*count50+100*count100+300*count300)*100/(300*(misses+count50+count100+count300)))
    return accuracy

def intToMods(m):
    r = ""
    if m == 0:
        r += ""
    if m & modToInt.get("NF"):
        r += "NF"
    if m & modToInt.get("EZ") > 0:
        r += "EZ"
    if m & modToInt.get("HD") > 0:
        r += "HD"
    if m & modToInt.get("HR") > 0:
        r += "HR"
    if m & modToInt.get("DT") > 0:
        r += "DT"
    if m & modToInt.get("HT") > 0:
        r += "HT"
    if m & modToInt.get("FL") > 0:
        r += "FL"
    if m & modToInt.get("SO") > 0:
        r += "SO"
    if m & modToInt.get("TD") > 0:
        r += "TD"
    if m & modToInt.get("RX") > 0:
        r += "RX"
    if m & modToInt.get("AP") > 0:
        r += "AP"	
    if m & modToInt.get("PF") > 0:
        r += "PF"
    if m & modToInt.get("V2") > 0:
        r += "V2"
    return r

def modsToInt(mods):
    summ = 0
    for i in range(0, len(mods), 2):
        mod = mods[i:i+2]
        summ+= modToInt.get(mod)
    return summ

def scoreFormat(
    username: str, title: str, m: int, accuracy: float, 
    combo: int, max_combo: int, misses:int, _pp: float, beatmap_id: int, pp_if_fc: float):
    if misses == 0: 
        misses = "" 
    else:
        misses = str(misses)+"xMiss"
    accuracy = str(round(float(accuracy), 2))
    mods = "" if m == 0 else "+" + intToMods(m)
    if _pp is not None:
        pp = str(_pp) + "pp"
        if _pp != pp_if_fc:
            pp += " ({}pp if FC)".format(pp_if_fc)
    else:
        pp = "" 
    if int(combo) == int(max_combo):
        combo = " "
    else:
        combo = " " + str(combo) + '/' + str(max_combo) + " "
    text = '{} | {} {} ({}%){}{} | {}\nhttps://osu.ppy.sh/b/{}'.format(
        username, title, mods,accuracy,combo,misses,pp, beatmap_id)
    return text