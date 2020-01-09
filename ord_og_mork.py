#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from os import listdir, remove
from os.path import isfile, join, dirname
import codecs
import operator
import collections

path_to_gull = "/media/starkadur/NewVolume/Gullstaðlar/GULL-MIM/v1.2/13_flokkar_med_skilum/txt/"

files = [f for f in listdir(path_to_gull) if isfile(join(path_to_gull, f)) and f.find(".correct")>0]
cnt_ath = 0

data = {}
for file in files:
    print(file)
    f = open(join(path_to_gull, file), "r")
    lines = f.readlines()
    f.close()

    for line in lines:
        splt =  line.split("\t")
        if len(splt)>2:

            ord = splt[0]
            mark = splt[1]
            if ord not in data:
                data[ord] = {}

            if mark not in data[ord]:
                data[ord][mark]=1
            else:
                data[ord][mark]+=1



od = collections.OrderedDict(sorted(data.items()))

with open("ord_og_mork.txt", "w") as f:
    for key in od:

        f.write(key+"\t")
        tmp = ""
        for mark in od[key]:
            cnt = od[key][mark]
            tmp+=mark+" "+str(cnt)+"#"

        f.write(tmp[:-1]+"\n")
