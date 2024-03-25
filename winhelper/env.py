import os

    
def updir(root_path,ddict,filelist,tools_env,cmd,path,dict_path,is_creat=False,is_hide=False,Is_hide=False):
    cache=os.listdir(path)
    exec("%s={}"%cmd)
    dircache=[]
    for i in cache:
        if os.path.isfile(path+'/'+i):
            if i[-4:]!='.bat':
                continue
            exec("%s['%s']=1"%(cmd,i))
            i=i[:i.rfind('.')]
            filelist[i]=[path,Is_hide]
        else:
            dircache.append(i)
    for i in dircache:
        if is_creat:
            if ' ' in path+'\\'+i:
                tools_env.append('"%s"'%(path+'\\'+i)+';')
            else:
                tools_env.append(path+'\\'+i+';')
        getdirlist(root_path,ddict,filelist,tools_env,dict_path+'$'+i,is_creat,is_hide=is_hide,Is_hide=Is_hide)
            
def getdirlist(root_path,ddict,filelist,tools_env,path='',is_creat=False,is_hide=False,Is_hide=False):

    if path:
        cmd='ddict'
        for i in path.split('$'):
            if i:
                cmd+='["%s"]'%i
            else:
                cmd+='["/"]'
        real_path=root_path+path.replace('$','\\')
        updir(root_path,ddict,filelist,tools_env,cmd,real_path,path,is_creat=is_creat,is_hide=is_hide,Is_hide=Is_hide)
    else:
        ddict['/']={}
        cache=os.listdir(root_path)
        dircache=[]
        for i in cache:
            if os.path.isfile(root_path+'\\'+i):
                if i[-4:]!='.bat':
                    continue
                ddict['/'][i]=1
                i=i[:i.find('.')]
                filelist[i]=[root_path,Is_hide]
            else:
                dircache.append(i)
        for i in dircache:
            if is_creat:
                if ' ' in root_path+'\\'+i:
                    tools_env.append('"%s"'%(root_path+'\\'+i)+';')
                else:
                    tools_env.append(root_path+'\\'+i+';')
            if i=='hide' and is_hide:
                Is_hide=True
            getdirlist(root_path,ddict,filelist,tools_env,'$'+i,is_creat,is_hide,Is_hide)
            Is_hide=False
                