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

class Cfg(object):
    def __init__(self,*arg,**karg):
        self.attr={}
        self.attrset={}
        super().__init__()
    
    def __getattribute__(self, name: str):
        try:
            return super().__getattribute__(name)
        except:
            pass
        if self.attr.get(name)==None:
            return self.attrset.get(name)
        return self.attr.get(name)
    
    def __setattr__(self, __name: str, __value):
        if __name=='attr' or __name=='attrset':
            return super().__setattr__(__name,__value)
        if type(__value)==str:
            self.attr[__name]=__value
        else:
            self.attrset[__name]=__value
    
    def __getitem__(self,name):
        return self.__getattribute__(name)
    
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
    
    def save(self,f):
        for i in self:
            if type(self[i])==str:
                f.write("%s=%s\n"%(i,self[i]))
            else:
                if self[i]==None:
                    continue
                f.write("\n[%s]\n"%(i))
                self[i].save(f)
            pass

    @staticmethod
    def cfgitem(cfg):
        for i in cfg.attr:
            yield i
        for i in cfg.attrset:
            yield i

    

cfg=Cfg()

defconfig={'deftype': None, 'defpath': None,'pad': {'chr': '32', 'num': '2'}, 'attrpad': {'chr': '32', 'num': '4'}}


def parse_cfg(cfgfile):
    currcfg=cfg
    currline=cfgfile.readline()
    while currline:
        currline=currline.strip()
        if currline=='':
            pass
        elif currline[0]=='[':
            subcfgname=currline[1:currline.find(']')]
            subcfg=Cfg()
            cfg[subcfgname]=subcfg
            currcfg=cfg[subcfgname]
            pass
        elif '=' in currline:
            eqind=currline.find('=')
            attrname=currline[:eqind]
            attrvalue=currline[eqind+1:]
            currcfg[attrname]=attrvalue
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
    for i in filestore.core.Storetypes:
        if i!=0:
            defconfig['deftype']=filestore.core.Storetypes[i].suffix
            break
    defconfig['defpath']=os.path.join(sys.path[0],'objs')
    pass

def make_must_cfg():
    if os.path.exists(cfg.defpath):
        if not os.path.isdir(cfg.defpath):
            raise CfgExce("defpath not direction",CfgExce.argerror)
    else:
        os.mkdir(cfg.defpath)
        pass
    pass

def checkcfg():
    make_defcfg()
    status=False
    for i in defconfig:
        if cfg[i]==None:
            status=True
            if type(defconfig[i])!=str:
                sub=Cfg()
                for j in defconfig[i]:
                    sub[j]=defconfig[i][j]
                cfg[i]=sub

            else:
                cfg[i]=defconfig[i]
    if status:
        savecfg()
    
    make_must_cfg()

def init():
    parsecfg()
    checkcfg()