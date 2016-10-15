#!/bin/sh

echo Generating plain "tropical" flat map with pinpoints ...
nugsl-worldmap -t flat \
               -o demo_tropical_flat.svg \
	       -P sample.pins \
	       -S tropical_world.sty
echo ''

echo Generating PNG "sepia" map of Laos and clickable page ...
echo '(with separate layers for country and pinpoint, for postprocessing)'
nugsl-worldmap -o demo_laopdr.svg \
               -c la \
	       -C sample.countryconfig \
               -P sample.pins \
	       -S sepia_country.sty,sepia_country_nopins.sty,pins_only.sty \
	       -T clickablepage.html \
	       -x 1024 -y 450 -D -X

echo ''

echo Generating "sepia" rotated Robinson projection and clickable page ...
echo '(suppressing clickable pinpoints)'
nugsl-worldmap -t rotated -o demo_index.svg -T clickablepage.html \
               -m 120e -P sample.pins -S sepia_world.sty \
	       -C sample.countryconfig -x 1000 -y 450 \
	       -Q -X

echo Generating "sepia" image of Japan and clickable page
echo '(scaling pinpoint size to a fixed pixel width in following images)'
nugsl-worldmap -o demo_japan.svg -c jp -C sample.countryconfig \
               -P sample.pins -S sepia?country.sty -T clickablepage.html \
	       -x 1024 -y 450 -D -X -W 20

echo Generating "sepia" image of Indonesia and clickable page
nugsl-worldmap -o demo_indonesia.svg -c id -C sample.countryconfig \
               -P sample.pins -S sepia_country.sty -T clickablepage.html \
	       -x 1024 -y 450 -D -X -W 20

echo Generating "sepia" image of Cuba and clickable page
nugsl-worldmap -o demo_cuba.svg -c cu -C sample.countryconfig \
               -P sample.pins -S sepia_country.sty -T clickablepage.html \
	       -x 1024 -y 450 -D -X -W 20

echo Generating "sepia" image of USA and clickable page
nugsl-worldmap -o demo_usa.svg -c us -C sample.countryconfig \
               -P sample.pins -S sepia_country.sty -T clickablepage.html \
	       -x 1024 -y 450 -D -X -W 20

echo Generating "sepia" image of Mongolia and clickable page
nugsl-worldmap -o demo_mn.svg -c mn -C sample.countryconfig \
               -P sample.pins -S sepia_country.sty -T clickablepage.html \
	       -x 1024 -y 450 -D -X -W 20

echo Generating "sepia" image of Britain and clickable page
nugsl-worldmap -o demo_gb.svg -c gb -C sample.countryconfig \
               -P sample.pins -S sepia_country.sty -T clickablepage.html \
	       -x 1024 -y 450 -D -X -W 20
