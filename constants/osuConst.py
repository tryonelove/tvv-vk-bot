import re

sig_colors = ['black', 'red', 'orange', 'yellow', 'green', 'blue', 'purple', 'pink', 'hex2255ee']

# score regex
beatmap_id_re = re.compile(r".*\/b/(\d+)")
title_re = re.compile(".+[\|丨].+-.+\[.+\]")