

"""
take in data from parse_cloudy_output data files and plot.
"""
from __future__ import print_function
import matplotlib.pyplot as plt
import numpy as np
#from variousutils import ion_state, int_to_roman
from collections import OrderedDict
from core import Model
import os,sys
from config import *
from subprocess import call


#roman nums are off by one bc ionization states are counted starting from "1", 
#whereas I need to enter in index starting from "0"

solarHIH = -0.000177 #basically zero.  solar ionization fraction is small  =log(1-ionfrac)

try:
    minNHI = observed['H'][0]['column'][0]
    maxNHI = observed['H'][0]['column'][2]
except:
    print("no constraints set for HI column", file=sys.stderr)
    pass

solar={}
for item in open(paths['solar_abundance']):
    item=item.split()
    solar[item[0]] = float(item[1])    

<<<<<<< HEAD
#plt.rc('text', usetex=True)
#plt.rc('font', family='serif')
=======
plt.rc('text', usetex=True)
plt.rc('font', family='serif',size=16)
>>>>>>> 70bd8703a267b22a816feec9ec803ffaaa7ac5ba

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
'N':[0,1,2,3,4],
'Si':[0,1,2,3,4,5,6,7],
'Fe':[0,1,2,3,4,5,6,7]
}

def makedir(string):
    if not os.path.isdir(os.path.join(paths["plot_path"],string)):
        try:
            msg="mkdir %s"%(os.path.join(paths["plot_path"],string))
            call(msg,shell=True)
        except:
            print("error calling:\n %s"%(msg),file=sys.stderr)
            raise

def ion_state(i,elem):
    """
    append ionization state to elem.
    following cloudy convention, i==2 means molecular Hydrogen for elem==H
    
    """
    if i==2 and elem=='H':
        return r"H_2"
    else:
        return elem+roman[i]

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

def plot_NT(elem,T,N,hcol,bounds=False):
    """
    plot N versus T
    parameters:
    -----------
    elem: elem name
    N: log N. should be list of lists like: [HI:[...],HII:[...],H2:[...]]
    T: log T. list of lists like N
    """
    hcol = np.array(hcol, dtype=np.float)

    for i in to_plot[elem]:
        x = np.array(T[i])   #since data is stored is min, best, max, filter out best
        y = np.array(N[i])

        #x,y,hcol = trim(x,y,hcol)
<<<<<<< HEAD
        y = hcol[0] - y
        plt.plot(x, y, color_map[i],label=ion_state(i,elem))
        xlims=[np.amin(x), np.amax(x)]
        ylims=[np.amin(y), np.amax(y)]
        try:
            if bounds:
                
                l = minNHI - observed[elem][i]["column"][2]
                if observed[elem][i]["column"][0]==-30.:
                    u=maxNHI
                else:
                    u = maxNHI - observed[elem][i]["column"][0]
                plt.fill(  [-30.,30., 30., -30.], [l,l,u,u], 
                            '0.50', alpha=0.2, edgecolor='b')
                #ax.fill_between(xx, l, u, where=u>=l, facecolor='gray', interpolate=True)
        except KeyError:
            pass
        plt.minorticks_on()
        plt.ylabel(r"log $N_{HI}/N_{%s}$"%(elem+str(roman[i])))
        plt.xlabel(r"log T (K)")
        
        makedir('logT')

        f=os.path.join(paths["plot_path"],"logT", elem+roman[i]+"NT.png")
        plt.xlim([2.,5.])
        #plt.ylim(ylims)



        #plt.xlim(xlims)
        #plt.ylim(ylims)
        plt.show()
        plt.savefig(f)
        plt.close()

def plot_bT(elem,T,b,bounds=False):
    """
    plot b versus T
    parameters:
    -----------
    elem: elem name
    b: b. should be list of lists like: [HI:[...],HII:[...],H2:[...]]
    T: log T. list of lists like N
    """

    for i in to_plot[elem]:
        x = np.array(T[i])   #since data is stored is min, best, max, filter out best
        y = np.array(b[i])
        plt.plot(x, y, color_map[i],label=ion_state(i,elem))
        xlims=[0.75*np.amin(x), 1.25*np.amax(x)]
        ylims=[0.75*np.amin(y), 1.25*np.amax(y)]
        try:
            if bounds:
                
                l = observed[elem][i]["b"][2]
                u = observed[elem][i]["b"][0]
                plt.fill(  [-30.,30., 30., -30.], [l,l,u,u], 
                            '0.50', alpha=0.2, edgecolor='b')
                #ax.fill_between(xx, l, u, where=u>=l, facecolor='gray', interpolate=True)
        except KeyError:
            pass

        plt.ylabel(r"$b_{%s})$"%(elem+str(roman[i])))
        plt.xlabel(r"log T (K)")
        plt.minorticks_on()
        makedir('logT')

        f=os.path.join(paths["plot_path"],"logT", elem+roman[i]+"bT.png")
        #plt.xlim(xlims)
        ##plt.ylim(ylims)

        #plt.xlim(xlims)
        #plt.ylim(ylims)
        plt.show()
        plt.savefig(f)
        plt.close()


def plot_NU(elem,U,N, hcol,bounds=False):
=======
        y = hcol - y
        ax.plot(x, y, color_map[i],label=ion_state(i,element))
    plt.ylabel(r"$log(N_{$HI$}/N)$")
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
>>>>>>> 70bd8703a267b22a816feec9ec803ffaaa7ac5ba
    """
    plot N versus ionization parameter U
    parameters:
    -----------
    elem: elem name
    N: log N. should be list of lists like: [HI:[...],HII:[...],H2:[...]]
    U: log U. list of lists like N
    """

    
    for i in to_plot[elem]:
        plt.clf()
        x = np.array(U,dtype=np.float)
        y = np.array(N[i])
        #x,y,hcol = trim(x,y,hcol)
<<<<<<< HEAD
        y = hcol[0] - y


        xlims=[0.75*np.amin(x), 1.25*np.amax(x)]
        ylims=[0.75*np.amin(y), 1.25*np.amax(y)]
        try:
            if bounds: 
                l = (minNHI - observed[elem][i]["column"][2])#*np.ones(x.shape[0])
                u = (maxNHI - observed[elem][i]["column"][0])#*np.ones(x.shape[0])

                plt.fill([-30.,30., 30., -30.], [l,l,u,u], 
                        '0.50', alpha=0.2, edgecolor='b')
                #ax.fill_between(x, l, u, where=u>=l, facecolor='gray', interpolate=True)
                #plt.fill_between(np.arange(xlims[0],xlims[1]),lower,upper,color='0.50')
        except KeyError:
            pass


        try:
            plt.plot(x, y, color_map[i],label=ion_state(i,elem))
            plt.minorticks_on()
        except ValueError:
            print(x.shape, y.shape)
            print("\n\n")
            raise

        plt.xlim([-5.,-2.5])
        #plt.ylim(ylims)
        plt.ylabel(r"log $N_{HI}/N_{%s}$"%(elem+roman[i]))
        plt.xlabel(r"log U")
        makedir('logU')

        f=os.path.join(paths["plot_path"], "logU", elem+roman[i]+"NU.png")
        plt.show()
        plt.savefig(f)
        plt.close()




def plot_bU(elem,U,b,bounds=False):
    """
    plot b versus ionization parameter U
    parameters:
    -----------
    elem: elem name
    N: log N. should be list of lists like: [HI:[...],HII:[...],H2:[...]]
    U: log U. list of lists like N
    """

    
    for i in to_plot[elem]:
        x = np.array(U,dtype=np.float)
        y = np.array(b[i])
        try:
            plt.plot(x, y, color_map[i],label=ion_state(i,elem))
        except ValueError:
            print(x.shape, y.shape)
            print("\n\n")
            raise
        xlims=[0.75*np.amin(x), 1.25*np.amax(x)]
        ylims=[0.75*np.amin(y), 1.25*np.amax(y)]
        plt.xlim([2.0,5.0])
        ##plt.ylim(ylims)
        plt.ylabel(r"$b_{%s}$"%(elem+roman[i]))
        plt.xlabel(r"log U")
        plt.minorticks_on()
        try:
            if bounds: 
                l = observed[elem][i]["b"][2]#*np.ones(x.shape[0])
                u = observed[elem][i]["b"][0]#*np.ones(x.shape[0])

                plt.fill([-30.,30., 30., -30.], [l,l,u,u], 
                        '0.50', alpha=0.2, edgecolor='b')
                #ax.fill_between(x, l, u, where=u>=l, facecolor='gray', interpolate=True)
                #plt.fill_between(np.arange(xlims[0],xlims[1]),lower,upper,color='0.50')
        except KeyError:
            pass
        makedir('logU')

        f=os.path.join(paths["plot_path"], "logU", elem+roman[i]+"bU.png")
        plt.show()
        plt.savefig(f)
        plt.close()


def plot_NZ(elem,Z,N, hcol,bounds=False):
=======
        y = hcol - y
        ax.plot(x, y, color_map[i],label=ion_state(i,element))
    xlims=[-10.2,0.2]
    ylims=[0.,20.]
    plt.xlim(xlims)
    plt.ylim(ylims)
    plt.ylabel(r"$log(N_{$HI$}/N)$")
    plt.xlabel(r"U")
    if not bounds is None: 
        l = 17.409 - max(bounds)
        u = 17.415 - min(bounds)

        plt.fill([xlims[0],xlims[1],xlims[1],xlims[0]], [l,l,u,u], '0.50', alpha=0.2, edgecolor='b')

        #plt.fill_between(np.arange(xlims[0],xlims[1]),lower,upper,color='0.50')
    plt.savefig('plots/'+element+"NU.png")
    return

def plot_NZ(element,Z,N, hcol,bounds=None):
>>>>>>> 70bd8703a267b22a816feec9ec803ffaaa7ac5ba
    """
    plot N versus T
    parameters:
    -----------
    elem: elem name
    N: log N. should be list of lists like: [HI:[...],HII:[...],H2:[...]]
    T: log T. list of lists like N
    """

    
    for i in to_plot[elem]:
        plt.clf()
        x = np.array(Z,dtype=np.float)
        y = np.array(N[i])
        #x,y,hcol = trim(x,y,hcol)
        y = hcol[0] - y  #NHI-NX

        #xlims=[0.75*np.amin(x), 1.25*np.amax(x)]
        #ylims=[0.75*np.amin(y), 1.25*np.amax(y)]

#-3.78<float(mod.data['U'])<2.95
        try:
            if bounds: 
                l = minNHI - observed[elem][i]["column"][2]
                if observed[elem][i]["column"][0]==-30.:
                    u=maxNHI
                else:
                    u = maxNHI - observed[elem][i]["column"][0]
                plt.fill([-30.,30., 30., -30.], [l,l,u,u], '0.50', alpha=0.2, edgecolor='b')

                #plt.fill_between(np.arange(xlims[0],xlims[1]),lower,upper,color='0.50')
        except KeyError:
            pass
        plt.plot(x, y, color_map[i],label=ion_state(i,elem))
        plt.minorticks_on()

        plt.xlim([-5.,-1.5])
        #plt.ylim(ylims)
        plt.ylabel(r"log $N_{HI}/N_{%s}$"%(elem+roman[i]))
        plt.xlabel(r"log Z (solar units)")
        makedir('Z')

        f=os.path.join(paths["plot_path"], "Z",elem+roman[i]+"NZ.png")
        plt.show()
        plt.savefig(f)
        plt.close()


def plot_ZU(Z,U,bounds=False):
    """
    plot b versus ionization parameter U
    parameters:
    -----------
    elem: elem name
    N: log N. should be list of lists like: [HI:[...],HII:[...],H2:[...]]
    U: log U. list of lists like N
    """

    plt.plot(Z,U,'ko')
    plt.xlabel(r'log Z')
    plt.ylabel(r'log U')
    plt.show()
    plt.close()

def plot_ionization(elem,U,N,hcol):
    plt.clf()
    for i in to_plot[elem]:
        x = np.array(U,dtype=np.float)
        y = np.array(N[i])
        #x,y,hcol = trim(x,y,hcol)
<<<<<<< HEAD
        #y = hcol[0] - y  #NHI-NX
=======
        y = hcol - y
        ax.plot(x, y, color_map[i],label=ion_state(i,element))
    xlims=[-5.0,0.]
    ylims=[0.,20.]
    plt.xlim(xlims)
    plt.ylim(ylims)
    plt.ylabel(r"$log(N_{$HI$}/N)$")
    plt.xlabel(r"Z")
    if not bounds is None: 
        l = 17.409 - max(bounds)
        u = 17.415 - min(bounds)
>>>>>>> 70bd8703a267b22a816feec9ec803ffaaa7ac5ba


        plt.plot(x, y, color_map[i],label=ion_state(i,elem))

    plt.minorticks_on()
    plt.ylabel(r"log $N_{%s}$"%(elem))
    plt.xlabel(r"log U")
    plt.legend(loc='lower right', shadow=True,numpoints=1)

    plt.show()

<<<<<<< HEAD
=======
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
    xlims=[-5.0,-2.]
    ylims=[10.,15.]
    plt.xlim(xlims)
    plt.ylim(ylims)
    plt.ylabel(r"$log(N_{"+element+r" III})$")
    plt.xlabel(r"["+element+r"/H]$")
    if not bounds is None: 
        ly = max(bounds)
        uy = min(bounds)
        lx= min(list(x[xbounds]))
        ux= max(list(x[xbounds]))
        plt.fill([lx,ux,ux,lx], [ly,ly,uy,uy], '0.50', alpha=0.2, edgecolor='b')
    plt.savefig('plots/'+element+"N_NH.png")
>>>>>>> 70bd8703a267b22a816feec9ec803ffaaa7ac5ba


def plot_ionization_(elem,model_lst,xlims=None):



    Zcolor=[ 'red','orangered','orange', 
             'yellow','yellowgreen','green', 'cyan',
             'teal','blue','blueviolet']
    Z = [-4.,-3.8,-3.6,
         -3.4,-3.2,-3.0,-2.8,
         -2.6,-2.4,-2.2]
    for i in to_plot[elem]:
        plt.clf()

        
        if xlims:
            l,u = observed[elem][i]["column"][0], observed[elem][i]["column"][2]
            if l==-30.:  l=0.   
            plt.fill( [xlims[0], xlims[1], xlims[1], xlims[0]], 
                      [l,l,u,u], '0.50', alpha=0.1)
            plt.axhline(y=u,linestyle='dashed',linewidth=2, color='k')


        for j in range(len(Z)):
            mods=[item for item in model_lst if Z[j]-0.05<float(item.data['Z'])<Z[j]+0.05]
            if len(mods)==0:
                print("skipping Z=%lf"%(Z[j]))
                continue
                
            U=[item.data['U'] for item in mods]
            N=Model.get_qty_lst(mods,elem,"column",i)
            #if elem=='Si':
            #    N=[item+1.34 for item in N]  #ISM to popII
            try:
                assert(len(N)>0 and len(U)>0)
            except AssertionError:
                print('N=',N)
                print('U=',U)
                raise



            plt.plot(U, N, 'o', color=Zcolor[j],label="Z="+str(Z[j]))



        plt.minorticks_on()
        plt.ylabel(r"log $N_{%s}$"%(elem+roman[i]))
        plt.xlabel(r"log U")
        plt.legend(loc='lower right', shadow=True,numpoints=1)
        plt.title('%s'%elem+roman[i])
        plt.xlim(min(U),max(U))
        plt.ylim(min(N)-1.,max(N)+1.)
        plt.show()



def plot_TZ(T,Z,bounds=False):
    """
    plot b versus ionization parameter U
    parameters:
    -----------
    elem: elem name
    N: log N. should be list of lists like: [HI:[...],HII:[...],H2:[...]]
    U: log U. list of lists like N
    """

    plt.plot(T,Z,'ko')
    plt.xlabel(r'log Temperature (K)')
    plt.ylabel(r'log Z (solar units)')
    plt.minorticks_on()
    plt.show()
    plt.close()


def plot_nhU(nh,U,bounds=False):
    """
    plot b versus ionization parameter U
    parameters:
    -----------
    elem: elem name
    N: log N. should be list of lists like: [HI:[...],HII:[...],H2:[...]]
    U: log U. list of lists like N
    """

    plt.plot(nh,U,'ko')
    plt.xlabel(r'log $n_{H}$')
    plt.ylabel(r'log U')
    plt.minorticks_on()
    plt.show()
    plt.close()



def plot_NZ(elem,Z,N, hcol,bounds=False):
    """
    plot N versus T
    parameters:
    -----------
    elem: elem name
    N: log N. should be list of lists like: [HI:[...],HII:[...],H2:[...]]
    T: log T. list of lists like N
    """

    
    for i in to_plot[elem]:
        plt.clf()
        x = np.array(Z,dtype=np.float)
        y = np.array(N[i])
        #x,y,hcol = trim(x,y,hcol)
<<<<<<< HEAD
        y = hcol[0] - y  #NHI-NX

        xlims=[0.75*np.amin(x), 1.25*np.amax(x)]
        ylims=[0.75*np.amin(y), 1.25*np.amax(y)]
        try:
            if bounds: 
                l = minNHI - observed[elem][i]["column"][2] 
                if observed[elem][i]["column"][0]==-30.:
                    u=maxNHI
                else:
                    u = maxNHI - observed[elem][i]["column"][0]

                plt.fill([-30.,30., 30., -30.], [l,l,u,u], '0.50', alpha=0.2, edgecolor='b')

                #plt.fill_between(np.arange(xlims[0],xlims[1]),lower,upper,color='0.50')
        except KeyError:
            pass
        plt.plot(x, y, color_map[i],label=ion_state(i,elem))
        plt.minorticks_on()

        #plt.xlim(xlims)
        #plt.ylim(ylims)
        plt.ylabel(r"log $N_{HI}/N_{%s}$"%(elem+roman[i]))
        plt.xlabel(r"log Z (solar)")
        makedir('Z')

        f=os.path.join(paths["plot_path"], "Z",elem+roman[i]+"NZ.png")
        plt.show()
        plt.savefig(f)
        plt.close()


def plot_N(elem,data,trans=0,bounds=True):
    """plot logNX versus [X/H]
    elem:  string.  elem name
    N: 
    hcol
    trans
    bounds
    """
    plt.clf()
    trans=int(trans)
    y = np.array( [ item.data[elem][trans]["column"][1]  for item in data ] )

    xbounds=[]  #i-indices of datapts within bounds 
    n=[]        #number density of elem X


    for i in range(0,y.shape[0]):
        #j = transition
        num=0.
        for j in range(0,ions[elem]):   #note that for most temperature ranges, ionmap may cut off very high ionizations.  not important for my range of interest.
            if j in data[i].data[elem].keys():
                """if j in observed[elem].keys()  and j==trans:
                    try:
                        if observed[elem][j]["column"][0]<= data[i].data[elem][j]["column"][1] <=observed[elem][j]["column"][2]:
                            xbounds.append(i) 
                    except:
                        print(observed[elem][j].keys())
                        print(data[i].data[elem][j].keys())
                        raise
                """
                num+=10.**data[i].data[elem][j]["column"][1]
            else:
                break
        n.append(np.log10(num))
    nH = np.array(
        [np.log10(10.**item.data["H"][0]["column"][1] +\
        10.**item.data["H"][1]["column"][1] +\
        10.**item.data["H"][2]["column"][1]) for item in data]
        )  #get total column for HI, HI and H2


    x = np.array(np.array(n) - nH -(solar[elem] - solar['H']),dtype=np.float)
    assert(x.shape[0]==y.shape[0]>2)
    xlims=[np.amin(x), np.amax(x)]
    ylims=[np.amin(y), np.amax(y)]
=======
        y = hcol - y
        ax.plot(x, y, color_map[i],label=ion_state(i,element))

    xlims=[-3.5,3.5]
    ylims=[0.,20.]
    plt.xlim(xlims)
    plt.ylim(ylims)
    plt.ylabel(r"$log(N_{$HI$}/N)$")
    plt.xlabel(r"$log(n_{$H$})$")
>>>>>>> 70bd8703a267b22a816feec9ec803ffaaa7ac5ba
    if bounds: 
        try:
            ly = observed[elem][trans]["column"][2]
            uy = observed[elem][trans]["column"][0]
            #lx= min(list(x[xbounds]))
            #ux= max(list(x[xbounds]))
            lx= min(xlims)
            ux= max(xlims)
            plt.fill([lx,ux,ux,lx], [ly,ly,uy,uy], '0.50', alpha=0.2, edgecolor='b')
        except:
            pass
    plt.plot(x, y, 'ko')
    plt.minorticks_on()


    #plt.xlim(xlims)
    #plt.ylim(ylims)
#4.07E-4,  -3.39
    plt.ylabel(r"$log(N_{"+elem+roman[trans]+r"})$")
    plt.xlabel(r"$["+elem+r"/H]$")


    f=os.path.join(paths["plot_path"], "N"+elem+roman[trans]+"_NH.png")
    plt.show()
    plt.savefig(f)
    plt.close()


def plot_NHIH(data,bounds=True):
    """plot logNHI versus [HI/H]
    elem:  string.  elem name
    N: 
    hcol
    trans
    bounds
    """
    plt.clf()
    trans=0
    y = np.array( [ item.data["H"][0]["column"][1]  for item in data ] )

    xbounds=[]  #i-indices of datapts within bounds 
    n=[]        #number density of elem X

    nH = np.array( [np.log10(10.**item.data["H"][0]["column"][1] + \
                    10.**item.data["H"][1]["column"][1] + \
                    10.**item.data["H"][2]["column"][1]) for item in data])  #get total column for HI, HI and H2
    nHI = np.array( [item.data["H"][0]["column"][1] for item in data])
    x = np.array(( (y-nH)-solarHIH),dtype=np.float)
    assert(x.shape[0]==y.shape[0]>2)

    xlims=[np.amin(x), np.amax(x)]
    ylims=[np.amin(y), np.amax(y)]
    if bounds: 
        ly = observed["H"][0]["column"][2]
        uy = observed["H"][0]["column"][0]
        #lx= min(list(x[xbounds]))
        #ux= max(list(x[xbounds]))
        lx= min(xlims)
        ux= max(xlims)
        plt.fill([lx,ux,ux,lx], [ly,ly,uy,uy], '0.50', alpha=0.2, edgecolor='b')
    plt.plot(x, y, 'ko')
    plt.minorticks_on()

    ##plt.xlim(xlims)
    ##plt.ylim(ylims)
    plt.ylabel(r"log($N_{HI}$)")
    plt.xlabel(r"[HI/H]")

    f=os.path.join(paths["plot_path"], "N_HI_NH.png")
    plt.savefig(f)

    plt.show()
    plt.close()

def plot_Nhden(elem,N,hcol,hden,bounds=False):
    for i in to_plot[elem]:
        plt.clf()
        x = np.array(hden,dtype=np.float)
        y = np.array(N[i])
        #x,y,hcol = trim(x,y,hcol)
        y = hcol[0] - y
        xlims=[0.75*np.amin(x), 1.25*np.amax(x)]
        ylims=[0.75*np.amin(y), 1.25*np.amax(y)]
        try:
            if bounds: 
                l = minNHI - observed[elem][i]["column"][2] 
                if observed[elem][i]["column"][0]==-30.:
                    u=maxNHI
                else:
                    u = maxNHI - observed[elem][i]["column"][0]
                plt.fill([-30.,30., 30., -30.], [l,l,u,u], '0.50', alpha=0.2, edgecolor='b')

                #plt.fill_between(np.arange(xlims[0],xlims[1]),lower,upper,color='0.50')
        except KeyError:
            pass
        plt.plot(x, y, color_map[i],label=ion_state(i,elem))
        plt.ylabel(r"log $N_{HI}/N_{%s}$"%(str(elem)+str(roman[i])))
        plt.xlabel("log $n_{H}$")
        plt.minorticks_on()

        makedir('hden')

        f=os.path.join(paths["plot_path"],"hden", elem+roman[i]+"N_Nhden.png")

        plt.xlim([-3.,0.])
        #plt.ylim(ylims)
        plt.savefig(f)
        plt.show()
        plt.close()

        

