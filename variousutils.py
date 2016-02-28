from math import log10, sqrt
import gzip

u=931.494061 #eV/c^2   w/ c in km/s  (or equivalently, but less relevantly, MeV/c^2 w c in m/s)
kb=8.6173324 #in eV/K

amu = {
        "H":1.00794,
        "C":12.0107,
        "N":14.00674,
        "Fe":55.845,
        "Si":28.0855,
        "O": 15.9994,
        "Al":26.981539,
        "D":2.014102
      }

def int_to_roman(n):
    """
    Convert an integer to Roman numerals.
    """
    if not type(n) is int:
        raise ValueError('type must be int.  instead got '+str(type(n)))   
    ints = (10,  9,   5,  4,   1)
    nums = ('X','IX','V','IV','I')
    result = ""
    for i in range(len(ints)):
        count = int( n / ints[i])
        result += nums[i] * count
        n -= ints[i] * count

    return result


def ion_state(i,element):
    """
    append ionization state to element.
    following cloudy convention, i==2 means molecular Hydrogen for element==H
    
    """
    if i==2 and element=='H':
        return r"H_2"
    else:
        return element+int_to_roman(i+1)

def getNonBlank(file):
    """return lines which are neither empty, nor contain any # symbols"""
    if file.endswith('.gz'):
        f = gzip.open(file, 'r')
    else:
        f=open(file,'r')
    filestream = f.readlines()
    f.close()

    for line in filestream:
        lines = line.strip()
        if len(lines)>0 and lines[0] != '#':
            yield lines 

def get_ind(fstream, string):
    """
    returns index of first instance of `string` in filestream `fstream`

    input params:
    -------------
    fstream : a filestream or list of strings
    string : substring in fstream for which to search

    output:
    -------
    index of first instance, i.e. what line does the string first appear
    """
    for i in range(len(fstream)):
        if string in fstream[i]:
            return i
    raise Exception("\""+string+"\" not found")

def b_to_K(elem,val):
    mass = amu[elem]*u  #in ev/c^2
    b=float(val)   #b in km/s
    return log10(0.5*b*b*mass/kb )

def K_to_b(elem, val):
    mass = amu[elem]*u  #in ev/c^2
    T=float(10.**val)   #b in km/s
    return sqrt(2.*T*kb/mass)
    
    

