import numpy as np

def running_mean(x, N):
    cumsum = np.cumsum(np.insert(x, 0, 0)) 
    return (cumsum[N:] - cumsum[:-N]) / N


print(np.round((running_mean([1,2,8,4,5,6,7,8], 5))))
