import math

def lerp(a, b):
    return lambda x: (x - a) / (b - a)

def valid_range(r0, r1, c0, c1):
    return lambda r, c: r >= r0 and r < r1 and c >= c0 and c < c1
    
def valid_coordinates(row, col, valid_test, rng = [-1, 0, 1]):
    return [e for e in [[row + r, col + c] for r in rng for c in rng] 
        if e != [row, col] and valid_test(e[0], e[1])]

def decay(c):
    return lambda x: math.exp(-x * c)

def clamp(a, b):
    return lambda x: max(a, min(x, b))

