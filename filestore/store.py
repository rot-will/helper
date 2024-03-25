import filestore.core as core
import os,zlib
from filestore.method import checkexists,transfer,getpre,MakeDir
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

    class Type:
        str=0
        branch=1
        list=2
    
    Id_Attr={Attr.commid:"command",
            Attr.runmid:"runmode",
            Attr.preid:"preboot",
            Attr.runpid:"runpath",
            Attr.icoid:"icopath",
            Attr.descid:"descript"}
    Needattr=[Attr.commid,Attr.runmid]
    

    Attr_types={Attr.commid:Type.str,
            Attr.runmid:Type.branch,
            Attr.preid:Type.list,
            Attr.runpid:Type.str,
            Attr.icoid:Type.str,
            Attr.descid:Type.str}
    
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
            if self.Attr_types[i]!=self.Type.branch and bool(self.attr.get(i))==False:
                errmessage="Some necessary attr were not initialized:"
                for i in self.Needattr:
                    errmessage+=self.Id_Attr[i]+','
                errmessage=errmessage.rstrip(',')
                raise core.StoreError(errmessage,core.StoreError.init)

    @staticmethod
    def make_sub_opt(grp,class_,attrid,**kargs):
        if class_.Attr_types[attrid]==class_.Type.str:
            kargs['default']=None
        elif class_.Attr_types[attrid]==class_.Type.branch:
            kargs['nargs']='?'
            kargs['default']=0
        elif class_.Attr_types[attrid]==class_.Type.list:
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
            if objtype.Attr_types[i]==objtype.Type.str:
                if resval==None:
                    resval=""
                else:
                    resval=resval.replace("'",'"')
                
            elif objtype.Attr_types[i]==objtype.Type.list:
                nresval=[]
                if resval==None or len(resval)==0:
                    nresval=['']
                else:
                    for o in resval:
                        value=o.replace("'",'"')
                        if value!='':
                            nresval.append(value)
                
                resval=nresval
            elif objtype.Attr_types[i]==objtype.Type.branch:
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
                    if obj.Attr_types[i]==obj.Type.branch or getattr(args,obj.Id_Attr[i])!=None:
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
        if len(kargs)==2:
            return
        for i in self.Id_Attr:
            if kargs.get(self.Id_Attr[i])!=None:
                self.attr[i]=kargs[self.Id_Attr[i]]
        self.checkNeedful()
        self.Make()

    def checkExist(self,level=1):
        if  os.path.exists(os.path.join(Cfg.cfg.defpath,self.name+'.'+self.suffix))==False:
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
set {self.Id_Attr[self.Attr.commid]}={self.attr[self.Attr.commid]}
set {self.Id_Attr[self.Attr.runmid]}={wmode}
"""
        file.write(wdata)
        return get_arg

    def Make(self):
        if self.is_join_suff:
            realpath=os.path.join(Cfg.cfg.defpath,self.name+'.'+self.suffix)
        else:
            realpath=os.path.join(Cfg.cfg.defpath,self.name)
        batf=open(realpath,'w')
        title="""@echo off
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
if not "%{self.Id_Attr[self.Attr.runpid]}%"=="" (cd /d %currpwd%)"""
        batf.write(bann)
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
            realpath=os.path.join(Cfg.cfg.defpath,self.name+'.'+File.suffix)
        else:
            realpath=os.path.join(Cfg.cfg.defpath,self.name)
        os.remove(realpath)
        return

    """
        解析备份文件,获取File对象
    """

    def parse_attr_branch(self,branch):
        value=0
        bit=0
        for i in branch:
            value|=ord(i)<<bit
            bit+=8
        return value

    def parse_attr_t(self,attrid,attrdata):
        attrtype=self.Attr_types[attrid]
        if attrtype==self.Type.str:
            self.attr[attrid]=attrdata
        elif attrtype==self.Type.branch:
            self.attr[attrid]=self.parse_attr_branch(attrdata)
        elif attrtype==self.Type.list:
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
        super().__init__(name=name)
        self.Parseattr(file)

    """
        Save
        保存命令列表文件
    """

    def save_attr_branch(self,attrdata):
        value=""
        while attrdata!=0:
            value=chr(attrdata&0xff)+value
            attrdata=attrdata>>8
        return value
        
    def save_attr_t(self,attrid,attrdata)->str:
        if self.Attr_types[attrid]==self.Type.str:
            return attrdata
        elif self.Attr_types[attrid]==self.Type.branch:
            return self.save_attr_branch(attrdata)
        elif self.Attr_types[attrid]==self.Type.list:
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
        self.Saveattr(file)
    
    def export_attr(self,attrid,attrdata):
        if self.Attr_types[attrid]==self.Type.str:
            attr_cache=attrdata.replace('"',"'")
            attrvalue=f'"{attr_cache}"'
        elif self.Attr_types[attrid]==self.Type.list:
            if attrdata==[]:
                return " "
            else:
                attrvalue=""
                for i in attrdata:
                    attr_cache=i.replace('"',"'")
                    attrvalue+=f'"{attr_cache}" '
        elif self.Attr_types[attrid]==self.Type.banch:
            attrvalue=attrdata
        return f" {self.Attr_Arg[attrid]} {attrvalue}"

    def export(self,file:core.fileio,path:str):
        title=f"helper -n {self.name} -p {path} -t {self.suffix}"
        for i in self.attr:
            title+=self.export_attr(i,self.attr[i])

        file.Write(title+'\n')
        pass

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
        note.add_argument("-rename",dest="is_rename",action="store_true",default=False,help="rename current node")
        # note.add_argument("-topath",dest='topath',default=None,help="Object entity storage location")

    @staticmethod
    def handle(args):
        if args.is_rename==False:
            path=(args.path+'/'+args.name).strip('/')
        else:
            path=args.name
        obj,_=checkexists(path)
        if obj==None and args.is_rename==False:
            pre,curname=getpre(path)
            pre[curname]=core.filetypes[args.type](name=curname)
        elif obj.suffix!=args.type:
            raise core.StoreError("%s already exists,and that its type is %s ,not %s"%(args.name,obj.suffix,args.type))
        elif args.path!=None and args.is_rename==True:
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
        super().__init__(name=kargs['name'])

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
    
    def export(self,file:core.fileio,path:str):
        if self.name!='/':
            file.Write(f"helper -n {self.name} -p {path} -t {self.suffix}\n")
            name=self.name
        else:
            path=""
            name=""
        if path=='/':
            path=''
        for obj in self.attr.values():
            obj.export(file,path+'/'+name)

        file.flush()

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

