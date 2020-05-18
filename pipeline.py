#! /usr/local/bin/python3
import datetime
import math
import multiprocessing
import os
import pickle
import time
import monitorFiles as mf
import logging

from googleapiclient.discovery import build

import average as avg
import calculateScore as calc
import notify
import operate
import parseData as pad
import quickstart as gs
import r0AverageTest as r0AverageTest
import readFile as rf
import regressions as rgx
import re
import pygsheets as pg


import sys
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# handler = logging.StreamHandler(stream=sys.stdout)
handler = logging.FileHandler('pipeline.log')
handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = handle_exception








def createR0Values(originalR0, searchRange):
    trueR0Values = [round(float(originalR0-searchRange),2), round(float(originalR0),2), round(float(originalR0+searchRange),2)]
    for i in range(len(trueR0Values)):
        if trueR0Values[i] <= 0:
            trueR0Values[i] = 0
    r0ValuesArr = []

    for i in range(len(trueR0Values)):
        try:
            if trueR0Values[i].is_integer():
                r0ValuesArr.append([[1, trueR0Values[i]]])
            else:
                percentages = math.modf(trueR0Values[i])
                r0ValuesArr.append([[round(1-percentages[0],2), round(percentages[1],2)], [1, round(percentages[1] + 1, 2)]])
        except AttributeError:
            r0ValuesArr.append([[1, trueR0Values[i]]])
    return (trueR0Values, r0ValuesArr)




def pipeline(CURRENT_DATE, COUNTY, FIRSTCASEDATE, FILE, POPULATION_SIZE, coeffs, PUBLISH_RUN = True, useCases=True, over=False, l=0, maxR0Eq=None):

    # CURRENT_DATE = "4-15-20"
    # COUNTY = "SantaClara"
    # FIRSTCASEDATE = '03-01-2020'
    # FILE = "Data/SantaClaraCases.txt"
    # POPULATION_SIZE = 206874
    

    os.chdir("main")
    DATA = list(map(int,list(rf.readDataFile(FILE))))
    logger.info(COUNTY + ":" + str(DATA))
    os.chdir("counties(" +datetime.date.today().strftime("%m-%d-%Y")+ ")")

    newpath = os.path.join(COUNTY)
    if not os.path.exists(newpath):
        os.makedirs(newpath)
        os.chdir(newpath)
    else:
        os.system('rm -rf ' + COUNTY)
        os.makedirs(newpath)
        os.chdir(newpath)

    

    # Open Multiprocessing, allow for process communication
    manager = multiprocessing.Manager()
    returnDict = manager.dict()
    
    # Initialize range (+/-), depth
    searchRange = 0.3 # 0.3
    depth = 2


    # Initialize parameters
    fileArr = [
        # "originalControl", 
        "start1", 
        "start2", 
        "start3"
    ]

    trueR0Values = [
        # 2.2,
        0.55,
        1.1,
        1.65
    ]
    
    r0ValuesArr = [
        # [[0.15, 1], [0.4, 3], [0.75,2], [0.9,4], [1,0]], 
        [[0.45,0],[1,1]], 
        [[1,1]],
        [[0.35,1], [1,2]]
    ]

    startingDayArr = [
        # 44,
        len(DATA[0:len(DATA)-10]),
        len(DATA[0:len(DATA)-10]),
        len(DATA[0:len(DATA)-10])
    ]

    newByDayArr = [
        # [1,1,3,2,2,3,6,4,8,5,6,2,3,18,13,12,23,24,17,20,14,7,67,39,19,73,84,83,32,17,55,202,42,66,63,75,54,59,17,61,95,62,42, 82, 55,45],
        DATA[0:len(DATA)-10],
        DATA[0:len(DATA)-10],
        DATA[0:len(DATA)-10],
        DATA
    ]

    iterations = 20

    for i in range(len(trueR0Values)):
            f = open(fileArr[i], "w")
            f.close()

    while searchRange > 0:
        print(fileArr)
        timeStart = time.time()
        
        # Empty return value container
        # returnDict = {}
        print(returnDict)

        # Begin processes
        processes = []

        for m in range(0, 3):
            p = multiprocessing.Process(target=r0AverageTest.multiprocessDef, args=(2, r0ValuesArr[m], fileArr[m], startingDayArr[m], newByDayArr[m], iterations, POPULATION_SIZE, False, coeffs, None))
            p.start()
            processes.append(p)

        for p in processes:
            p.join()
               
        processes = []

        for m in range(0, 3):
            p = multiprocessing.Process(target = operate.operate, args = (fileArr[m], returnDict, newByDayArr[m], m, trueR0Values[m], FIRSTCASEDATE, DATA, useCases))
            p.start()
            processes.append(p)
            time.sleep(1)
            print("Process" + str(m))
        
        for p in processes:
            p.join()

        print(time.time() - timeStart)
    
        # Find best performing process
        processScores = []

        for i in range(0, 3):
            try:
                processScores.append(calc.calculateScore(avg.average(newByDayArr[3], 5), returnDict[i][0][0], i))
            except:
                processScores.append(99999)
        bestProcessID = processScores.index(min(processScores))
        for i in range(len(processScores)):
            # logging.basicConfig(filename='pipline.log',level=logging.DEBUG, datefmt='%Y-%m-%d %H:%M:%S')
            logger.info(COUNTY + ": " +str(trueR0Values[i]) + "," + str(processScores[i]))

        # print("0: " + str(calc.calculateScore(avg.average(newByDayArr[3], 5), returnDict[0][0], 0)))
        # print("1: " + str(calc.calculateScore(avg.average(newByDayArr[3], 5), returnDict[1][0], 0)))
        # print("2: " + str(calc.calculateScore(avg.average(newByDayArr[3], 5), returnDict[2][0], 0)))
        # print("3: " + str(calc.calculateScore(avg.average(newByDayArr[3], 5), returnDict[3][0], 0)))

        # Create list of new R0 values
        # Create array of possible R0 values for each true value
        newR0Values = createR0Values(trueR0Values[bestProcessID], searchRange)

        trueR0Values = newR0Values[0]
        r0ValuesArr = newR0Values[1]

        # Create new file names
        fileArr = []

        for i in range(len(trueR0Values)):
            fileArr.append("(" + CURRENT_DATE + ")" + "minus5R0" + str(trueR0Values[i]))
            f = open(fileArr[i], "w")
            f.close()


        print(trueR0Values)
        print(r0ValuesArr)
        if searchRange > 0.1:
            searchRange -= 0.1
        elif searchRange >= 0.01:
            if searchRange == 0.1:
                searchRange -= 0.05
            else:
                searchRange -= 0.01
        else:
            print("DONE")
            break

        searchRange = round(searchRange, 4)

        returnDict = manager.dict()
        print(fileArr[bestProcessID])
    
    
    
    returnDict = manager.dict()
    # r0ValuesArr = [[1,1]]
    # trueR0Values = 1.01
    # Len of knownData is startingDay
    os.makedirs("FINAL")
    os.chdir("FINAL")

    # r0AverageTest.multiprocessDef(2, r0ValuesArr[1], "(" + CURRENT_DATE + ")" + "FINAL", len(DATA), DATA, 100, POPULATION_SIZE)
    # operateOut = operate.operate("(" + CURRENT_DATE + ")" + "FINAL", returnDict,newByDayArr[3], 0, trueR0Values[1], FIRSTCASEDATE, DATA, True)
    p = multiprocessing.Process(target=r0AverageTest.multiprocessDef, args=(2, r0ValuesArr[1], "(" + CURRENT_DATE + ")" + "FINAL", len(DATA), DATA, 2, POPULATION_SIZE, True, coeffs, None))
    p.start()
    p.join()

    os.chdir('..')
    os.chdir('..')
    os.chdir('..')
    os.chdir('..')

    try:

        if over:
           raise Exception("Override")

        coeffs = rgx.findCoeffs(COUNTY, useCases)
        print(coeffs)
        os.chdir("main/counties(" +datetime.date.today().strftime("%m-%d-%Y")+ ")/" + COUNTY+"/Final")
        os.remove("(" + CURRENT_DATE + ")" + "FINAL")
        print("Here")
        print(os.getcwd())
        logger.info(COUNTY + ": " + "Using coeffs")
        logger.info(COUNTY + ": "  + str(coeffs))

        processes = []
        for m in range(0,3):
            p = multiprocessing.Process(target=r0AverageTest.multiprocessDef, args=(2, r0ValuesArr[1], "(" + CURRENT_DATE + ")" + "FINAL", len(DATA), DATA, 33, POPULATION_SIZE, True, coeffs, FIRSTCASEDATE, False))
            processes.append(p)
            p.start()
        for p in processes:
            p.join()
        p12 = multiprocessing.Process(target=r0AverageTest.multiprocessDef, args=(2, r0ValuesArr[1], "(" + CURRENT_DATE + ")" + "FINAL", len(DATA), DATA, 1, POPULATION_SIZE, True, coeffs, FIRSTCASEDATE, True))
        p12.start()
        p12.join()
        print("ME" + os.getcwd())
        # os.chdir('..')
        # os.chdir('..')
        # os.chdir('..')
        # os.chdir('..')
        # os.chdir("main/counties(" +datetime.date.today().strftime("%m-%d-%Y")+ ")/" + COUNTY+"/Final")
        p11 = multiprocessing.Process(target=operate.operate, args=("(" + CURRENT_DATE + ")" + "FINAL", returnDict,newByDayArr[3], 0, trueR0Values[1], FIRSTCASEDATE, DATA, True, True, COUNTY, CURRENT_DATE, useCases))
        p11.start()
        p11.join()

        os.chdir('..')
        os.chdir('..')
        os.chdir('..')
        os.chdir('..')
    except Exception as e:
        # logging.basicConfig(filename='pipeline.log',level=logging.DEBUG)
        # logging.warning("NO R0 DATA: " + COUNTY)
        # log = logging.getLogger("pipeline.log")
        logger.warning("NO R0 DATA: " + COUNTY)
        logger.warning(e)
        if PUBLISH_RUN:
            print(os.getcwd())
            os.chdir("main/counties(" +datetime.date.today().strftime("%m-%d-%Y")+ ")/" + COUNTY+"/Final")
            os.remove("(" + CURRENT_DATE + ")" + "FINAL")
            print("Here")
            print(os.getcwd())
            processes = []
            for m in range(0,3):
                p = multiprocessing.Process(target=r0AverageTest.multiprocessDef, args=(2, r0ValuesArr[1], "(" + CURRENT_DATE + ")" + "FINAL", len(DATA), DATA, 33, POPULATION_SIZE, True, None, None, False))
                processes.append(p)
                p.start()
            for p in processes:
                p.join()
            p = multiprocessing.Process(target=r0AverageTest.multiprocessDef, args=(2, r0ValuesArr[1], "(" + CURRENT_DATE + ")" + "FINAL", len(DATA), DATA, 1, POPULATION_SIZE, True, None, None))
            p.start()
            p.join()
            os.chdir('..')
            os.chdir('..')
            os.chdir('..')
            os.chdir('..')

        print("LOOK HERE NOW: " + str(os.getcwd()))
        os.chdir("main/counties(" +datetime.date.today().strftime("%m-%d-%Y")+ ")/" + COUNTY+"/Final")
        p = multiprocessing.Process(target=operate.operate, args=("(" + CURRENT_DATE + ")" + "FINAL", returnDict,newByDayArr[3], 0, trueR0Values[1], FIRSTCASEDATE, DATA, True, True, COUNTY, CURRENT_DATE, useCases))
        p.start()
        p.join()

        os.chdir('..')
        os.chdir('..')
        os.chdir('..')
        os.chdir('..')
        

    # pad.parseData("web/data/"+COUNTY+"NewCases.json")
    # pad.parseData("web/data/"+COUNTY+"TotalCases.json")

    # os.chdir('web/data')
    # with open(COUNTY, 'wb') as fp:
    #     pickle.dump(returnDict[0], fp)
    # f.close()


    # print("SCORE: " + str(calc.calculateScore(avg.average(newByDayArr[3], 5), operateOut[0][0], 0)))

def fullPipeline(maxOut, PUBLISH_RUN, state, tierRange=range(0,6), counties=None, over=False):
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    service = build('sheets', 'v4', credentials=creds)
    gSheetsCOVID = gs.COVIDSpreadsheetOperations(service)
    spreadsheet_id = "1w_67qHjxVyYtegiQLapKlk7NIlbUMvsL6Ucak-EL_Eg"
    gc = pg.authorize()    
    sh = gc.open('covidProbabilityModels')
    countyTitles = gSheetsCOVID.getSheets(spreadsheet_id)
    if over == False:
        for x in range(len(countyTitles)+1):
            if x != 0:
                sh.del_worksheet(sh[x])
        # gSheets.update_values(spreadsheet_id, "SantaClara!A1:A", 0,0)

        # counties = gSheetsCOVID.getCountiesState("CA")
        if counties == None:
            counties = ["Santa Clara", "Alameda", "San Francisco", "Sonoma", "Contra Costa", "San Mateo", "Orange", "Santa Barbara", "Los Angeles", "San Diego", "Sacramento"]
            # counties = ["Santa Clara", "Alameda", "Contra Costa", "Orange", "Santa Barbara", "Los Angeles"]
        # counties = ["Alameda"]
        
        for county in counties:
            try:
                countyData = gSheetsCOVID.getCountyData(gSheetsCOVID.fetchCountyId("CA", county), "CA")
                gSheetsCOVID.rewriteSheet(county, "CA", sh, countyData)
                gSheetsCOVID.updateData(county, "CA", sh, spreadsheet_id)
            except Exception as e:
                # logging.basicConfig(filename='pipeline.log',level=logging.DEBUG, datefmt='%Y-%m-%d %H:%M:%S')
                logger.info("Exception in get county data: " + county + ": " + str(e))
        
        # Add CA
        gSheetsCOVID.rewriteSheet("CA", "CA", sh, gSheetsCOVID.fetchStateData("CA"))
        gSheetsCOVID.updateStateData("CA", sh, spreadsheet_id)
    
    countyTitles = gSheetsCOVID.getSheets(spreadsheet_id)

    mapCounties = {}

    for i in countyTitles:
        mapCounties[i] = mf.checkForFileCompatibility("main/R0/"+i+"R0")

    # for filename in countyTitles:    
    #     gSheetsCOVID.createFile(spreadsheet_id, "./main/Data/"+filename+".txt", filename, maxOut)

    for l in tierRange:
        for filename in countyTitles:   
            if (l >= 4 and l < 8) or l == 0:
                useCases = False
            else:
                useCases = True 
            try:
                gSheetsCOVID.createFile(spreadsheet_id, "./main/Data/"+filename+".txt", filename, state, maxOut, useCases)
            except Exception as e:
                # logging.basicConfig(filename='pipeline.log',level=logging.info, datefmt='%Y-%m-%d %H:%M:%S')
                logger.info("Exception in get county data: " + filename + ": " + str(e))
                continue
            parameters = pad.pullParameters("./main/Data/" + filename+".txt", l)
            if parameters != None:
                try:
                    if over:
                        coeffs = None
                        raise Exception("Override")
                    coeffs = rgx.findCoeffs(filename, useCases)
                except:
                    coeffs = None
                print(filename)

                
                    
                p1 = multiprocessing.Process(target=pipeline, args=(parameters["START_DATE"], parameters["COUNTY_NAME"], parameters["FIRST_CASE_DATE"], "Data/"+filename+".txt", parameters["POPULATION_SIZE"], coeffs, PUBLISH_RUN, useCases, over))
                p1.start()
                p1.join()
                notify.notify("VID Model", "Completed "+ filename)
                # break # REMOVE
                
    return mapCounties
    # pipeline("4-18-20", "LosAngeles", "3-12-20", "Data/LosAngeles.txt", 10040000)
    # pipeline("4-18-20", "Orange", "3-02-20", "Data/Orange.txt", 3176000)
    # pipeline("4-17-20", "SanMateo", "3-09-20", "Data/SanMateo.txt", 105025)
    # pipeline("4-17-20", "SantaClara", "3-01-20", "Data/SantaClara.txt", 1928000)
    # pipeline("4-18-20", "SanFrancisco", "3-05-20", "Data/SanFrancisco.txt", 883305)
    # pipeline("4-17-20", "California", "3-04-20", "Data/California.txt", 39510000) 


def redoPipeline(county, loc, useCases=True):
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    service = build('sheets', 'v4', credentials=creds)
    gSheetsCOVID = gs.COVIDSpreadsheetOperations(service)
    spreadsheet_id = "1w_67qHjxVyYtegiQLapKlk7NIlbUMvsL6Ucak-EL_Eg"
    gc = pg.authorize()    
    sh = gc.open('covidProbabilityModels')

    countiesTODO = {county: 1}
    countiesList = list(countiesTODO.keys())

    worksheet = sh.worksheet_by_title(county)
    worksheet.update_col(7, [8], row_offset=2)
    # iterRange = gSheetsCOVID.getLastFive(countiesList[i], "CA", spreadsheet_id, countiesTODO[countiesList[i]])
    
    fullPipeline(str(loc), False, "CA", range(8,9), over=True)
    worksheet.update_col(7, [1], row_offset=2)

    try:
        # filename = county.replace("CA", "")
        # filename = re.sub(r"(\w)([A-Z])", r"\1 \2", filename)
        filename = county
        gSheetsCOVID.createFile(spreadsheet_id, "./main/Data/"+filename+".txt", filename, "CA", '', useCases)
    except Exception as e:
        # logging.basicConfig(filename='pipeline.log',level=logging.info, datefmt='%Y-%m-%d %H:%M:%S')
        logger.info("Exception in get county data: " + county + ": " + str(e))
            
            

if __name__ == "__main__":

    # for i in range(47,53):
    #     fullPipeline(str(i))
    #SCC - 44,50 -10
    #LA - 37,43 -11
    #CA-44,50 -12
    # if os.path.exists('token.pickle'):
    #     with open('token.pickle', 'rb') as token:
    #         creds = pickle.load(token)
    # service = build('sheets', 'v4', credentials=creds)
    # gSheetsCOVID = gs.COVIDSpreadsheetOperations(service)
    # spreadsheet_id = "1w_67qHjxVyYtegiQLapKlk7NIlbUMvsL6Ucak-EL_Eg"
    # gc = pg.authorize()    
    # sh = gc.open('covidProbabilityModels')

    # countiesTODO = {"CASanFrancisco": 1}
    # countiesList = list(countiesTODO.keys())

    # worksheet = sh.worksheet_by_title("CASanFrancisco")
    # worksheet.update_col(7, [8], row_offset=2)
    # # iterRange = gSheetsCOVID.getLastFive(countiesList[i], "CA", spreadsheet_id, countiesTODO[countiesList[i]])
    
    # fullPipeline(str(80), False, "CA", range(8,9), over=True)
    # worksheet.update_col(7, [1], row_offset=2)
            



    #for i in range(41,42):
    # counties = ["Los Angeles"]
    # for county in counties:
    #     fullPipeline('80', False, "CA", counties=[county])
    #     fullPipeline('85', False, "CA", counties=[county])
    #     fullPipeline('89', False, "CA", counties=[county])
        
    # fullPipeline('')
    fullPipeline('', True, "CA")
    notify.notify("VID Model", "Completed main")
    
    # returnDict = {}
    # DATA = list(map(int,list(rf.readDataFile('main/Data/LosAngeles.txt'))))
    # r0AverageTest.multiprocessDef(2, [[0.97,1],[1,2]], "(" + "4-14-20" + ")" + "FINAL", len(DATA), DATA, 100, 200000)
    # operateOut = operate.operate("(" + "4-14-20" + ")" + "FINAL", returnDict,DATA, 0, 1.03, "3-12-20", DATA, True)
