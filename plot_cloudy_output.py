

"""
take in data from parse_cloudy_output data files and plot.
"""

import matplotlib.pyplot as plt
import numpy as np
from variousutils import int_to_roman, ion_state
from collections import OrderedDict
import os

solar={}
for item in open('SolarAbundance.txt'):
    item=item.split()
    solar[item[0]] = float(item[1])    

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

#states to plot
ionmap = {
'H':[0,1,2],
'C':[2],
'O':[],
'Si':[2]
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

def plot_NT(element,T,N,hcol,bounds=None):
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
    for i in ionmap[element]:
        try:
            x = np.array([item[i] for item in T],dtype=np.float)
            y = np.array([item[i] for item in N],dtype=np.float)
        except:
            raise Exception(str(len(item))+" "+str(ionmap[element])+" "+str(i))
        #x,y,hcol = trim(x,y,hcol)
        y = hcol - y
        ax.plot(x, y, color_map[i],label=ion_state(i,element))
    plt.ylabel(r"$log(N_{HI}/N)$")
    plt.xlabel(r"log(T)")
    xlims=[3.6,5.0]
    ylims=[0.,20.]
    plt.xlim(xlims)
    plt.ylim(ylims)

    if not bounds is None: 
        l = 17.409 - max(bounds)
        u = 17.415 - min(bounds)
        plt.fill([xlims[0],xlims[1],xlims[1],xlims[0]], [l,l,u,u], '0.50', alpha=0.2, edgecolor='b')

    plt.savefig('plots/'+element+"NT.png")
    return

def plot_NU(element,U,N, hcol,bounds=None):
    """
    plot N versus ionization parameter U
    parameters:
    -----------
    element: element name
    N: log N. should be list of lists like: [HI:[...],HII:[...],H2:[...]]
    U: log U. list of lists like N
    """
    fig,ax = plt.subplots()
    
    for i in ionmap[element]:
        x = np.array([item for item in U],dtype=np.float)
        y = np.array([item[i] for item in N],dtype=np.float)
        #x,y,hcol = trim(x,y,hcol)
        y = hcol - y
        ax.plot(x, y, color_map[i],label=ion_state(i,element))
    xlims=[-10.2,0.2]
    ylims=[0.,20.]
    plt.xlim(xlims)
    plt.ylim(ylims)
    plt.ylabel(r"$log(N_{HI}/N)$")
    plt.xlabel(r"U")
    if not bounds is None: 
        l = 17.409 - max(bounds)
        u = 17.415 - min(bounds)

        plt.fill([xlims[0],xlims[1],xlims[1],xlims[0]], [l,l,u,u], '0.50', alpha=0.2, edgecolor='b')

        #plt.fill_between(np.arange(xlims[0],xlims[1]),lower,upper,color='0.50')
    plt.savefig('plots/'+element+"NU.png")
    return

def plot_NZ(element,Z,N, hcol,bounds=None):
    """
    plot N versus T
    parameters:
    -----------
    element: element name
    N: log N. should be list of lists like: [HI:[...],HII:[...],H2:[...]]
    T: log T. list of lists like N
    """
    fig,ax = plt.subplots()
    
    for i in ionmap[element]:
        x = np.array(Z,dtype=np.float)
        y = np.array([item[i] for item in N],dtype=np.float)
        #x,y,hcol = trim(x,y,hcol)
        y = hcol - y
        ax.plot(x, y, color_map[i],label=ion_state(i,element))
    xlims=[-5.0,0.]
    ylims=[0.,20.]
    plt.xlim(xlims)
    plt.ylim(ylims)
    plt.ylabel(r"$log(N_{HI}/N)$")
    plt.xlabel(r"Z")
    if not bounds is None: 
        l = 17.409 - max(bounds)
        u = 17.415 - min(bounds)

        plt.fill([xlims[0],xlims[1],xlims[1],xlims[0]], [l,l,u,u], '0.50', alpha=0.2, edgecolor='b')

        #plt.fill_between(np.arange(xlims[0],xlims[1]),lower,upper,color='0.50')
    plt.savefig('plots/'+element+"NZ.png")
    return


def plot_N(element,N,hcol,bounds=None):
    fig,ax = plt.subplots()

    xbounds=[]  #i-indices of datapts within bounds 
    n=[]
    for i in range(len(N)):
        if min(bounds)<=N[i][2][1]<=max(bounds):
            xbounds.append(i)  
        num=sum([ 10.**N[i][j][1] for j in range(len(N[i]))  ])
        n.append(np.log10(num))
    nH = np.array([np.log10(10.**item[0][1] + 10.**item[1][1] + 10.**item[2][1]) for item in hcol])  #get total column for HI, HI and H2
    x = np.array(np.array(n) - nH -(solar[element] - solar['H']),dtype=np.float)
    y = np.array([item[2] for item in N],dtype=np.float)
    ax.plot(x, y, 'ko')
    xlims=[-6.0,0.]
    ylims=[5.0,20.]
    plt.xlim(xlims)
    plt.ylim(ylims)
    plt.ylabel(r"$log(N_{"+element+r" III})$")
    plt.xlabel(r"$["+element+r"/H]$")
    if not bounds is None: 
        ly = max(bounds)
        uy = min(bounds)
        lx= min(list(x[xbounds]))
        ux= max(list(x[xbounds]))
        plt.fill([lx,ux,ux,lx], [ly,ly,uy,uy], '0.50', alpha=0.2, edgecolor='b')
    plt.savefig('plots/'+element+"N_NH.png")


def plot_Nhden(element,N,hcol,hden,bounds=None):
    fig,ax = plt.subplots()

    for i in ionmap[element]:
        x = np.array(hden,dtype=np.float)
        y = np.array([item[i] for item in N],dtype=np.float)
        #x,y,hcol = trim(x,y,hcol)
        y = hcol - y
        ax.plot(x, y, color_map[i],label=ion_state(i,element))

    xlims=[-3.5,3.5]
    ylims=[0.,20.]
    plt.xlim(xlims)
    plt.ylim(ylims)
    plt.ylabel(r"$log(N_{HI}/N)$")
    plt.xlabel(r"$log(n_{H})$")
    if bounds: 
        l = 17.409 - max(bounds)
        u = 17.415 - min(bounds)

        plt.fill([xlims[0],xlims[1],xlims[1],xlims[0]], [l,l,u,u], '0.50', alpha=0.2, edgecolor='b')
    plt.savefig('plots/'+element+"N_Nhden.png")

def _plot(ax,xlabel,ylabel,name,xlims=None,ylims=None):
    plt.xlims(xlims)
    plt.ylims(ylims)
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    if bounds:
        plt.fill(bounds[0], bounds[1], '0.50', alpha=0.2, edgecolor='b')
    plt.savefig(plots+os.sep+name)
        
    

