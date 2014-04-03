from config import elem_names, ions, default, input_dict
from variousutils import getNonBlank, ion_state
import warnings

defaults = [default, default, default]  #  best, upper and lower limits default values

class Element(object):
    def __init__(self,name,**kwargs):
        self.name=name  #symbol of element (w/o ionisation state)
        self.ions = ions[self.name]
        #print("%s:%d"%(self.name,ions[self.name]))
        for item in list(input_dict.keys()):
            selfval = kwargs.get(item,[defaults for i in range(self.ions)])
            #correct number of args?
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
            #print(selfval)
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
                #print("self.%s[%i] != other.%s[%i]"%(item,i,item,i))
                #print("other.%s[%i]=[%lf, %lf, %lf]"%(item,i,obsmin,obsbest,obsmax))
                #print("self.%s[%i]=[%lf, %lf, %lf]"%(item,i,selfmin,selfbest,selfmax))
                return False
            #if item=='column' and self.name in ['H','C','Si'] and i in [0,2]:
            #    print("%s: self.%s[%i] == other.%s[%i]"%(ion_state(i,self.name),item,i,item,i))
            #    print("other.%s[%i]=[%lf, %lf, %lf]"%(item,i,obsmin,obsbest,obsmax))
            #    print("self.%s[%i]=[%lf, %lf, %lf]"%(item,i,selfmin,selfbest,selfmax))
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
            data[key] = self._get_vals(fstream,val)

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

        lst = retrieve_section(fstream,key)
        h_dat = lst.pop(0)[1:4]  #need to 4 since text is included in this line
        output = {elem_names['Hydrogen']:h_dat}

        for row in lst:  #repeat for other elements what we did for H
            try:
                row[1:]=list(map(float, row[1:]))
            except:
                raise Exception(row)
            output[elem_names[row[0]]] = row[1:]
        return output 

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
    #strip off blank lines and comments
    llst = LinkedList([ item for item in getNonBlank(datastream)])
    ret_data = []
    curr = llst.head
    while curr is not None:
        if section_key in curr.data:
            while "Zinc" not in curr.data:
                ret_data.append(curr.data)
                curr=curr.gonext()
            ret_data.append(curr.data)  #to get Zinc
            curr=curr.gonext()
        else:
            curr=curr.gonext()
    if ret_data[0][:8]=='Hydrogen':
        ret_data = mult_lines(ret_data)
    return ret_data

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
        item = (item.replace('-',' -')).strip()
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
