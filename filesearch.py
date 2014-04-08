import os
from os.path import join, getsize
import shutil
import filecmp


newdir = 'output'
olddir = 'oldoutput'
prefix = 'm'


if not os.path.exists(newdir): os.makedirs(newdir)

for root, dirs, files in os.walk(olddir):
    for fname in files:
        fname_dup =join(root,fname)
        fname_new = join(newdir,fname)
        if fname in os.listdir(newdir):
            if not filecmp.cmp(fname_dup, fname_new):
                shutil.move(fname_dup, join(newdir, prefix+fname))
        else:
            shutil.move(fname_dup, join(newdir, fname))
    
