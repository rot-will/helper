from PySide6.QtCore import Qt,Signal,QEvent,QPoint,QPropertyAnimation,QSize,QParallelAnimationGroup
from PySide6.QtWidgets import QMessageBox
import filestore.filesystem as filesystem
import core.config as config
import re

Node_type=-1
class Child_Info(object):
    def __init__(self,name,path,type,childs=None,child_nodes=None):
        self.name=name
        self.path=path
        self.type=type
        self.childs=childs
        self.child_nodes=child_nodes
    
    def __str__(self):
        if self.childs!=None:
            return f"{self.name}:{self.childs}"
        else:
            return f"{self.name}->obj"
    
    def __repr__(self):
        return str(self)

    def __iter__(self):
        return iter(self.childs)
    
class sortMode:
    Nonsort=0
    Order=1
    Invert=2

class ViewMode:
    List=1
    Tree=2
    @staticmethod
    def listMode(TopNode):
        result=Child_Info(TopNode.name,TopNode.path,Node_type,[],{})
        currNode=TopNode
        currInd=0
        currChild=[]
        stack=[]
        while True:
            currChild=[]
            for child in currNode.childs:
                if child.type==Node_type:
                    currChild.append(child)
                else:
                    result.childs.append(child)
            
            if len(currChild)==0 and len(stack)!=0:
                currNode,currInd,currChild=stack.pop()
            while currInd >= len(currChild) and len(stack)>0:
                currNode,currInd,currChild=stack.pop()

            if currInd>=len(currChild):
                break

            stack.append((currNode,currInd+1,currChild))
            currNode=currChild[currInd]
            currInd=0
        return result
        pass
    @staticmethod
    def treeMode(TopNode):
        return TopNode
        pass

    method={List:listMode,Tree:treeMode}

application_ico=None
windows_dire=None
root=Child_Info("/","/",-1,[],{})
filterRule=""
curr_path=["",""]
rebuild=lambda xx:print("No bound function!!!")
sort_mode=lambda : sortMode.Nonsort
topinfo=lambda a,b,c: None
view_mode=lambda : ViewMode.Tree
expendBox=[]

def get_child(path,name):
    path=path.strip('/').strip()
    if path!='':
        path=path.split("/")
    top=root
    for i in path:
        if i=='':
            continue
        top=top.child_nodes.get(i)
        if top==None:
            return None
    if bool(name)==False:
        return top
    return top.child_nodes.get(name)

def sortchild(top,depth=0,mode=0):
    if top==None:
        top=root
    result=Child_Info(top.name,top.path,Node_type,[],{})
    if depth>1:
        return result,None,None
    objs=[]
    nodes=[]
    for child in top.childs:
        if child.type==Node_type:
            nodes.append(child)
        else:
            objs.append(Child_Info(child.name,child.path,child.type))
    if mode==sortMode.Nonsort:
        result.childs=objs.copy()
    else:
        if mode==sortMode.Invert:
            reverse=True
        else:
            reverse=False
        result.childs=sorted(objs,key=lambda d:d.name,reverse=reverse).copy()
        nodes.sort(key=lambda d:d.name,reverse=reverse)

    for node in nodes:
        child,_,_=sortchild(node,depth+1,mode)
        result.childs.append(child)

        pass
    return result,len(objs),len(nodes)
    pass

def useRule(child,rule):
    if re.search(rule,child.name):
        return True
    return False
    pass

def filterChild(TopNode,filterRule):
    if TopNode==None:
        return Child_Info("未找到","",Node_type,[],{})
    
    result=Child_Info(TopNode.name,TopNode.path,Node_type,[],{})
    for child in TopNode.childs:
        if child.type==Node_type:
            filter_child=filterChild(child,filterRule)
            if len(filter_child.childs)!=0 or bool(filterRule)==False:
                result.childs.append(filter_child)
                result.child_nodes[filter_child.name]=filter_child
        elif useRule(child,filterRule):
            result.childs.append(Child_Info(child.name,child.path,child.type))
            pass
            
        pass
    return result
    pass

def splitPath(path):
    path=path.rstrip('/')
    slashIndex=path.rfind('/')
    
    if slashIndex==-1:
        name=path
        path=""
    else:
        name=path[slashIndex+1:]
        path=path[:slashIndex]
    return path,name

def viewMode(TopNode,mode):
    #return TopNode
    return ViewMode.method[mode](TopNode)
    pass

def Restore(path=None,name=None):
    global curr_path,expendBox
    sort=sort_mode()
    view=view_mode()
    if path==None:
        path,name=curr_path
    else:
        if name==None:
            path,name=splitPath(curr_path[0])
        curr_path=[path,name]
        expendBox=[]
    root,child_num,child_node_num=sortchild(
        viewMode(
            filterChild(
                get_child(path,name),
                filterRule),
            view
            ),
        0,sort)
    if root.name=="/":
        name="/"
    else:
        name=f"{root.path}/{root.name}"
    
    topinfo(name,str(child_num),str(child_node_num))
    rebuild(root)

def rename(srcpath,name,targetpath,targetname):
    if name!=targetname and filesystem.isexists(targetname):
        return False
    status=filesystem.rename(srcpath,name,targetpath,targetname)
    MakeRoot()
    Restore()
    return status

def remove(path,name):
    filesystem.remove(f"{path}/{name}")
    MakeRoot()
    Restore()
    pass

def FormatPath(path):
    childpath=path.split('/')
    formatPath=''
    for cpath in childpath:
        formatPath+=f'/{cpath}'
    pass

def Search(path,rule):
    global filterRule
    filterRule=rule
    path,name=splitPath(path)
    Restore(path,name)

def referse():
    filesystem.fileroot=None
    filesystem.init()
    filesystem.clear_error()
    MakeRoot()
    Restore()
    pass

def changeExpBox(name,add=True):
    global expendBox
    if add==True and name not in expendBox:
        expendBox.append(name)
    elif add==False and name in expendBox:
        expendBox.remove(name)
        
    pass

def getTypeNames():
    names=[]
    for store_type_id in filesystem.core.Storetypes:
        store_type=filesystem.core.Storetypes[store_type_id]
        
        names.append(store_type.suffix)
    return names

def getTypeAttrFromName(name):
    for store_type in filesystem.core.Storetypes.values():
        if store_type.suffix==name:
            attr={}
            needAttr=[]
            if hasattr(store_type,"Attr_info")==None:
                return attr
            attrinfo=store_type.Attr_info
            if hasattr(store_type,"Needattr"):
                needAttr=store_type.Needattr.copy()

            
            for attrid in attrinfo:
                if attrinfo[attrid].type==filesystem.core.attrType.str:
                    attrtype=str
                if attrinfo[attrid].type==filesystem.core.attrType.list:
                    attrtype=list
                elif attrinfo[attrid].type==filesystem.core.attrType.branch:
                    attrtype=bool
                isneed=(attrid in needAttr)
                attr[attrinfo[attrid].name]=(attrtype,None,isneed)
            
            return attr
    return None
    
def getChildNode(path):
    Processed_path="/"
    nodeL=path.split("/")
    for node in nodeL[:-1]:
        if node=='':
            continue
        Processed_path+=f"{node}/"
    sname=nodeL[-1]

    curr=get_child(Processed_path,"")
    if curr==None:
        return [],[]
    result=[f"{Processed_path}{sname}"]
    for child_node in curr.child_nodes:
        if child_node.startswith(sname):
            result.append(f"{Processed_path}{child_node}")
    return list(curr.child_nodes.keys()),result

def getAttrFromPath(path,name):
    obj=filesystem.getObj(path,name)
    if obj==None:
        return None
    
    needAttr=[]
    
    objType=filesystem.core.Storetypes[obj.tid]
    if hasattr(objType,"Needattr") and hasattr(objType,"Attr_info") :
        for attrid in objType.Needattr:
            needAttr.append(objType.Attr_info[attrid].name)
    attrs=obj.getAttr()
    result={}
    for attr in attrs:
        attrtype=str
        if attrs[attr][0]==filesystem.core.attrType.list:
            attrtype=list
        elif attrs[attr][0]==filesystem.core.attrType.branch:
            attrtype=bool
        isneed=(attr in needAttr)
        result[attr]=(attrtype,attrs[attr][1],isneed)
    return obj.suffix,result

def typeExists(childType):
    for store_type in filesystem.core.Storetypes.values():
        if store_type.suffix==childType:
            return True
    return False
    pass

def addCheckChildInfo(childType,childname,childpath,childAttr):
    if typeExists(childType)==False:
        return 1
    if childname=='':
        return 3
    if filesystem.isexists(childname):
        return 2
    args=filesystem.makeArgs(childType,childname,childpath,childAttr)
    filesystem.make_filesystem(*args)
    MakeRoot()
    Restore()
    return 0

def changeCheckChildInfo(originPath,originName,childType,childname,childpath,childAttr):
    if typeExists(childType)==False:
        return 1 
    if childname=="":
        return 3
    obj,objPath=filesystem.getObjInfoFromName(childname)
    if obj!=None and obj.name !=originName:
        return 2
    if originName!=childname:
        status=rename(originPath,originName,childpath,childname)
        if status==False:
            return 2
    args=filesystem.makeArgs(childType,childname,childpath,childAttr)
    filesystem.make_filesystem(*args)
    
    MakeRoot()
    Restore()
    return 0


def getConfigGroup():
    cfgDict=config.cfg.toDict()
    groups=[]
    globalcfg={}
    for cfg in cfgDict:
        if type(cfgDict[cfg])==dict:
            groups.append((cfg,cfgDict[cfg]))
        else:
            globalcfg[cfg]=cfgDict[cfg]
    if len(globalcfg)!=0:
        groups.insert(0,('global',globalcfg))
    return groups
        
def setConfigFromDict(cfgDict):
    if cfgDict.get("global") !=None:
        for i in cfgDict['global']:
            cfgDict[i]=cfgDict['global'][i]
        cfgDict.pop("global")
    config.makeCfgFromDict(cfgDict)
    return True
    pass
    


def MakeRoot():
    global root
    root=Child_Info("","",Node_type,[],{})
    i=0
    stack=[]
    this=filesystem.fileroot
    this_info=root
    this_node_index=0

    while True:
        i=0
        
        subnotes=[]
        while i<len(this):
            if this[i].tid==Node_type:
                subnotes.append(this[i])
            else:
                this_info.childs.append(Child_Info(this[i].name,f"{this_info.path}/{this_info.name}",this[i].tid))
            i+=1
        
        while this_node_index>=len(subnotes) and len(stack)>0:
            this,parent_info,this_node_index,subnotes=stack.pop()
            parent_info.childs.append(this_info)
            parent_info.child_nodes[this_info.name]=this_info
            this_info=parent_info

        if this_node_index<len(subnotes):
            stack.append((this,this_info,this_node_index+1,subnotes))
            child=subnotes[this_node_index]
            if this_info!=root:
                child_path=f"{this_info.path}/{this_info.name}"
            else:
                child_path=f""
            child_info=Child_Info(child.name,child_path,child.tid,[],{})

            this=child
            this_info=child_info
            this_node_index=0
            pass
        else:
            break
    root.name='/'
            
def init():
    global curr_path
    global Node_type
    Node_type=filesystem.core.Storetypes[0].tid
    curr_path=["",""]
    MakeRoot()

