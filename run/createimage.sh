#!/bin/sh

## @file This script generates circular diagrams for a given tabular file matching the requirement of the tableviewer program in the circos-tools package

DATA_FILE=$(readlink -f $1)
FILE_NAME=$(basename "$DATA_FILE")
BASE_NAME=${FILE_NAME%.*}
CONF_FILE=

if echo "$1" | grep --quiet "without_productions"
then
    CONF_FILE=parse-table-without-produtions.conf
else
    CONF_FILE=parse-table.conf
fi

TMP_DIR=/tmp/$BASE_NAME
mkdir $TMP_DIR
#tar xvf circos-conf.tar.gz -C $TMP_DIR
cp -v ./etc/ $TMP_DIR
pushd $TMP_DIR
mkdir results

parse-table -conf etc/$CONF_FILE -file $DATA_FILE -segment_order=ascii,size_desc -placement_order=row,col -intra_cell_handling=hide -interpolate_type count  -color_source row -transparency 2 -fade_transparency 0 -ribbon_bundle_order=size_asc -ribbon_layer_order=size_asc | make-conf -dir data 

circos  -conf etc/circos.conf

./svg_name_fix.py results/circos-table-conf-large.svg results/${FILE_NAME%.*}.svg

rsvg-convert results/${BASE_NAME}.svg | convert png:- -background white -flatten results/${FILE_NAME%.*}.jpg

rm -v results/circos*

popd

if [ ! -d ./results ]
then
    mkdir results
fi
mv -v $TMP_DIR/results/* ./results/
rm -rfv $TMP_DIR
