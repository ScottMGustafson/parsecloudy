def compare(a,b, default=-30.):
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
