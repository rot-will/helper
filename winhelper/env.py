import os

class file(str):
    def __init__(self,path,hide,name):
        self.hide=hide

    def __new__(self,path,hide,name):
        return str.__new__(self,path+'\\'+name+'.bat')
    
def updir(root_path,ddict,filelist,is_creat=False,is_hide=False,Is_hide=False):
    cache=os.listdir(root_path)
    dircache=[]
    for i in cache:
        if os.path.isfile(root_path+'\\'+i):
            if i[-4:]!='.bat':
                continue
            ddict[i]=1
            i=i[:i.find('.')]
            filelist[i]=file(root_path,Is_hide,i)
        else:
            dircache.append(i)
    for i in dircache:
        ddict[i]={}
        R_hide=Is_hide
        if i=='hide' and is_hide:
            Is_hide=True
        updir(root_path+'\\'+i,ddict[i],filelist,is_creat,is_hide,Is_hide)
        Is_hide=R_hide
            
def getdirlist(root_path,ddict,filelist,is_creat=False,is_hide=False,Is_hide=False):
    ddict['/']={}
    updir(root_path,ddict['/'],filelist,is_creat=is_creat,is_hide=is_hide,Is_hide=Is_hide)
    tools_env=[]
    getenv(ddict['/'],root_path,tools_env)
    return ';'.join(tools_env)

def getenv(ddict,path,tools_env):
    for i in ddict:
        if ddict[i] != 1:
            spath=f"{path}\\{i}"
            tools_env.append(spath)
            getenv(ddict[i],spath,tools_env)
                