import numpy as np

def readDataFile(FILE):
    return np.loadtxt(FILE, dtype = int, comments="#", delimiter="\n", unpack=False)