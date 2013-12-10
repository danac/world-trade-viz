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

## @file faostat_trade_data.py
#
# This file contains the code needed to parse trade and production data and to create trade matrices.

# Module required to handle XML files.
import xml.etree.ElementTree as etree
# Module required to retrieve the arguments provided on the command line (sys.argv).
import sys
# Numpy provides handy matrix support.
import numpy as np
# Module needed for advanced text pattern matching and replacement.
import re
# Module needed for CSV file parsing
import csv

## This class holds trade matrices and production quantities.
# Data is loaded from XML files retrieved from the faostat website
# (faostat.fao.org). Any number of years and commodities is supported.
# The list of all countries is loaded from one such file as well.
class FAOStatTradeData:

    # Attributes

    ## Dictionary of trade matrices (stored as square 2D Numpy arrays) indexed by (year, comodity) tuples.
    trade_matrices = None
    ## Dictionary indexed by (year, comodity) holding dictionaries of production quantities indexed by region name
    productions = None
    ## Dictionary holding the country-to-region mapping
    country_regions = None
    ## Dictionary holding the region-to-number mapping
    region_numbers = None
    ## Dictionary holding the number-to-region mapping
    region_numbers_reverse = None

    ## The constructor initiliazes the country list and indices (alphabetically for now).
    def __init__(self):
        self.trade_matrices = dict()
        self.productions = dict()
        self.region_numbers = dict()
        self.region_numbers_reverse = dict()
        self.country_regions = dict()
        self.productions = dict()

    ## This function loads the countries from a CSV file
    # @param file_name A simple two-column, tab-delmited CSV file containing a list of countries with their corresponding region (the region names must match the names given to load_regions().
    def load_country_regions(self, file_name):
        print("Loading countries to regions mapping from file: {}".format(file_name))

        with open(file_name, 'rb') as f:
            reader = csv.reader(f, delimiter='\t')
            count = 0
            for row in reader:
                country_name = self._fix_name(row[0].decode('utf-8'))
                region_name = self._fix_name(row[1])
                if region_name not in self.region_numbers.keys():
                    sys.exit("ERROR: Country {} assigned to region {} which hasn't been loaded"
                        .format(country_name, region_name))
                self.country_regions[country_name] = region_name
                count = count + 1

        print(" - Loaded {} countries!".format(count))

    ## This function loads the regions (visible on the diagram) from a CSV file
    # @param file_name A simple two-column, tab-delmited CSV file containing a list of regions and numbers used for ordering (floats ok)
    def load_regions(self, file_name):
        print("Loading regions from file: {}".format(file_name))

        region_numbers = dict()
        count = 0

        with open(file_name, 'rb') as f:
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                region_name = self._fix_name(row[0])
                region_number = float(row[1])
                if region_name in region_numbers.keys():
                    sys.exit("ERROR: Region {} cannot be loaded a second time!".format(region_name))
                region_numbers[region_name] = region_number
                count = count + 1

        region_list = sorted(region_numbers.keys(), key = region_numbers.get)
        self.region_numbers = dict(zip(region_list, range(count)))
        self.region_numbers_reverse = dict(zip(range(count), region_list))

        print(" - Loaded {} regions!".format(count))

    ## Loads trade data from a faostat XML file into the class.
    # Years and commodities are automatically detected and added.
    # @param file_name A faostat XML file holding a trade matrix.
    # @param threshold A lower bound value below which trade quantities are ignored
    def load_trade_data(self, file_name, threshold = 0):
        print("Loading trade data from file: {}".format(file_name))
        data_set = etree.parse(file_name).getroot()
        num_regions = len(self.region_numbers)
        count = dict(zip(self.region_numbers.keys(), [0] * num_regions))
        total_count = 0

        # Loop over all <Table1> elements in the tree.
        # Each of these elements represents one country.
        for table in data_set:
            # We only look at exports, so ignore imports...
            trade_type = table.find("element").text
            if trade_type == "Import":
                continue

            # See what this table deals with
            country_name = self._fix_name(table.find("reporter").text.strip())
            year = int(table.find("years").text)
            commodity = table.find("items").text
            region = self.country_regions[country_name]
            region_number = self.region_numbers[region]

            # We look if there's already a matrix for that commodity/year combination
            if (year, commodity) not in self.trade_matrices.keys():
                print(" - Creating an empty matrix for commodity {} for year {}!".format(commodity, year))
                matrix = np.zeros([num_regions, num_regions], dtype = np.int)
                self.trade_matrices[(year,commodity)] = matrix

            matrix = self.trade_matrices[(year,commodity)]

            # Loop over all partner countries in the <Table1> element
            for entry in table:
                # Skip tags already dealt with
                if entry.tag in ("reporter", "years", "items", "element"):
                    continue

                partner_country_name = self._fix_name(entry.tag)
                try:
                    partner_region = self.country_regions[partner_country_name]
                except KeyError:
                    print("WARNING! Unknown country: {}".format(self.name_decode(partner_country_name)))
                    continue

                partner_region_number = self.region_numbers[partner_region]
                quantity = entry.text

                if quantity is not None and region != partner_region and int(quantity) > threshold:
                    matrix[region_number, partner_region_number] += int(quantity)
                    count[region] += 1
                    total_count += 1

        print(" - Loaded {} export quantities:".format(total_count))
        for key in sorted(count.keys()):
            print ("   - {}: {} exports".format(self.name_decode(key), count[key]))

    ## Loads production data from a faostat XML file into the class.
    # Years and commodities are automatically detected and added.
    # @param file_name A faostat XML file holding commodity production data.
    def load_production_data(self, file_name):
        print("Loading trade data from file: {}".format(file_name))
        data_set = etree.parse(file_name).getroot()
        num_regions = len(self.region_numbers)
        count = dict(zip(self.region_numbers.keys(), [0] * num_regions))
        total_count = 0

        for table in data_set:
            # We only look at production quantities, so ignore other info (e.g. yield).
            trade_type = table.find("element").text
            if trade_type != "Production (tonnes)":
                continue

            # See what this table deals with
            country_name = self._fix_name(table.find("countries").text.strip())
            commodity = table.find("item").text
            region = self.country_regions[country_name]
            region_number = self.region_numbers[region]

            # Loop over all years in the <Table1> element
            for entry in table:
                # Skip tags already dealt with
                if entry.tag in ("countries", "country_x0020_codes", "item", "item_x0020_codes", "element", "element_x0020_codes"):
                    continue
                year = int(self.name_decode(entry.tag))
                quantity = entry.text

                # We look if there's already an entry for that commodity/year combination
                if (year, commodity) not in self.productions.keys():
                    self.productions[(year, commodity)] = dict()
                prod_dict = self.productions[(year, commodity)]

                # We look if there's already an entry for this region
                if region not in prod_dict.keys():
                    prod_dict[region] = 0

                if quantity is not None and int(quantity) != 0:
                    prod_dict[region] += int(quantity)
                    count[region] += 1
                    total_count += 1

        print(" - Loaded {} production values:".format(total_count))
        for key in sorted(count.keys()):
            print ("   - {}: {} production values".format(self.name_decode(key), count[key]))

    ## Returns a trade matrix for a given year/commodity combination as a square 2D Numpy array.
    # @param year The year, as an integer or string.
    # @param commodity The commodity, as a string.
    def _get_trade_matrix(self, year, commodity):
        matrix = None
        try:
            matrix = self.trade_matrices[(int(year),commodity)]
        except KeyError:
            print("No data matching commodity {} for year {}!".format(commodity, year))
            raise
        return matrix

    ## Saves a trade matrix for a given year/commodity combination as a file readable
    #  by the Circos tableviewer utility.
    # @param year The year, as an integer or string.
    # @param commodity The commodity, as a string.
    # @param file_name Path to the target file.
    # @param with_production Boolean indicating whether to take the production quantities into account
    # @param threshold A quantity lower bound which filters out regions whose total imports + production is below the value
    def save_trade_matrix(self, year, commodity, file_name, with_production = False, threshold = 0):
        # Retrieve the matrix
        matrix = self._get_trade_matrix(year, commodity)
        prod_dict = self.productions[(year, commodity)]
        num_regions = len(self.region_numbers)

        # Open a file descriptor to the target path
        with open(file_name, 'w') as file_handle:
            # Write the header on the first line:
            # word "data" followed by the country names, separated by tabs
            file_handle.write("data\tdata\t")
            if with_production:
                file_handle.write("data\t")
            regions_to_write = []

            # This dictionary will hold the "size" of each regions (i.e. imports + production)
            sizes = dict()

            # Loop over all regions
            for i in range(num_regions):
                region_name = self.region_numbers_reverse[i]
                if region_name == "Unspecified":
                    continue

                # We first set the size equal to the imported quantity
                sizes[region_name] = np.sum(matrix[:,i])

                # If this region produces something, we add it to the size
                if prod_dict.has_key(region_name):
                    sizes[region_name] += prod_dict[region_name]

                # If the size is not null, we take this region into account
                if sizes[region_name] > threshold:
                    regions_to_write.append(region_name)
                    file_handle.write(self.region_numbers_reverse[i])
                    # Add a tab if this is not the last region
                    if i != num_regions - 1:
                        file_handle.write('\t')

            file_handle.write('\n')

            # Write the lines of the matrix, starting each row by the country name.
            for region in regions_to_write:
                i = self.region_numbers[region]
                file_handle.write(str(i))
                file_handle.write('\t')
                if with_production:
                    file_handle.write(str(sizes[region]))
                    file_handle.write('\t')
                file_handle.write(region)
                file_handle.write('\t')

                # Write each entry in the matrix in integer format, with tabs as delimiter.
                for partner in regions_to_write:
                    j = self.region_numbers[partner]
                    file_handle.write("{:d}".format(matrix[i,j]))
                    if partner != regions_to_write[-1]:
                        file_handle.write('\t')
                file_handle.write('\n')

        print("Matrix for commodity {} and year {} saved to {}".format(commodity, year, file_name))

    ## Loads all countries (both reported and partner countries)
    # contained in a faostat XML trade matrix.
    # @param file_name A faostat trade matrix XML file
    # <DocumentElement> tag of an faostat XML trade matrix.
    def _get_country_list_from_xml(self, file_name):
        root = etree.parse(file_name).getroot()

        # Declare an empty dictionary. The names will be added to it.
        # Since dictionary keys are unique, duplicates will be ignored.
        countries = {}
        # Loop over all countries in the file (i.e. over each <Tree1> element).
        for table in tree_root:
            # The country's name is in the "reporter" tag.
            name = self._fix_name(table.find("reporter").text.strip())
            countries[name] = None

        # Look at the first <Table1> element
        table = tree_root.getchildren()[0]
        # Loop over all sub-elements in that <Table1> element.
        # Each entry in those sub-elements represents one partner country,
        # apart from the first 4 entries (reporter, years, etc.)
        for entry in table:
            # Skip what's not interested or already dealt with.
            if entry.tag in ("reporter", "years", "items", "element"):
                continue
            name = self._fix_name(entry.tag)
            # Add a new (empty) entry in the dictionary for that country
            countries[name] = None
        country_list = countries.keys()
        # Sort the list, based on a sorting rule, because the names are assumed to be Unicode objects.
        return sorted(country_list)

    ## Circos only supports alphanumeric names with underscores but without spaces.
    # Besides, in the FaoStat XML file, names appear both in human-readable format
    # and with unicode numbers.
    # This functions replaces all illegal characters by a unicode value
    # (see the _name_encode function below).
    # @param The name of a country, assumed to be a Unicode object, or an ASCII text string.
    def _fix_name(self, name):
        return self.name_encode(name)

    ## This static function returns a copy of the input string as a Unicode object with all
    # unicode characters, spaces, parentheses, commas and apostrophes replaced
    # by _x####_ where ### is the correpsonding unicode hex number.
    # @param name The text to parse, assumed to be a Unicode object, or an ASCII text string.
    @staticmethod
    def name_encode(name):
        # Break the text into a list of characters
        string_list = list(unicode(name).strip())

        for i, val in enumerate(string_list):
            # Convert all characters that are not pure ASCII alphanumeric
            if not val.isalnum() and val != u'_' or ord(val) >= 128:
                string_list[i] = u'_x{:04X}_'.format(ord(val))

        # Assemble the characters back into a string
        fixed_string = u''.join(string_list)

        return fixed_string

    ## This static function is the inverse of the _name_encode method and
    # returns a Unicode object corresponding to the input string
    # with all codes translated back to their corresponding character.
    # @param name The text to decode (an ASCII text string with only alphanumeric characters or underscores).
    @staticmethod
    def name_decode(name):
        # Pattern corresponding to a character code
        pattern = re.compile("_x([0-9a-fA-F]{4})_")
        # Find all matches in the text string
        fixed_string = name
        for match in pattern.finditer(name):
            # The code is the first and only "group"
            # (i.e. parenthesized sub-expression in the pattern above).
            code = match.groups()[0]
            # Convert the code to integer, knowing that it's in base 16 (hexadecimal).
            hex_code = int(code, 16)
            # Replace the pattern by the right character
            fixed_string = re.sub("_x" + code + "_", unichr(hex_code), fixed_string)

        return fixed_string

if __name__ == "__main__":
    pass
