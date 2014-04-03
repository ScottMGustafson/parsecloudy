#import configparser
from configparser import ConfigParser

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
    'P':16,
    'S':17,
    'Cl':18,
    'Ar':19,
    'K':20,
    'Ca':21,
    'Sc':22,
    'Ti':23,
    'V':24,
    'Cr':25,
    'Mn':26,
    'Fe':27,
    'Co':28,
    'Ni':29,
    'Cu':30,
    'Zn':31
}


def get_config_data(config_file='config_data.cfg'):
    config = ConfigParser()
    config.read(config_file)
    return config

