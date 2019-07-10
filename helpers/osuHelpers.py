from constants import osuConst

def acc_calc(misses, count50, count100, count300):
    accuracy = str((50*count50+100*count100+300*count300)*100/(300*(misses+count50+count100+count300)))
    return accuracy

def intToMods(mods):
    """Convert a mod integer to a mod string."""
    mods_a = []
    for k, v in osuConst.modToInt.items():
        if v & mods == v:
            mods_a.append(k)
    ordered_mods = list(filter(lambda m: m in mods_a, osuConst.mod_order))
    "NC" in ordered_mods and ordered_mods.remove("DT")
    "PF" in ordered_mods and ordered_mods.remove("SD")

    return "%s" % "".join(ordered_mods) if ordered_mods else ""


def modsToInt(mods):
    summ = 0
    for i in range(0, len(mods), 2):
        mod = mods[i:i+2]
        summ+= osuConst.modToInt.get(mod)
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