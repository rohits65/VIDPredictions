import multiprocessing
import os
import statistics

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
from scipy.ndimage.filters import uniform_filter1d

import average as avg
import R0Operations as rops


def intCastArr(arr):
    for i in range(0, len(arr)):
        arr[i] = int(arr[i])
    
    return arr

def graphArr(arr, max):
    
    graphMinimums = []
    graphMaximums = []
    graphAverages = []
    graphMedians = []
    for x in range(0,max):
        graphMinimumsInter = []
        graphMaximumsInter = []
        graphAveragesInter = []
        graphMediansInter = []
        # print(len(arr[x]))
        yAtI = []
        for i in range(0, len(arr)):
            
            #d = len(arr[x])
            yAtI.append(arr[i][x])
            
            yAtI = sorted(yAtI)
        graphMinimumsInter.append(yAtI[0])
        graphMaximumsInter.append(yAtI[-1])
        graphAveragesInter.append(sum(yAtI)/len(yAtI))
        graphMediansInter.append(statistics.median(yAtI))
        graphMinimums.append(sum(graphMinimumsInter)/len(graphMinimumsInter))
        graphMaximums.append(sum(graphMaximumsInter)/len(graphMaximumsInter))
        graphMedians.append(sum(graphMediansInter)/len(graphMediansInter))
        graphAverages.append(sum(graphAveragesInter)/len(graphAveragesInter))
    
    return [graphAverages, graphMaximums, graphMinimums, graphMedians]


def operate(file, returnDict, newByDayReal, process, r0, firstCaseDate, trueData, auto=False, isFinal=False, county=None, currentDate=None, useCases=True):
    print("Data set running: " + file)
    print(os.getcwd())
    f = open(file, "r")

    xMaxes = []
    yNewArr = []
    yTotArr = []

    maxYNewArrLen = 0
    maxYTotArrLen = 0

    x = 0
    while True:
        line = f.readline()
        if len(line) > 0:
            if line.startswith("I", 0, 4) == False:
                if line.startswith("X", 0, 4):
                    line = line.lstrip("X: ")
                    line = line.replace(']', '')
                    line = line.replace('[', '')
                    line = line.replace('\n', '')
                    line = line.replace(' ', '')
                    processLine = line.split(',')
                    processArray = list(processLine)
                    processArray = intCastArr(processArray)
                    xMaxes.append(processArray[-1])
                    # print(xMaxes)
                if line.startswith("YNEW", 0, 6):
                    line = line.lstrip("YNEW: ")
                    line = line.replace(']', '')
                    line = line.replace('[', '')
                    line = line.replace('\n', '')
                    line = line.replace(' ', '')
                    processLine = line.split(',')
                    processArray = list(processLine)
                    processArray = intCastArr(processArray)
                    yNewArr.append(processArray)
                    if len(processArray) > maxYNewArrLen:
                        maxYNewArrLen = len(processArray)
                if line.startswith("YTOT", 0, 6):
                    line = line.lstrip("YTOT: ")
                    line = line.replace(']', '')
                    line = line.replace('[', '')
                    line = line.replace('\n', '')
                    line = line.replace(' ', '')
                    processLine = line.split(',')
                    processArray = list(processLine)
                    processArray = intCastArr(processArray)
                    yTotArr.append(processArray)
                    if len(processArray) > maxYTotArrLen:
                        maxYTotArrLen = len(processArray)
                        # print(processArray)

        x+=1

        if line == "END":
            break
    
    xMaxes = sorted(xMaxes)
    xMax = xMaxes[-1]
    # print(xMax)
    # print(maxYNewArrLen)
    # print(maxYTotArrLen)
    newByDayReal = trueData
    newByDayReal2 = np.array(avg.hullMovingAverage(newByDayReal, 5))

    # ii = np.where(newByDayReal2 == 0)[0]

    if maxYNewArrLen > xMax or maxYTotArrLen > xMax:
        xMax = maxYNewArrLen
    

    for i in range(0, len(yNewArr)):
        if len(yNewArr[i]) < maxYNewArrLen:
            # print(i)
            ma = maxYNewArrLen - len(yNewArr[i])
            for j in range(0, maxYNewArrLen - len(yNewArr[i])):
                yNewArr[i].append(0)
            # print(len(yNewArr[i]))

    for i in range(0, len(yNewArr)):
        if len(yTotArr[i]) < maxYTotArrLen:
            # print(i)
            ma = maxYTotArrLen - len(yTotArr[i])
            for j in range(0, maxYTotArrLen - len(yTotArr[i])):
                yTotArr[i].append(yTotArr[i][-1])
            # print(len(yTotArr[i]))

    # for i in ii:
    #     for j in range(len(yNewArr)):
    #         yNewArr[j].insert(i, 0)
    #     for j in range(len(yTotArr)):
    #         yTotArr[j].insert(i, 0)
    
    # maxYNewArrLen += len(ii)
    # maxYTotArrLen += len(ii)

    newCases = graphArr(yNewArr, maxYNewArrLen)
    totalCases = graphArr(yTotArr, maxYTotArrLen)
    # returns [graphAverages, graphMaximums, graphMinimums, graphMedians]

    f.close()

    newCases[0] = [round(num) for num in newCases[0]]
    totalCases[0] = [round(num) for num in totalCases[0]]

    

    time = pd.date_range(start=firstCaseDate, periods=int(xMax))
    # for i in range(0, xMax):
    #     time.append(i)

    
    # N = 5
    # newByDayReal = np.array(newByDayReal)
    
    # newByDayReal = list(uniform_filter1d(x, size=N))

    # UNCOMMENT
    newCases[0] = newCases[0][0:(len(newCases[0])-5)]
    newCases[1] = newCases[1][0:(len(newCases[1])-5)]
    newCases[2] = newCases[2][0:(len(newCases[2])-5)]
    totalCases[0] = totalCases[0][0:(len(totalCases[0])-5)]
    totalCases[1] = totalCases[1][0:(len(totalCases[1])-5)]
    totalCases[2] = totalCases[2][0:(len(totalCases[2])-5)]

    print("Creating imgs . . .",end=' ')
    
    
    
    print("Imgs created")
    print("Data set " + file + " completed")

    if isFinal:
        fig = go.Figure()

        #Create/Style Traces
        # fig.add_trace(go.Scatter(x=time, y=newCases[2]+newCases[1][::-1], fill='toself', line_color='pink', showlegend=False, name="uncertainty"))
        
        fig.add_trace(go.Scatter(x=time, y=newCases[1], name="Maximum", line=dict(color="pink", width=4, dash="dash")))
        fig.add_trace(go.Scatter(x=time, y=newCases[2], name="Minimum", line=dict(color="pink", width=4, dash="dash"), fill="tonexty"))
        fig.add_trace(go.Scatter(x=time, y=newCases[0], name="Average", line=dict(color="firebrick", width=4)))
        fig.add_trace(go.Scatter(x=time, y=newByDayReal2, name="ActualMovingAvg", line=dict(color="yellow", width=4)))
        
        fig.add_trace(go.Scatter(x=time, y=newByDayReal, name="Actual", line=dict(color="royalblue", width=4)))
        # fig.add_trace(go.Scatter(x=time, y=newCases[3], name="Medians", line=dict(color="goldenrod", width=4)))

        # Edit the layout
        if useCases:
            fig.update_layout(title='New Cases by Day (adj) ' + file + "(" + str(r0) + ")", xaxis_title='Day', yaxis_title='New Cases')
            pio.write_html(fig, "newCases"+str(r0)+".html", auto_open=False)
        else:
            fig.update_layout(title='New Deaths by Day (adj) ' + file + "(" + str(r0) + ")", xaxis_title='Day', yaxis_title='New Cases')
            pio.write_html(fig, "newCases"+str(r0)+".html", auto_open=False)
        # pio.write_json(fig, "newCases"+str(r0)+".json")

        fig2 = go.Figure()

        # fig.add_trace(go.Scatter(x=time, y=totalCases[2]+totalCases[1][::-1], fill='toself', line_color='pink', showlegend=False, name="uncertainty"))
        # fig.add_trace(go.Scatter(x=time, y=totalCases[0], name="Average", line=dict(color="firebrick", width=4)))
        fig2.add_trace(go.Scatter(x=time, y=totalCases[1], name="Maximum", line=dict(color="pink", width=4, dash="dash"), fill ="none"))
        fig2.add_trace(go.Scatter(x=time, y=totalCases[2], name="Minimum", line=dict(color="pink", width=4, dash="dash"), fill="tonexty"))
        fig2.add_trace(go.Scatter(x=time, y=totalCases[0], name="Average", line=dict(color="firebrick", width=4)))    
        # fig.add_trace(go.Scatter(x=time, y=totalCases[3], name="Medians", line=dict(color="goldenrod", width=4)))

        # Edit the layout
        if useCases:
            fig2.update_layout(title='Total Cases by Day (adj) ' + file + "(" + str(r0) + ")", xaxis_title='Day', yaxis_title='Total Cases')

            # pio.write_html(fig, "totalCases"+str(r0)+".html", auto_open=auto)

            pio.write_html(fig2, "totalCases"+str(r0)+".html", auto_open=False)
        else:
            fig2.update_layout(title='Total Deaths by Day (adj) ' + file + "(" + str(r0) + ")", xaxis_title='Day', yaxis_title='Total Cases')

            # pio.write_html(fig, "totalCases"+str(r0)+".html", auto_open=auto)

            pio.write_html(fig2, "totalCases"+str(r0)+".html", auto_open=False)
        # pio.write_json(fig2, "totalCases"+str(r0)+".json")
        os.chdir("..")
        os.chdir("..")
        os.chdir("..")
        os.chdir("..")
        os.chdir("web/data")
        pio.write_json(fig2, county+"TotalCases"+".json")
        pio.write_json(fig, county+"NewCases"+".json")
        os.chdir("..")
        os.chdir("..")
        rops.addR0(r0, "main/R0/"+county+"R0", county, currentDate)

    returnDict[process] = [newCases, totalCases, time, newByDayReal2, newByDayReal, file, r0]
    


if __name__ == "__main__":
    '''
    r0_1 = operate("r0_1")
    print("Started Next")
    r0_2 = operate("r0_2")
    r0_3 = operate("r0_3")
    r0_4 = operate("r0_4")
    r0_5 = operate("r0_5")
    r0_6 = operate("r0_6")

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=range(0, len(r0_1[0][0])), y=r0_1[0][0], name="r0_1", line=dict(width=4)))
    fig.add_trace(go.Scatter(x=range(0, len(r0_2[0][0])), y=r0_2[0][0], name="r0_2", line=dict(width=4)))
    fig.add_trace(go.Scatter(x=range(0, len(r0_3[0][0])), y=r0_3[0][0], name="r0_3", line=dict(width=4)))
    fig.add_trace(go.Scatter(x=range(0, len(r0_4[0][0])), y=r0_4[0][0], name="r0_4", line=dict(width=4)))
    fig.add_trace(go.Scatter(x=range(0, len(r0_5[0][0])), y=r0_5[0][0], name="r0_5", line=dict(width=4)))
    fig.add_trace(go.Scatter(x=range(0, len(r0_6[0][0])), y=r0_6[0][0], name="r0_6", line=dict(width=4)))

    fig.update_layout(title='New Cases Avg by Day (adj)', xaxis_title='Day', yaxis_title='New Cases')

    pio.write_html(fig, "NewCasesByDay.html", auto_open=True)


    fig = go.Figure()

    fig.add_trace(go.Scatter(x=range(0, len(r0_1[1][0])), y=r0_1[1][0], name="r0_1", line=dict(width=4)))
    fig.add_trace(go.Scatter(x=range(0, len(r0_2[1][0])), y=r0_2[1][0], name="r0_2", line=dict(width=4)))
    fig.add_trace(go.Scatter(x=range(0, len(r0_3[1][0])), y=r0_3[1][0], name="r0_3", line=dict(width=4)))
    fig.add_trace(go.Scatter(x=range(0, len(r0_4[1][0])), y=r0_4[1][0], name="r0_4", line=dict(width=4)))
    fig.add_trace(go.Scatter(x=range(0, len(r0_5[1][0])), y=r0_5[1][0], name="r0_5", line=dict(width=4)))
    fig.add_trace(go.Scatter(x=range(0, len(r0_6[1][0])), y=r0_6[1][0], name="r0_6", line=dict(width=4)))

    fig.update_layout(title='Total Cases Avg by Day (adj)', xaxis_title='Day', yaxis_title='Total Cases')

    pio.write_html(fig, "TotalCasesByDay.html", auto_open=True)
    '''
    ###################
    '''
    r0=[]
    r0.append(operate("r0_3"))
    print("Started Next")
    r0.append(operate("r0_2-4"))
    r0.append(operate("r0_1-5"))

    x=["r0_3", "r0_2-4", "r0_1-5"]

    time = []

    for i in range(0, 100):
        time.append(i)

    for i in range(0, 2):
        fig = go.Figure()
        for j in range(1, 4):
            fig.add_trace(go.Scatter(x=time, y=r0[j-1][i][0], name="r0_"+x[j-1], line=dict(width=4)))
        if i == 0:
            fig.update_layout(title='New Cases Avg by Day (adj)', xaxis_title='Day', yaxis_title='New Cases')
            pio.write_html(fig, "NewCasesByDay.html", auto_open=True)
        else:
            fig.update_layout(title='Total Cases Avg by Day (adj)', xaxis_title='Day', yaxis_title='Total Cases')
            pio.write_html(fig, "TotalCasesByDay.html", auto_open=True) 
    '''

    operate("truePopulationWithData4-10xc")

