
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

class fobj(object):
    suffix=None
    
    @staticmethod
    def make_opt(arg):
        pass
    
    @staticmethod
    def handle(args):
        pass

    
    def __init__(self,*arg,**kargs):
        self.name:str=kargs.get('name')
        pass

    def moveto(self,topath):
        pass

    def remove(self,key=None):
        pass


    def Parse(self,file:fileio):
        pass
    

    def Save(self,file:fileio):
        pass

    def export(self,file:fileio,path:str):
        pass
    
    def getAttr(self):
        return None


Storetypes:dict[int,type[fobj]]={}
filetypes:dict={}


