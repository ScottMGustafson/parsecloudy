import os
import plot_cloudy_output as plot
import config
import numpy as np
from data_structures import LinkedList
import warnings
import variousutils

element_names = config.element_names
species = config.ions
default = -30.000
defaults = [default, default, default]  #  best, upper and lower limits default values
#input_dict = config.get_config_data()
input_dict = {
    "column": "(H2)                Log10 Column density (cm^-2)",
    "ionization": "Log10 Mean Ionisation (over radius)",    
    "ionization_e": "Log10 Mean Ionisation (over radius*electron density)",
    "temp": "Log10 Mean Temperature (over radius)",
    "temp_e": "Log10 Mean Temperature (over radius*electron density)"
}

class Element(object):
    def __init__(self,name,**kwargs):
        self.name=name
        self.species = species[self.name]
        for item in input_dict.keys():
            selfval = kwargs.get(item)
            try:
                assert(len(selfval)==self.species)
            except:
                msg = str(selfval) + "\n  not of correct length: "+ \
                              str(self.species)
                if len(selfval)>self.species:
                    raise Exception(msg)
                else:
                    warnings.warn(msg)
                    while len(selfval)<self.species:
                        selfval.append(default)
            setattr(self,item,selfval)

    def __eq__(self,observed):
        if not isinstance(observed,ObsData):
            msg = """
              the point of this comparison operator is to compare model 
              data to observed data.  What are you doing?"""
            raise Exception(msg)
        if observed.name!=self.name:
            return False
        for item in input_dict.keys():
            for i in range(species[self.name]):
                selfval = getattr(self,item)
                obsval  = getattr(observed,item)
                if obsval = defaults: #if all default case, skip
                    continue
                upper = obsval[i][-1] 
                lower = obsval[i][0]
        
                if isinstance(self,ObsData):
                    selfmin, selfbest, selfmax = tuple(selfval[i])
                else:
                    selfmin, selfbest, selfmax = tuple(selfval[i],selfval[i],selfval[i])
                #code will ignore default cases
                if upper == default:  upper=selfbest 
                if lower == default:  lower=selfbest
                
                if lower > selfmax or selfmin > upper:
                    return False
        return True

    def __ne__(self,observed):
        return not self.__eq__(observed)
                    
                
class ObsData(Element):
    def __init__(self,name,state,**kwargs):
        """
        Subclass of Element.   Each physical quantity as list :[min, best, max] 
        where min and max correspond to upper and lower limits.
        """
        
        self.state = int(state)
        for key, val in kwargs.iteritems():
            kw[key] = [ defaults for i in range(species[name]) ]
            kw[key][int(state)] = val
        super(ObsData,self).__init__(name,**kw)

    def join(self,absorber):
        """
        join another obsData instance with the current one
        """
        name = self.name+variousutils.int_to_roman(self.state)
        absname=absorber.name+variousutils.int_to_roman(absorber.state)
        if self.state == absorber.state:
            msg='cannot join absorbers:  same state '+ \
                name + '=='+ absname +'\n'
            raise Exception(msg)
        for item in input_dict.keys():
            try:
                setattr(self,item[absorber.state],absorber.item[absorber.state])
            except:
                raise Exception('cannot join two absorbers: %s, %s\n' % (name,absname))

class Model(object):
    def __init__(self,fstream,input_dict=input_dict):
        """
        each attribute will be a dict of lists with each list element 
        corresponding to a different ionization state

        input parameters:
        -----------------
        fstream: a filestream-like list of data from cloudy output
        input_dict : dict of input data as defined above
        """

        data = {}
        for key,val in input_dict.iteritems():
            data[key] = self._get_vals(fstream,val))

        self.elem = []
        for key, val in element_names.iteritems():
            item['name']=val
            for attr in data.keys():
                item[attr] = data[attr][key] 
                elem = Element(**item)
            self.elem[elem.name] = elem

    def __str__(self):
        return "a string of the model"


    def _get_vals(self, fstream, key):
        """
        parse value for some element's attribute given by key

        input parameters:
        -----------------
        fstream : standard cloudy output file
        key :     name of attribute according to cloudy output.
        for example, column density would be 
            `key = "Log10 Column density (cm^-2)"`

        output:
        -------
        a dict of key, val where:
        key  = element name
        val  = list of ions' attribute: val[0]=neutral, val[n]=nth ionization
        """

        if type(fstream) == file:
            fstream = [ item for item in getNonBlank(open(fstream,'r')) ]

        lst = retrieve_section(fstream,key)
        h_dat = lst.pop(0)[1:4]  #need to 4 since text is included in this line
        output = {element_names['Hydrogen']:h_dat}

        for row in lst:  #repeat for other elements what we did for H
            try:
                map(float, row[1:])
            except:
                raise Exception(row)
            output[element_names[row[0]]] = row[1:]
        return output 

def retrieve_section(datastream, section_key):

    """
    retrieve a section's data.  note that this may sometimes go over multiple lines

    Parameters:
    ===========
    datastream:  list of data.  one line per element
    section_key: key name for the section of interest.  This may (unfortunately) be in the first line of data
    separator:   separator in text that separates this from other sections

    output:
    =======
    dict of parsed data
    """
    #strip off blank lines and comments
    llst = LinkedList([ item for item in getNonBlank(datastream) ])
    ret_data = []

    curr = llst.head
    while curr is not None:
        if section_key in curr.data:
            while "Zinc" not in curr.data:
                ret_data.append(curr.data)
                curr=curr.next
        else:
            curr=curr.next
    if ret_data[0][:8]=='Hydrogen':
        ret_data = mult_lines(ret_data)
    return ret_data

def mult_lines(lst,keys=element_names.keys()):
    """
    sometimes the output crosses over multiple lines.  takes the extra lines 
    and appends them to the primary line.

    Parameters:
    ===========
    lst: input data (one section of data from retrieve_section)

    output:
    =======
    returns reformatted data list
    """

    out_list = []

    for item in lst:
        item = (item.replace('-',' -')).strip()
        if item.split()[0] in keys:
            out_list.append(item.split())
        else:
            try:
                out_list[-1]+=item.split()
            except:
                raise Exception("first list item not element name: "+str(out_list))
    return out_list

def getNonBlank(filestream):
    """return lines which are neither empty, nor contain any # symbols"""
    for line in filestream:
        lines = line.strip()
        if len(lines)>0 and lines[0] not in '#*':
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

def write_out(data, element, return_data=False):
    """
    input params:
    -------------
    data_lst: list of Model instances
    key:  a string of which attribute to parse.
    element: a string of which element.

    output:
    -------
    if return_data is false:
        data file named `<element>_<key>.dat` of the format:
        (assuming element name X...)
            ```
            <datum for X_I>  <datum for X_II>  <datum for X_III (or H2 if X==H)>

            ```
    if return_data is True:
        list of lists in the same format as above
    """

    ret_dict = {}
    for key in input_dict.keys():
        if not return_data:
            f = open(element+"_"+key+".dat",'w')
            for item in data:
                f.write(item.get_element(element, key)+"\n")
            f.close()
        else: 
            ret_dict[key] = [getattr(item,key)[element] for item in data ]
    return ret_dict
    
def search(observed_vals, model_data):
    """
    convert observed vals into a Model instance with tolerances defined by 
    upper and lower limits:  each entry like 
      `{ionname : {ion : num, qty1 : [best, lowest, highest], qty2 : [b,l,h], ...} }`
    ion is which state its in.  0=Neutral, 1=singly ionized, etc
    qty is any quantity like logN, logU, etc
    
    suppose you observed CIV with logN=14+/-0.1.
    entry would be:
    '{ C: { ion:3, column:[14,13.9,14.1] } }'
    
    input params:
    =============
    observed_vals: a list of ObsData instances corresponding to all observed 
        quantities.  For now this means only one absorption system.
    model_data: list of Model instances
    
    output:
    =======
    model w/ observed values (within tolerances)
    """

    for model in model_data:
        result = [ observed_vals[key]==model.elem[key] for key in observed_vals.keys() ] 
        if len(set(result))==1 and result[0]==True:  #if all elements in result are True:
            return model
    return None
            
            
        

def get_observed(fstream=open("observed_data.dat","r"))
    """
    format of observed data should be:
    C 2 column lower best upper

    <element name (symbol)> <ionization state> <quantity> lower, best, upper estimate

    quantity should follow input_dict's keys
    """

    out={}
    for item in getNonBlank(fstream):
        name, state, qty, low, best, hi = tuple(item.split())
        if qty in input_dict.keys():
            lst = input_dict.keys()
            dat = {'name':name,lst[lst.index(qty)]=[low,best,hi]}
            if name in out.keys():
                out[name].join(ObsData(name, state, **dat))
            else:
                out[name] = ObsData(name, state, **dat)
        else:
            raise Exception(qty+" not in "+str(input_dict.keys()))
    return out

        
    
      
def main():
    all_outputs = []
    outpath = os.path.join(os.getcwd(),'output')
    for item in os.listdir(outpath):
        if item.endswith(".out"):
            all_outputs.append( [f for f in getNonBlank(open(os.path.join(outpath,item)))] )

    #stored as list of Model instances
    all_data = [ Model(item) for item in all_outputs ]
    
    hdat = write_out(all_data, 'Hydrogen', return_data=True)
    hcol = np.array( [ item[0] for item in hdat['column'] ], dtype=np.float)  #neutral H column



    obs_vals = get_observed()
    model = search(obs_vals, all_data)
    print(str(model))

    """
    for element in ['Silicon', 'Carbon', 'Oxygen']:
        data = write_out(all_data, element,return_data=True)  

        plot.plot_NT(element_names[element], data['temp'], data['column'], hcol)
        plot.plot_NU(element_names[element], data['ionization_e'], data['column'], hcol)
    """


if __name__ == '__main__':
    main()

 
