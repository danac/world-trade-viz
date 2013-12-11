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

## @file latex.py
#
# This file creates a latex document to visualize the diagrams

import os, os.path

if __name__ == "__main__":

    commodities = ("Wheat", "Maize", "Soybeans")
    years = range(2000, 2012, 2)
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
\centering \Large \textbf{Wheat in the 2000s}
\end{framed}
}
\date{December 2013}

\begin{document}

\maketitle
\pagebreak
%%TABLE%%

\end{document}
    """

    try:
        os.mkdir("latex")
    except OSError:
        pass

    for commodity in commodities:

        tex = backbone.replace("%%COMMODITY%%", commodity)

        table = ""

        for year in years:
            table += r"""
\begin{center}
\begin{tabular}{@{}cc@{}}
\includegraphics[width=.5\linewidth]{%%COMMODITY%%_%%YEAR1%%.jpg} &
\includegraphics[width=.5\linewidth]{%%COMMODITY%%_%%YEAR2%%.jpg} \\
\tiny \textbf{%%YEAR1%%} & \tiny \textbf{%%YEAR2%%}
\end{tabular}
\end{center}
            """.replace("%%YEAR1%%", str(year)).replace("%%YEAR2%%", str(year+1)).replace("%%COMMODITY%%", commodity)

        tex = tex.replace("%%TABLE%%", table)

        with open(os.path.join('latex', commodity + "_raster.tex"), 'w') as f:
            f.write(tex)
            print("Generated LaTeX code for commodity {}, years {}-{} (JPG)".format(commodity, years[0], years[-1]+1))

        tex = tex.replace(".jpg", ".pdf")

        with open(os.path.join('latex', commodity + "_vectorized.tex"), 'w') as f:
            f.write(tex)
            print("Generated LaTeX code for commodity {}, years {}-{} (EPS)".format(commodity, years[0], years[-1]+1))







