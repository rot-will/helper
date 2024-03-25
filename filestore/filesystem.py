import os,sys
import filestore.core as core
import filestore.store as store
import filestore.method as method
import config.config as config
from information.log import log

log_title="filesystem"
fileroot:core.fobj=None
def checkinit():
    if fileroot==None:
        raise core.StoreError("The filesystem is not initialized",core.StoreError.init)

def map_types()->dict[str,core.fobj]:
    checkinit()
    types={}
    typel:list[type[core.fobj]]=list(core.Storetypes.values())

    for i in typel:
        if i!=None and i.suffix!=None and types.get(i.suffix)==None:
            types[i.suffix]=i
        else:
            core.StoreError("There are multiple objects using a suffix",core.StoreError.Exist)
    return types

parse_status=0


def parse_(fio):
    tid=fio.ReadByte()
    return core.Storetypes[tid](fio)

def parse(file:str):
    fio=core.fileio(file,'rb')
    try:
        root=parse_(fio)
    except core.FileExec as e:
        if type(file)!=str:
            raise core.StoreError("Second attempt failed",core.StoreError.init)
        parse_status=1
        bak=file+'.bak'
        if os.path.exists(bak):
            fio.close()
            log("Failed to parse %s, attempting to backup files %s soon"%(file,bak),0,log_title)
            try:
                fio=core.fileio(bak,'rb')
                root=parse_(fio)
            except core.StoreError:
                parse_status=2
                log("Failed to parse %s and %s, A new data file will be created soon"%(file,bak),0,log_title)
                root=core.Storetypes[0](name='/')
        else:
            log("Failed to parse %s, nor does the backup file exist. A new data file will be created soon"%file,0,log_title)        
            root=core.Storetypes[0](name='/')
            
    fio.close()
    return root

def save_(file:str,store:core.fobj):
    if store==None:
        return
    fio=core.fileio(file,"wb")
    store.Save(fio)
    fio.close()

def save():
    
    backfilestore()
    file=os.path.join(sys.path[0],'helper2.hfg')
    save_(file,fileroot)
    pass

def backfilestore():
    hfg=os.path.join(sys.path[0],'helper2.hfg')
    if os.path.exists(hfg)==False:
        return
    back=os.path.join(sys.path[0],'helper2.hfg')+'.bak'
    fio=open(hfg,'rb')
    backup=open(back,'wb')
    backup.write(fio.read())
    fio.close()
    backup.close()
    pass

def load_fileplugin():
    fpluginpath=os.path.join(sys.path[0],'filestore/plugin')
    if os.path.exists(fpluginpath)==False:
        os.mkdir(fpluginpath)
        return
    fplugins=os.listdir(fpluginpath)
    for i in fplugins:
        pluginpath=os.path.join(fpluginpath,i)
        __import__(pluginpath)
    pass

def init():
    global fileroot
    if fileroot!=None:
        return
    load_fileplugin()
    
    hfgpath=os.path.join(sys.path[0],'helper2.hfg')
    if os.path.exists(hfgpath):
        fileroot=parse(hfgpath)
    else:
        fileroot=core.Storetypes[0](name='/')
        save()
    core.filetypes=map_types()
    
    if os.path.exists(config.cfg.defpath)==False:
        method.MakeDir(config.cfg.defpath)

def make_filesystem(arg,objtype:type[core.fobj]):

    try:
        objtype.handle(arg)
    except core.StoreError as e:
        log(e.ErrorMessage,2,log_title)
    save()
    pass

def moveto(topath:str):
    try:
        if os.path.exists(os.path.realpath(topath))==False:
            os.mkdir(os.path.realpath(topath))
        fileroot.moveto(topath)
    except core.StoreError as e:
        log(e.ErrorMessage,2,log_title)
    save()
        

def remove(objpath):
    try:
        fileroot.remove(objpath.strip('/').split('/'))
    except core.StoreError as e:
        log(e.ErrorMessage,2,log_title)
    save()


def search(root,search_str=None,note=False):
    backroot=core.Storetypes[0](name='/')
    stack=[]
    backstack=[]
    statustack=[]
    curr_note=root
    currback=backroot
    curr_status=False
    i=0
    while True:
        if i<len(curr_note):
            if curr_note[i].tid==0:
                stack.append((curr_note,i+1))
                curr_note=curr_note[i]
                currback[curr_note.name]=core.Storetypes[0](name=curr_note.name)
                backstack.append(currback)
                currback=currback[curr_note.name]
                i=-1
                if note:
                    statustack.append(curr_status)
                    if search_str==None or curr_status==True:
                        curr_status=True
                    else:
                        curr_status=search_str in curr_note.name
            else:
                if (note==False and ((search_str!=None and (search_str in curr_note[i].name)) or search_str==None)) or \
                    (note==True and curr_status==True):
                    currback[curr_note[i].name]=curr_note[i]

        i+=1
        if i>=len(curr_note):
            if len(stack)==0:
                break
            curr_note,i=stack.pop()
            currback=backstack.pop()
            if note:
                curr_status=statustack.pop()
        pass
    return backroot

    pass

def clear_empty(notes):
    stack=[]
    curr_note=notes
    curr_objs=False
    i=0
    while True:
        if i<len(curr_note):
            if curr_note[i].tid==0:
                stack.append((curr_note,i+1,curr_objs))
                curr_note=curr_note[i]
                
                curr_objs=False
                i=-1
            else:
                curr_objs=True
           
        i+=1
        if i>=len(curr_note):
            if len(stack)==0:
                break
            curr_note,i,temp_objs=stack.pop()
            if curr_objs==False:
                curr_note.pop(curr_note[i-1].name)
                i=i-1
            else:
                temp_objs=True
            curr_objs=temp_objs
        pass
    
    return notes


def get_objs(notes):
    objs=[]
    stack=[]
    curr_note=notes
    i=0
    while True:
        if i<len(curr_note):
            if curr_note[i].tid==0:
                stack.append((curr_note,i+1))
                curr_note=curr_note[i]
                i=-1
            else:
                objs.append(curr_note[i])
           
        i+=1
        if i>=len(curr_note):
            if len(stack)==0:
                break
            curr_note,i=stack.pop()
        pass
    return objs

def get_attr(obj,need=None):
    attrs={}
    if need==None:
        need=list(obj.Id_Attr.keys())
    for i in need:
        attrs[obj.Id_Attr[i]]=obj.attr[i]
    return attrs

def get_need_attr(obj):
    return get_attr(obj,obj.Out_need_attr)

def get_maxpad(objs):
    maxlen=0
    for i in objs:
        if len(i.name)>maxlen:
            maxlen=len(i.name)
    return maxlen

    pass

def clear_error():
    stack=[]
    curr_note=fileroot
    i=0
    while True:
        if i<len(curr_note):
            if curr_note[i].tid==0:
                stack.append((curr_note,i+1))
                curr_note=curr_note[i]
                i=-1
            else:
                if curr_note[i].checkExist(level=0)==False:
                    curr_note.pop(curr_note[i].name)
                    i-=1
           
        i+=1
        if i>=len(curr_note):
            if len(stack)==0:
                break
            curr_note,i=stack.pop()
        pass
    save()