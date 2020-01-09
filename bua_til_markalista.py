#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from os import listdir, remove
from os.path import isfile, join, dirname
import codecs
import operator


path_to_gull = "/media/starkadur/NewVolume/Gullstaðlar/GULL-MIM/v1.2/13_flokkar_med_skilum/txt/"

files = [f for f in listdir(path_to_gull) if isfile(join(path_to_gull, f)) and f.find(".correct")>0]
cnt_ath = 0

marks = set()
for file in files:
    print(file)
    f = open(join(path_to_gull, file), "r")
    lines = f.readlines()
    f.close()

    for line in lines:
        line = line.strip()
        splt = line.split("\t")
        if len(splt)>2:

            mark = splt[1]
            if mark not in marks:
                marks.add(mark)




marks_sorted = sorted(marks)
print(len(marks_sorted))
with open("markamengi.txt", "w") as f:
    for mark in marks_sorted:
        f.write(mark+"\n")
