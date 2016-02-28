from __future__ import print_function
import config
from variousutils import *
import re
from linked_list import LinkedList
import os
import sys

#import multiprocessing as multi
#os.system("taskset -p 0xff %d" % os.getpid())

defaults = [config.default, config.default, config.default]  #  best, upper and lower limits default values
bounds={}


class FormatError(BaseException):
    def __init__(self, val=None):
        if type(val) is int:
            self.msg = 'input must be list of length 3.  Instead got length %d'%(val)
        else:
            self.msg = 'input must be list of length 3.'
    def __str__(self):
        return self.msg

class ModelFailed(BaseException):
    def __init__(self, val=None):
        self.msg = 'Model failed'
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
        self.msg = 'Input must be length '+str(expected)+\
                   ' list of length 3 lists. '+string
    def __str__(self):
        return self.msg    

class Model(object):
    def __init__(self,input_dict=config.input_dict,data=None,fname=None):
        """
        each attribute will be a dict of lists with each list element 
        corresponding to a different ionization state

        input parameters:
        -----------------
        fstream: a filestream-like list of data from cloudy output
        input_dict : dict of input data as defined above
        """

        if data:
            self.data=data
        else:
            if not fname:
                raise Exception("must specify input file")
            if 'Warnings exist, this calculation has serious problems' in open(fname).read():
                raise ModelFailed()
            if '>>>>>>>>>> Cautions are present.' in open(fname).read():
                raise ModelFailed()

            #if 'abundances ism' in open(fname).read():
            #    raise ModelFailed()

            else:
                self.data=get_dict(fname)

        self.fname=fname


    def append_datum(self, name, trans, qty, value=defaults):
        """
        append a data entry into data dict
        """    

        if type(value) in [float, int, str]:
            value = (config.default, float(value), config.default) 
        elif len(value)==3:
            pass
        else:
            raise FormatError()
        
        if name in self.data.keys():
            if trans in self.data[name].keys():
                self.data[name][trans][qty] = value
            else:
                self.data[name][trans] = {qty:value}
        else:
            self.data[name] = {trans: {qty:value}}

    def get(self, name, trans, qty, errors=False, observed=False):

        data = config.observed if observed else self.data

        try:
            if errors:
                return data[name][trans][qty]
            else:
                return data[name][trans][qty][1]
        except KeyError:
            print("available keys: ",data.keys(),"\nchosen key ",name,'\n\n', 
                file=sys.stderr) 
            raise
            
        
    def get_list_by_ionization(self, atom, qty):
        """returns a list of values for each ionization given a qty

        for example:    
            model.get_list("column")
        returns column densities of  [HI, HII, H2]
        """
        return [self.data[atom][i][qty] for i in range(0,config.ions[atom])]

    @staticmethod
    def get_qty_lst(modellist, atom, qty, trans, errors=False):
        out=[]
        for item in modellist:
            try:        
                if errors:
                    out.append(item.data[atom][trans][qty])
                else:
                    out.append(item.data[atom][trans][qty][1])
            except KeyError:
                if (trans+1)>len(item.data[atom].keys()):
                    pass
                else:
                    print("\n\natom=%s transition=%d qty=%s"%(atom, trans, qty),
                        file=sys.stderr)
                    print("available quantities:\n  ", config.input_dict.keys(),
                        file=sys.stderr) 
                    print("this datum's keys:\n  ",item.data[atom][trans].keys(),
                        file=sys.stderr) 
                    raise
        return out



def compare(a,b, default=config.default):
    """
    returns True if a is consistent with b
    a = observed limits  [lower, best, upper]
    b = model limits [lower, best, upper]

    user specifies observed limits, so these are more hard.
    The model limits are specified as follows:
        b[0]=default, b[1]=number, b[2]=default:
        -->no limits specified, ignore them
        b[0]=number, b[2]=default or vice-a-versa:
        -->upper or lower limits specified.  listen to them
        all b[0,1,2] =number:
        -->hard range specified.

    The observed limits are specified as follows:
        a[0]==a[2] == default:
        -->no upper or lower limits established. User doesn't understand 
        the point of error bars so raise exception

        a[2]!=a[0]==default: 
        --> upper limit established
        a[0]!=a[2]==default:
        --> lower limit established
        a[0]!=a[2]!=default:
        -->hard range defined.
        
    """


    #check for an error:
    if a[0]!=a[2]!=default and a[0]>a[2]:
        a[0], a[2] = a[2], a[0]
    if b[0]!=b[2]!=default and b[0]>b[2]:
        b[0], b[2] = b[2], b[0]
       

    if   a[0]==a[2]==default:    
        raise Exception("need to specifiy SOME observed limits")

    elif a[0]!=a[2]==default:  #lower limit observed specified
        if   b[0]==b[2]==default:  #no model limits applied
            return b[1]>=a[0]
        elif b[0]!=b[2]==default:  #lower model limits specified
            return b[1]>=a[0]
        elif b[2]!=b[0]==default:  #upper model limits specified
            return b[2]>=a[0]
        else:   #hard range determined for b.
            return b[2]>=a[0]

    elif a[2]!=a[0]==default: #upper limit observed specified  
        if   b[0]==b[2]==default:    
            return b[1]<=a[2]
        elif b[0]!=b[2]==default:  
            return b[0]<=a[2]
        elif b[2]!=b[0]==default:  
             return b[1]<=a[2]
        else:
            return b[0]<=a[2]

    else:  #an error bar (confidence interval) is specified
        if   b[0]==b[2]==default:    
            return a[0]<=b[1]<=a[2]
        elif b[0]!=b[2]==default:  
            return b[0]<=a[2]
        elif b[2]!=b[0]==default:  
            return b[2]>=a[0]
        else:
            return b[2]>=a[0] and b[0]<=a[2]

def _filter(model):
    """
    returns True if model is consistent with constraints
    returns False on an error or if model is NOT consistent with constraints

    """
    if not ("H" in model.data.keys()):
        return False
    for atom in config.constraints.keys():
        for trans in config.constraints[atom].keys():
            for attr in config.constraints[atom][trans].keys():
                if attr=="b":  #for b, we can only do lower limits since cannot a priori know the thermal contribution to line width
                    b=K_to_b(atom,model.data[atom][int(trans)]["temp"][1]) #this will be lower than the actual line width
                    mod=[b,b,-30.]

                else:
                    try:
                        mod=model.data[atom][int(trans)][attr]
                        #mod=model.get(atom, int(trans), attr, errors=True)
                    except KeyError:
                        print("no key called \"%s\""%(attr))
                        #print("input is get(%s, %d, %s)"%(
                        #    atom, int(trans), attr),file=sys.stderr
                        #)
                        return False
                obs = config.constraints[atom][trans][attr]
                assert(len(obs)==len(mod)==3) 
                if not compare(obs,mod):  
                    return False
                for key in config.input_dict.keys():
                    try:
                        assert(key in model.data[atom][trans].keys())
                    except AssertionError:
                        print("%s not in "%(key),model.data[atom][trans].keys(),
                            file=sys.stderr) 
                        raise
    return True


def filter_models(models):
    """filter list of models based on observed values"""
    out=[]
    for model in models:
        if _filter(model):
           out.append(model)
    return out


def walk_dirs(start_dir):
    output=[]
    print(start_dir)
    for path, dirs, files in os.walk(start_dir):
        for f in files:
            if f.endswith(".out"):
                output.append(os.path.join(path,f))
                #output.append(Model(fname=os.path.join(path,f)))
    return output

def walk_dirs_(start_dir):
    output=[]
    for path, dirs,files in os.walk(start_dir):
        for f in files:
            if f.endswith(".out"):
                output.append(os.path.join(path,f))
                #output.append(Model(os.path.join(path,f)))
    return output

def walkdirs(path):
    manager=multi.Manager()
    output=manager.list([])
    unsearched = multi.JoinableQueue()
    unsearched.put(path)

    def explore_path(path):
        print('exploring')
        directories = []
        nondirectories = []
        for filename in os.listdir(path):
            fullname = os.path.join(path, filename)
            if os.path.isdir(fullname):
                directories.append(fullname)
            else:
                nondirectories.append(filename)
            for filename in nondirectories:
                print('.')
                #do work on file
                if filename.endswith(".out"):
                    #output.append(Model(os.path.join(path,filename)))
                    #print(os.path.join(path,filename))
                    print(len(output))
                    output.append(os.path.join(path,filename))

        return directories

    def parallel_worker():
        while True:
            dirs = explore_path( unsearched.get() )
            for newdir in dirs:
                unsearched.put(newdir)
            unsearched.task_done()
            print('-\n')


    pool = multi.Pool(processes=config.nproc)
    #for i in range(config.nproc):
    #    pool.apply_async(parallel_worker)
    #    print(str(i))

    pool.apply_async(parallel_worker)
    unsearched.join()

    return list(output)




def get_dict(fname,input_dict=config.input_dict):
    """
    each attribute will be a dict of lists with each list element 
    corresponding to a different ionization state

    input parameters:
    -----------------
    fstream: a filestream-like list of data from cloudy output
    input_dict : dict of input data as defined above
    """

    data = {}

    #print("parsing %s"%fname)
    for qty in list(input_dict.keys()):
        try:
            lst=retrieve_section(fname,input_dict[qty])
            for row in lst:  
                if row[0]=="Hydrogen":
                    for i in [0,1,2]:
                        data = append_datum(data,"H", i, qty, float(row[i+1]))
                else:
                    name=config.elem_names[row[0]]
                    for i in range(1, config.ions[name]):
                        if len(row)>i:
                            data = append_datum(data, name, i-1, qty, float(row[i]))
                        else: 
                            data = append_datum(data,name, i-1, qty, config.default)
        except:
            print(fname+" has no key: %s"%input_dict[qty], file=sys.stderr)
            pass

    for key, val in config.other_attrs.iteritems():
        data[key]=_get(fname,val)
    return data

def _get(fname, string, as_float=True):
    bad_chars='* '
    if as_float:
        for item in getNonBlank(fname):
            if string in item:
                return float(re.findall(r"[-+]?\d*\.\d+|\d+",item)[0])
    else:
        for item in getNonBlank(fname):
            if string in item:
                out=item.replace(string,"")   #remove entire substring
                try:
                    return out.translate(
                                {ord(x): y for (x, y) in zip(bad_chars, "")}
                                        ) #strip off all unwanted chars
                except:
                    raise Exception(str(item))
    return None

def retrieve_section(datastream, section_key):

    """
    retrieve a section's data.  This may sometimes go over multiple lines

    Parameters:
    ===========
    datastream:  list of data.  one line per element
    section_key: key name for the section of interest.  This may
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
    except AssertionError:
        raise Exception(datastream+' has no key: '+section_key)
    if 'Hydrogen' in dat[0]:
        dat = mult_lines(dat)
    return dat

def mult_lines(lst,keys=list(config.elem_names.keys())):
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
                raise Exception("first list item not element name: "+\
                                str(out_list))
    return out_list

def append_datum(data, name, trans, qty, value=defaults):
    """
    append a data entry into data dict
    """    

    if type(value) in [float, int, str]:
        value = (config.default, float(value), config.default) 
    elif len(value)==3:
        pass
    else:
        raise Exception
    
    if name in data.keys():
        if trans in data[name].keys():
            data[name][trans][qty] = value
        else:
            data[name][trans] = {qty:value}
    else:
        data[name] = {trans: {qty:value}}
    return data

def object_list(verbose=False):
    filelist=walk_dirs_(config.configDict["paths"]["start_dir"])
    pool = multi.Pool(processes=config.nproc)
    if verbose:
        print("pool initiated with %d processes"%config.nproc)
    object_list = pool.map(get_dict, filelist)
    return object_list



