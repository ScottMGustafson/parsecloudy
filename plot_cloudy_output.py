

"""
take in data from parse_cloudy_output data files and plot.
"""

import matplotlib.pyplot as plt
import numpy as np
from variousutils import int_to_roman, ion_state

plt.rc('text', usetex=True)
plt.rc('font', family='serif')

color_map={
    0:'ko',
    1:'bo',
    2:'co',
    3:'go',
    4:'yo',
    5:'ro',
    6:'mo'
}

#this is a dirty hack to just get something done.  go max to six
ionmap = {
'H':3,
'C':4,
'O':4,
'Si':4
}


    
def trim(x,y):
    while len(x) > len(y):
        if x[-1] == '-30.000':
            del(x[-1])

    while len(y) > len(x):
        if y[-1] == '-30.000':
            del(y[-1])

    if len(y) != len(x):
        raise Exception(str(x)+str(y))

    return np.array(x,dtype=np.float), np.array(y, dtype=np.float)

def trim(x,y,hcol):
    end = min(y.shape[0],x.shape[0])
    return x[0:end], y[0:end], hcol[0:end]

def plot_NT(element,T,N, hcol):
    """
    plot N versus T
    parameters:
    -----------
    element: element name
    N: log N. should be list of lists like: [HI:[...],HII:[...],H2:[...]]
    T: log T. list of lists like N
    """
    hcol = np.array(hcol, dtype=np.float)
    fig,ax = plt.subplots()
    for i in range(ionmap[element]):
        try:
            x = np.array([item[i] for item in T],dtype=np.float)
            y = np.array([item[i] for item in N],dtype=np.float)
        except:
            raise Exception(str(len(item))+" "+str(ionmap[element])+" "+str(i))
        x,y,hcol = trim(x,y,hcol)
        y = hcol - y
        ax.plot(x, y, color_map[i],label=ion_state(i,element))

    plt.ylabel(r"$log(N_{HI}/N)$")
    plt.xlabel(r"log(T)")

    plt.savefig(element+"NT.png")
    return

def plot_NU(element,U,N, hcol):
    """
    plot N versus T
    parameters:
    -----------
    element: element name
    N: log N. should be list of lists like: [HI:[...],HII:[...],H2:[...]]
    T: log T. list of lists like N
    """
    fig,ax = plt.subplots()
    
    for i in range(ionmap[element]):
        
        x = np.array([item[i] for item in U],dtype=np.float)
        y = np.array([item[i] for item in N],dtype=np.float)
        x,y,hcol = trim(x,y,hcol)
        y = hcol - y
        ax.plot(x, y, color_map[i],label=ion_state(i,element))
    plt.xlim([-5,0])
    plt.ylim([-2,12])
    plt.ylabel(r"$log(N_{HI}/N)$")
    plt.xlabel(r"U")
    plt.savefig(element+"NU.png")
    return



# solar O abundance = 8.73 +/- 0.07

# where the abundance is defined A(O) = log N(O)/N(H) + 12


#observed abundances
HI = 17.409, 17.413, 17.415

CI   = 10,12.6, 12.6
CII  = 10, 12.0, 12.0
CIII = 12.6, 12.62, 12.64
CIV  = 10,11.3,11.3

SiII  = 10,11.1,11.1
SiIII = 11.52, 11.62, 11.72
SiIV  = 10,11.1,11.1
OI    = 10,12.5,12.5
OIV   = 10,12.3,12.3

Cmin = np.log10(sum([ 10.**item[0] for item in [CI,CII,CIII,CIV]]))
C = np.log10(sum([ 10.**item[1] for item in [CI,CII,CIII,CIV]]))
Cmax = np.log10(sum([ 10.**item[2] for item in [CI,CII,CIII,CIV]]))
C = Cmin, C, Cmax

def calc_Zlim(X, Y, NX, NY):

    from barak.abundances import Asolar, calc_abund, cond_temp
    """
    X = atom X
    Y = atom Y
    NX = lower lim, best, upper lim
    NY = lower lim, best, upper lim
    """
    Zmin = calc_abund(X, Y, NX[0], NY[2])
    Z    = calc_abund(X, Y, NX[1], NY[1])
    Zmax = calc_abund(X, Y, NX[2], NY[0])
    return np.array([Zmin, Z, Zmax])

print('OI   %5.2f %5.2f %5.2f'  % tuple(calc_Zlim('O', 'H', OI, HI)      ) )
print('OIV   %5.2f %5.2f %5.2f' % tuple(calc_Zlim('O', 'H', OIV, HI)      ))
print('SiIII %5.2f %5.2f %5.2f' % tuple(calc_Zlim('Si','H', SiIII, HI)    )) 
print('CIII %5.2f %5.2f %5.2f'  % tuple(calc_Zlim('C', 'H', CIII, HI)    ) )
print('C %5.2f %5.2f %5.2f'  % tuple(calc_Zlim('C', 'H', C, HI)    ) )



