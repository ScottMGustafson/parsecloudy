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


