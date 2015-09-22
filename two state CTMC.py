#compute transition probablities given rate of a two state contiuous Markoc chain
from numpy import *
from scipy import *
#define forward and reverse rate
alpha, beta = 0.5, 0.25



vi = alpha + beta # sum rates

#prob of being in state 0 at some time
def P00(alpha, beta, time):
    p00_1 = beta/(alpha + beta)
    p00_2 = alpha/(alpha + beta) * exp(-(alpha + beta) * time)
    return p00_1 + p00_2