import pylab
import numpy.random as rand
#draw many times from exponential
draws = 10000
scale = 10

rr = rand.exponential(scale,draws)

#now only keep values that are greater than 10
morethan10=[]
for i in range(draws):
    tt = rand.exponential(scale)
    if tt > 10:
        morethan10.append(tt)
    else:
        morethan10.append(rand.exponential(scale))
        
lessthan10=[]

for i in range(draws):
    tt = rand.exponential(scale)
    if tt < 10:
        lessthan10.append(tt)
    else:
        lessthan10.append(rand.exponential(scale))
        
        
print(mean(rr), mean(morethan10), mean(lessthan10))        
        
#draw a number
# if it is more than x, discard it and draw again



