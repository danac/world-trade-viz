#!/usr/bin/env python2

import re
import sys
from faostat_trade_data import FAOStatTradeData

if len(sys.argv) != 3:
    print("Syntax: svg_name_fix <input_file> <output_file>")
    sys.exit()


with open(sys.argv[1], 'r') as f, open(sys.argv[2], 'wb') as f_hdl:
    pattern = re.compile("_x([0-9a-zA-Z]{4})_")
    for line in f:
        new_line = FAOStatTradeData.name_decode(line)
        f_hdl.write(new_line.encode('utf-8'))
