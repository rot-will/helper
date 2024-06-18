import filestore.core as core
import os,zlib,sys
from filestore.filesystem import checkexists,transfer,getpre,parse_object,save_object
import  core.config as Cfg
import argparse

"""
作为文件父类
之后创建文件子类如 Fbat,Fsh等
"""
class File(core.fobj):
    suffix="bat"
    tid=1
    is_join_suff=True
    class Attr:
        commid=0
        runmid=1
        preid=2
        runpid=3
        icoid=4
        descid=5

    Id_Attr={Attr.commid:"command",
            Attr.runmid:"runmode",
            Attr.preid:"preboot",
            Attr.runpid:"runpath",
            Attr.icoid:"icopath",
            Attr.descid:"descript"}
    
    Needattr=[Attr.commid,Attr.runmid]
    
    Attr_types={Attr.commid:core.attrType.str,
            Attr.runmid:core.attrType.branch,
            Attr.preid:core.attrType.list,
            Attr.runpid:core.attrType.str,
            Attr.icoid:core.attrType.str,
            Attr.descid:core.attrType.str}
    
    Attr_Arg={
        Attr.commid:"-com",
        Attr.runmid:"-start",
        Attr.preid:"-pre",
        Attr.runpid:"-rpath",
        Attr.icoid:"-ico",
        Attr.descid:"-desc"
    }

    Out_need_attr={Attr.descid}
    def checkNeedful(self):
        for i in self.Needattr:
            if self.Attr_types[i]!=core.attrType.branch and bool(self.attr.get(i))==False:
                errmessage="Some necessary attr were not initialized:"
                for i in self.Needattr:
                    errmessage+=self.Id_Attr[i]+','
                errmessage=errmessage.rstrip(',')
                raise core.StoreError(errmessage,core.StoreError.init)

    @staticmethod
    def make_sub_opt(grp,class_,attrid,**kargs):
        if class_.Attr_types[attrid]==core.attrType.str:
            kargs['default']=None
        elif class_.Attr_types[attrid]==core.attrType.branch:
            kargs['nargs']='?'
            kargs['default']=0
        elif class_.Attr_types[attrid]==core.attrType.list:
            kargs['nargs']='+'
            kargs['default']=None
        grp.add_argument(class_.Attr_Arg[attrid],dest=class_.Id_Attr[attrid],**kargs)
        pass

    @staticmethod
    def make_opt(arg:argparse.ArgumentParser):
        grp=arg.add_argument_group("%s obj"%File.suffix)
        File.make_sub_opt(grp, File, File.Attr.commid, \
                    help="Command executed at runtime")
        
        File.make_sub_opt(grp, File, File.Attr.runmid, \
                    help="Whether to execute independently (0: console , 1: window&console , 2: window)")
        
        File.make_sub_opt(grp, File, File.Attr.preid, \
                    help="Environment configuration before command execution(Allow multiple)")
        
        File.make_sub_opt(grp, File, File.Attr.runpid, \
                    help="Directory where the command is executed")
        
        File.make_sub_opt(grp, File, File.Attr.icoid, \
                    help="Icons of objects in the window")
        
        File.make_sub_opt(grp, File, File.Attr.descid, \
                    help="Description of the current object")
        
    
    @staticmethod 
    def checkname(name):
        legal_char='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-'
        for i in name:
            if i not in legal_char:
                return False
        return True

    @staticmethod
    def handle(args):
        if File.checkname(args.name)==False:
            raise core.StoreError("%s is illegal"%args.name,core.StoreError.args)
        if args.path==None:
            path='/'
        else:
            path=args.path
        obj,oripath=checkexists(args.name,path)
        resarg={}
        objtype=core.filetypes[args.type]
        for i in objtype.Id_Attr:
            resval=getattr(args,objtype.Id_Attr[i])
            if objtype.Attr_types[i]==core.attrType.str:
                if resval==None:
                    resval=""
                else:
                    resval=resval.replace('"','^"')
                
            elif objtype.Attr_types[i]==core.attrType.list:
                nresval=[]
                if resval==None or len(resval)==0:
                    nresval=['']
                else:
                    for o in resval:
                        value=o#.replace('"','""')
                        if value!='':
                            nresval.append(value)
                
                resval=nresval
            elif objtype.Attr_types[i]==core.attrType.branch:
                if resval==None:
                    resval=1
                resval=int(resval)
            resarg[objtype.Id_Attr[i]]=resval

        if obj==None:
            pre,curname=getpre(path+'/'+args.name)
            obj=objtype(name=curname,**resarg)
            pre[curname]=obj
        elif obj.suffix != args.type:
            raise core.StoreError("%s already exists,and that its type is %s ,not %s"%(args.name,obj.suffix,args.type))
        else:
            if args.path!=None and oripath != path :
                tarname,obj=transfer(oripath+'/'+args.name,path)
            else:
                for i in obj.Id_Attr:
                    if obj.Attr_types[i]==core.attrType.branch or getattr(args,obj.Id_Attr[i])!=None:
                        obj.attr[i]=resarg.get(obj.Id_Attr[i])
                
            obj.Make()
            
    def __init__(self,*args,**kargs):
        self.attr={}
        if len(kargs)==0 and len(args)==1 and type(args[0])==core.fileio:
            self.Parse(args[0])
            return
        if kargs.get('name')==None:
            raise core.StoreError("Build a File object need path,name attr",core.StoreError.init)
        super().__init__(name=kargs['name'])
        if len(kargs)==1:
            return
        for i in self.Id_Attr:
            if kargs.get(self.Id_Attr[i])!=None:
                self.attr[i]=kargs[self.Id_Attr[i]]
        self.checkNeedful()
        self.Make()

    def checkExist(self,level=1):
        if  os.path.exists(os.path.join(Cfg.cfg.bat.defpath,self.name+'.'+self.suffix))==False:
            if level==1:
                raise core.StoreError("The File object is invalid",core.StoreError.Exist)
            return False
        return True
    

    """
        EditComm
        EditIco
        EditDesc
        编辑bat文件指定内容
        Make
        编译bat文件开头结尾
    """
    def EditComm(self,file):
        get_arg="%*"
        if self.attr[self.Attr.runmid]==1:
            wmode=f'start "{self.name}" '
        elif self.attr[self.Attr.runmid]==2:
            wmode=f"explorer "
            get_arg=""
        else:
            wmode=""
            
        wdata=f"""set {self.Id_Attr[self.Attr.runpid]}={self.attr[self.Attr.runpid]}
set "{self.Id_Attr[self.Attr.commid]}={self.attr[self.Attr.commid]}"
set {self.Id_Attr[self.Attr.runmid]}={wmode}
"""
        file.write(wdata)
        return get_arg

    def Make(self):
        if self.is_join_suff:
            realpath=os.path.join(Cfg.cfg.bat.defpath,self.name+'.'+self.suffix)
        else:
            realpath=os.path.join(Cfg.cfg.bat.defpath,self.name)
        batf=open(realpath,'w')
        title="""@echo off
setlocal enabledelayedexpansion 
"""
        batf.write(title)
        get_arg=self.EditComm(batf)
        predata=""
        if type(self.attr[self.Attr.preid])==str:
            predata=self.attr[self.Attr.preid]
        elif type(self.attr[self.Attr.preid])==list:
            for i in self.attr[self.Attr.preid]:
                predata+=i+'\n'
        else:
            raise core.StoreError("preboot Expected str/bytes type",core.StoreError.VarType)
        if predata.strip()=="":
            predata=""
        

        bann=f"""set currpwd=%CD%
if not "%{self.Id_Attr[self.Attr.runpid]}%"=="" (cd /d %{self.Id_Attr[self.Attr.runpid]}%)
{predata}
%{self.Id_Attr[self.Attr.runmid]}% %{self.Id_Attr[self.Attr.commid]}% {get_arg}
if not "%{self.Id_Attr[self.Attr.runpid]}%"=="" (cd /d %currpwd%)
"""
        
        batf.write(bann)
        batf.write("endlocal")
        batf.close()
        pass

    """
        用于删除对象
    """
    def remove(self,key=None):
        if bool(key):
            raise core.StoreError("%s is File,not Dire"%self.name,core.StoreError.missing)
        self.checkExist()
        if self.is_join_suff:
            realpath=os.path.join(Cfg.cfg.bat.defpath,self.name+'.'+File.suffix)
        else:
            realpath=os.path.join(Cfg.cfg.bat.defpath,self.name)
        os.remove(realpath)
        return

    def export_attr(self,attrid,attrdata):
        if self.Attr_types[attrid]==core.attrType.str:
            attr_cache=attrdata.replace('"','""')
            attrvalue=f'"{attr_cache}"'
        elif self.Attr_types[attrid]==core.attrType.list:
            if attrdata==[]:
                return " "
            else:
                attrvalue=""
                for i in attrdata:
                    attr_cache=i.replace('"','""')
                    attrvalue+=f'"{attr_cache}" '
        elif self.Attr_types[attrid]==core.attrType.branch:
            attrvalue=attrdata
        return f" {self.Attr_Arg[attrid]} {attrvalue}"

    def export(self,file:core.fileio,path:str):
        title=f"helper -n {self.name} -p {path} -t {self.suffix}"
        for i in self.attr:
            title+=self.export_attr(i,self.attr[i])

        file.Write(title+'\n')
        pass
    
    def getAttr(self):
        result={}
        for i in self.attr:
            result[self.Id_Attr[i]]=(self.Attr_types[i],self.attr[i])
        return result
    
    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return str(self)

FILETYPES=[File]

def CheckCONFIG():
    defcfg={'defpath':os.path.join(sys.path[0],'objs')}
    Cfg.checkConfig('bat',defcfg)
    #print(Cfg.cfg)
    defpath=Cfg.cfg.bat.defpath
    if os.path.exists(defpath):
        if not os.path.isdir(defpath):
            raise Cfg.CfgExce("defpath not direction",Cfg.CfgExce.argerror)
    else:
        os.mkdir(defpath)
        pass