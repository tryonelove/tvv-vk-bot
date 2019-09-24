from constants import osuConst

class Formatter:
    def __init__(self, 
    username, title, m, accuracy, 
    combo, max_combo, misses, pp, beatmap_id, pp_if_fc):
        self.username   = username
        self.title      = title
        self.mods       = self.intToMods(m)
        self.max_combo  = max_combo
        self.combo      = combo
        self.pp         = self.fmPP(pp, pp_if_fc)
        self.beatmap_id = beatmap_id
        self.accuracy   = accuracy
        self.misses     = misses

    def fmAccuracy(self, accuracy):
        return str(round(float(accuracy), 2))

    def fmPP(self, _pp, pp_if_fc):
        if _pp is not None:
            pp = str(_pp) + "pp"
        if _pp != pp_if_fc:
            pp += " ({}pp if FC)".format(pp_if_fc)
        else:
            pp = ""
        return pp

    def fmCombo(self):
        if int(self.combo) == int(self.max_combo):
            combo = " "
        else:
            combo = " " + str(combo) + '/' + str(self.max_combo) + " "
        return combo

    def intToMods(self, mods):
        """Convert a mod integer to a mod string."""
        mods_a = []
        for k, v in osuConst.modToInt.items():
            if v & mods == v:
                mods_a.append(k)
        ordered_mods = list(filter(lambda m: m in mods_a, osuConst.mod_order))
        "NC" in ordered_mods and ordered_mods.remove("DT")
        "PF" in ordered_mods and ordered_mods.remove("SD")

        return "%s" % "".join(ordered_mods) if ordered_mods else ""

    def modsToInt(self, mods):
        summ = 0
        for i in range(0, len(mods), 2):
            mod = mods[i:i+2]
            summ+= osuConst.modToInt.get(mod)
        return summ

    def __str__(self):
        return '{} | {} {} ({}%){}{} | {}\nhttps://osu.ppy.sh/b/{}'.format(
            self.username,
            self.title, 
            self.mods,
            self.accuracy,
            self.combo,
            self.misses,
            self.pp, 
            self.beatmap_id)