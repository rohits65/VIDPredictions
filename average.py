
import numpy as np
import math

def average(arr, N):
    roundedArr = []
    for i in range(N-1):
        roundedArr.append(arr[i])
    
    for i in range((N-1),len(arr)):
        avg = 0
        listToCalc = [arr[i]]

        for j in range((i+1)-N,i):
            listToCalc.append(arr[j])
        
        avg = round(sum(listToCalc)/len(listToCalc))
        roundedArr.append(avg)
    
    return roundedArr

def expMovingAvg(values, window):
    weights = np.exp(np.linspace(-1.,0.,window))
    weights /= weights.sum()

    a = np.convolve(values, weights)[:len(values)]
    a[:window] = a[window]
    a = list(a)
    for i in range(len(a)):
        a[i] = round(a[i], 0)

    return a

def weightedMovingAverage(arr, N):
    if len(arr) != N:
        raise Exception(IndexError, "length of array does not match window")

    dataSum = 0
    for i in range(len(arr)):
        dataSum += arr[i] * (i + 1)
    
    denominator = 0
    for i in range(N+1):
        denominator += i
    
    return round(dataSum/denominator)

def hullMovingAverage(arr, N):
    roundedArr = []
    for i in range(N-1):
        roundedArr.append(arr[i])
    
    for i in range(N-1,len(arr)):
        listToCalc = []
        for j in range(i-4, i+1):
            listToCalc.append(arr[j])

        roundedArr.append(weightedMovingAverage(listToCalc, N))

    return roundedArr


if __name__ == "__main__":
    print(average([2,0,6,0,5,1], 5))
    print(weightedMovingAverage([2,0,6,0,5], 5))
    print(hullMovingAverage([2,0,6,0,5,1,8,21,34,2,74,3,9,3], 5))
        

