#import configparser
from configparser import ConfigParser
import os
from variousutils import *



def get_config_data(config_file=os.path.join('data','config_data.cfg')):
    config = ConfigParser()
    config.optionxform=str
    config.read(config_file)
    return config

def dict_update(elem, trans, qty, val, a={}):
    """a and b are two dicts. b has as many layers as a, but only one datum
       insert b into a """
    if elem in list(a.keys()):
        if trans in list(a[elem].keys()):
            if qty in list(a[elem][trans].keys()):
                pass #if entry already present, then this is an error
            else:
                a[elem][trans][qty]=val
        else:
            a[elem][trans] = {qty:val}
    else:
        a[elem] = {trans:{qty:val}}
    return a


def init_dict(fname):
    """
    parse the constraints or observed data.
    format of access is
    d[elem][transition][quantity] = (min, best, max)
    """
    d={}
    for line in getNonBlank(fname):
        if line[0] in ['Z','U','hden']:
            try:
                qty, mn,mx = tuple(line.split())
                mn=float(mn)
                mx=float(mx)
                d[qty] = [min([mn,mx]), (mn+mx)/2., max([mn,mx])]
            except ValueError:
                qty, mn, best, mx = tuple(line.split())
                mn=float(mn)
                mx=float(mx)
                d[qty] = [min([mn,mx]), best, max([mn,mx])]
        else:
            elem, trans, qty, mn, best, mx = tuple(line.split())
            trans = int(trans)
            vals = tuple(map(float, (mn,best,mx)))
            
            d = dict_update(elem, trans, qty, vals, d)
            
    return d

configDict = get_config_data()

default    = float(configDict['Config']['default'])
try:
    nproc    = int(configDict['Config']['processes'])
except:
    from multiprocessing import cpu_count
    nproc=cpu_count()
    print("running %d processes\n"%nproc)
ions       = {key:int(val) for key, val in dict(configDict['Species']).items()}
elem_names = dict(configDict.items('Element Names'))
input_dict = dict(configDict.items('Output Data'))
paths      = dict(configDict.items('paths'))
plotpath   = paths['plot_path']
observed = init_dict(paths['observed_data'])

constraints = init_dict(paths['constraint_data'])
roman= [
        "I","II","III","IV","V",
        "VI","VII","VIII","IX","X",
        "XI","XII","XIII","XIV","XV"
       ]



#access for observed is observed[elem symbol][transition num][quantity] = tuple(min, best, max)
    
other_attrs={
    "Z":'metals',
    "U":"***> Log(U):",
    "hden":'hden',
    "radius":"* radius",   
    "z_cmb": "* CMB redshift",  
    "stoptemp":"* stop temperature =", 
    "fnu":"* f(nu) ="
    }
    
"""
to_plot={
    "C":[1,2,3],
    "N":[0],
    "Si":[1,2,3],
    "O":[0,5],
    "Fe":[1],
    "Al":[1],
    }

"""
to_plot={
    "C":[0,1,2,3],
    "Si":[1,2,3],
    #"O":[0,5],
    }



if not os.path.isdir('plots/'):
    from subprocess import call
    call("mkdir %s"%(plotpath), shell=True)
