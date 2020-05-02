#! /usr/local/bin/python3
import random
from itertools import groupby

import numpy as np
import pandas as pd
from pandas import Series, DataFrame
import matplotlib.pyplot as plt

import multiprocessing

import timing

def trueRandom(lower, upper):
    systemRandom = random.SystemRandom()
    return systemRandom.uniform(lower, upper)

def trueRandomInt(lower, upper):
    systemRandom = random.SystemRandom()
    return systemRandom.randint(1,3)

def model(r0, r0Arr, file, knownData):
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
    '''


    r0 = r0
    
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
    illPeriod = 12
    incPeriod = 5 #5.1
    totalPopulation = 2000000

    population = knownData

    

    populationIntermediate = [[0 for i in range(7)] for j in range(totalPopulation-len(knownData))] 
    population = population + populationIntermediate
    # print("Made a pop")
    time = []

    #Prep sys
    f = open(file, "a")
    # print(len(population))
    # print(population[9996])

    for i in range(0, len(population)):
        # print(i)
        population[i][6] = i

    # print(population)
    # print(time)
    #Add the index case, 1 --> sick
    
    day = 1
    if len(knownData) == 0:
        population[0][0] = 1
        population[0][1] = day + incPeriod
        population[0][2] = day + illPeriod + incPeriod
        population[0][3] = r0
        population[0][5] = -1

    # print(population)
    # print("\n")

    def infect(infectingIndividual, day, last):
        simulatedDay = day
        infectivity = True
        while infectingIndividual[3] > 0 and infectivity == True:
            rand = trueRandom(0, 1)
            denom = (infectingIndividual[2] - simulatedDay + 1)
            if denom <= 0:
                denom = 1
            check = infectingIndividual[3]/denom
            # print("RAND: " + str(rand))
            # print("CHECK: " + str(check))
            j = last 
            rand2 = trueRandom(0,1)
            if rand <= check:
                if rand2 <= (j)/len(population):
                    infectingIndividual[3] -= 1
                else:
                    while True:
                        if j >= len(population)-1:
                            # raise Exception("Population exceeded")
                            infectivity = False
                            break
                        if population[j][0] == 0:
                            # print("Entered second if with " + str(j))
                            population[j][0] = 1
                            population[j][1] = simulatedDay + incPeriod
                            population[j][2] = simulatedDay + illPeriod + incPeriod
                            rand3 = trueRandom(0,1)
                            keyId = 0
                            while True:
                                if rand3 < r0Arr[keyId][0]:
                                    population[j][3] = r0Arr[keyId][1]
                                    break
                                keyId += 1
                                
                            population[j][5] = infectingIndividual[6]
                            infectingIndividual[3] -= 1
                            break
                        j += 1
            simulatedDay += 1
            return j
        #return j
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
    newJ = infect(population[0], day, 1)
    day += 1
    # if population[1][1] <= day and population[1][1] != 0 and population[1][3] >= 0:
    #     infect(population[1], day)
    # if population[2][1] <= day and population[2][1] != 0 and population[2][3] >= 0:
    #     infect(population[2], day)
    x = 0
    while day < 100:
        # print(day)
        x = 0
        # print(population)
        while True:
            if population[x][1] == 0:
                break
            x+=1
        # print(population)

        # print("DAY" + str(day))

        for i in range(0,x):
            if population[i][1] <= day and population[i][1] != 0 and population[i][3] > 0:
                newJ = infect(population[i], day, newJ)
        print(newJ)
        # print(population)
        continueCalc = False
        for i in range(len(population)):
            if population[i][2] >= day and population[i][3] != 0:
                continueCalc = False
            else:
                continueCalc = True
        if continueCalc:
            day += 1
        




    newCasesByDate = []

    for i in range(0, len(population)):
        newCasesByDate.append(population[i][1])

    newCasesByDate = sorted(newCasesByDate)
    newCasesByDate = list(filter(lambda a: a != 0, newCasesByDate))
    # print(newCasesByDate)
    minimumX = newCasesByDate[0]
    maximumX = newCasesByDate[len(newCasesByDate) - 1]

    # print("Infecting done")


    graphingInfoY = [len(list(group)) for key, group in groupby(newCasesByDate)]
    # print(len(graphingInfoY))
    for i in range(0, len(graphingInfoY)):
        time.append(i)
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


def createCases():
    newByDay = [1,1,3,2,2,3,6,4,8,5,6,2,3,18,13,12,23,24,17,20,14,7,67,39,19,73,84,83,32,17,55,202,42,66,63,75,54,59,17,61,95]
    knownDataIn = []
    r0Arr = [[0.15, 4], [0.4, 5], [0.75,6], [0.9,7], [1,8]]
    for i in range(len(newByDay)):
        for j in range(newByDay[i]):
            rand3 = trueRandom(0,1)
            keyId = 0
            while True:
                if rand3 < r0Arr[keyId][0]*(i/len(newByDay)):
                    x = r0Arr[keyId][1]
                    break
                keyId += 1
                if keyId >= len(r0Arr):
                    x=0
                    break
            knownDataIn.append([1,i+1,i+13, 0,x,0,0])
    return knownDataIn


def multiprocessDef(r0, r0Arr, file):
    for i in range(0,1):
        knownDataIn = createCases()
        model(r0, r0Arr, file, knownDataIn)
    f = open(file, "a")
    f.write("\n\nEND")

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
    # p1 = multiprocessing.Process(target=multiprocessDef, args=(2, [[0.15, 4], [0.4, 5], [0.75,6], [0.9,7], [1,8]], "realisticEstimates", ))
    # p1.start()
    
    multiprocessDef(2, [[0.15, 4], [0.4, 5], [0.75,6], [0.9,7], [1,8]], "truePopulationWithData4-8")

    # p2.join()
    # p3.join()



    #print("ALL DONE")
