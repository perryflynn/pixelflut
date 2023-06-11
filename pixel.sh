#!/bin/bash

# Very basic pixelflut script
# which uses netcat

buffer=""

for X in $(seq 1500 1600); do
    for Y in $(seq 600 700); do
        buffer="${buffer}PX $X $Y ff0000\n"
    done
done

for I in $(seq 1 10); do
    buffer="${buffer}${buffer}"
done

while true; do
    echo -en "$buffer" | netcat -q2 gpn-flut.poeschl.xyz 1234
done
