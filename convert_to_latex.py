from variousutils import *
from config import roman, observed

qty_map = {'N': 'N', 'column':'N', 'b':'b','z':'z'}
def name_map(elem,trans):
    return "\\"+elem+roman[int(trans)]

def _round(lst,i,keep):
    if len(lst)>i+1:
        try:
            if int(lst[i+1])>=5:
                return str(int(lst[i])+1)
        except:
            pass
    return lst[i]

def sigfigs(num, digits=None):

    lst = list("%lf"%num)
    if digits==None:
        i=0
        keep=''
        while True:
            if i==len(lst):
                return keep
            elif lst[i] in ['0','.','1']:
                keep+=lst[i]
                if '1' in keep[0:-2]:
                    return keep
                i+=1
            else:        
                return keep+_round(lst,i,keep)
    else:
        digits=int(digits)
        if digits>7:
            raise Exception("too many digits for the code to handle: %d"%digits)
        if int(lst[digits])<5:
            lst[digits-1] = lst[digits-1]
        else: 
            str(int(lst[digits-1])+1)
        return ''.join(lst[0:digits])

def tex_num(mn, best, mx):
    mn, best, mx = tuple(map(float, (mn, best, mx)))

    upper=sigfigs(mx-best)
    lower=sigfigs(best-mn)
    if len(upper)>len(lower):
        lower=sigfigs(best-mn,digits=len(upper))
    elif len(upper)<len(lower):
        upper=sigfigs(mx-best,digits=len(lower))

    decimals = len(upper.split('.')[-1])
    best = str(best).split('.')
    try:
        end = best[-1][0:decimals+1].split()
        if end[-1]>=5:
            end[-2] = str(int(end[-2])+1)
        best[1] = ''.join(end[0:decimals])
    except IndexError:
        pass

    best='.'.join( [best[0], best[1]] )
    
    

    if upper != lower:
        num = "\\tol{%s}{+%s}{-%s}"%(best, upper, lower)
    else:
        num = "%s \\pm %s" % (best, upper)
    return num
    

if __name__=="__main__":
    f=open("table.tex","w")
    for key in observed.keys():
        for trans in observed[key].keys():
            lst=[ name_map(key, trans) ]
            for qty in ['column','b','z']:
                if qty in observed[key][trans].keys():
                    try:
                        lst+=[ tex_num( *observed[key][trans][qty] ) ]
                    except:
                        lst+=[str(observed[key][trans][qty])]
                else:
                    lst+=[ ' ' ]

            f.write(" & ".join(lst)+"\n")
    f.close()
