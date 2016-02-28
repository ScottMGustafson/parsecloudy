import math
import sys

u=931.494061 #eV/c^2   w/ c in km/s  (or equivalently, but less relevantly, MeV/c^2 w c in m/s)
kb=8.6173324 #in eV/K
#u=1.660538921E-27  #in kg
#kb=1.3806488E-23 #in J/K

mass_dict = {
    'C':12.0107,
    'Si':28.0855,
    'O':15.9994,
    'H':1.007825,
    'N':14.0067
}

mass = mass_dict[sys.argv[1]]*u  #in ev/c^2
T=float(sys.argv[2])   #b in km/s
b = math.sqrt(2.*T*kb/mass)
#T=0.5*b*b*mass/kb  #mass in kelvin

print("b >= %lf"%(b))




