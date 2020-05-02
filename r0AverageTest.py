#! /usr/local/bin/python3
import math
import multiprocessing
import random
import time
from datetime import datetime, timedelta
from itertools import groupby

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pandas import DataFrame, Series
from scipy.ndimage.filters import uniform_filter1d

import average as avg
import operate
import regressions as rgx
import timing
import os
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



def trueRandom(lower, upper):
    systemRandom = random.SystemRandom()
    return systemRandom.uniform(lower, upper)

def trueRandomInt(lower, upper):
    systemRandom = random.SystemRandom()
    return systemRandom.randint(lower, upper)
# Day doesn't need to be 100, just len(knownData)
def model(r0In, r0ArrIn, file, knownData, startingDay, totalPopulation, origin, newByDay, final=False, coeffs=None, dateOfFirstCase="03-01-2020"):
    #Init list and time

    '''
    - [0] --> wellness status 
        - 0 --> susceptible
        - 1 --> sick
        - 99 --> immune
    - [1] --> illness start date
    - [2] --> illness end date
    - [3] --> number to infect
    - [4] --> survivability
    - [5] --> who gave it to them
    - [6] --> id
    - [7] --> day when first person is infected by infecter
    '''

    
    '''
    range of infectivity
    asymptomatic r0
    symptomatic r0
    likelyhood of being asymptomatic
    age and symptoms
    inc period --> age
    ill peiod --> age
    2.2 reported avg 
    1:25%
    2:50%
    3:25%
    '''
    illPeriod = 7
    incPeriod = 5 #5.1
    # totalPopulation = 206874

    population = np.array(knownData)

    r0 = r0In
    r0Arr = r0ArrIn
    if dateOfFirstCase != None and len(coeffs) != 0:
        ordinalStartDay = datetime.strptime(dateOfFirstCase, "%m-%d-%Y")
        ordinalStartDay += timedelta(days=startingDay)
        ordinalStartDay = datetime.toordinal(ordinalStartDay)
        oldOrdinal = ordinalStartDay


    populationIntermediate = np.zeros([len(knownData),4], dtype = int)
    if len(populationIntermediate) == 0:
        populationIntermediate = [[0,0,0,0]]
    if len(population) == 0:
        population = [[0,0,0,0]]
    population = np.concatenate((population, populationIntermediate))
    # print("Made a pop")
    time = []
    path = os.getcwd()
    path = path.split("/")
    logger.info(path)
    if path[-1] == "FINAL":
        os.chdir("..")
        os.chdir("..")
        os.chdir("..")
        os.chdir("..")
        coeffsForState = getStateR0Eq("CA")
        os.chdir(path[-4] + "/" + path[-3] + "/" + path[-2] + "/" + path[-1])
        logger.info(os.getcwd())
    else:
        os.chdir("..")
        os.chdir("..")
        os.chdir("..")
        coeffsForState = getStateR0Eq("CA")
        os.chdir(path[-3] + "/" + path[-2] + "/" + path[-1])

    #Prep sys
    f = open(file, "a")
    # print(len(population))
    # print(population[9996])

    # for i in range(0, len(population)):
    #     # print(i)
    #     population[i][6] = i

    # print(population)
    # print(time)
    #Add the index case, 1 --> sick
    
    day = startingDay
    if len(knownData) == 0:
        population[0][0] = 1
        population[0][1] = day + incPeriod
        population[0][2] = day + illPeriod + incPeriod
        population[0][3] = r0
        # population[0][5] = -1

    # print(population)
    # print("\n")

    def infect(infectingIndividual, day, last, population):
        simulatedDay = day
        infectivity = True
        j = last
        while infectingIndividual[3] > 0 and infectivity == True:
            randArr = np.random.uniform(size=3)
            denom = math.sqrt(abs(infectingIndividual[2] - simulatedDay)**1.5 + 1)
            if denom <= 0:
                denom = 1
            check = infectingIndividual[3]/denom
            # print("RAND: " + str(rand))
            # print("CHECK: " + str(check))
            j = last 
            if randArr[0] <= check:
                if randArr[1] <= (j)/totalPopulation:
                    infectingIndividual[3] -= 1
                else:
                    while True:
                        # if j >= len(population)-1:
                        #     # raise Exception("Population exceeded")
                        #     infectivity = False
                        #     break
                        try:
                            if population[j][0] == 0:
                                # print("Entered second if with " + str(j))
                                population[j][0] = 1
                                population[j][1] = simulatedDay + incPeriod
                                population[j][2] = simulatedDay + illPeriod + incPeriod
                                keyId = 0
                                while True:
                                    if randArr[2] < r0Arr[keyId][0]:
                                        population[j][3] = r0Arr[keyId][1]
                                        break
                                    keyId += 1
                                    
                                # population[j][5] = infectingIndividual[6]
                                infectingIndividual[3] -= 1
                                break
                            else:
                                j+= 1
                        except:
                            if len(population) < totalPopulation:
                                for i in range(infectingIndividual[3] + 1):
                                    arr2 = [[0,0,0,0]]
                                    population = np.concatenate((population, arr2), axis = 0)
                            # else:
                            #     infectivity = False
                            #     break
            simulatedDay += 1
        return j
        return last
            # print("\n")

    def changeIllnessStatus(individual, day):
        if individual[2] < day and individual[2] != 0:
            individual[0] = 99

    '''
    while day < 3:
        for i in range(0, len(population)):
            changeIllnessStatus(population[i], day) 
        
        for i in range(0, i):
            if population[i][0] == 1:
                infect(population[i], day)
                
        
        # print("\n")
        # print(population)
        day += 1
    '''
    '''
    for i in range(0, len(population)):
        changeIllnessStatus(population[i], day) 
    '''
    for i in range(len(population)):
        if population[i][3] != 0:
            break
    newJ = infect(population[i], day, i, population)
    day = population[i][1]
    # if population[1][1] <= day and population[1][1] != 0 and population[1][3] >= 0:
    #     infect(population[1], day)
    # if population[2][1] <= day and population[2][1] != 0 and population[2][3] >= 0:
    #     infect(population[2], day)
    x = 0
    lastInI = 0
    continueCalc = True
    dayEnd = startingDay + 11
    if final:
        dayEnd = startingDay + 50
    backlen = 0
    r0BadCount = 0
    while day < dayEnd and continueCalc:
        # print(day)
        # x = 0
        # print(population)
        # population.sort(key=lambda z: z[1])
        population = population[population[:,1].argsort()]
        
        population = np.flip(population, axis=0)
        iterateMax = np.nonzero(population[:,1] <= day + 13)
        iterateMin = np.nonzero(population[:,1] >= day - 13)
        iterate = np.intersect1d(iterateMax, iterateMin, assume_unique=True)
        

        while True:
            try:
                if population[x][1] == 0:
                    # print(population[x][1])
                    break
                x+=1
            except IndexError:
                if len(population) < totalPopulation:
                    arr2 = [[0,0,0,0]]
                    population = np.concatenate((population, arr2), axis = 0)
                else:
                    continueCalc = False
                    break
        # print(population)

        # print("DAY" + str(day))
        oldJ=0
        # for b in range(len(population)):
        #     if population[i][3] != 0:
        #         break
        # print(population)
        
        try:
            add = round((np.count_nonzero(population==(day-1), axis=0)[1])*r0)
            # backlen = len(iterate)
            if np.count_nonzero(population==0, axis=0)[1] < add and len(population) < totalPopulation:
                populationIntermediate = np.zeros([int(add),4], dtype = int)
                population = np.concatenate((population, populationIntermediate))
            continueCalc = False
            for i in range(iterate[0], iterate[len(iterate)-1]):
            # for i in range(0, len(population)):
                # print(population[i])
                if population[i][1] <= day and population[i][1] != 0 and population[i][3] > 0:
                    oldJ = newJ
                    newJ = infect(population[i], day, newJ, population)
                    lastInI = i
                    continueCalc = True
                    # if newJ == oldJ:
                    #     newJ += 1
           
            
            day += 1
            if day > dayEnd:
                break
            logger.warning("BEFORE IF")
            if dateOfFirstCase != None and len(coeffs) != 0:

                # if ordinalStartDay - oldOrdinal > 5 and coeffs[0] > 0:
                #     coeffs[0] = -1*coeffs[0]
                    
                #     yInt = coeffs[1]
                #     coeffs[1] = yInt - (coeffs[0]*(ordinalStartDay*2))
                # if ordinalStartDay - oldOrdinal > 7:
                #         coeffs[0] = 0
                #         coeffs[1] = 0
                #         r0 = 0
                logger.warning("ENTERED IF DATEOFFIRSTCASE == NONE STATEMENT")
                logger.info(str(os.getcwd()))
                pathNow = os.getcwd()
                pathNow = pathNow.split("/")

                state = False
                for part in pathNow:
                    if part == "CACA":
                        state = True
                        break
            
                if state:
                    logger.warning("IN CACA")
                    logger.critical(str(coeffsForState))
                    logger.critical(str(ordinalStartDay))
                    coeffsForState = [float(coeffInState) for coeffInState in coeffsForState]
                    r0 = stateR0Equation(coeffsForState, ordinalStartDay) 
                else:
                    r0 = rgx.findR0(coeffs, ordinalStartDay)
                logger.warning("GOT R0")
                
                if r0 < 0 or isinstance(r0, complex):
                    r0 = 0
                elif r0 > 2.2:
                    r0BadCount += 1
                    r0 = 2.2
                    
                    
                    
                ordinalStartDay += 1
                percentages = math.modf(r0)
                r0Arr = [[round(1-percentages[0],2), round(percentages[1],2)], [1, round(percentages[1] + 1, 2)]]
        except:
            pass

            
            
        # print(newJ)
        # print(population)
        # continueCalc = False
        # for i in range(len(population)):
        #     if population[i][2] >= day and population[i][3] != 0:
        #         continueCalc = False
        #     else:
        #         continueCalc = True
        #         break
        # if continueCalc:
        
        
    



    # newCasesByDate = []

    # for i in range(0, len(population)):
    #     newCasesByDate.append(population[i][1])
    # print("EXITED")
    
    newCasesByDate = population[:,1]
    logger.info(file + ": "+ str(r0BadCount))

    newCasesByDate = sorted(newCasesByDate)
    newCasesByDate = list(filter(lambda a: a != 0, newCasesByDate))
    # print(newCasesByDate)
    minimumX = newCasesByDate[0]
    maximumX = newCasesByDate[len(newCasesByDate) - 1]

    # print("Infecting done")


    graphingInfoY = [len(list(group)) for key, group in groupby(newCasesByDate)]
    locs = np.where(origin == 0)[0]
    for i in range(len(locs)):
        graphingInfoY.insert(locs[i], 0)
    
    newByDay = np.array(avg.hullMovingAverage(newByDay, 5))
    ii = np.where(newByDay == 0)[0]
    for i in ii:

        graphingInfoY.insert(i, 0)

    # max = 0
    # for i in range(40):
    #     if graphingInfoY[i] > graphingInfoY[max]:
    #         max = i
    # graphingInfoY.pop(max)
    # print(len(graphingInfoY))
    time = [*range(0,len(graphingInfoY)+1)]
    # print(len(time))

    '''
    for i in range(0, len(graphingInfoY)):
        print("(" + str(i) + "," + str(graphingInfoY[i]) + ")")
    '''
    # print("SUM: " + str(sum(graphingInfoY)))
    y2 = []
    sumArr = 0
    for i in range(0, len(graphingInfoY)):
        sumArr = graphingInfoY[i] + sumArr
        y2.append(sumArr) 
    
    # print("Y2: " + str(y2))

    def plotBarHorizontal():
        data = graphingInfoY
        plt.bar(time, data)
        plt.show()
    
    def lineGraph():
        x = time
        y = y2
        plt.plot(x, y)
        plt.show()  

    def logInfo():
        f.write("\n")
        f.write("\nINFO: Total Population: " + str(totalPopulation))
        f.write("\nINFO: R0: " + str(r0))
        f.write("\nINFO: Incubation Period: " + str(incPeriod))
        f.write("\nINFO: Illness Period: " + str(illPeriod))
        f.write("\nX:" + str(time))
        
        f.write("\nYNEW:" + str(graphingInfoY))

        f.write("\nYTOT: " + str(y2))
        f.close()

    # print(graphingInfoY)

    logInfo()
    
    #plotBarHorizontal()
    #lineGraph()


''' 

if __name__ == "__main__": 

    p1 = multiprocessing.Process(target=model, args=()) 
    p2 = multiprocessing.Process(target=model, args=()) 


    # starting process 1 
    p1.start() 

    # starting process 2 
    p2.start() 


    # wait until process 1 is finished 
    p1.join() 
    # wait until process 2 is finished 
    p2.join() 

'''


def generalInfect(infectingIndividual, day, last, populationSize, incPeriod, illPeriod, r0Arr):
    simulatedDay = day
    infectivity = True
    while infectingIndividual[3] > 0:
        randArr = np.random.uniform(size=2)
        denom = math.sqrt(abs(infectingIndividual[2] - simulatedDay)**1.5 + 1)
        if denom <= 0:
            denom = 1
        check = infectingIndividual[3]/denom
        
        # print("RAND: " + str(rand))
        # print("CHECK: " + str(check))
        j = last 
        if randArr[0] <= check and np.random.uniform(size=1)[0] <= (j)/populationSize:
            
            infectingIndividual[3] -= 1
            return [infectingIndividual, [0,0,0,0], j]
        else:
            while True:
                if j >= populationSize-1:
                    # raise Exception("Population exceeded")
                    infectivity = False
                    break
                else:
                    # print("Entered second if with " + str(j))
                    one = 1
                    two = simulatedDay + incPeriod
                    three = simulatedDay + illPeriod + incPeriod
                    keyId = 0
                    while True:
                        if randArr[1] < r0Arr[keyId][0]:
                            four = r0Arr[keyId][1]
                            break
                        keyId += 1
                        
                    # five = infectingIndividual[6]
                    infectingIndividual[3] -= 1
                    return [infectingIndividual, [one, two, three, four], j]
                    break
                j += 1
        simulatedDay += 1



def createCases(popSize,incPeriod,illPeriod,r0Arr, startingDay, newByDay):
    # newByDay = [1,1,3,2,2,3,6,4,8,5,6,2,3,18,13,12,23,24,17,20,14,7,67,39,19,73,84,83,32,17,55,202,42,66,63,75,54,59,17,61,95,62,42]
    newByDay = np.array(avg.hullMovingAverage(newByDay, 5))
    newByDay = [ int(x) for x in newByDay ]
    otherNewByDay = newByDay
    # N = 5
    # newByDay = np.array(newByDay)
    # newByDay = np.concatenate([x[0],x[1],x[2],x[3],np.round(running_mean(x, N))])
    # print(sum(newByDay))
    knownDataIn = []
    # r0Arr = [[0.15, 1], [0.4, 3], [0.75,2], [0.9,4], [1,0]]
    newByDay = list(newByDay)
    for i in range(len(newByDay)):
        for j in range(int(newByDay[i])):
            rand3 = np.random.uniform(size=1)[0]
            keyId = 0
            while True:
                if rand3 < r0Arr[keyId][0]:
                    x = r0Arr[keyId][1]
                    break
                keyId += 1
                if keyId >= len(r0Arr):
                    x=0
                    break
            knownDataIn.append([1,i+1,i+13,x])
    # print(knownDataIn)

    startDay = len(newByDay) - 5 # Maybe reduce this?? --> 7 --> 5
    newSum = 0
    for i in range(12):
        # print(newByDay[-(i+1)])
        # print(round(((i+1)/12)*newByDay[-(i+1)]))
        newSum = newSum + newByDay[-i]

    originalSum = sum(newByDay)
    index = sum(newByDay) - newSum
    # print(knownDataIn[index])

    stop = len(knownDataIn)
    '''Change Day? Change Known? Come here, increase 44'''
    for i in range(int(index),int(stop-1)):
        add = knownDataIn[i][2] - startingDay
        if add <= 0:
            add = 0
            randDay = startingDay
        else:
            randDay = np.random.randint(low=startingDay, high=startingDay+add)

        rand4 = np.random.uniform(size=1)[0]
        output = None
        # Removed for LA, add if needed
        check = add/12 #11 or 12? 11 dropped peak early
        if check > 1:
            check = 1

        if rand4 < check:

            output = generalInfect(knownDataIn[i],randDay,len(knownDataIn) + i,popSize,incPeriod,illPeriod,r0Arr)
        # print(output)
        if output != None:
            # print(knownDataIn[i])
            # print(output[0])
            knownDataIn[i] = output[0]
            knownDataIn.append(output[1])


    # print(knownDataIn[2000])
    for i in range(int(originalSum)):
        knownDataIn[i][3] = 0
    return (knownDataIn, otherNewByDay)


def multiprocessDef(r0, r0Arr, file, startingDay, newByDay, iterations, populationSize, final=False, coeffs=None, dateOfFirstCase=1, addEnd = True):

    for i in range(0,iterations):
        output = createCases(populationSize,5,12,r0Arr, startingDay, newByDay)
        knownDataIn = np.array(output[0])
        model(r0, r0Arr, file, knownDataIn, startingDay, populationSize, output[1], newByDay, final, coeffs, dateOfFirstCase)
    if addEnd:
        f = open(file, "a")
        f.write("\n\nEND")


def getStateR0Eq(state):
    with open("main/R0Equations/" + state) as f:
        currentLine = f.readline().split(",")
        logger.info("CURRENT LINE: " + str(currentLine))
        return currentLine

def stateR0Equation(coeffsForState, ordinalStartDay):
    while True:
        try:
            coeffsForState.remove('')
        except:
            break
    sumx = 0
    x = len(coeffsForState) - 1
    for coeef in coeffsForState:
        sumx += coeef * ordinalStartDay ** (x)
        x -= 1
    return round(sumx, 2)
    # for coeefForState in coeffsForState:
    #     sumx += coeefForState * (ordinalStartDay ** (x))
    #     x -= 1
    return round(sumx, 2)

if __name__ == "__main__": 
    '''
    - [0] --> wellness status 
        - 0 --> susceptible
        - 1 --> sick
        - 99 --> immune
    - [1] --> illness start date
    - [2] --> illness end date
    - [3] --> number to infect
    - [4] --> survivability
    - [5] --> who gave it to them
    - [6] --> id
    '''

    '''
    data = [1,1,3,2,2,3,6,4,8,5,6,2,3,18,13,12,23,24,17,20,14,7,67,39,19,73,84,83,32,17,55,202,42,66,63,75,54,59,17,61,95,62,42,82,55,45]
    
    
    # multiprocessDef(2,[[0.15, 1], [0.4, 3], [0.75,2], [0.9,4], [1,0]], "truePopulationWithData4-10xe", 43, data, 2)
    multiprocessDef(2, [[0.9, 1],[1, 2]], "truePopulationWithData4-10xf", 36, [1,1,3,2,2,3,6,4,8,5,6,2,3,18,13,12,23,24,17,20,14,7,67,39,19,73,84,83,32,17,55,202,42,66,63,75,54,59,17,61,95], 5, 20000)
    dictionary = {}
    operate.operate("truePopulationWithData4-10xf", dictionary, data, 0, 9.99, "3-01-20",data, county="TestCounty")

    '''
    print(stateR0Equation([-0.03531367551826282, 52086.13399425061, -19206195007.857452], 737546))

    #print("ALL DONE")
