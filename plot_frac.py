import matplotlib.pyplot as plt
import numpy as np
from config import paths
import os

path=paths['plot_path']

#plot ion fractions for C and Si

f, (C_ax, Si_ax, O_ax) = plt.subplots(3, sharex=True, figsize=[4.2,9.])


color_map={
    0:'k-',
    1:'b-',
    2:'c-',
    3:'g-',
    4:'y-',
    5:'r-',
    6:'m-',
    7:'k-',
    8:'b-',
    9:'c-',
    10:'g-'
}

xlims=[-4.0,-1.05]
ylims=[0.,1.0]

bounds = { 'C':[12.5,14.5], 'Si':[13.,15.], 'O':[-31.,14.]}

xx = np.linspace(xlims[0],xlims[-1],1000)

def get_tot_bounds(logtot,logN, delta):
    tot = 10.**logtot
    dtot = np.log(10.)*np.exp(logN)*delta
    return dtot


def find_nearest(arr, val):
    return (np.abs(arr-val)).argmin()

def plot_it(ax,element):
    data = np.loadtxt(os.path.join(path,element+'_frac_out.dat'), unpack=True)
#x,I,II,III,IV,V,VI,VII,N_tot,NIII
    x=list(data).pop(0)
    NIII=list(data).pop(-1)
    N_tot=list(data).pop(-1)

    Nerr = (max(bounds[element])-min(bounds[element]))/2.
    toterr = get_tot_bounds(N_tot, NIII, Nerr)


    u=max(bounds[element])
    l=max(bounds[element])
    ind = list(set(np.where(NIII<=u+0.2)[0])&set(np.where(NIII>=l-0.2)[0]))

    """ 
    z1 = np.poly1d(np.polyfit(xx,I,8))
    z2 = np.poly1d(np.polyfit(xx,II,8))
    z3 = np.poly1d(np.polyfit(xx,III,8))
    z4 = np.poly1d(np.polyfit(xx,IV,8))
    z5 = np.poly1d(np.polyfit(xx,V,8))
    logN =  np.poly1d(np.polyfit(xx,NIII,8))

    ax.plot(xx,z1(xx),'k-',label=element+'I')
    ax.plot(xx,z2(xx),'b-',label=element+'II')
    ax.plot(xx,z3(xx),'c-',label=element+'III')
    ax.plot(xx,z4(xx),'g-',label=element+'IV')
    ax.plot(xx,z5(xx),'r-',label=element+'V')
    """
    for i in range(len(list(data))):
        z=np.poly1d(np.polyfit(x,data[i],8))
        ax.plot(xx,z(xx),color_map[i])
   



#axis options
#C_ax.get_yaxis().get_major_formatter().set_useOffset(False)
#Si_ax.set_xticks(np.arange(-8.5,-6.,.5))
#Si_ax.set_ylim( [-4.3,-4.4])
#Si_ax.set_xlim([-8.5,-6.])
#C_ax.set_ylim([1832.,1835.])
#C_ax.set_yticks(np.arange(1832.,1835.,.5))

#plt.gca().get_yaxis().get_major_formatter().set_useOffset(False)

plot_it(Si_ax,'Si')
plot_it(C_ax,'C')
plot_it(O_ax,'O')

#manually set coordinates for labels
Si_ax.text(-1.,0.03,'SiIII')
Si_ax.text(-1.,0.6,'SiIV')
Si_ax.text(-1.,0.11,'SiII')
Si_ax.text(-1.,0.19,'SiVI')

C_ax.text(-1.,0.03,'SiIII')
C_ax.text(-1.,0.6,'SiII')
C_ax.text(-1.,0.11,'SiIV')
C_ax.text(-1.,0.19,'SiVI')
O_ax.text(-1.,0.03,'OIII')
O_ax.text(-1.,0.6,'OIV')
O_ax.text(-1.,0.10,'OII')
O_ax.text(-1.,0.18,'OVI')
O_ax.text(-1.,0.23,'OVIII')

Si_ax.set_ylabel(r'$N_X/N_{Si}$')
C_ax.set_ylabel(r'$N_X/N_{C}$')
O_ax.set_ylabel(r'$N_X/N_{O}$')
O_ax.set_xlabel(r"$log(U)$)")

Si_ax.set_xlim(xlims)
Si_ax.set_ylim(ylims)
C_ax.set_ylim(ylims)
O_ax.set_ylim(ylims)

plt.subplots_adjust(left=0.17, right=0.9, top=0.9, bottom=0.1)
#plt.gcf().tight_layout()

plt.savefig(os.path.join(path,'ionfrac.png'))
