import os
import sys
import filestore.core
from information.log import log

log_title="cfg"
class CfgExce(Exception):
    parse=0
    argerror=1
    def __init__(self,message,id):
        super(CfgExce,self).__init__()
        self.ErrorMessage=message
        self.Errorid=id
        pass

class CfgObj():
    int="int"
    
    def __init__(self,type,value):
        self.type=type
        value=self.parseValue(value)
        self.value=value

    def parseValue(self,value):
        if self.type=='':
            self.type='Any'
        if self.type==CfgObj.int:
            return int(value)
        return value

class Cfg(object):
    def __init__(self,*arg,**karg):
        self.attr={}
        self.attrset={}
        super().__init__()
    
    def __getattribute__(self, name: str,status=False):
        try:
            
            return super().__getattribute__(name)
        except:
            pass
        if self.attr.get(name)==None:
            return self.attrset.get(name)
        
        if status==False:
            return self.attr.get(name).value
        else:
            return self.attr.get(name)
        
    
    def __setattr__(self, __name: str, __value):
        if __name=='attr' or __name=='attrset':
            return super().__setattr__(__name,__value)
        
        if type(__value)==CfgObj:
            self.attr[__name]=__value
        else:
            self.attrset[__name]=__value
    
    def __getitem__(self,index):
        if type(index)==tuple:
            name,status=index
        else:
            name=index
            status=False
        return self.__getattribute__(name,status)
    
    def __setitem__(self,name,value):
        self.__setattr__(name,value)

    def __iter__(self):
        return Cfg.cfgitem(self)

    def __str__(self):
        out=""
        if bool(self.attr):
            out+=str(self.attr)
        if bool(self.attrset):
            out+=str(self.attrset)
        return out

    def __repr__(self):
        return str(self)
    
    def save(self,f,depth=0):
        if depth==0:
            left='{'
            right='}'
        else:
            left='['
            right=']'
        for i in self:
            
            if type(self[i])!=Cfg:
                f.write(f"{i}:{self[i,True].type}={self[i]}\n")
            else:
                if self[i]==None:
                    continue
                f.write(f"{left}{i}{right}\n")
                self[i].save(f,depth+1)
                if depth==0:
                    f.write('\n')
            pass
    
    def length(self):
        return len(self.attr),len(self.attrset)
    
    def groupName(self):
        return list(cfg.attrset.keys())
            
    
    def toDict(self):
        result={}
        attr=self.attr
        for i in attr:
            result[i]=(attr[i].type,attr[i].value)
        attrset=self.attrset
        for i in attrset:
            result[i]=attrset[i].toDict()
        return result

    @staticmethod
    def cfgitem(cfg):
        for i in cfg.attr:
            yield i
        for i in cfg.attrset:
            yield i

cfg=Cfg()

defconfig={'deftype': None}

def makeCfgFromDict(cfgDict,depth=0):
    if depth==0:
        global cfg
    cacheCfg=Cfg()
    for i in cfgDict:
        if type(cfgDict[i])==dict:
            cacheCfg[i]=makeCfgFromDict(cfgDict[i],depth+1)
        else:
            Type,value=cfgDict[i]
            cacheCfg[i]=CfgObj(Type,value)
    if depth!=0:
        return cacheCfg
    else:
        cfg=cacheCfg
        savecfg()

    pass

def parse_cfg(cfgfile):
    currcfg=cfg
    currline=cfgfile.readline()
    groupcfgname=""
    while currline:
        currline=currline.strip()
        if currline=='':
            pass
        elif currline[0]=='{':
            groupcfgname=currline[1:currline.find('}')]
            groupcfg=Cfg()
            cfg[groupcfgname]=groupcfg
            currcfg=groupcfg
            pass
        elif currline[0]=='[':
            subcfgname=currline[1:currline.find(']')]
            subcfg=Cfg()
            cfg[groupcfgname][subcfgname]=subcfg
            currcfg=subcfg
            pass
        elif '=' in currline:
            eqind=currline.find('=')
            attrname=currline[:eqind]
            attrvalue=currline[eqind+1:]
            colonind=attrname.find(':')
            if colonind==-1:
                attrtype="Any"
            else:
                attrtype=attrname[colonind+1:]
                attrname=attrname[:colonind]

            currcfg[attrname]=CfgObj(attrtype,attrvalue)
        else:
            raise CfgExce("cfg format error",CfgExce.parse)

        currline=cfgfile.readline()

def parsecfg():
    global cfg
    cfgpath=os.path.join(sys.path[0],"helper2.cfg")
    if os.path.exists(cfgpath)==False:
        return
    try:
        f=open(cfgpath,'r')
        parse_cfg(f)
    except CfgExce as e:
        f.close()
        bak=cfgpath+'.bak'
        if os.path.exists(bak):
            log("Failed to parse %s,attempting to backup files %s soon"%(cfgpath,bak),0,log_title)
            cfg=Cfg() 
            try:
                f=open(bak,'r')
                parse_cfg(f)
            except CfgExce:
                log("Failed to parse %s, %s"%(cfgpath,bak),0,log_title)
                return
        else:
            log("Failed to parse %s, %s does not exists"%(cfgpath,bak),0,log_title)
            return
    f.close()

def backupcfg():
    cfgpath=os.path.join(sys.path[0],"helper2.cfg")
    if os.path.exists(cfgpath)==False:
        return
    f=open(cfgpath,'r')
    back=open(cfgpath+'.bak','w')
    back.write(f.read())

def savecfg():
    backupcfg()
    f=open(os.path.join(sys.path[0],"helper2.cfg"),'w')
    cfg.save(f)
    f.close()

def make_defcfg():
    global defconfig
    for i in filestore.core.Storetypes:
        if i!=0:
            defconfig['deftype']=filestore.core.Storetypes[i].suffix
    pass

def checkConfig(headName,defcfg,topcfg=None):
    global cfg
    if topcfg==None:
        headCfg=cfg[headName]
    else:
        headCfg=topcfg[headName]

    if headCfg==None:
        headCfg=Cfg()

    status=False
    for cfggroup in defcfg:
        groupCfg=headCfg[cfggroup]


        if type(defcfg[cfggroup])!=dict:
            if groupCfg!=None:
                continue
            status=True
            value=defcfg[cfggroup]
            
            if type(value)!=tuple or len(value)>2:
                cfgobj=CfgObj("Any",str(value))
            else:
                cfgobj=CfgObj(*value)
            headCfg[cfggroup]=cfgobj
            continue

        cstatus=checkConfig(cfggroup,defcfg[cfggroup],headCfg)
        if cstatus==True:
            status=cstatus

    if topcfg==None:
        cfg[headName]=headCfg
    else:
        topcfg[headName]=headCfg

    if status==True and topcfg==None:
        savecfg()
    return status

def checkcfg():
    global cfg
    make_defcfg()
    checkConfig('config',defconfig)
    
def init():
    parsecfg()