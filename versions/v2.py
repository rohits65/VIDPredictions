#! /usr/local/bin/python3
import random
from itertools import groupby

import numpy as np
import pandas as pd
from pandas import Series, DataFrame
import matplotlib.pyplot as plt

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
population = [[0 for i in range(7)] for j in range(20)] 
print("Made a pop")
time = []

for i in range(0, len(population)):
    population[i][6] = i

# print(population)
# print(time)
#Add the index case, 1 --> sick
day = 1
population[0][0] = 1
population[0][1] = day
population[0][2] = day + 5
population[0][3] = 2
population[0][5] = -1

# print(population)
# print("\n")

def infect(infectingIndividual, day):
    simulatedDay = day
    infectivity = True
    while infectingIndividual[3] > 0 and infectivity == True:
        rand = random.uniform(0, 1)
        denom = (infectingIndividual[2] - simulatedDay + 1)
        if denom <= 0:
            denom = 1
        check = infectingIndividual[3]/denom
        # print("RAND: " + str(rand))
        # print("CHECK: " + str(check))
        if rand <= check:
            j = 0
            while True:
                if j >= len(population)-1:
                    # raise Exception("Population exceeded")
                    infectivity = False
                    break
                if population[j][0] == 0:
                    # print("Entered second if with " + str(j))
                    population[j][0] = 1
                    population[j][1] = simulatedDay
                    population[j][2] = simulatedDay + 5
                    population[j][3] = 2
                    population[j][5] = infectingIndividual[6]
                    infectingIndividual[3] -= 1
                    break
                j += 1
        simulatedDay += 1
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

for i in range(0, len(population)):
    changeIllnessStatus(population[i], day) 

infect(population[0], day)
day += 1
if population[1][1] <= day and population[1][1] != 0 and population[1][3] >= 0:
    infect(population[1], day)
if population[2][1] <= day and population[2][1] != 0 and population[2][3] >= 0:
    infect(population[2], day)


print(population)

newCasesByDate = []

for i in range(0, len(population)):
    newCasesByDate.append(population[i][1])

newCasesByDate = sorted(newCasesByDate)
print(newCasesByDate)
minimumX = newCasesByDate[0]
maximumX = newCasesByDate[len(newCasesByDate) - 1]

print("Infecting done")


graphingInfoY = [len(list(group)) for key, group in groupby(newCasesByDate)]
print(len(graphingInfoY))
for i in range(0, len(graphingInfoY)):
    time.append(i)
print(len(time))

def plotBarHorizontal():
    data = graphingInfoY
    plt.bar(time, data)
    plt.show()

plotBarHorizontal()

# print(graphingInfoY)

for i in range(0, len(graphingInfoY)):
    print("(" + str(i) + "," + str(graphingInfoY[i]) + ")")



    




