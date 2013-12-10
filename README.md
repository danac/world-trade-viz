
This projects aims at graphically representing world-wide trade statistics for a selection of commodities during the 2000s in a visually intuitive way.

Tabular data as circular diagrams
=================================

The visualistion technique used in this project is inspired by the work of a Canadian research team on genomic data visualization (see Krzywinski M. <em>et al.</em>, Circos: an information aesthetic for comparative genomics., *Genome Res.*, Sep. 2009, 19(9):1639-45).

To address the challenge of visualizing similarities and differences arising from genome comparisons, Krzywinski's team uses circular ideograms showing the relationships between genes as ribbons linking colored arc segments:

![Circular diagram (image by M. Krzywinski)](https://bitbucket.org/danachristen/world-trade-viz/raw/master/doc/diagram.jpg)

Such data is traditionally presented in tabular form. However, this does not give any visual overview of the dataset and, in particular, does not reveal any underlying pattern in the dataset, as opposed to circular diagrams, which give a direct insight into such patterns. This property makes them ideal to graphically represent any kind of tabular data reflecting relationships between elements of a set. Rows in the table are then represented by interconnected arc segments. Typical examples include flows between elements of a set, interactions between individuals in a population, to mention but a few.

An in-depth discussion of the advantages of circular diagrams for tabular data visualization can be found at [http://circos.ca/presentations/articles/vis_tables1].

Circos
------

*Circos* is a visualization program and developed by Krzywinski's team to generate circular ideograms based on genomic datasets. It is written in Perl and released under the terms of the GPL license. Even though Circos was designed to manipulate genomic data, a helper script has been made available by the authors to handle non-genomic data. This script allows to easily turn a standard tabular file into a file matching the specifications of Circos' genomic-oriented input format.

This functionality is available online on the website of Circos' author at [http://mkweb.bcgsc.ca/tableviewer].

Circos and the helper script (called *tableviewer* and available in the "circos-tools" package) can be downloaded at [http://circos.ca/software/download].

The helper script has several requirements on the format of the input data files. These requirements are introduced at [http://mkweb.bcgsc.ca/tableviewer/samples/#5]. Typically, a 7-by-7 table is expected to be passed to the script in the following form:

    data	data	data	A	B	C	D	E	F	G
    5	3000	A	105	450	92	96	5	301	195
    2	2750	B	20	46	78	33	53	28	83
    7	2500	C	118	553	94	317	25	89	287
    4	2500	D	100	18	108	104	105	25	173
    1	1250	H	23	83	123	342	98	48	205
    3	2000	I	173	428	103	325	82	215	23
    6	1500	J	305	173	138	49	81	258	207

where the values in the first column indicate the order of the arc segments in the diagram and those in the second column reflect the size of each arc segment.

> **A working version of Circos as well as the *tableviewver* tool are included in the repository, in the third-pary/ folder.**

Data parsing
============

The data used in this visualization project are published by the *Food and Agriculture Organization of the United Nations*, and is available in various formats at [http://faostat.fao.org].

Format
------

Data is retrieved from the FAOStat website in XML format. It includes production quantities and trade matrices for all countries, relevant to a selection of commodities (namely wheat, maize and soy beans). Below is an sample of an XML file retrieved from the FAOStat website containing trade information:

    <DocumentElement>
        <Table1>
            <reporter>Argentina</reporter>
            <element>Export</element>
            <years>2009</years>
            <items>Maize</items>
            <Afghanistan />
            <Albania>342</Albania>
            <Algeria>1052857</Algeria>
            <Angola>3071</Angola>
            <Antigua_x0020_and_x0020_Barbuda />
            <Argentina />
            <Armenia>49</Armenia>
            <Aruba />
            <Australia>206</Australia>
            <Austria />
            <Azerbaijan />
            <Bahamas />
            <Bahrain>176</Bahrain>
            <Bangladesh />
            <Barbados />
            <Belarus />
            <Belgium>2014</Belgium>
    ...

All trade information for a given country, a given year and a given commodity is contained into a \<Table1\> element.

Below is an example of an XML file containing production quantities:

    <DocumentElement>
        <Table1>
            <countries>Afghanistan</countries>
            <country_x0020_codes>2</country_x0020_codes>
            <item>Wheat</item>
            <item_x0020_codes>15</item_x0020_codes>
            <element>Yield (Hg/Ha)</element>
            <element_x0020_codes>5419</element_x0020_codes>
            <_x0032_000>7240</_x0032_000>
            <_x0032_001>8977</_x0032_001>
            <_x0032_002>15419</_x0032_002>
            <_x0032_003>15000</_x0032_003>
            <_x0032_004>12659</_x0032_004>
            <_x0032_005>18215</_x0032_005>
            <_x0032_006>13760</_x0032_006>
            <_x0032_007>18183</_x0032_007>
            <_x0032_008>12263</_x0032_008>
            <_x0032_009>19666</_x0032_009>
            <_x0032_010>19252</_x0032_010>
            <_x0032_011>15179</_x0032_011>
        </Table1>
    ...

Again, all information relevant to a given combination of parameters is enclosed into a \<Table1\> element. For some reason, tag names are sometimes contain unicode numbers even for ASCII characters (\\x0032 maps to number 2 in the listing above).

> **Raw files retrieved from the FAOStat website are located in the data/ folder of the repository.**

Conversion
----------

Data files matching the specifications required by the Circos helper script are generated by a Python script, based on the XML files retrieved from the FAOStat website. Extensive Doxygen documentation is available for this script in the doc/ folder of the repository. It is also available online at [http://gnugen.epfl.ch/~dchriste/world_trade_viz].

The script is compatible with Python 2.x only (mainly because of the divergence in Unicode handling between the two versions). This choice was motivated by the fact that the *Enthought Python Distribution* (now *Enthought Canopy*), a widely-used Python distribution among Windows users, has not been ported to Python 3.x yet.

Besides the creation of a data file matching the requirements of the *tableviewer* script introduced above, the Python script also implements the following functionalities:
 - support for internationalized country names
 - aggregation of country-wise data into regions
 - support for loading data scattered across an arbitrary number of XML files
 - support for manual ordering of regions

 > **Source code relevant to the conversion step is located in the src/ folder of the repository.**

 > **Converted files for several commodities are available in the output/ folder.**

Diagram generation
==================

Currently, circular diagrams are generated by a UNIX shell (located in the run/ folder of the repository) which passes data files to the *tableviewer* tool, retrieves the resulting image and performs some post-processing on it (namely Unicode character subsitution).

A set of custom Circos configuration files are used to generate the diagrams.

> **Source code relevant to diagram generation is to be found in the run/ folder of the repository.**



