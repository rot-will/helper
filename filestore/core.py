
version=1.0
"""
目录中的目录使用json
目录中的文件整合为一段数据
如：
    {d1:{d2:[{d3:[f1,f2,f3]}],[f1,f3,f4]}}
    整合为
    {d1:[{d2:[{d3:fdata}]},fdata]}
"""
import struct
import enum
# from filestore.filesystem import checkexists,transfer,getpre # ,parse_object,save_object

class FileExec(Exception):
    EOF=-1
    Format=0
    Mode=1
    Open=2
    def __init__(self,*args,**kargs):
        super(FileExec,self).__init__()
        self.ErrorMessage=args[0]
        self.Errorid=args[1]
    pass

class fileio:
    def __init__(self,path,mode='r'):
        try:
            self.body=open(path,mode)
        except :
            raise FileExec("Open file error,Please check if the path is legal",FileExec.Open)
        self.mode=self.Makemode(mode)
        self.path=path


    def Makemode(self,mode):
        fmode=0
        for i in mode:
            if i == 'w':
                fmode|=1
            elif i=='b':
                fmode|=2
            elif i=='r':
                fmode|=4
        if fmode==2:
            fmode|=4
        return fmode
    
    def Write(self,data):
        if type(data)==str:
            if self.mode&3==1:
                return self.body.write(data)
            raise FileExec("Need to open in write mode",FileExec.Mode)
        elif type(data)==bytes:    
            if self.mode&3==3:
                return self.body.write(data)
            raise FileExec("Need to open in byte write mode",FileExec.Mode)
        else:
            raise FileExec("data Expected str/bytes type",FileExec.Format)
        
    def WriteByte(self,data:int):
        if self.mode&3==3:
            return self.body.write(data.to_bytes(1,'little'))
        raise FileExec("Need to open in byte write mode",FileExec.Mode)
    
    def WriteWord(self,data:int):
        if self.mode&3==3:
            return self.body.write(data.to_bytes(2,'little'))
        raise FileExec("Need to open in byte write mode",FileExec.Mode)
    
    def WriteInt(self,data:int):
        if self.mode&3==3:
            return self.body.write(data.to_bytes(4,'little'))
        raise FileExec("Need to open in byte write mode",FileExec.Mode)
    
    def WriteNumber(self,data:int):
        if self.mode&3!=3:
            raise FileExec("Need to open in byte write mode",FileExec.Mode)
        
        wdata=[]
        if (data==0):
            wdata=[0]
            pass
        while data!=0:
            if data>=0x80:
                wdata.append((data&0x7f)|0x80)
            else:
                wdata.append(data)
            data=data>>7
        return self.body.write(bytes(wdata))


    @staticmethod
    def CheckNull(data):
        if len(data)==0:
            raise FileExec("File read reached end",FileExec.EOF)

    def Read(self,len=-1):
        if len==-1:
            return self.body.read()
        return self.body.read(len)
        
    def ReadByte(self):
        if self.mode&6==6:
            cache:bytes=self.body.read(1)
            fileio.CheckNull(cache)
            return struct.unpack("<b",cache)[0]
        raise FileExec("Need to open in byte read mode",FileExec.Mode)
    
    def ReadWord(self):
        if self.mode&6==6:
            cache:bytes=self.body.read(2)
            fileio.CheckNull(cache)
            if len(cache)!=2:
                self.body.seek(-1,1)
                raise FileExec("Insufficient remaining file length",FileExec.Format)
            return struct.unpack("<h",cache)[0]
        raise FileExec("Need to open in byte read mode",FileExec.Mode)
    def ReadInt(self):
        if self.mode&6==6:
            cache:bytes=self.body.read(4)
            fileio.CheckNull(cache)
            if len(cache)!=4:
                self.body.seek(-len(cache),1)
                raise FileExec("Insufficient remaining file length",FileExec.Format)
            return struct.unpack("<i",cache)[0]
        raise FileExec("Need to open in byte read mode",FileExec.Mode)
    
    def ReadNumber(self):
        if self.mode&6!=6:
            raise FileExec("Need to open in byte read mode",FileExec.Mode)
        value=0
        readnum=0
        while True:
            cache=self.body.read(1)
            if len(cache)==0:
                self.body.seek(-readnum,1)
                raise FileExec("Insufficient remaining file length",FileExec.Format)
            readnum+=1
            number=cache[0]
            value+=number&0x7f
            if number&0x80!=0:
                value=value<<7
            else:
                break

        return value
        
    

    
    def ReadUntil(self,data,drop=False):
        if self.mode&2==0:
            raise FileExec("Need to open in byte read mode",FileExec.Mode)
        if type(data)==str:
            data=data.encode('utf-8')
        res=b''
        ind=0
        end=len(data)
        while ind<end:
            cache=self.body.read(1)
            if len(cache)==0:
                self.body.seek(-len(res)-1,1)
                raise FileExec("Not Found data",FileExec.Format)
            if cache==data[ind:ind+1]:
                res+=cache
                ind+=1
            elif ind!=0:
                ind=0
        if drop==True:
            res=res[:-len(data)]
        return res

    def flush(self):
        self.body.flush()
        
    def close(self):
        self.body.close()

class StoreError(Exception):
    VarType=1
    Exist=2
    init=3
    missing=4
    def __init__(self,*args,**kargs):
        super(StoreError,self).__init__()
        self.ErrorMessage=args[0]
        self.Errorid=args[1]

class attrType:
    str=0
    branch=1
    list=2
    @staticmethod
    def parse_branch(branch):
        value=0
        bit=0
        for i in branch:
            value|=ord(i)<<bit
            bit+=8
        return value

    @staticmethod
    def parse(attr_type,attr_data):
        if attr_type==attrType.str:
            result=attr_data
        elif attr_type==attrType.branch:
            result=attrType.parse_branch(attr_data)
        elif attr_type==attrType.list:
            if attr_data=='':
                value=[]
            else:
                value=attr_data.split('\n')
            result=value
        return result

    @staticmethod
    def save_branch(branch):
        value=""
        while branch!=0:
            value=chr(branch&0xff)+value
            branch=branch>>8
        return value
    
    @staticmethod
    def save(attr_type,attr_data):
        result=""
        if attr_type==attrType.str:
            result=attr_data
        elif attr_type==attrType.branch:
            result=attrType.save_branch(attr_data)
        elif attr_type==attrType.list:
            result='\n'.join(attr_data)
        return result

class attrInfo:
    def __init__(self,name,type,arg,desc):
        self.name=name
        self.type=type
        self.arg=arg
        self.desc=desc

class Enum(enum.Enum):
    pass

class fCore(object):
    suffix=None
    tid=None
    
    @classmethod
    def handle(cls,args):
        pass

    @classmethod
    def make_opt(cls,arg):
        pass

    
    def __init__(self,*args,**kargs):
        self.name:str=kargs.get('name')
        pass

    """
        用于删除对象
    """
    def remove(self,key=None):
        pass

    """
        用于导出属性
    """
    def export_attr(self,attrid,attrdata):
        pass

    """
        用于导出对象
    """
    def export(self,file:fileio,path:str):
        pass
    
    """
        获取属性信息
    """
    def getAttr(self):
        pass
    
    def __str__(self):
        pass

    def __repr__(self):
        pass

class dobj(fCore):
    suffix=None
    tid=None
    @classmethod
    def make_opt(cls,arg):
        # note=arg.add_argument_group("%s"%cls.suffix)
        pass

    @classmethod
    def handle(cls, args):
        return super().handle(args)
        
    def __init__(self,*args,**kargs):
        self.attr:dict[str,fCore]={}
        if kargs.get('name')==None:
            StoreError("Build a File object need name attr",StoreError.init)
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
                raise StoreError("%s is not exist"%key,StoreError.missing)
        elif type(key)==list:
            if self.attr.get(key[0])!=None:
                if len(key)==1:
                    self.remove(key[0])
                elif len(key)==2:
                    self.attr[key[0]].remove(key[1])
                else:
                    self.attr[key[0]].remove(key[1:])
            else:
                raise StoreError("%s is not exist"%key[0],StoreError.missing)
        else:
            raise StoreError("The type of key needs to be str",StoreError.args)
        
    def export(self,file:fileio,path:str):
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
    
    def __setitem__(self,key,value):
        if type(key)!=str:
            raise ValueError("Value must be str")
        if type(value)==str:
            self.attr[key]=self.__class__(value)
        else:
            self.attr[key]=value

    def __len__(self):
        return len(self.attr)
    
    def __iter__(self):
        return self.iter(self)
    
    @staticmethod
    def iter(objset):
        for objname in objset.attr:
            yield objname
    def pop(self,key):
        return self.attr.pop(key)
    
    def get(self,key) -> fCore|None:
        return self.attr.get(key)

    def __getitem__(self,key) -> fCore|None:
        if type(key)==int:
            key=list(self.attr.keys())[key]
        res=self.attr.get(key)
        return res
    
    def checkExist(self,key) -> bool :
        res=self.attr.get(key)
        if res==None:
            return False
        return True

class fobj(fCore):
    suffix=None
    is_physical=False
    is_join_suff=False
    tid=None
    
    class Attr(Enum):
        none=0

    Needattr={Attr.none}

    Attr_info={
        Attr.none.value:attrInfo("none",attrType.str,"-none","None")
    }

    Out_need_attr={}
    

    def checkNeedful(self):
        for i in self.Needattr:
            if self.Attr_info[i].type!=attrType.branch and bool(self.attr.get(i))==False:
                errmessage="Some necessary attr were not initialized:"
                for i in self.Needattr:
                    errmessage+=self.Attr_info[i].name+','
                errmessage=errmessage.rstrip(',')
                raise StoreError(errmessage,StoreError.init)

    @staticmethod 
    def checkname(name):
        legal_char='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-'
        for i in name:
            if i not in legal_char:
                return False
        return True
    
    @classmethod
    def handle(cls,args):
        from filestore.filesystem import checkexists,transfer,getpre
        if cls.checkname(args.name)==False:
            raise StoreError("%s is illegal"%args.name,StoreError.args)
        if args.path==None:
            path='/'
        else:
            path=args.path
        obj,oripath=checkexists(args.name,path)
        resarg={}
        objtype=filetypes[args.type]
        for id in objtype.Attr_info:
            resval=getattr(args,objtype.Attr_info[id].name)
            if objtype.Attr_info[id].type==attrType.str:
                if resval==None:
                    resval=""
                else:
                    resval=resval.replace('"','^"')
                
            elif objtype.Attr_info[id].type==attrType.list:
                nresval=[]
                if resval==None or len(resval)==0:
                    nresval=['']
                else:
                    for o in resval:
                        value=o#.replace('"','""')
                        if value!='':
                            nresval.append(value)
                
                resval=nresval
            elif objtype.Attr_info[id].type==attrType.branch:
                if resval==None:
                    resval=1
                resval=int(resval)
            resarg[objtype.Attr_info[id].name]=resval

        if obj==None:
            pre,curname=getpre(path+'/'+args.name)
            obj=objtype(name=curname,**resarg)
            pre[curname]=obj
        elif obj.suffix != args.type:
            raise StoreError("%s already exists,and that its type is %s ,not %s"%(args.name,obj.suffix,args.type))
        else:
            if args.path!=None and oripath != path :
                # print("123")
                tarname,obj=transfer(oripath+'/'+args.name,path)
            else:
                for i in obj.Attr_info:
                    if obj.Attr_info[i].type==attrType.branch or getattr(args,obj.Attr_info[i].name)!=None:
                        obj.attr[i]=resarg.get(obj.Attr_info[i].name)
                
            obj.Make()

    @classmethod
    def make_sub_opt(cls,grp,attrid,**kargs):
        if cls.Attr_info[attrid].type==attrType.str:
            kargs['default']=None
        elif cls.Attr_info[attrid].type==attrType.branch:
            kargs['nargs']='?'
            kargs['default']=0
        elif cls.Attr_info[attrid].type==attrType.list:
            kargs['nargs']='+'
            kargs['default']=None
        grp.add_argument(cls.Attr_info[attrid].arg,\
                         dest=cls.Attr_info[attrid].name,\
                         help=cls.Attr_info[attrid].desc,\
                         **kargs)
        pass

    @classmethod
    def make_opt(cls,arg):
        grp=arg.add_argument_group("%s obj"%cls.suffix)
        for id in cls.Attr_info:
            cls.make_sub_opt(grp, id,)

    def __init__(self,*args,**kargs):
        self.attr={}
        if kargs.get('name')==None:
            raise StoreError("Build a File object need path,name attr",StoreError.init)
        super().__init__(name=kargs['name'])
        if len(kargs)==1:
            return
        for i in self.Attr_info:
            if kargs.get(self.Attr_info[i].name)!=None:
                self.attr[i]=kargs[self.Attr_info[i].name]
        self.checkNeedful()
        self.Make()

    """
        创建后的实际操作
    """
    def Make():

        pass
    """
        用于删除对象
    """
    def remove(self,key=None):
        if bool(key):
            raise StoreError("%s is File,not Dire"%self.name,StoreError.missing)

    """
        用于导出属性
    """
    def export_attr(self,attrid,attrdata):
        if self.Attr_info[attrid].type==attrType.str:
            attr_cache=attrdata.replace('"','""')
            attrvalue=f'"{attr_cache}"'
        elif self.Attr_info[attrid].type==attrType.list:
            if attrdata==[]:
                return " "
            else:
                attrvalue=""
                for i in attrdata:
                    attr_cache=i.replace('"','""')
                    attrvalue+=f'"{attr_cache}" '
        elif self.Attr_info[attrid].type==attrType.branch:
            attrvalue=attrdata
        return f" {self.Attr_info[attrid].arg} {attrvalue}"

    """
        用于导出对象
    """
    def export(self,file:fileio,path:str):
        title=f"helper -n {self.name} -p {path} -t {self.suffix}"
        for i in self.attr:
            title+=self.export_attr(i,self.attr[i])

        file.Write(title+'\n')
        pass
    
    """
        获取属性信息
    """
    def getAttr(self):
        result={}
        for i in self.attr:
            result[self.Attr_info[i].name]=(self.Attr_info[i].type,self.attr[i])
        return result
    
    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return str(self)

    pass



Storetypes:dict[int,type[fobj]]={}
filetypes:dict={}


