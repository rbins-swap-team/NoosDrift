#!/usr/bin/env python

import sys
import os
import json
import datetime as dt
import noosdrift_json_request as NDR
import pytz

utc = pytz.utc

inDir = "/home/optos_v2/data_center/NWS/maps/results/png/"
outDirRoot = "/home/web/noosdrift_maps/results/"

sl = "/"
un = "_"
sp = " "


##########################################

def String2DT(string):
    return dt.datetime(int(string[0:4]), int(string[5:7]), int(string[8:10]), hour=int(string[11:13]),
                       minute=int(string[14:16]), tzinfo=utc)


def createListOfDates(Start, End):
    toReturn = []
    date = Start - dt.timedelta(seconds=Start.minute * 60)
    while date <= End:
        toReturn.append(date.strftime("%Y%m%d%H") + "00")
        date += dt.timedelta(seconds=3600)
    return toReturn


#########################################
# main
########################################

try:
    requestFile = sys.argv[1]
except:
    sys.stderr.write("Syntax is ./copyMaps.py <requestfile>")
    exit(1)

try:
    req = NDR.Noosdrift_JSON_request(requestFile)
except:
    sys.stderr.write("The requestFile could not be loaded")
    exit(2)

########################################
# get the data and create the subdir

Start = String2DT(req.get_value("simulation_start_time"))
End = String2DT(req.get_value("simulation_end_time"))
ListOfDates = createListOfDates(Start, End)

outdir = outDirRoot + str(req.get_value("request_id")) + sl
if not os.path.exists(outdir):
    try:
        os.system("mkdir " + outdir)
    except:
        sys.stderr.write("could not create dir ", outdir)
        exit(3)

###########################################
# Copy the data to destination outdir

try:
    # Copy the color bars
    os.system("cp " + inDir + ListOfDates[-1][:8] + sl + "cb*png " + outdir)

    # Copy the files
    for date in ListOfDates:
        os.system("cp " + inDir + date[:8] + sl + "*" + date + "* " + outdir)
except:
    sys.stderr.write("The files could not be copied - please investigate")
    exit(4)

sys.stdout.write("All clear - exit")
exit(0)
