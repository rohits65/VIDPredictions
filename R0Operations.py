#! /usr/local/bin/python3
import os.path


def addR0(R0, file, county, currentDate):
    if os.path.isfile(file) == False:
        f = open(file, "a")
        f.write("# COUNTY_NAME = " + str(county))
        f.write("\n# FIRST_DATA_POINT = " + str(currentDate))
        f.write("\n"+str(currentDate) + " , " + str(R0))
        f.close()
    else:
        f = open(file, "a")
        f.write("\n"+str(currentDate) + " , " + str(R0))
        f.close()

    # else:
    #     f = open(file, "w+")
    #     f.write(R0)
