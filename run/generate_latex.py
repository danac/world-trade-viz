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

## @file generate_latex.py
#
# This file generates latex documents to visualize the diagrams.
# The LaTeX source in saved in the latex/ folder of the current directory (it is created if it does not exist)
# Two sets of documents are created: one set with rasterized images and one set with vectorized images.
# Diagrams must be available in JPG and EPS formats in the run/results/ directory for the LaTeX source to compile.

import os, os.path

## Generates the LaTeX code for the table
# @param template Tempalte code with %%..%% placeholders
# @param commodity Commodity
# @years List of years (even, with one out of two years skipped)
# @param Extension of image files
# @suffix Suffix to add to the image files
def generate_tables(template, commodity, years, img_ext, suffix=""):

    tables = ""

    for year in years:
        tables += template.replace("%%YEAR1%%", str(year)).replace("%%YEAR2%%", str(year+1)).replace("%%SUFFIX%%", suffix).replace("%%EXT%%", img_ext).replace("%%COMMODITY%%", commodity)

    return tables

## Write to a text file
# @param out_dir Name of sub-folder where to write the file
# @param contents Text to write to the file
# @param commodity Name of the commodity
# @param suffix Suffix to append to the saved file name
def write_to_file(out_dir, contents, commodity, suffix):
    fpath = os.path.join(out_dir, commodity + suffix + ".tex")

    with open(fpath, 'w') as f:
        f.write(tex)
    print("Saved LaTeX file: {}".format(fpath))


if __name__ == "__main__":

    ## The name of the sub-folder where the LaTeX is to be saved
    out_dir = "latex"
    ## The commodities to take into consideration
    commodities = ("Wheat", "Maize", "Soybeans")
    ## The years to take into consideration. For the time being, this only works for even numbers of years!
    years = range(2000, 2012, 2)
    ## Template of the LaTeX document. It contains %%..%% placeholders to substitute.
    backbone = r"""

\documentclass[12pt, a4paper]{article}

\usepackage{a4wide}
\usepackage{graphicx}
\usepackage{array}
\usepackage{framed}

\graphicspath{{../../run/results/}}

\author{Victoria Junquera \& Dana Christen}
\title{
\begin{framed}
\centering \huge \underline{World Trade Visualization} \\
\vspace{1cm}
\centering \Large \textbf{%%COMMODITY%% %%WHAT%% in the 2000s}\\
(in millions of tonnes)
\end{framed}
}
\date{December 2013}

\begin{document}

\maketitle
\pagebreak
%%TABLE%%

\end{document}
    """

    ## Template of the LaTeX table containing the images. It contains %%..%% placeholders to substitute.
    table_template = r"""
\begin{center}
\begin{tabular}{@{}cc@{}}
\includegraphics[width=.5\linewidth]{%%COMMODITY%%_%%YEAR1%%%%SUFFIX%%.%%EXT%%} &
\includegraphics[width=.5\linewidth]{%%COMMODITY%%_%%YEAR2%%%%SUFFIX%%.%%EXT%%} \\
\tiny \textbf{%%YEAR1%%} & \tiny \textbf{%%YEAR2%%}
\end{tabular}
\end{center}
    """

    try:
        os.mkdir("latex")
    except OSError:
        pass

    for commodity in commodities:

        # With productions (raster)
        tex = backbone.replace("%%COMMODITY%%", commodity).replace("%%WHAT%%", "production and trade")
        tables = generate_tables(table_template, commodity, years, "jpg")
        tex = tex.replace("%%TABLE%%", tables)
        write_to_file(out_dir, tex, commodity, "_raster")

        # With productions (raster)
        tex = backbone.replace("%%COMMODITY%%", commodity).replace("%%WHAT%%", "trade")
        tables = generate_tables(table_template, commodity, years, "jpg", suffix="_without_productions")
        tex = tex.replace("%%TABLE%%", tables)
        write_to_file(out_dir, tex, commodity, "_without_productions_raster")

        # With productions (vectorized)
        tex = backbone.replace("%%COMMODITY%%", commodity).replace("%%WHAT%%", "production and trade")
        tables = generate_tables(table_template, commodity, years, "pdf")
        tex = tex.replace("%%TABLE%%", tables)
        write_to_file(out_dir, tex, commodity, "_vectorized")

        # With productions (vectorized)
        tex = backbone.replace("%%COMMODITY%%", commodity).replace("%%WHAT%%", "trade")
        tables = generate_tables(table_template, commodity, years, "pdf", suffix="_without_productions")
        tex = tex.replace("%%TABLE%%", tables)
        write_to_file(out_dir, tex, commodity, "_without_productions_vectorized")

