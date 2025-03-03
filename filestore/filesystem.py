import os,sys
import filestore.core as core
import core.config as Cfg
import core.args as args
from information.log import log
import zlib

log_title="filesystem"
fileroot:core.dobj=None
default_node=None
def init_filestore_config():
    # print('123')
    defcfg={'defpath':os.path.join(sys.path[0],'objs'),'defnode':"node"}
    Cfg.checkConfig('filestore',defcfg)
    #print(Cfg.cfg)
    defpath=Cfg.cfg.filestore.defpath
    if os.path.exists(defpath):
        if not os.path.isdir(defpath):
            raise Cfg.CfgExce("defpath not direction",Cfg.CfgExce.argerror)
    else:
        os.mkdir(defpath)
        pass

def checkinit():
    if fileroot==None:
        raise core.StoreError("The filesystem is not initialized",core.StoreError.init)




def map_types()->dict[str,core.fobj]:
    types={}
    typel:list[type[core.fobj]]=list(core.Storetypes.values())

    for i in typel:
        if i!=None and i.suffix!=None and types.get(i.suffix)==None:
            types[i.suffix]=i
        else:
            core.StoreError("There are multiple objects using a suffix",core.StoreError.Exist)
    return types

parse_status=0



def parse_name(file:core.fileio):
    tid=file.ReadByte()
    if (tid&0x80)!=0:
        tid=tid
    name_l=file.ReadNumber()
    name=file.Read(name_l).decode("utf-8")
    return core.Storetypes[tid](name=name)

def parse_object(obj,file:core.fileio):
    attrnum=file.ReadNumber()
    i=0
    while i<attrnum:
        attrsize=file.ReadWord()
        zattrdata=file.Read(attrsize)
        attrdata=zlib.decompress(zattrdata).decode("utf-8")
        attrid=file.ReadByte()
        obj.attr[attrid]=core.attrType.parse(obj.Attr_info[attrid].type,attrdata)
        i+=1
    

def parse_names(file:core.fileio,parent=None):
    if parent==None:
        parent=parse_name(file)
    objnum=file.ReadNumber()
    i=0
    while i<objnum:
        obj=parse_name(file)
        if obj.tid<0:
            parse_names(file,obj)
        parent[obj.name]=obj
        i+=1
    return parent
def parse_attributes(node,file):
    for attrname in node:
        if node[attrname].tid<0:
            parse_attributes(node[attrname],file)
        elif node[attrname].tid>0:
            parse_object(node[attrname],file)
    pass

def parse_(fio:core.fileio,status):
    store=parse_names(fio)
    if status:
        parse_attributes(store,fio)
    return store

def parse(file:str,status=True):
    fio=core.fileio(file,'rb')
    try:
        root=parse_(fio,status)
    except core.FileExec as e:
        if type(file)!=str:
            raise core.StoreError("Second attempt failed",core.StoreError.init)
        bak=file+'.bak'
        if os.path.exists(bak):
            fio.close()
            if os.path.exists(file+'.error'):
                os.remove(file+'.error')
            os.rename(file,file+'.error')
            os.rename(bak,file)
            log("Failed to parse %s, attempting to backup files %s soon"%(file,bak),0,log_title)
            try:
                fio=core.fileio(file,'rb')
                root=parse_(fio,status)
            except core.StoreError:
                log("Failed to parse %s and %s, A new data file will be created soon"%(file,bak),0,log_title)
                root=default_node(name='/')
        else:
            log("Failed to parse %s, nor does the backup file exist. A new data file will be created soon"%file,0,log_title)        
            root=default_node(name='/')
            
    fio.close()
    return root

def save_name(obj,file:core.fileio):
    file.WriteByte(obj.tid&0xff)
    wname=obj.name.encode("utf-8")
    file.WriteNumber(len(wname))
    file.Write(wname)

def save_object(obj:core.fobj,file:core.fileio):
    attrnum=len(obj.attr)
    file.WriteNumber(attrnum)
    for attrid in obj.attr:
        attrvalue:str=core.attrType.save(obj.Attr_info[attrid].type,obj.attr[attrid])
        zattrdata=zlib.compress(attrvalue.encode("utf-8"))
        file.WriteWord(len(zattrdata))
        file.Write(zattrdata)
        file.WriteByte(attrid)

def save_names(node,file:core.fileio):
    save_name(node,file)
    file.WriteNumber(len(node))
    for objname in node:
        if node[objname].tid<0:
            save_names(node[objname],file)
        elif node[objname].tid>0:
            save_name(node[objname],file)

def save_subnode(node,file:core.fileio):
    for objname in node:
        if node[objname].tid<0:
            save_subnode(node[objname],file)
        elif node[objname].tid>0:
            save_object(node[objname],file)
    pass
def save_(file:str,store:core.fobj):
    if store==None:
        return
    fio=core.fileio(file,"wb")
    save_names(store,fio)
    save_subnode(store,fio)
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

def trim_dir(dirs):
    if '__pycache__' in dirs:
        dirs.remove("__pycache__")
    ndirs=[]
    for i in dirs:
        if '.py' == i[-3:]:
            i=i[:-3]
        ndirs.append(i)
    return ndirs

def load_fileplugin():
    global default_node
    fpluginpath=os.path.join(sys.path[0],'filestore/store')
    if os.path.exists(fpluginpath)==False:
        os.mkdir(fpluginpath)
        return
    fplugins=trim_dir(os.listdir(fpluginpath))
    for pluname in fplugins:

        #pluginpath=os.path.join(fpluginpath,i)
        plugin=__import__(f"filestore.store.{pluname}",fromlist=("*"))
        if hasattr(plugin,"FILETYPES"):
            for filetype in plugin.FILETYPES:
                if (filetype.suffix==Cfg.cfg.filestore.defnode and default_node==None):
                    default_node=filetype
                    # filetype.tid=-1
                core.Storetypes[filetype.tid]=filetype
        if hasattr(plugin,"CheckCONFIG"):
            plugin.CheckCONFIG()
    pass

def init():
    global fileroot
    if fileroot!=None:
        return
    
    init_filestore_config()
    load_fileplugin()
    
    hfgpath=os.path.join(sys.path[0],'helper2.hfg')
    if not os.path.exists(hfgpath):
        fileroot=default_node(name='/')
        save()
    core.filetypes=map_types()
    

def init_filestore(status):

    global fileroot
    hfgpath=os.path.join(sys.path[0],'helper2.hfg')

    fileroot=parse(hfgpath,status)

def make_filesystem(arg,objtype:type[core.fobj]):

    try:
        objtype.handle(arg)
    except core.StoreError as e:
        log(e.ErrorMessage,2,log_title)
        return False
    save()
    return True
    pass


def split_path(path):
    if path[0]=='/':
        path=path[1:]
    path_split=path.split('/')
    parent_path='/'.join(path_split[:-1])
    current_name=path_split[-1]

    return parent_path,current_name

def checkdire(name):
    if name[0]=='/':
        name=name[1:]
    node=fileroot
    for i in name.split('/'):
        if i=='':
            continue
        node=node[i]
        if node==None:
            return None
    return node

def get_path(stack,node):
    path=""
    for i in stack:
        if i[0].name=='/':
            continue
        path=path+'/'+i[0].name
    path+='/'+node.name
    return path



def checkexists(name,path=None):
    if path==None:
        return checkdire(name),None
    elif path!=None:
        if type(path)!=str:
            raise core.StoreError("the type of path must be str",core.StoreError.VarType)
        obj= checkdire(path+'/'+name)
        if obj!=None:
            return obj,path
    
    stack=[]
    node=fileroot
    node_ind=0
    while True:
        if node_ind<len(node):
            if node[node_ind].tid>0:
                if node[node_ind].name==name:
                    return node[node_ind],get_path(stack,node)
            elif node[node_ind].tid<0:
                stack.append((node,node_ind+1))
                node=node[node_ind]
                node_ind=-1
        node_ind+=1
        if node_ind>=len(node):
            if len(stack)==0:
                break
            node,node_ind=stack.pop()
    return None,None


def getpre(path,iscreat=True):
    pathstack=path.strip('/').split('/')
    node=fileroot
    pre=node
    stacknum=len(pathstack)
    i=0
    while i<stacknum-1:
        curname=pathstack[i]
        if curname=="":
            i+=1
            continue
        pre=node
        node=node[curname]
        if node==None:
            if iscreat!=True:
                return None,None
            pre[curname]=core.Storetypes[0](name=curname)
            node=pre[curname]
        i+=1

    return node,pathstack[i]

def getobj(path):
    pre,objname=getpre(path,False)
    if pre==None:
        return None
    return pre[objname]

    pass

def transfer(oripath,target):
    oripre,oriname=getpre(oripath)
    tarpre,tarname=getpre(target)
    if tarpre==oripre[oriname]:
        raise core.StoreError("target's parent is current obj",1)
    tarobj,tarpath=checkexists(tarname,'/'.join(target.split('/')[:-1]))
    oriobj=oripre[oriname]
    if oriobj==None:
        raise core.StoreError("error",1)
    if  tarobj!=oriobj and getattr(oriobj,"is_physical")==True:
        oriroute=os.path.join(Cfg.cfg.filestore.defpath,oriname+('.'+oriobj.suffix if oriobj.is_join_suff else ''))
        tarroute=os.path.join(Cfg.cfg.filestore.defpath,tarname+('.'+oriobj.suffix if oriobj.is_join_suff else ''))
        if (tarobj!=None):
            if tarobj.tid<0:
                raise core.StoreError("%s is exists, it is a node"%(target),core.StoreError.Exist)
            elif tarobj.tid>0:
                raise core.StoreError("%s is exists, it is %s"%(tarobj.name,tarpath+'/'+tarobj.name),core.StoreError.Exist)
                
        if oriroute !=tarroute:
            try:
                if os.path.exists(tarroute):
                    raise core.StoreError("%s is exists"%(tarroute),core.StoreError.Exist)
                os.rename(oriroute,tarroute)
            except:
                raise core.StoreError("%s -> %s error"%(oriroute,tarroute),core.StoreError.missing)
    
    if tarpre==oripre and oriname==tarname :
        return oriname,oriobj
    tarpre[tarname]=oriobj
    tarpre[tarname].name=tarname
    oripre.pop(oriname)
    return tarname,tarpre[tarname]

def MakeDir(path):
        dlist=[]
        while True:
            cpath,cname=os.path.split(path)
            dlist.insert(0,cname)
            if os.path.exists(cpath):
                break
        for i in dlist:
            cpath=os.path.join(cpath,i)
            os.mkdir(cpath)
        pass


def remove(objpath):
    try:
        fileroot.remove(objpath.strip('/').split('/'))
    except core.StoreError as e:
        log(e.ErrorMessage,2,log_title)
    save()


def search(root,search_str=None,note=False):
    backroot=default_node(name='/')
    stack=[]
    backstack=[]
    statustack=[]
    curr_note=root
    currback=backroot
    curr_status=False
    i=0
    while True:
        if i<len(curr_note):
            if curr_note[i].tid<0:
                stack.append((curr_note,i+1))
                curr_note=curr_note[i]
                currback[curr_note.name]=default_node(name=curr_note.name)
                backstack.append(currback)
                currback=currback[curr_note.name]
                i=-1
                if note:
                    statustack.append(curr_status)
                    if search_str==None or curr_status==True:
                        curr_status=True
                    else:
                        curr_status=search_str in curr_note.name
            elif curr_note[i].tid>0:
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


def remake():
    clear_error()
    def makeargs(obj):
        result=args.args()
        for i in obj.Attr_info:
            result[obj.Attr_info[i]]=obj.attr[i]
            pass
        result.name=obj.name
        result.type=obj.suffix
        return result
        pass
    objs=get_objs(fileroot)
    for obj in objs:
        obj.__class__.handle(makeargs(obj))
    pass

def clear_empty(notes):
    
    stack=[]
    curr_note=notes
    curr_objs=False
    i=0
    while True:
        if i<len(curr_note):
            if curr_note[i].tid<0:
                stack.append((curr_note,i+1,curr_objs))
                curr_note=curr_note[i]
                
                curr_objs=False
                i=-1
            elif curr_note[i].tid>0:
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
            if curr_note[i].tid<0:
                stack.append((curr_note,i+1))
                curr_note=curr_note[i]
                i=-1
            elif curr_note[i].tid>0:
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
        need=list(obj.Attr_info.keys())
    for i in need:
        attrs[obj.Attr_info[i].name]=obj.attr[i]
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
            if curr_note[i].tid<=0:
                stack.append((curr_note,i+1))
                curr_note=curr_note[i]
                i=-1
            elif curr_note[i].tid>0:
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
    

def export(to_file,from_note):
    to_fd=core.fileio(to_file,'w')
    note=checkdire(from_note)
    parent,_=split_path(from_note)
    note.export(to_fd,parent)
    to_fd.close()

def isexists(name):
    if bool(name)==False:
        return False
    obj,_=checkexists(name)
    if obj==None:
        return False
    else:
        return True

def rename(srcpath,name,targetpath,targetname):
    try:
        transfer(f"{srcpath}/{name}",f"{targetpath}/{targetname}")
    except core.StoreError as e:
        #print(e.ErrorMessage,f"{srcpath}/{name}",f"{targetpath}/{targetname}")
        return False
    save()
    return True

def getObj(path,name):
    return getobj(f"{path}/{name}")

def getObjInfoFromName(name):
    return checkexists(name)

def makeArgs(type_,name,path,attrs):
    result=args.args()
    for i in attrs:
        result[i]=attrs[i]
    result.name=name
    result.path=path
    for storeType in core.Storetypes.values():
        if storeType.suffix==type_:
            resultType=storeType
            break
    result.type=type_
    return result,resultType
    pass
