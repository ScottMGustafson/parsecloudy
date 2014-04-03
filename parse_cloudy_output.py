import os
import plot_cloudy_output as plot
from config import elem_names, paths, input_dict
import numpy as np
from core import *
from variousutils import getNonBlank, get_ind, ion_state

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
    for key in list(input_dict.keys()):
        if not return_data:
            f = open(element+"_"+key+".dat",'w')
            for item in data:
                f.write(str(item.elem[element]))
            f.close()
        else: 
            elems = [ item.elem[element] for item in data ] 
            ret_dict[key] = [ getattr(item,key) for item in elems ]
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
            return model
    return None
            

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
        low, best, hi = tuple(map(float, [low, best, hi]))
        state = int(state)
        if qty in list(input_dict.keys()):
            lst = list(input_dict.keys())
            dat = {lst[lst.index(qty)]:[low,best,hi]}
            try:    
                out[name].join(ObsData(name, state, **dat))
            except KeyError:
                out[name] = ObsData(name, state, **dat)
        else:
            raise Exception(qty+" not in "+str(list(input_dict.keys())))
    return out

def main():
    pth=paths['output_path']
    outputs = [os.path.join(pth,f) for f in os.listdir(pth) if f.endswith('.out')]

    #stored as list of Model instances
    all_data = [ Model(item) for item in outputs ]

    obs_vals = get_observed()
    model = search(obs_vals, all_data)
    
    open(os.path.join(paths['home_path'],'modelout.txt'),'w').write(str(model))

    """
    hdat = write_out(all_data, 'H', return_data=True)
    hcol = np.array( [ item[0] for item in hdat['column'] ], dtype=np.float)
    for element in ['Silicon', 'Carbon', 'Oxygen']:
        data = write_out(all_data, element,return_data=True)  

        plot.plot_NT(elem_names[element], data['temp'], data['column'], hcol)
        plot.plot_NU(elem_names[element], data['ionization_e'], data['column'], hcol)
    """


if __name__ == '__main__':
    main()

 
