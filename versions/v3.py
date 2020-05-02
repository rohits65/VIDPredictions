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

def model():
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


    r0 = 2
    '''
    1:25%
    2:50%
    3:25%
    '''
    illPeriod = 5
    incPeriod = 0
    totalPopulation = 10000

    population = [[0 for i in range(7)] for j in range(totalPopulation)] 
    # print("Made a pop")
    time = []

    #Prep sys
    f = open("r0_2", "a")

    for i in range(0, len(population)):
        population[i][6] = i

    # print(population)
    # print(time)
    #Add the index case, 1 --> sick
    
    day = 1
    population[0][0] = 1
    population[0][1] = day + incPeriod
    population[0][2] = day + illPeriod
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
                            population[j][1] = simulatedDay
                            population[j][2] = simulatedDay + illPeriod
                            population[j][3] = 2
                            
                            population[j][5] = infectingIndividual[6]
                            infectingIndividual[3] -= 1
                            break
                        j += 1
            simulatedDay += 1
            return j
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
    newJ = infect(population[0], day, 0)
    day += 1
    # if population[1][1] <= day and population[1][1] != 0 and population[1][3] >= 0:
    #     infect(population[1], day)
    # if population[2][1] <= day and population[2][1] != 0 and population[2][3] >= 0:
    #     infect(population[2], day)
    x = 0
    while day < 100:
        # x = 0
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
        # print(population)
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



if __name__ == "__main__": 
    for i in range(0,100):
        model()

    #print("ALL DONE")
