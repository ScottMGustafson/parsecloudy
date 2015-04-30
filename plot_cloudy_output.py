

"""
take in data from parse_cloudy_output data files and plot.
"""

import matplotlib.pyplot as plt
import numpy as np
from variousutils import int_to_roman, ion_state
from collections import OrderedDict
import os
from config import *

solar={}
for item in open(paths['solar_abundance']):
    item=item.split()
    solar[item[0]] = float(item[1])    

#plt.rc('text', usetex=True)
#plt.rc('font', family='serif')

color_map={
    0:'ko',
    1:'bo',
    2:'co',
    3:'go',
    4:'yo',
    5:'ro',
    6:'mo',
    7:'ko'
}

colors={
    0:'k-',
    1:'b-',
    2:'c-',
    3:'g-',
    4:'y-',
    5:'r-',
    6:'m-',
    7:'k-'
}

#states to plot
ionmap = {
'H':[0,1,2],
'C':[0,1,2,3,4,5,6],
'O':[0,1,2,3,4,5,6,7],
'Si':[0,1,2,3,4,5,6,7]
}


def total_col(lst):
    assert(type(lst) is list)
    return np.log10(sum([10**item[1] for item in lst]))

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
    xlims=[3.6,5.0]
    ylims=[0.,20.]
    hcol = np.array(hcol, dtype=np.float)

    for i in ionmap[element]:
        fig,ax = plt.subplots()
        try:
            x = np.array([item[i] for item in T],dtype=np.float)
            y = np.array([item[i] for item in N],dtype=np.float)
        except:
            raise Exception(str(len(item))+" "+str(ionmap[element])+" "+str(i))
        #x,y,hcol = trim(x,y,hcol)
        y = hcol - y
        ax.plot(x, y, color_map[i],label=ion_state(i,element))
        if not bounds is None: 
            l = 17.38 - max(bounds)
            u = 17.41 - min(bounds)
            plt.fill([xlims[0],xlims[1],xlims[1],xlims[0]], [l,l,u,u], '0.50', alpha=0.2, edgecolor='b')
        plt.ylabel(r"$log(N_{HI}/N_{%s})$"%{element+int_to_roman(i)})
        plt.xlabel(r"log(T)")

        #plt.xlim(xlims)
        #plt.ylim(ylims)

        f=os.path.join(paths["plot_path"], element+int_to_roman(i)+"NT.png")
        plt.savefig(f)
        plt.close(fig)

def plot_NU(element,U,N, hcol,bounds=None):
    """
    plot N versus ionization parameter U
    parameters:
    -----------
    element: element name
    N: log N. should be list of lists like: [HI:[...],HII:[...],H2:[...]]
    U: log U. list of lists like N
    """

    
    for i in ionmap[element]:
        fig,ax = plt.subplots()
        x = np.array([item for item in U],dtype=np.float)
        y = np.array([item[i] for item in N],dtype=np.float)
        #x,y,hcol = trim(x,y,hcol)
        y = hcol - y
        ax.plot(x, y, color_map[i],label=ion_state(i,element))
        xlims=[-10.2,0.2]
        ylims=[0.,20.]
        #plt.xlim(xlims)
        #plt.ylim(ylims)
        plt.ylabel(r"$log(N_{HI}/N_{%s})$"%{element+int_to_roman(i)})
        plt.xlabel(r"U")
        if not bounds is None: 
            l = 17.38 - max(bounds)
            u = 17.41 - min(bounds)

            plt.fill([xlims[0],xlims[1],xlims[1],xlims[0]], [l,l,u,u], '0.50', alpha=0.2, edgecolor='b')

            #plt.fill_between(np.arange(xlims[0],xlims[1]),lower,upper,color='0.50')
        f=os.path.join(paths["plot_path"], element+int_to_roman(i)+"NU.png")
        plt.savefig(f)
        plt.close(fig)

def plot_NZ(element,Z,N, hcol,bounds=None):
    """
    plot N versus T
    parameters:
    -----------
    element: element name
    N: log N. should be list of lists like: [HI:[...],HII:[...],H2:[...]]
    T: log T. list of lists like N
    """

    
    for i in ionmap[element]:
        fig,ax = plt.subplots()
        x = np.array(Z,dtype=np.float)
        y = np.array([item[i] for item in N],dtype=np.float)
        #x,y,hcol = trim(x,y,hcol)
        y = hcol - y
        ax.plot(x, y, color_map[i],label=ion_state(i,element))
        xlims=[-5.0,0.]
        ylims=[0.,20.]
        #plt.xlim(xlims)
        #plt.ylim(ylims)
        plt.ylabel(r"$log(N_{HI}/N_{%s})$"%{element+int_to_roman(i)})
        plt.xlabel(r"Z")
        if not bounds is None: 
            l = 17.38 - max(bounds)
            u = 17.41 - min(bounds)

            plt.fill([xlims[0],xlims[1],xlims[1],xlims[0]], [l,l,u,u], '0.50', alpha=0.2, edgecolor='b')

            #plt.fill_between(np.arange(xlims[0],xlims[1]),lower,upper,color='0.50')
        f=os.path.join(paths["plot_path"], element+int_to_roman(i)+"NZ.png")
        plt.savefig(f)
        plt.close(fig)


def plot_N(element,N,hcol,bounds=None):
    fig,ax = plt.subplots()

    xbounds=[]  #i-indices of datapts within bounds 
    n=[]
    for i in range(len(N)):
        """
        if min(bounds)<=N[i][2][1]<=max(bounds):
            xbounds.append(i)  """
        num=sum([ 10.**N[i][j][1] for j in range(len(N[i]))  ])
        n.append(np.log10(num))
    nH = np.array([np.log10(10.**item[0][1] + 10.**item[1][1] + 10.**item[2][1]) for item in hcol])  #get total column for HI, HI and H2
    x = np.array(np.array(n) - nH -(solar[element] - solar['H']),dtype=np.float)
    y = np.array([item[2] for item in N],dtype=np.float)


    assert(x.shape[0]==y.shape[0]>2)

    ax.plot(x, y, 'ko')
    xlims=[-5.0,-2.]
    ylims=[10.,15.]
    #plt.xlim(xlims)
    #plt.ylim(ylims)
    plt.ylabel(r"$log(N_{"+element+r" III})$")
    plt.xlabel(r"$["+element+r"/H]$")
    if bounds: 
        try:
            ly = max(bounds)
            uy = min(bounds)
            lx= min(list(x[xbounds]))
            ux= max(list(x[xbounds]))
            plt.fill([lx,ux,ux,lx], [ly,ly,uy,uy], '0.50', alpha=0.2, edgecolor='b')
        except:
            pass
    f=os.path.join(paths["plot_path"], element+"N_NH.png")
    plt.savefig(f)
    plt.close(fig)

def plot_Nhden(element,N,hcol,hden,bounds=None):


    for i in ionmap[element]:
        fig,ax = plt.subplots()
        x = np.array(hden,dtype=np.float)
        y = np.array([item[i] for item in N],dtype=np.float)
        #x,y,hcol = trim(x,y,hcol)
        y = hcol - y
        ax.plot(x, y, color_map[i],label=ion_state(i,element))

        xlims=[-3.5,3.5]
        ylims=[0.,20.]
        ##plt.xlim(xlims)
        ##plt.ylim(ylims)
        plt.ylabel(r"$log(N_{HI}/N_{%s})$"%{element+int_to_roman(i)})
        plt.xlabel(r"$log(n_{H})$")
        if bounds: 
            l = 17.409 - max(bounds)
            u = 17.415 - min(bounds)

            plt.fill([xlims[0],xlims[1],xlims[1],xlims[0]], [l,l,u,u], '0.50', alpha=0.2, edgecolor='b')
        f=os.path.join(paths["plot_path"], element+int_to_roman(i)+"N_Nhden.png")
        plt.savefig(f)
        plt.close(fig)
        
  
def plot_frac(element,U,N,bounds=None):
    #fig,ax = plt.subplots()
    f= os.path.join( paths['plot_path'], element+'_frac_out.dat')
    output=open(f,'w')
    outputlst = [np.array(U,dtype=np.float)]
    for i in ionmap[element]:
        #x = np.array(U,dtype=np.float)
        y = np.array([10.**(item[i][1] - total_col(item)) for item in N],dtype=np.float)
        outputlst.append(y)
        #ax.plot(x, y, color_map[i],label=ion_state(i,element))

    outputlst.append(np.array([item[2][1] for item in N],dtype=np.float))
    outputlst.append(np.array([total_col(item) for item in N]))


    form = ""
    for i in range(len(outputlst)):
        form+="%lf "
    form+="\n"

    for i in range(len(outputlst[0])):
        datum=tuple([outputlst[j][i] for j in range(len(outputlst))])
        output.write(form % datum)

    #xlims=[-4.0,-2.5]
    #ylims=[0.,1.1]
    ##plt.xlim(xlims)
    ##plt.ylim(ylims)
    #plt.ylabel(r"$N_X/N$")
    #plt.xlabel(r"$log(U)$")
    #f=os.path.join(paths["plot_path"], element+"frac.png")
    #plt.savefig(f)


def _plot(ax,xlabel,ylabel,name,xlims=None,ylims=None):
    ###plt.xlims(xlims)
    ##plt.ylims(ylims)
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    if bounds:
        plt.fill(bounds[0], bounds[1], '0.50', alpha=0.2, edgecolor='b')
    f=os.path.join(paths["plot_path"], name)
    plt.savefig(f)
    plt.close(fig)
        
    

