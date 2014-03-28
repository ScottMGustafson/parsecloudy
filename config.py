#import configparser
from ConfigParser import ConfigParser

element_names = {
 'Hydrogen':'H',
 'Helium':'He',
 'Lithium':'Li',
 'Beryllium':'Be',
 'Boron':'B',
 'Carbon':'C',
 'Nitrogen':'N',
 'Oxygen':'O',
 'Fluorine':'F',
 'Neon':'Ne',
 'Sodium':'Na',
 'Magnesium':'Mg',
 'Aluminium':'Al',
 'Silicon':'Si',
 'Phosphorus':'P',
 'Sulphur':'S',
 'Chlorine':'Cl',
 'Argon':'Ar',
 'Potassium':'K',
 'Calcium':'Ca',
 'Scandium':'Sc',
 'Titanium':'Ti',
 'Vanadium':'V',
 'Chromium':'Cr',
 'Manganese':'Mn',
 'Iron':'Fe',
 'Cobalt':'Co',
 'Nickel':'Ni',
 'Copper':'Cu',
 'Zinc':'Zn'
}

ions = {  #how many states allowed for each
    'H':3,
    'He':3,
    'Li':4,
    'Be':5,
    'B':6,
    'C':7,
    'N':8,
    'O':9,
    'F':10,
    'Ne':11,
    'Na':12,
    'Mg':13,
    'Al':14,
    'Si':15,
    'P':15,
    'S':16,
    'Cl':16,
    'Ar':17,
    'K':17,
    'Ca':18,
    'Sc':18,
    'Ti':18,
    'V':19,
    'Cr':19,
    'Mn':19,
    'Fe':19,
    'Co':20,
    'Ni':21,
    'Cu':21,
    'Zn':21
}

#  this separates out results separated by diff ionization states
notes="NOTE"
trimflag='-30.000'

def get_config_data(config_file='config_data.cfg'):
    config = ConfigParser()
    config.read(config_file)
    return config
