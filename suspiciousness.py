import math


def gp19(ep, np, ef, nf):
    return ef * math.sqrt(abs(ep - ef + nf - np))