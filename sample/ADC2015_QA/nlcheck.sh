#!/bin/sh

for i in 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20
do
    #nlcheck.py --input Q/Q${i}.txt --target A/A${i}.txt --gif A/A${i}.gif
    nlcheck.py --input Q/Q${i}.txt --target A/A${i}.txt
    nlcheck.py --input Q.2016/Q${i}.2016.txt --target A.2016/A${i}.2016.txt
done
