from config import elem_names, ions, default, input_dict
from variousutils import getNonBlank, ion_state
import warnings
import re

defaults = [default, default, default]  #  best, upper and lower limits default values

class Element(object):
    def __init__(self,name,**kwargs):
        self.name=name  #symbol of element (w/o ionisation state)
        self.ions = ions[self.name]
        for item in list(input_dict.keys()):
            selfval = kwargs.get(item,[defaults for i in range(self.ions)])
            try:  
                assert(len(selfval)==self.ions)
            except:
                if len(selfval)>self.ions:
                    while len(selfval)>self.ions:
                        if float(selfval[-1])!=default:
                            msg = name+":"+str(selfval) + \
                            "\n  not of correct length "+str(self.ions)
                            raise Exception(msg)
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
            if getattr(self,'column')[i]!=defaults:
                out += "%s: N=[%5.3lf %5.3lf %5.3lf] U=%5.3lf Ue=%5.3lf T=%5.3lf Te=%5.3lf\n" % \
                    (ion_state(i,self.name),getattr(self,'column')[i][0],
                    getattr(self,'column')[i][1], getattr(self,'column')[i][2],
                    getattr(self,'ionization')[i][1],getattr(self,'ionization_e')[i][1], 
                    getattr(self,'temp')[i][1],getattr(self,'temp_e')[i][1])
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
            superkwargs[key][int(state)] = val
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

        self.Z = float(self._get('metals'))
        self.U = float(self._get("***> Log(U):"))
        self.hden=float(self._get('hden'))
 
        self.elem = {}
        for name in list(elem_names.values()):
            attrs={}
            for attr in list(data.keys()):
                attrs[attr] = data[attr][name] 
            self.elem[name] = Element(name,**attrs)

    def __str__(self):
        s = '---------------------------------------------------\n'
        for item in list(self.elem.keys()):
            s+=str(self.elem[item])
        return s

    def _get(self,string):
        for item in getNonBlank(self.fname):
            if string in item:
                return re.findall(r"[-+]?\d*\.\d+|\d+",item)[0]
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
            return None   #this will occur with an erroneous file

        h_dat = lst.pop(0)[1:4]  #need to 4 since text is included in this line
        output = {elem_names['Hydrogen']:h_dat}

        for row in lst:  #repeat for other elements what we did for H
            row[1:]=list(map(float, row[1:]))
            output[elem_names[row[0]]] = row[1:]
        return output 

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
        if not qty:
            return item
        else:
            vals=getattr(item,qty)
            if state:
                if not error:
                    return vals[state][1]
                else:
                    return tuple(vals[state])
            else:
                if not error:
                    return [item[1] for item in vals]
                else:
                    return [tuple(item) for item in vals]
            

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

class _Link(object):
    def __init__(self,val):
        self.data=val
        self._next=None
    def gonext(self):
        return self._next
    def __str__(self):
        return str(self.data)

class LinkedList(object):
    def __init__(self,in_list=None):
        """
        params:
        =======
        head : optional initial data for linked list
        input_list : optional parameter.  if specified, list will be converted 
                    to linked list
        """
        self.head=None
        self.tail=None
        if in_list is not None:
            for item in in_list:
                self.new_link(item)
  
    def new_link(self,val):
        newlink=_Link(val)
        if self.head == None:
            self.head=newlink
        if self.tail != None:
            self.tail._next = newlink
        self.tail=newlink
  
    def pop(self,index=0):
        prev=None
        curr=self.head
        i=0
        while curr!=None and i<index:
            prev=curr
            curr=curr._next
            i+=1
        if prev==None:
            self.head=curr._next
            return curr.data
        else:
            prev._next=curr._next
            return curr.data
    def __str__(self):
        curr=self.head
        s=''
        while curr:
            s+=str(curr.data)+'\n'
            curr=curr.gonext()
        return s
