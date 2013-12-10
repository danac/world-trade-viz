#!/usr/bin/env python2

#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#

## @file faostat_main.py
#
# This file contains the main program.

from faostat_trade_data import FAOStatTradeData
import os.path, sys
from glob import glob

if __name__ == "__main__":

    data_dir = sys.argv[1]
    output_dir = sys.argv[2]

    data_structure = FAOStatTradeData()
    data_structure.load_regions(os.path.join(data_dir, "regions.csv"))
    data_structure.load_country_regions(os.path.join(data_dir, "country_regions.csv"))

    for data_file in glob(os.path.join(data_dir, "TradeMatrix*")):
        data_structure.load_trade_data(data_file)
    data_structure.load_production_data(os.path.join(data_dir, "StatisticalDataProductionWheat2000-11.xml"))

    years = range(2000, 2012)
    for year in years:
        data_structure.save_trade_matrix(year, "Wheat", os.path.join(output_dir, "{}_Wheat.txt".format(year)), threshold = 10, with_production=True)

