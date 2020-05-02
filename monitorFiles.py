import os


def checkForFileCompatibility(fileName):
    count = 0
    try:
        with open(fileName, 'r') as f:
            for line in f:
                count += 1
    except:
        return 5

    if count >= 7:
        return 0
    else:
        return 7-count
