"""
various utility functions
"""

def int_to_roman(n):
    """
    Convert an integer to Roman numerals.
    """
    if not type(n) is int:
        raise ValueError('type must be int.  instead got '+str(type(n)))   
    ints = (10,  9,   5,  4,   1)
    nums = ('X','IX','V','IV','I')
    result = ""
    for i in range(len(ints)):
        count = int( n / ints[i])
        result += nums[i] * count
        n -= ints[i] * count
    return result


def ion_state(i,element):
    """
    append ionization state to element.
    following cloudy convention, i==2 means molecular Hydrogen for element==H
    
    """
    if i==2 and element=='H':
        return r"H_2"
    else:
        return element+int_to_roman(i+1)

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







