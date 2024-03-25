import filestore.core as core
import os,zlib
from filestore.method import checkexists,transfer,getpre,MakeDir
from core.config import cfg
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

        pass
    
    Id_Attr={Attr.commid:"command",
            Attr.runmid:"runmode",
            Attr.preid:"preboot",
            Attr.runpid:"runpath",
            Attr.icoid:"icopath",
            Attr.descid:"descript"}
    Needattr=[Attr.commid,Attr.runmid]
    Attr_types={Attr.commid:str,
            Attr.runmid:bool,
            Attr.preid:list,
            Attr.runpid:str,
            Attr.icoid:str,
            Attr.descid:str
    }
    Out_need_attr={Attr.descid}
    def checkNeedful(self):
        for i in self.Needattr:
            if self.Attr_types[i]!=bool and bool(self.attr.get(i))==False:
                errmessage="Some necessary attr were not initialized:"
                for i in self.Needattr:
                    errmessage+=self.Id_Attr[i]+','
                errmessage=errmessage.rstrip(',')
                raise core.StoreError(errmessage,core.StoreError.init)
        pass
    @staticmethod
    def make_opt(arg:argparse.ArgumentParser):
        obj=arg.add_argument_group("%s obj"%File.suffix)
        obj.add_argument("-com",dest=File.Id_Attr[File.Attr.commid],default=None,help="Command executed at runtime")
        obj.add_argument("-start",dest=File.Id_Attr[File.Attr.runmid],action="store_true",default=False,help="Whether to execute independently")
        obj.add_argument("-pre",dest=File.Id_Attr[File.Attr.preid],nargs='+',default=None,help="Environment configuration before command execution(Allow multiple)")
        obj.add_argument("-rpath",dest=File.Id_Attr[File.Attr.runpid],default=None,help="Directory where the command is executed")
        obj.add_argument("-ico",dest=File.Id_Attr[File.Attr.icoid],default=None,help="Icons of objects in the window")
        obj.add_argument("-desc",dest=File.Id_Attr[File.Attr.descid],default=None,help="Description of the current object")
        obj.add_argument("-topath",dest='topath',default=None,help="Object entity storage location")
    
    @staticmethod 
    def checkname(name):
        legal_char='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-'
        for i in name:
            if i not in legal_char:
                return False
        return True
        pass

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
            if objtype.Attr_types[i]==str:
                if resval==None:
                    resval=""
                else:
                    resval=resval.replace("'",'"')
                
            elif objtype.Attr_types[i]==list:
                nresval=[]
                if resval==None or len(resval)==0:
                    nresval=['']
                else:
                    for o in resval:
                        value=o.replace("'",'"')
                        if value!='':
                            nresval.append(value)
                
                resval=nresval
            resarg[objtype.Id_Attr[i]]=resval
        if args.topath==None:
            realpath=cfg.defpath
        else:
            realpath=args.topath
        if obj==None:
            pre,curname=getpre(path+'/'+args.name)
            obj=objtype(name=curname,path=realpath,**resarg)
            pre[curname]=obj
        elif obj.suffix != args.type:
            raise core.StoreError("%s already exists,and that its type is %s ,not %s"%(args.name,obj.suffix,args.type))
        else:
            if args.path!=None and oripath != path :
                tarname,obj=transfer(oripath+'/'+args.name,path)
            elif args.topath!=None:
                obj.moveto(args.topath)
            else:
                for i in obj.Id_Attr:
                    if obj.Attr_types[i]==bool or getattr(args,obj.Id_Attr[i])!=None:
                        obj.attr[i]=resarg.get(obj.Id_Attr[i])
                
            obj.Make()
            
    def __init__(self,*args,**kargs):
        self.attr={}
        if len(kargs)==0 and len(args)==1 and type(args[0])==core.fileio:
            self.Parse(args[0])
            return
        if kargs.get("path")==None or kargs.get('name')==None:
            raise core.StoreError("Build a File object need path,name attr",core.StoreError.init)
        super().__init__(path=kargs['path'],name=kargs['name'])
        if len(kargs)==2:
            return
        for i in self.Id_Attr:
            if kargs.get(self.Id_Attr[i])!=None:
                self.attr[i]=kargs[self.Id_Attr[i]]
        self.checkNeedful()
        self.Make()

    def checkExist(self,level=1):
        if self.path==None or type(self.path)!=str or os.path.exists(os.path.join(self.path,self.name+'.'+self.suffix))==False:
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
        if self.attr[self.Attr.runmid]==True:
            wmode=f'start "{self.name}" '
        else:
            wmode=""
        wdata=f"""set {self.Id_Attr[self.Attr.runpid]}={self.attr[self.Attr.runpid]}
set {self.Id_Attr[self.Attr.commid]}={self.attr[self.Attr.commid]}
set {self.Id_Attr[self.Attr.runmid]}={wmode}
"""
        file.write(wdata)

    def Make(self):
        if self.is_join_suff:
            realpath=os.path.join(self.path,self.name+'.'+self.suffix)
        else:
            realpath=os.path.join(self.path,self.name)
        batf=open(realpath,'w')
        title="""@echo off
"""
        batf.write(title)
        self.EditComm(batf)
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
%{self.Id_Attr[self.Attr.runmid]}% %{self.Id_Attr[self.Attr.commid]}% %*
if not "%{self.Id_Attr[self.Attr.runpid]}%"=="" (cd /d %currpwd%)"""
        batf.write(bann)
        batf.close()
        pass

    """
        用于修改名称
    """
    def moveto(self,topath:str):
        self.checkExist()
        
        if File.is_join_suff:
            realname=self.name+'.'+File.suffix
        else:
            realname=self.name
        rtopath=os.path.join(os.path.realpath(topath),realname)
        if os.path.exists(topath)==False:
            os.rename(self.path,rtopath)
            self.path=rtopath
            return
        raise core.StoreError("The target location for the move already exists",core.StoreError.Exist)

    """
        用于删除对象
    """
    def remove(self,key=None):
        if bool(key):
            raise core.StoreError("%s is File,not Dire"%self.name,core.StoreError.missing)
        self.checkExist()
        if self.is_join_suff:
            realpath=os.path.join(self.path,self.name+'.'+File.suffix)
        else:
            realpath=os.path.join(self.path,self.name)
        os.remove(realpath)
        self.path=None
        return

    """
        解析备份文件,获取File对象
    """

    def parse_attr_t(self,attrid,attrdata):
        attrtype=self.Attr_types[attrid]
        if attrtype==str:
            self.attr[attrid]=attrdata
        elif attrtype==bool:
            if attrdata=="True":
                self.attr[attrid]=True
            else:
                self.attr[attrid]=False
        elif attrtype==list:
            if attrdata=='':
                value=[]
            else:
                value=attrdata.split('\n')
            self.attr[attrid]=value
        
    def Parseattr(self,file:core.fileio):
        attrnum=file.ReadByte()
        i=0
        while i<attrnum:
            attrsize=file.ReadWord()
            zattrdata=file.Read(attrsize)
            attrdata=zlib.decompress(zattrdata).decode("utf-8")
            attrid=file.ReadByte()
            self.parse_attr_t(attrid,attrdata)
            i+=1

    def Parse(self,file:core.fileio):
        name_l=file.ReadByte()
        name=file.Read(name_l).decode("utf-8")
        path_l=file.ReadWord()
        zpath=file.Read(path_l)
        path=zlib.decompress(zpath).decode("utf-8")
        super().__init__(path=path,name=name)
        self.Parseattr(file)

    """
        Save
        保存命令列表文件
    """
    def save_attr_t(self,attrid,attrdata)->str:
        if self.Attr_types[attrid]==str:
            return attrdata
        elif self.Attr_types[attrid]==bool:
            if attrdata==True:
                return 'True'
            return 'False'
        elif self.Attr_types[attrid]==list:
            return '\n'.join(attrdata)
        return ''

    def Saveattr(self,file:core.fileio):
        attrnum=len(self.attr)
        file.WriteByte(attrnum)
        for i in self.attr:
            attrvalue:str=self.save_attr_t(i,self.attr[i])
            zattrdata=zlib.compress(attrvalue.encode("utf-8"))
            file.WriteWord(len(zattrdata))
            file.Write(zattrdata)
            file.WriteByte(i)

    def Save(self,file:core.fileio):
        file.WriteByte(self.tid)
        wname=self.name.encode("utf-8")
        file.WriteByte(len(wname))
        file.Write(wname)
        zpath=zlib.compress(self.path.encode("utf-8"))
        file.WriteWord(len(zpath))
        file.Write(zpath)
        self.Saveattr(file)

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return str(self)

core.Storetypes[File.tid]=File

class Dire(core.fobj):
    suffix="node"
    tid=0
    @staticmethod
    def make_opt(arg:argparse.ArgumentParser):
        note=arg.add_argument_group("%s"%Dire.suffix)
        note.add_argument("-topath",dest='topath',default=None,help="Object entity storage location")

    @staticmethod
    def handle(args):
        obj,_=checkexists(args.name)
        if obj==None:
            pre,curname=getpre(args.name)
            pre[curname]=core.filetypes[args.type](name=curname)
        elif obj.suffix!=args.type:
            raise core.StoreError("%s already exists,and that its type is %s ,not %s"%(args.name,obj.suffix,args.type))
        elif args.topath!=None:
            obj.moveto(args.topath)
        elif args.path!=None:
            transfer(args.name,args.path)
            pass
        else:
            raise core.StoreError("%s already exists"%args.name)

    def __init__(self,*args,**kargs):
        self.attr:dict[str,core.fobj]={}
        if len(args)!=0 and type(args[0])==core.fileio:
            self.Parse(args[0])
            return
        if kargs.get('name')==None:
            core.StoreError("Build a File object need name attr",core.StoreError.init)
        super().__init__(None,name=kargs['name'])

    def remove(self,key=None):
        if key==None:
            keys=list(self.attr.keys())
            for key in keys:
                self.attr[key].remove()
                self.attr.pop(key)
        elif type(key)==str:
            if self.attr.get(key)!=None:
                self.attr[key].remove()
                self.attr.pop(key)
            else:
                raise core.StoreError("%s is not exist"%key,core.StoreError.missing)
        elif type(key)==list:
            if self.attr.get(key[0])!=None:
                if len(key)==1:
                    self.remove(key[0])
                elif len(key)==2:
                    self.attr[key[0]].remove(key[1])
                else:
                    self.attr[key[0]].remove(key[1:])
            else:
                raise core.StoreError("%s is not exist"%key[0],core.StoreError.missing)
        else:
            raise core.StoreError("The type of key needs to be str",core.StoreError.args)
    
    @staticmethod
    

    def moveto(self,topath):
        topath=os.path.realpath(topath)
        if os.path.exists(topath)==False:
            MakeDir(topath)
        
        for v in self.attr.values():
            v.moveto(topath)
            pass

    def ParseAttr(self,file:core.fileio):
        attrlen=file.ReadWord()
        i=0
        while i<attrlen:
            atype=file.ReadByte()
            if core.Storetypes.get(atype)==None:
                raise core.StoreError("Parse error",core.StoreError.init)
            aobj:core.fobj=core.Storetypes[atype](file)
            self.attr[aobj.name]=aobj
            i+=1

    def Parse(self,file:core.fileio):
        nlen=file.ReadByte()
        name=file.Read(nlen).decode("utf-8")
        super().__init__(None,name=name)
        self.ParseAttr(file)
        pass

    def SaveAttr(self,file:core.fileio):
        attrlen=len(self.attr)
        file.WriteWord(attrlen)
        for v in self.attr.values():
            v.Save(file)
        pass
    
    def Save(self,file:core.fileio):
        file.WriteByte(self.tid)
        wname=self.name.encode("utf-8")
        file.WriteByte(len(wname))
        file.Write(wname)
        self.SaveAttr(file)
        pass
    
    def __str__(self):
        return str(self.attr)

    def __repr__(self):
        return str(self)
    
    def get(self,key) -> core.fobj|None:
        return self.attr.get(key)

    def __getitem__(self,key) -> core.fobj|None:
        if type(key)==int:
            key=list(self.attr.keys())[key]
        res=self.attr.get(key)
        return res
    
    def checkExist(self,key) -> bool :
        res=self.attr.get(key)
        if res==None:
            return False
        return True

    def __setitem__(self,key,value):
        if type(key)!=str:
            raise ValueError("Value must be str")
        if type(value)==str:
            self.attr[key]=Dire(value)
        else:
            self.attr[key]=value

    def __len__(self):
        return len(self.attr)

    def __iter__(self):
        return Dire.iter(self)
    
    def pop(self,key):
        return self.attr.pop(key)


    @staticmethod
    def iter(objset):
        for i in objset.attr:
            yield i

core.Storetypes[Dire.tid]=Dire

