import config
import os, sys
import plot_cloudy_output as plot
import numpy as np
from core import *
from variousutils import getNonBlank, get_ind, ion_state, K_to_b
import warnings
from time import time



def main():
    pt0 = time()
    
    all_data = []
    survivors=[]


    print('starting')
    for item in walk_dirs(config.configDict["paths"]["start_dir"]):
        if item.endswith('.out'):
            try:
                mod=Model(fname=item)
            except:
                continue

            t=0
            while t<len(mod.data['Si'].keys()):
                a=mod.data['Si'][t]['column']
                #boost columns by a factor of 2 to make popII. also boost by factor of 1.04 dex, since initially used ISM abundnaces
                mod.data['Si'][t]['column']=tuple((a[0]+1.34, 
                                                   a[1]+1.34, 
                                                   a[2]+1.34))
                t+=1

            """
            pass: 1
            CIII: temp 4 -- 4.29
                    Z  == -4.33 -- -1.
            SiII:  Z<-1.63


            pass 2
            CIII:  T=4.03--4.29
            CIII:   U>-4.56
            SiIII:  SiIII nh<-0.3


            pass 3
            CIII:  Z<-1.9
            SiIII:  Z<-2.48

            pass 4:  
            CIII:  U>-4.05
            CIII:  nh<-.85

            SiIII:  U>-4.22
            SiII:  Z<-2.59
            SiIII:  nh<-0.7


            pass 5:
            SiII:  Z<-2.77

            final pass:
            [HI/H] = -1.33 -- -2.54
            """
            all_data.append(mod)
            if 4.03<mod.data['H'][0]['temp'][1]<4.3 \
                and -4.33<float(mod.data['Z'])<-2.77\
                and -4.05<float(mod.data['U'])\
                and float(mod.data['hden'])<-.85:
               
                print(item[-12:])
                survivors.append(mod)

    pt1=time()
    print("walk and load=%lf" % (pt1-pt0))
    print("out of %d files"%len(all_data))

    survivors = filter_models(survivors)   

    pt2=time()
    print("filter=%lf" % (pt2-pt1)) 

    if len(survivors)<1:
        print("no survivors...")
        return
    else:
        print("%d models survived."%len(survivors))
    #for item in survivors:
    #    str(item)


    hdat, hcol= [], [[],[],[]]
    for item in survivors:
        try:
            hdat.append(item.data["H"])
        except KeyError:
            print("available keys: ",item.data.keys())

    for j in [0,1,2]:
       for i in range(0,len(hdat)):
            try:
                hcol[j]=hdat[i][j]["column"][1]
            except IndexError:
                print(i, len(hdat)-1)
                print(j, 3-1)
                raise

    pt3=time()
    print("get hcol: %lf"%(pt3-pt2))

    #survivors = [item for item in survivors if float(item.data['Z'])<-2.]
    #survivors = [item for item in survivors if float(item.data['temp'])>4.08]
    #survivors = [item for item in survivors if float(item.data['U'])<-2.]
    #survivors = [item for item in survivors if float(item.data['hden'])<-1.]




    temp =Model.get_qty_lst(survivors,'H',"temp",0)
    hden = [item.data['hden'] for item in survivors]
    U    = [item.data['U']    for item in survivors]
    Z    = [item.data['Z']    for item in survivors]


    

    plot.plot_TZ(temp,Z)
    plot.plot_ZU(U,Z)
    plot.plot_NHIH(survivors,True)
    plot.plot_nhU(hden,U)


    for elem in config.to_plot.keys():
        bounds=config.observed[elem]
        column, temp = [], []
        for i in range(0,config.ions[elem]):

            column.append(Model.get_qty_lst(survivors,elem,"column",i))
            temp.append(Model.get_qty_lst(survivors,elem,"temp",i))
            if len(column[-1])!=len(survivors):
                column[-1] = config.default*np.ones( len(survivors) ) 
            if len(temp[-1])!=len(survivors):
                temp[-1]   = config.default*np.ones( len(survivors) ) 
        """
        try:
            b=[ [K_to_b(elem,item) for item in temp[i]] for i in range(len(temp)) ]
        except:
            print("parsing b failed.  prolley a bug")
            raise
        try:
            plot.plot_bT(   elem, temp,  b, True)#, xlims=[1.,5.], ylims=[10., 16.5])
        except:
            print("plotting bT failed.  prolley a bug")
        
        try:
            plot.plot_bU(   elem, U,     b, True)#, xlims=[-3.5,0.], ylims=[10., 16.5])
        except:
            print("plotting bU failed.  prolley a bug")
        """
        data = [item.data[elem] for item in survivors] 


        #if elem=='Si':
        #    for i in range(len(column)):
        #        column[i]+=1.34  #ISM to popII

           
        plot.plot_ionization_(elem, all_data, xlims=[min(U), max(U)])#, xlims=[1.,5.], ylims=[10., 16.5])
        plot.plot_NT(   elem, temp,  column, hcol, True)#, xlims=[1.,5.], ylims=[10., 16.5])
        plot.plot_NU(   elem, U,     column, hcol, True)#, xlims=[-3.5,0.], ylims=[10., 16.5])

        plot.plot_NZ(   elem, Z,     column, hcol, True)#, xlims=[-4.,-0.5], ylims=[10., 16.5])
        plot.plot_Nhden(elem, column,hcol,   hden, True)#, xlims=[-3.5,1.5], ylims=[10., 16.5])
        try:
            pass#plot.plot_frac( elem, U,     column)
        except: 
            print('cannot run plot_frac')



    for elem in config.to_plot.keys():
        for trans in config.to_plot[elem]:
            try:
                pass                
                #plot.plot_N(elem, survivors,trans,True)
            except IndexError:
                pass

    pt4=time()
    print("plot and finish: %lf" % (pt4-pt3))



if __name__ == '__main__':
    main()


