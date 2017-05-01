import math

def normVector(v):
    if len(v) == v.count(0):
        return v
    length = math.sqrt(sum([i**2 for i in v]))
    new_v = []
    for i in range(len(v)):
        new_v.append(v[i]/length)
    return tuple(new_v)

def subVector(v1, v2):
    res = []
    for i in range(len(v1)):
        res.append(v1[i]-v2[i])
    return tuple(res)

def addVector(v1, v2):
    res = []
    for i in range(len(v1)):
        res.append(v1[i]+v2[i])
    return tuple(res)

def multiplyVector(v, multiplier):
    return tuple([i*multiplier for i in v])
