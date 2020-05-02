# Importing the libraries
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
import readFile as rf
import datetime
import scipy
import average as avg
import pipeline


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

def tail(f, window=20):
    """
    Returns the last `window` lines of file `f` as a list.
    f - a byte file-like object
    """
    if window == 0:
        return []
    BUFSIZ = 1024
    f.seek(0, 2)
    bytes = f.tell()
    size = window + 1
    block = -1
    data = []
    while size > 0 and bytes > 0:
        if bytes - BUFSIZ > 0:
            # Seek back one whole BUFSIZ
            f.seek(block * BUFSIZ, 2)
            # read BUFFER
            data.insert(0, f.read(BUFSIZ))
        else:
            # file too small, start from begining
            f.seek(0, 0)
            # only read what was not read
            data.insert(0, f.read(bytes))
        linesFound = data[0].count('\n')
        size -= linesFound
        bytes -= BUFSIZ
        block -= 1
    return ''.join(data).splitlines()[-window:]


def oldfindCoeffs(COUNTY):
    # Importing the dataset
    # with open("main/R0/" + COUNTY + "R0",'r+') as file:
    #     for line in file:
    #         if not line.isspace():
    #             file.write(line)
    count = 0
    with open("main/R0/" + COUNTY + "R0", 'r') as f:
        for line in f:
            count += 1
    useData = tail(open("main/R0/" + COUNTY + "R0", "r"), window=count-2)

    xValues = []
    yValues = []
    for elem in useData:
        x, y = elem.split(",")
        x = x.strip(" ")
        y = y.strip(" ")
        xValues.append(x)
        yValues.append(y)

    yValues = [float(i) for i in yValues]
    xValues = [datetime.strptime(i, "%m-%d-%Y") for i in xValues]
    xValues = [datetime.toordinal(i) for i in xValues]

    mymodel = np.poly1d(np.polyfit(xValues, yValues, 4))

    # for coeff in mymodel.coeffs:
    #     coeff *= 2
    if mymodel.coeffs[0] > 0:
        # mymodel.coeffs[0] = 0
        mymodel = np.poly1d(np.polyfit(xValues, yValues, 3))
        if mymodel.coeffs[0] > 0:
            mymodel = np.poly1d(np.polyfit(xValues, yValues, 1))
            if mymodel.coeffs[0] > 0:
                mymodel = np.poly1d(np.polyfit(xValues, yValues, 4))
                if mymodel.coeffs[0] > 0:
                    mymodel.coeffs[0] = 0
                    if mymodel.coeffs[1] > 0:
                        for i in range(len(mymodel.coeffs)):
                            mymodel.coeffs[i] = mymodel.coeffs[i] * -1

    return mymodel.coeffs

def findAnotherCoeffs(COUNTY, useCases=True):
    # Count data points in R0 file for County
    count = 0
    with open("main/R0/" + COUNTY + "R0", 'r') as f:
        for line in f:
            count += 1
    useData = tail(open("main/R0/" + COUNTY + "R0", "r"), window=count-2)    

    # Get past CASE data from County file
    caseData = rf.readDataFile("main/Data/" + COUNTY + ".txt")
    startIndex = datetime.datetime.strptime("01-22-2020", "%m-%d-%Y").toordinal()

    # Loop through CASE data and search for first case and recreate array
    newCaseData = []
    first = True
    for i in range(len(caseData)):
        if caseData[i] != 0 and first == True:
            newCaseData.append(caseData[i])
            newStartIndex = i + startIndex
            first = False
            end = i
        elif first == False:
            newCaseData.append(caseData[i])
            
    
    # Avg of newCasesData
    newCasesData = avg.hullMovingAverage(newCaseData, 5)

    # Find first set of 'defining' case in Avg...
    first = True
    for i in range(len(caseData)):
        if newCasesData[i] >= 5 and first == True:        
            nextEnd = i
            break
    
    # Create x values for data 
    xValues = []
    for i in range(len(caseData)):
        if (startIndex + i) >= newStartIndex:
            xValues.append(startIndex+i)
    
    # Perform regression on known data (Quadratic)
    quadraticCaseModel = np.poly1d(np.polyfit(xValues, newCaseData, 2))
    print(quadraticCaseModel.coeffs)

    # Search R0 file 
    dates = []
    R0Values = []
    for elem in useData:
        x, y = elem.split(",")
        x = x.strip(" ")
        y = y.strip(" ")
        if float(y) == 0:
            continue
        dates.append(x)
        R0Values.append(float(y))
    
    # Find peak cases and associate with R0 and quad regx
    maxLoc = 0

    for i in range(len(newCasesData)):
        if newCasesData[i] > newCasesData[maxLoc]:
            maxLoc = i

    maxDate = datetime.datetime(2020, 1, 22) + datetime.timedelta(days=(end+(maxLoc)))

    # Check if data exists for highest day
    dateExists = False
    logger.info("Looking for: " + maxDate.strftime("%m-%d-%Y"))
    for i in range(len(dates)):
        if maxDate.strftime("%m-%d-%Y") == dates[i]:
            dateExists = True
            maxR0 = R0Values[i]
            break
    
    if not dateExists:
        logger.critical(COUNTY + ":Run r0 for " + str(maxDate.toordinal()-737444))
        pipeline.redoPipeline(COUNTY, str(maxDate.toordinal()-737444), useCases)
        # maxDate = datetime.datetime(2020,4,4)
        for i in range(len(dates)):
            if maxDate.strftime("%m-%d-%Y") == dates[i]:
                dateExists = True
                maxR0 = R0Values[i]
                break
    
        

    

    maxR0 = max(R0Values)  

    apexX = (quadraticCaseModel.roots[0] + quadraticCaseModel.roots[1]) / 2
    apexY = (quadraticCaseModel.coeffs[0] * (apexX ** 2)) + (quadraticCaseModel.coeffs[1] * apexX )+ quadraticCaseModel.coeffs[2] 

    linX = (apexY, 0)
    linY = (maxR0, 0)
    
    logger.info(COUNTY + ": " + "Apex: " + str(apexY) + ", maxR0:" + str(maxR0))

    linearR0Model = np.poly1d(np.polyfit(linX, linY, 1))
    
    newCaseDataFromRegression = [quadraticCaseModel.coeffs[0] * i ** 2 + quadraticCaseModel.coeffs[1] * i + quadraticCaseModel.coeffs[2] for i in xValues]
    
    R0DataEstimates = [linearR0Model.coeffs[0] * i + linearR0Model.coeffs[1] for i in newCaseDataFromRegression]
    logger.info(COUNTY + ": " + "R0DataEstimates: " + str(R0DataEstimates))
    # Create R0 Model
    quadraticR0Model = np.poly1d(np.polyfit(xValues, R0DataEstimates, 2))
    logger.info("XVALUES: " + str(xValues))

    returnCoeffs = []
    for i in range(len(quadraticR0Model.coeffs)):
        returnCoeffs.append(quadraticR0Model.coeffs[i] * 2)
    if COUNTY == "CACA":
        with open("main/R0Equations/CA", "w") as f:
            f.write(str(returnCoeffs).replace("[", "").replace("]", ""))
            
    return returnCoeffs


def findCoeffs(COUNTY, useCases=True):
    # Count data points in R0 file for County
    count = 0
    with open("main/R0/" + COUNTY + "R0", 'r') as f:
        for line in f:
            count += 1
    useData = tail(open("main/R0/" + COUNTY + "R0", "r"), window=count-2)    

    # Get past CASE data from County file
    caseData = rf.readDataFile("main/Data/" + COUNTY + ".txt")
    startIndex = datetime.datetime.strptime("01-22-2020", "%m-%d-%Y").toordinal()

    # Loop through CASE data and search for first case and recreate array
    newCaseData = []
    first = True
    for i in range(len(caseData)):
        if caseData[i] == 0 and first == True:
            newCaseData.append(caseData[i])
            newStartIndex = i + startIndex
            first = False
            end = i
        elif first == False:
            newCaseData.append(caseData[i])
            
    
    # Avg of newCasesData
    newCasesData = avg.hullMovingAverage(newCaseData, 5)

    # Find first set of 'defining' case in Avg...
    first = True
    for i in range(len(caseData)):
        if newCasesData[i] >= 10 and first == True:        
            nextEnd = i
            break
    
    # Create x values for data 
    xValues = []
    for i in range(len(caseData)):
        if (startIndex + i) >= newStartIndex:
            xValues.append(startIndex+i)
    
    # Perform regression on known data (Quadratic) until coeff[0] is negative (negative slope)
    backData = -10
    while True:
        quadraticCaseModel = np.poly1d(np.polyfit(xValues[backData:], newCaseData[backData:], 2))
        if quadraticCaseModel.coeffs[0] < -0.1:
            break
        backData -= 1
    print(quadraticCaseModel.coeffs)

    # Search R0 file 
    dates = []
    R0Values = []
    for elem in useData:
        x, y = elem.split(",")
        x = x.strip(" ")
        y = y.strip(" ")
        if float(y) == 0:
            continue
        dates.append(x)
        R0Values.append(float(y))
    
    # Find peak cases and associate with R0 and quad regx
    maxLoc = 0

    for i in range(len(newCasesData)):
        if newCasesData[i] > newCasesData[maxLoc]:
            maxLoc = i

    maxDate = datetime.datetime(2020, 1, 22) + datetime.timedelta(days=(end+(maxLoc)))

    # Check if data exists for highest day
    dateExists = False
    logger.info("Looking for: " + maxDate.strftime("%m-%d-%Y"))
    for i in range(len(dates)):
        if maxDate.strftime("%m-%d-%Y") == dates[i]:
            dateExists = True
            maxR0 = R0Values[i]
            break
    
    if not dateExists:
        logger.critical(COUNTY + ":Run r0 for " + str(maxDate.toordinal()-737444))
        pipeline.redoPipeline(COUNTY, str(maxDate.toordinal()-737444), useCases)
        # maxDate = datetime.datetime(2020,4,4)
        for i in range(len(dates)):
            if maxDate.strftime("%m-%d-%Y") == dates[i]:
                dateExists = True
                maxR0 = R0Values[i]
                break
    
        

    

    maxR0 = max(R0Values)  

    apexX = (quadraticCaseModel.roots[0] + quadraticCaseModel.roots[1]) / 2
    apexY = (quadraticCaseModel.coeffs[0] * (apexX ** 2)) + (quadraticCaseModel.coeffs[1] * apexX )+ quadraticCaseModel.coeffs[2] 

    linX = (apexX, quadraticCaseModel.roots[0], datetime.datetime.strptime(dates[-1], "%m-%d-%Y").toordinal())
    linY = (maxR0, 0, R0Values[-1])
    
    

    linearR0Model = np.poly1d(np.polyfit(linX, linY, 1))
    
    
    returnCoeffs = []
    for i in range(len(linearR0Model.coeffs)):
        returnCoeffs.append(linearR0Model.coeffs[i])
    if COUNTY == "CACA":
        with open("main/R0Equations/CA", "w") as f:
            f.write(str(returnCoeffs).replace("[", "").replace("]", ""))
            
    return returnCoeffs




def findR0(coeffs, b=1):
    # return round(coeffs[0]*b**2 + coeffs[1]*b + coeffs[2], 2)
    sumx = 0
    x = len(coeffs) - 1
    for coeef in coeffs:
        sumx += coeef * b ** (x)
        x -= 1
    return round(sumx, 2)


if __name__ == "__main__":
    coeffs = findCoeffs("CACA")
    # coeffs = findCoeffs("CASonoma")
    r0 = findR0(coeffs, 737546)
