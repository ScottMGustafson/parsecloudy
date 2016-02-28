import matplotlib.pyplot as plt
import numpy as np
plt.rc('text',usetex=True)
plt.rc('font', family='serif',size=16)
f, (C_ax, Si_ax) = plt.subplots(2, sharex=True, figsize=[4.2,5.])

xlims=[-4.0,-2.5]
ylims=[0.,1.0]

bounds = { 'C':[12.55,12.66], 'Si':[11.52,11.72]}

xx = np.linspace(xlims[0],xlims[-1],1000)

def get_tot_bounds(logtot,logN, delta):
    tot = 10.**logtot
    dtot = np.log(10.)*np.exp(logN)*delta
    return dtot


def find_nearest(arr, val):
    return (np.abs(arr-val)).argmin()

def plot_it(ax,element,coords):
    x,I,II,III,IV,V,N_tot,NIII = np.loadtxt(element+'_frac_out.dat',unpack=True)

    Nerr = (max(bounds[element])-min(bounds[element]))/2.
    toterr = get_tot_bounds(N_tot, NIII, Nerr)


    u=max(bounds[element])
    l=max(bounds[element])
    ind = list(set(np.where(NIII<=u+0.2)[0])&set(np.where(NIII>=l-0.2)[0]))

    #yerr = np.abs(NIII[ind]/N_tot[ind])*np.sqrt((Nerr/NIII[ind])**2 + (toterr[ind]/N_tot[ind])**2) 

    z1 = np.poly1d(np.polyfit(x,I,5))
    z2 = np.poly1d(np.polyfit(x,II,5))
    z3 = np.poly1d(np.polyfit(x,III,5))
    z4 = np.poly1d(np.polyfit(x,IV,5))
    z5 = np.poly1d(np.polyfit(x,V,5))
    logN =  np.poly1d(np.polyfit(x,NIII,5))

    #err = np.poly1d(np.polyfit(x[ind],yerr,5))

    #ax.plot(x,I,  'ko',label=element+'I')
    #ax.plot(x,II, 'bo',label=element+'II')
    #ax.plot(x,III,'co',label=element+'III')
    #ax.plot(x,IV, 'go',label=element+'IV')
    #ax.plot(x,V,  'ro',label=element+'V')

    ax.plot(xx,z1(xx),'k-',label=element+'I')
    ax.plot(xx,z2(xx),'b',label=element+'II')
    ax.plot(xx,z3(xx),'c-',label=element+'III')
    ax.plot(xx,z4(xx),'g-',label=element+'IV')
    ax.plot(xx,z5(xx),'r-',label=element+'V')
    #ax.errorbar(x[ind],III[ind],yerr=yerr,fmt='o')
    #ax.text(coords[0][0],coords[0][1],element+'I')
    ax.text(coords[1][0],coords[1][1],element+'II',size=12)
    ax.text(coords[2][0],coords[2][1],element+'III',size=12)
    ax.text(coords[3][0],coords[3][1],element+'IV',size=12)
    ax.text(coords[4][0],coords[4][1],element+'V',size=12)
    
    ax2=ax.twinx()
    ax2.plot([-2.9,-2.9],[0,1])
    plt.setp(ax2.get_yticklabels(), visible=False)
    #l=xx[find_nearest(np.array(N(xx)),min(bounds[element]))]
    #u=xx[find_nearest(np.array(N(xx)),max(bounds[element]))]

#axis options
#C_ax.get_yaxis().get_major_formatter().set_useOffset(False)
#Si_ax.set_xticks(np.arange(-8.5,-6.,.5))
#Si_ax.set_ylim( [-4.3,-4.4])
#Si_ax.set_xlim([-8.5,-6.])
#C_ax.set_ylim([1832.,1835.])
#C_ax.set_yticks(np.arange(1832.,1835.,.5))

#plt.gca().get_yaxis().get_major_formatter().set_useOffset(False)

plot_it(Si_ax,'Si',[[-2.48,0.],[-2.48,-0.04],[-2.48,0.7],[-2.48,0.05],[-2.48,0.14]])
plot_it(C_ax,'C',[[-2.48,-0.05],[-2.48,0.11],[-2.48,0.82],[-2.48,0.03],[-2.48,-0.033]])

Si_ax.set_ylabel(r"$N_X/N_{Si}$")
C_ax.set_ylabel(r"$N_X/N_{C}$")
Si_ax.set_xlabel(r"$log(U)$")

Si_ax.set_xlim(xlims)
Si_ax.set_ylim(ylims)
C_ax.set_ylim(ylims)

plt.subplots_adjust(left=0.17, right=0.9, top=0.9, bottom=0.1)
#plt.gcf().tight_layout()

plt.savefig('plots/ionfrac.png')
