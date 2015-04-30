from config import *
from variousutils import getNonBlank, ion_state, b_to_K
import warnings
import re
from linked_list import LinkedList

defaults = [default, default, default]  #  best, upper and lower limits default values

class FormatError(BaseException):
    def __init__(self, val=None):
        if type(val) is int:
            self.msg = 'input must be list of length 3.  Instead got length %d'%(val)
        else:
            self.msg = 'input must be list of length 3.'
    def __str__(self):
        return self.msg

class ExtendedFormatError(BaseException):
    def __init__(self, expected, lst):
        if type(lst) is list:
            try:
                l2=str(len(lst[0]))
            except IndexError:
                l1=0
            except TypeError:
                l1=len(lst)
                l2=str(type(lst[0]))
            string = 'Instead got %d X %s'%(l1,l2)  
        else:
            string = 'Instead got '+str(type(lst))
        self.msg = 'Input must be length '+str(expected)+' list of length 3 lists. '+string
    def __str__(self):
        return self.msg


class Element(object):
    def __init__(self,name,**kwargs):
        self.name=name  #symbol of element (w/o ionisation state)
        self.ions = ions[self.name]
        for item in list(input_dict.keys())+['b']:
            selfval = kwargs.get(item, [defaults for i in range(self.ions)])
            try:  
                assert(len(selfval)==self.ions)
            except:
                if len(selfval)>self.ions:
                    while len(selfval)>self.ions:
                        if float(selfval[-1])!=default:
                            raise ExtendedFormatError(self.ions,selfval)
                        else:
                            del[selfval[-1]]
                else:
                    while len(selfval)<self.ions:
                        selfval.append(defaults)
            #include [min,best,max] for each.  
            for i in range(len(selfval)):  
                if not type(selfval[i]) is list:
                    selfval[i] = [selfval[i], selfval[i], selfval[i]]
                else:
                    assert(len(selfval[i])==3)
                selfval[i] = list(map(float, selfval[i]))
            setattr(self,item,selfval)
        for i in range(self.ions):
            if self.temp[i]==defaults and self.b[i]!=defaults:
                self.temp[i][0] = -30.000
                self.temp[i][1] = b_to_K(self.name, float(self.b[i][1]))
                self.temp[i][2] = b_to_K(self.name, float(self.b[i][2]))


    def __eq__(self,observed):
        if observed.name!=self.name:
            return False
        for item in list(input_dict.keys()):
            if not self._attr_eq(observed,item):
                return False
        return True

    def __ne__(self,observed):
        return not self.__eq__(observed)

    def __str__(self):
        out='\n'
        for i in range(ions[self.name]):
            if self.column[i]!=defaults:
                out+='%s: '%(ion_state(i,self.name))
                N = ' logN=[ %5.3lf %5.3lf %5.3lf ]'%(self.column[i][0],
                    self.column[i][1], self.column[i][2])
                U = ' logU=%5.3lf'%(self.ionization[i][1])
                try:
                    T = ' logT=%5.3lf\n'%(self.temp[i][1])
                except:
                    raise Exception(str(self.temp))
                out += N+U+T
        out+='\n'
        return out

    def _attr_eq(self,observed,item):
        selfval = getattr(self,item)
        obsval  = getattr(observed,item)
        for i in range(ions[self.name]):
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
                return False
        return True

    def get(self,key,state,bounds=False):
        """
        a convenience function to simplify Element access
        """
        if bounds:
            val = getattr(self,key)[state]
            return float(val[0]), float(val[2])
        else:
            return float(getattr(self,key)[state][1])
                   
class ObsData(Element):
    def __init__(self,name,state,**kwargs):
        """
        Subclass of Element.   Each physical quantity as list :[min, best, max] 
        where min and max correspond to upper and lower limits.
        """
        self.name = name
        self.state = int(state)
        superkwargs={}
        for key, val in list(kwargs.items()):
            superkwargs[key] = [defaults for i in range(ions[self.name])]
            superkwargs[key][int(state)] = val if len(val)==3 else [val,val,val]
        super(ObsData,self).__init__(name,**superkwargs)

    def join(self,absorber):
        """
        join another obsData instance with the current one
        """
        name = ion_state(self.state,self.name)
        absname=absorber.name
        for item in list(input_dict.keys()):
            old = getattr(self,item)
            new = getattr(absorber,item)
            if old[absorber.state] == defaults or new[absorber.state] == defaults:
                old[absorber.state] = new[absorber.state]
            else:
                raise Exception('cannot join two absorbers: %s %s\n' % (str(self), str(absorber)))
            setattr(self,item,old)

#@Bug:   for some reason self.key is only beig written as a len3 list, instead of list of len3 lists
    def _update(self,state,key,val):
        old = getattr(self,key)
        for item in old:
            assert(len(item)==3)
        if old[state] != defaults:
            warnings.warn('overwriting old data.')
        old[state] = val
        setattr(self,key,old)

    def append(self,state,**kwargs):
        for key, val in kwargs.items():
            if key in input_dict.keys():
                if type(val) is list or type(val) is tuple:
                    if len(val)==3:
                        self._update(state,key,list(val))
                    else:
                        raise FormatError(len(val))
                elif type(val) is float:
                    self._update(state,key,[val, val, val])
                else:
                    raise TypeError('expected float or list of lists of floats')
            elif key=='b':
                if type(val) is list or type(val) is tuple:
                    if len(val)==3:
                        val = [ b_to_K(self.name,float(item)) for item in val ]
                    else:
                        raise FormatError(len(val))
                elif type(val) is float:
                    v = b_to_K(self.name,float(val))
                    val = [ -30.000, v, v ] 
                else:
                    raise TypeError('expected float or list of lists of floats')
                self._update(state,'temp',val)
            else:
                raise KeyError('unrecognized key %s'%(key))
        
                

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
        self.fname=fstream
        for key, val in list(input_dict.items()):
            data[key] = self._get_vals(val)

        self.Z       = self._get('metals')
        self.U       = self._get("***> Log(U):")
        self.hden    = self._get('hden')
        self.title   = self._get("* title", as_float=False)
        self.radius  = self._get("* radius")   
        self.z_cmb   = self._get("* CMB redshift")  
        self.stoptemp= self._get("* stop temperature =") 
        self.fnu     = self._get("* f(nu) =") 
 
        self.elem = {}
        for name in list(elem_names.values()):
            attrs={}
            for attr in list(data.keys()):
                try:
                    attrs[attr] = data[attr][name] 
                except TypeError:
                    raise
            self.elem[name] = Element(name,**attrs)
    #number accessed as model.elem['element name'].quantity[ionization][0(min), 1(best) or 2(max)]

    def __str__(self):
        s = '---------------------------------------------------\n'
        for item in list(self.elem.keys()):
            s+=str(self.elem[item])
        return s



    def _get(self,string, as_float=True):
        bad_chars='* '
        if as_float:
            for item in getNonBlank(self.fname):
                if string in item:
                    return float(re.findall(r"[-+]?\d*\.\d+|\d+",item)[0])
        else:
            for item in getNonBlank(self.fname):
                if string in item:
                    out=item.replace(string,"")   #remove entire substring
                    return out.translate({ord(x): y for (x, y) in zip(bad_chars, "")}) #strip off all unwanted chars
        return None


    def _get_vals(self, key):
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
        try:
            lst = retrieve_section(self.fname,key)
        except:
            raise
            return None   #this will occur with an erroneous file

        h_dat = lst.pop(0)[1:4]  #need to 4 since text is included in this line
        output = {elem_names['Hydrogen']:h_dat}

        for row in lst:  #repeat for other elements what we did for H
            row[1:]=list(map(float, row[1:]))
            output[elem_names[row[0]]] = row[1:]
        return output 

    def read_model(self):
        for key in input_dict.keys():
            setattr(self,key,self._get_vals(key))   

    def get_elem(self,element, state=None, qty=None, error=False):
        """
        get output for a specific element.
    
        input params:
        -------------
        element:  which element to parse
        state:  ionization state (0=I, 1=II, etc)
        qty:  which quantity?  (keys from input_dict)
        bounds: list of bounds: [lower, upper]

        """
        item=self.elem[element]
        if qty is None:
            return item
        else:
            vals=getattr(item,qty)
            if state is None:
                if not error:
                    return [float(item[1]) for item in vals]
                else:
                    return [tuple(item) for item in vals]
            else:
                if not error:
                    return float(vals[state][1])
                else:
                    return tuple(vals[state])

def retrieve_section(datastream, section_key):

    """
    retrieve a section's data.  note that this may sometimes go over multiple lines

    Parameters:
    ===========
    datastream:  list of data.  one line per element
    section_key: key name for the section of interest.  This may (unfortunately) 
                 be in the first line of data
    separator:   separator in text that separates this from other sections

    output:
    =======
    dict of parsed data
    """

    llst = LinkedList([ item for item in getNonBlank(datastream)])
    curr = llst.head
    dat=[]
    while not curr is None:
        if section_key in curr.data:
            while "Zinc" not in curr.data:
                dat.append(curr.data)
                curr=curr.gonext()
            dat.append(curr.data)  #to get Zinc
            curr=curr.gonext()
        else:
            curr=curr.gonext()
    try:
        assert(len(dat)>0)
    except:
        raise Exception(datastream+'\n'+section_key)
    if 'Hydrogen' in dat[0]:
        dat = mult_lines(dat)
    return dat


def mult_lines(lst,keys=list(elem_names.keys())):
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
        item=item.replace('-',' -').strip()
        if item.split()[0] in keys:
            out_list.append(item.split())
        else:
            try:
                out_list[-1]+=item.split()
            except:
                raise Exception("first list item not element name: "+str(out_list))
    return out_list


