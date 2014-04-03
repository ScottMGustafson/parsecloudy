#import configparser
from configparser import ConfigParser

def get_config_data(config_file='config_data.cfg'):
    config = ConfigParser()
    config.optionxform=str
    config.read(config_file)
    return config

configDict = get_config_data()

default    = float(configDict['Config']['default'])
ions       = {key:int(val) for key, val in dict(configDict['Species']).items()}
elem_names = dict(configDict['Element Names'])
input_dict = dict(configDict['Output Data'])
paths      = dict(configDict['paths'])

