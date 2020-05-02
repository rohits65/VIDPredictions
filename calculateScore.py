import numpy as np

def calculateScore(knownData, predictedAvg, startIndex):
    scorePred = 0
    for i in range(startIndex, len(knownData)):
        scorePred += predictedAvg[i]
    trueScore = 0
    for i in range(startIndex, len(knownData)):
        trueScore += knownData[i]
    
    return abs(scorePred-trueScore)