

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

#max number of species to care about for a few diff ions
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

    plt.savefig('plots/'+element+"NT.png")
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
    plt.savefig('plots/'+element+"NU.png")
    return






