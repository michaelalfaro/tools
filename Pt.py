import numpy as np
nt = 'ACGT'
def show(A,x):
    print x
    print '     ' + '       '.join(list(nt))
    for i,e in enumerate(A):
        print nt[i] + ' ',
        L = [str(round(n,4)).ljust(7) for n in e]
        print ' '.join(L)
    print 

I = np.eye(4)
A = I
T = I * 0.96 + 0.01
show(A,0)
for i in range(1,101):
    A = np.dot(T,A)
    R = range(2,10,2) + range(20,101,10)
    if i in [1] + R:
        show(A,i)