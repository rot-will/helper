import filestore.filesystem
from filestore.core import StoreError
import os




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
    node=filestore.filesystem.fileroot
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
            raise StoreError("the type of path must be str",StoreError.VarType)
        obj= checkdire(path+'/'+name)
        if obj!=None:
            return obj,path
    
    stack=[]
    node=filestore.filesystem.fileroot
    node_ind=0
    while True:
        if node_ind<len(node):
            if node[node_ind].tid!=0:
                if node[node_ind].name==name:
                    return node[node_ind],get_path(stack,node)
            else:
                stack.append((node,node_ind+1))
                node=node[node_ind]
                node_ind=-1
        node_ind+=1
        if node_ind>=len(node):
            if len(stack)==0:
                break
            node,node_ind=stack.pop()
    return None,None


def getpre(path):
    pathstack=path.strip('/').split('/')
    node=filestore.filesystem.fileroot
    pre=node
    stacknum=len(pathstack)
    i=0
    while i<stacknum-1:
        curname=pathstack[i]
        pre=node
        node=node[curname]
        if node==None:
            pre[curname]=filestore.filesystem.core.Storetypes[0](name=curname)
            node=pre[curname]
        i+=1

    return node,pathstack[i]

def transfer(oripath,target):
    oripre,oriname=getpre(oripath)
    tarpre,tarname=getpre(target)
    tarobj,tarpath=checkexists(tarname,'/'.join(target.split('/')[:-1]))
    oriobj=oripre[oriname]
    if oriobj==None:
        raise StoreError("error",1)
    if tarobj!=None and tarobj!=oriobj:
        oriroute=os.path.join(oriobj.path,oriname+'.'+oriobj.suffix)
        tarroute=os.path.join(oriobj.path,tarname+'.'+oriobj.suffix)
        if tarobj.tid!=0:
            raise StoreError("%s is exists, and its path is %s"%(tarobj.name,tarpath+'/'+tarobj.name),StoreError.Exist)
        elif tarobj.tid==0:
            raise StoreError("%s is exists, it is a node"%(target),StoreError.Exist)
        if oriroute !=tarroute:
            try:
                if os.path.exists(tarroute):
                    raise StoreError("%s is exists"%(tarroute),StoreError.Exist)
                os.rename(oriroute,tarroute)
            except:
                raise StoreError("%s -> %s error"%(oriroute,tarroute),StoreError.missing)
    
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