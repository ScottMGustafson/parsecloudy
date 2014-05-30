import os
import plot_cloudy_output as plot
from config import elem_names, paths, input_dict
import numpy as np
from core import *
from variousutils import getNonBlank, get_ind, ion_state
import warnings

def write_out(data, element, filter_vals=False, **kwargs):
    """
    write all model data as dict of lists

    input params:
    -------------
    data: list of Model instances
    element: a string of which element.
    filter_vals:  should they be filtered?
    key:  input for filter_data
    bounds:  input for filter_data
    state: input for filter_data
    

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
    if filter_vals:
        state = kwargs.get(state,None)
        bounds= kwargs.get(bounds,None)
        data = filter_data(data, key, bounds, element, state)

    elems = [ item.elem[element] for item in data ] 
    ret_dict = {}
    for key in list(input_dict.keys()):
        ret_dict[key] = [ getattr(item,key) for item in elems ]
    ret_dict['Z']=[item.Z for item in data]
    ret_dict['U']=[item.U for item in data]
    ret_dict['hden']=[item.hden for item in data]
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

    results = []
    for model in model_data:
        s=[('-------%s---------')%(model.fname)]
        for key in list(observed_vals.keys()):
            if observed_vals[key]==model.elem[key]:
                s.append(ion_state(0,model.elem[key].name)+": "+str(model.elem[key].column[0][1]))
                s.append(ion_state(2,model.elem[key].name)+": "+str(model.elem[key].column[2][1]))
        if len(s)>3:
            for i in range(len(s)):
                print(s[i])
        result = [ observed_vals[key]==model.elem[key] for key in list(observed_vals.keys()) ] 
        if len(set(result))==1 and result[0]==True:  #if all elements in result are True:
            results.append(model.fname)
    return results
            

def get_observed(fstream="observed/observed_data.dat"):
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
        try:
            name = elem_names[name]
        except KeyError:
            if name not in elem_names.values():
                raise
            else:
                pass
            
        low, best, hi = tuple(map(float, [low, best, hi]))
        state = int(state)
        if qty in list(input_dict.keys())+['b']:
            try:    
                out[name].append(state, **{qty:[low,best,hi]})
            except KeyError:
                out[name] = ObsData(name, state, **{qty:[low,best,hi]})
        else:
            raise Exception(qty+" not in "+str(list(input_dict.keys()) + ['b']))
    return out


def filter_data(indata, key, bounds, element_key=None, state=None):
    """
    filter list of Model instances by key,

    input params:
    -------------
    indata : list of model instances
    element_key: element
    state: if looking at specific element, ionization state needed
    key : key of data to look at    
    bounds: list of constraints.  [min, max]

    output:
    --------
    list of model instances
    
    """
    def cond(item):
        if element_key is None:
            return bounds[0]<=getattr(item,key)<=bounds[-1]
        else:
            return bounds[0]<=item.get_elem(element_key,state,key,False)<=bounds[-1]
    
    return [item for item in indata if cond(item)]
    


if __name__ == '__main__':

    obs_vals = get_observed()
    pth=paths['output_path']
    outputs = [os.path.join(pth,f) for f in os.listdir(pth) if f.endswith('.out')]
    #stored as list of Model instances

    all_data = []
    for item in outputs:
        try:
            all_data.append(Model(item))
        except:
            warnings.warn('model '+item+' has critical issues.  skipping')       

    obs_vals = get_observed()
    #print(search(obs_vals, all_data))

    #filter values out here
    #sys.exit()
    #all_data = filter_data(all_data, 'Z', [-4.5, -2.5])
    all_data = filter_data(all_data, 'U', [-5., 0.])
    #all_data = filter_data(all_data, 'hden', [-2.6, -1.2])
    #all_data = filter_data(all_data, 'temp', [0., 4.4], 'H', state=0)
    #all_data = filter_data(all_data, 'temp', [-30.,obs_vals['Si'].get('temp',2)],'Si',state=2)
    #all_data = filter_data(all_data, 'temp', [-30.,obs_vals['C'].get('temp',2)],'C',state=2)

    #assert(len(all_data)>0)

    #now plot it all
    hdat = write_out(all_data, 'H', return_data=True)
    hcol = np.array( [ item[0] for item in hdat['column'] ] )
    for element in ['Si', 'C']:
        print(element)
        bounds = [obs_vals[element].column[2][0],obs_vals[element].column[2][2]]
        data = write_out(all_data, element,return_data=True)  

        #Z = filter_data(outdata, 'Z', [-5.2,-1.2])
        #plot.plot_N(element,data['column'],hdat['column'],bounds)
        #plot.plot_NT(element, data['temp'], data['column'], hcol, bounds)
        #plot.plot_NU(element, data['U'], data['column'], hcol, bounds)
        #plot.plot_NZ(element, data['Z'], data['column'], hcol, bounds)
        plot.plot_frac(element, data['U'], data['column'])
        #plot.plot_Nhden(element,data['column'],hcol,data['hden'],bounds)


