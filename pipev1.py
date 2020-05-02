#! /usr/local/bin/python3

import r0AverageTest as r0AverageTest
import operate
import calculateScore as calc

from os import getpid

import multiprocessing
import time

import average as avg

if __name__ == "__main__":
    # Open Multiprocessing, allow for process communication
    manager = multiprocessing.Manager()
    returnDict = manager.dict()
    
    # Initialize range (+/-), depth
    searchRange = 1
    depth = 2


    # Initialize parameters
    fileArr = [
        # "originalControl", 
        "minus1r0Normal", 
        "minus1r0_1", 
        "minus1r0_1-5"
    ]

    trueR0Values = [
        # 2.2,
        2.2,
        1,
        1.5
    ]
    
    r0ValuesArr = [
        # [[0.15, 1], [0.4, 3], [0.75,2], [0.9,4], [1,0]], 
        [[0.15, 1], [0.4, 3], [0.75,2], [0.9,4], [1,0]], 
        [[1,1]],
        [[0.5,1], [1,2]]
    ]

    startingDayArr = [
        # 44,
        39,
        39,
        39
    ]

    newByDayArr = [
        # [1,1,3,2,2,3,6,4,8,5,6,2,3,18,13,12,23,24,17,20,14,7,67,39,19,73,84,83,32,17,55,202,42,66,63,75,54,59,17,61,95,62,42],
        [1,1,3,2,2,3,6,4,8,5,6,2,3,18,13,12,23,24,17,20,14,7,67,39,19,73,84,83,32,17,55,202,42,66,63,75,54,59],
        [1,1,3,2,2,3,6,4,8,5,6,2,3,18,13,12,23,24,17,20,14,7,67,39,19,73,84,83,32,17,55,202,42,66,63,75,54,59],
        [1,1,3,2,2,3,6,4,8,5,6,2,3,18,13,12,23,24,17,20,14,7,67,39,19,73,84,83,32,17,55,202,42,66,63,75,54,59],
        [1,1,3,2,2,3,6,4,8,5,6,2,3,18,13,12,23,24,17,20,14,7,67,39,19,73,84,83,32,17,55,202,42,66,63,75,54,59,17,61,95,62,42]
    ]


    for i in range(depth):
        timeStart = time.time()
        
        # Empty return value container
        returnDict = {}
        print(returnDict)

        # Begin processes
        processes = []

        for m in range(0, 3):
            p = multiprocessing.Process(target=r0AverageTest.multiprocessDef, args=(2, r0ValuesArr[m], fileArr[m], startingDayArr[m], newByDayArr[m], 10))
            p.start()
            processes.append(p)

        for p in processes:
            p.join()
               
        processes = []

        for m in range(0, 3):
            p = multiprocessing.Process(target = operate.operate, args = (fileArr[m], returnDict, newByDayArr[m], m))
            p.start()
            processes.append(p)
            time.sleep(1)
            print("Process" + str(m))
        
        for p in processes:
            p.join()

        print(time.time() - timeStart)
        time.sleep(5)

        # Find best performing process
        processScores = []

        for i in range(0, 3):
            processScores.append(calc.calculateScore(avg.average(newByDayArr[3], 5), returnDict[i][0], 0))

        # print("0: " + str(calc.calculateScore(avg.average(newByDayArr[3], 5), returnDict[0][0], 0)))
        # print("1: " + str(calc.calculateScore(avg.average(newByDayArr[3], 5), returnDict[1][0], 0)))
        # print("2: " + str(calc.calculateScore(avg.average(newByDayArr[3], 5), returnDict[2][0], 0)))
        # print("3: " + str(calc.calculateScore(avg.average(newByDayArr[3], 5), returnDict[3][0], 0)))

        # Create list of new R0 values

        # Create array of possible R0 values for each true value

        # Create new file names
