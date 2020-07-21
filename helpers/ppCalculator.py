import io
import pyttanko
import requests


class PpCalculator:
    def __init__(self, beatmap_id, m, misses, count50, count100, count300, combo, **kwargs):
        self.beatmap_id = beatmap_id
        self.mods = int(m)
        self.misses = int(misses)
        self.count50 = int(count50)
        self.count100 = int(count100)
        self.count300 = int(count300)
        self.combo = int(combo)
        self.parser = pyttanko.parser()
        self.bmap = None
        self.objcount = 0

    def parse_map(self):
        url = f'https://osu.ppy.sh/osu/{self.beatmap_id}'
        r = requests.get(url)
        self.bmap = self.parser.map(io.StringIO(r.text))
        self.objcount = self.bmap.ncircles + self.bmap.nsliders + self.bmap.nspinners

    def get_real_pp(self):
        stars = pyttanko.diff_calc().calc(self.bmap, self.mods)
        ppv2 = pyttanko.ppv2(aim_stars=stars.aim, speed_stars=stars.speed, mods=self.mods, n100=self.count100,
                             n50=self.count50, n300=self.count300, nmiss=self.misses, combo=self.combo, bmap=self.bmap)
        return round(ppv2[0], 2)

    def get_if_fc_pp(self):
        # Set miss count to zero
        self.misses = 0
        self.combo = self.bmap.max_combo()
        stars = pyttanko.diff_calc().calc(self.bmap, self.mods)
        # max_combo used if combo is not provided => 
        # don't need to set it manually
        ppv2 = pyttanko.ppv2(stars.aim, stars.speed, n100=self.count100,
                             n50=self.count50, n300=self.count300, mods=self.mods, bmap=self.bmap)
        return round(ppv2[0], 2)