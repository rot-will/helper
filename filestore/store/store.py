import filestore.core as core
from filestore.filesystem import checkexists,transfer,getpre,save_name,parse_name
import argparse


class Dire(core.fobj):
    suffix="node"
    tid=0
    Attr_info={
    }
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
            path=f"{args.path}/{args.name}"
        obj,_=checkexists(path)
        
        if obj==None and bool(args.is_rename)==False:
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
        for objname in objset.attr:
            yield objname

FILETYPES=[Dire]