from constants import osuConstants


class Formatter:
    def __init__(self,
                 username, title, m, accuracy,
                 combo, max_combo, misses, pp, beatmap_id, pp_if_fc, rank):
        self.username = username
        self.title = title
        self.beatmap_id = beatmap_id
        self.mods = self.int_to_mods(m)
        self.combo = self.format_combo(combo, max_combo)
        self.pp = self.format_pp(pp, pp_if_fc)
        self.accuracy = self.format_accuracy(accuracy)
        self.misses = self.format_misses(misses)
        self.rank = rank

    def format_accuracy(self, accuracy):
        return round(float(accuracy), 2)

    def format_misses(self, misses):
        if int(misses) == 0:
            return ""
        return f"{misses}xMiss"

    def format_pp(self, _pp, pp_if_fc):
        if _pp is not None:
            pp = str(_pp) + "pp"
        if _pp != pp_if_fc:
            pp += " ({}pp if FC)".format(pp_if_fc)
        else:
            pp = ""
        return pp

    def format_combo(self, combo, max_combo):
        if int(combo) == int(max_combo):
            combo = " "
        else:
            combo = " " + str(combo) + '/' + str(max_combo) + " "
        return combo

    def int_to_mods(self, mods):
        """
        Convert a mod integer to a mod string.
        """
        mods_a = []
        mods = int(mods)
        for k, v in osuConstants.mod_to_int.items():
            if v & mods == v:
                mods_a.append(k)
        ordered_mods = list(
            filter(lambda m: m in mods_a, osuConstants.mod_order))
        "NC" in ordered_mods and ordered_mods.remove("DT")
        "PF" in ordered_mods and ordered_mods.remove("SD")

        return "%s" % "".join(ordered_mods) if ordered_mods else ""

    def modsToInt(self, mods):
        summ = 0
        for i in range(0, len(mods), 2):
            mod = mods[i:i+2]
            summ += osuConstants.mod_to_int.get(mod)
        return summ

    def __str__(self):
        result = ""
        if self.rank == "F":
            result+="UNSUBMITTED\n"
        result += f"{self.username} | {self.title} {self.mods} ({self.accuracy}%) {self.combo} {self.misses} | {self.pp}\nhttps://osu.ppy.sh/b/{self.beatmap_id}"
        return result 
