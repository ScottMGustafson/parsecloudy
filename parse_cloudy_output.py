import os
import plot_cloudy_output as plot
import config
import numpy as np
from data_structures import LinkedList
import warnings
import variousutils

element_names = config.element_names
species = config.ions
default = -30.000000
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
        self.name=name  #symbol of element (w/o ionization state)
        self.species = species[self.name]
        #print("%s:%d"%(self.name,species[self.name]))
        for item in input_dict.keys():
            selfval = kwargs.get(item,[defaults for i in range(self.species)])
            #correct number of args?
            try:  
                assert(len(selfval)==self.species)
            except:
                if len(selfval)>self.species:
                    msg = str(selfval) + "\n  not of correct length "+ \
                              str(self.species)
                    raise Exception(msg)
                else:
                    while len(selfval)<self.species:
                        selfval.append(defaults)
            #include [min,best,max] for each.  
            for i in range(len(selfval)):  
                if not type(selfval[i]) is list:
                    selfval[i] = [selfval[i], selfval[i], selfval[i]]
                else:
                    assert(len(selfval[i])==3)
            #print(selfval)
            setattr(self,item,selfval)

    def __eq__(self,observed):
        if observed.name!=self.name:
            return False
        for item in input_dict.keys():
            if not self._attr_eq(observed,item):
                return False
        return True

    def __ne__(self,observed):
        return not self.__eq__(observed)

    def __str__(self):
        out='\n'
        for i in range(species[self.name]):
            out += "    %s: N=%5.3lf U=%5.3lf Ue=%5.3lf T=%5.3lf Te=%5.3lf\n" % \
                (variousutils.ion_state(i,self.name),getattr(self,'column')[i][1],
                getattr(self,'ionization')[i][1],getattr(self,'ionization_e')[i][1], 
                getattr(self,'temp')[i][1],getattr(self,'temp_e')[i][1])
        out+='\n'
        return out

    def _attr_eq(self,observed,item):
        selfval = getattr(self,item)
        obsval  = getattr(observed,item)
        for i in range(species[self.name]):
            if obsval[i] == defaults: #if all default case, skip
                continue
            def checklen(lst):
                if not type(lst) is list:
                    lst = [lst, lst, lst]
                else:
                    assert(len(lst)==3)
                return lst

            selfval[i] = checklen(selfval[i])
            obsval[i]  = checklen( obsval[i])

            obsmin,  obsbest,  obsmax  = tuple(obsval[i]) 
            selfmin, selfbest, selfmax = tuple(selfval[i])


            def overlap(a,b):
                conda = a[2] >= b[0] if a[2]!=b[0]!=default else True
                condb = a[0] <= b[2] if a[0]!=b[2]!=default else True
                return conda and condb

            if not overlap(obsval[i],selfval[i]):
                print("self.%s[%i] != other.%s[%i]"%(item,i,item,i))
                print("other.%s[%i]=[%lf, %lf, %lf]"%(item,i,obsmin,obsbest,obsmax))
                print("self.%s[%i]=[%lf, %lf, %lf]"%(item,i,selfmin,selfbest,selfmax))
                return False
        return True
        
                    
                
class ObsData(Element):
    def __init__(self,name,state,**kwargs):
        """
        Subclass of Element.   Each physical quantity as list :[min, best, max] 
        where min and max correspond to upper and lower limits.
        """
        self.name = name
        self.state = int(state)
        superkwargs={}
        for key, val in kwargs.iteritems():
            superkwargs[key] = [defaults for i in range(species[self.name])]
            superkwargs[key][int(state)] = val
        super(ObsData,self).__init__(name,**superkwargs)

    def join(self,absorber):
        """
        join another obsData instance with the current one
        """
        name = self.name+variousutils.int_to_roman(self.state)
        absname=absorber.name#+variousutils.int_to_roman(absorber.state)
        if self.state == absorber.state:
            msg='cannot join absorbers:  same state '+ \
                name + '=='+ absname +'\n'
            raise Exception(msg)
        for item in input_dict.keys():
            old = getattr(self,item)
            new = getattr(absorber,item)
            if old[absorber.state] != defaults:
                raise Exception('cannot join two absorbers: %s %s\n' % (str(self), str(absorber)))
            old[absorber.state] = new[absorber.state]
            setattr(self,item,old)

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
            data[key] = self._get_vals(fstream,val)

        self.elem = []
        for key, val in element_names.iteritems():
            item['name']=val
            for attr in data.keys():
                item[attr] = data[attr][key] 
                elem = Element(**item)
            self.elem[elem.name] = elem

    def __str__(self):
        return "a string of the model.  write more later"


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
            
            
        

def get_observed(fstream=open("observed/observed_data.dat","r")):
    """
    format of observed data should be:
    C 2 column lower best upper

    <element name (symbol)> <ionization state> <quantity> lower, best, upper estimate

    quantity should follow input_dict's keys

    example input:
    ` 
        H 0 column 1 2 3
        H 0 ionisation 2 3 4
        C 3 temp 2 3 5
        C 3 temp_e 4 5 6
        C 3 column 12 13 14
    `

    """

    out={}
    for item in getNonBlank(fstream):
        name, state, qty, low, best, hi = tuple(item.split())
        if qty in input_dict.keys():
            lst = input_dict.keys()
            dat = {'name':name,lst[lst.index(qty)]:[low,best,hi]}
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

 
