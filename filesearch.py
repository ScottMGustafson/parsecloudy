import os
import shutil
import filecmp

"""move files from olddir to newdir.  if duplicates, replace, if not, but smae name, prepend prefix and move"""

newdir = 'output'
olddir = 'output2'
prefix = 'm'


if not os.path.exists(newdir): os.makedirs(newdir)

for root, dirs, files in os.walk(olddir):
    for fname in files:
        new_file = os.path.join(newdir,fname)
        fname_dup = os.path.join(root,fname)
        flag=False
        while fname in os.listdir(newdir):
            fname=prefix+fname
            flag=True
        new_name = os.path.join(newdir,fname)
        if flag:
            if not filecmp.cmp(fname_dup, new_file):
                shutil.move(fname_dup, new_name)
        else:
            shutil.move(fname_dup, new_file)
    
