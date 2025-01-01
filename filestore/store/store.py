import filestore.core as core
from filestore.filesystem import checkexists,transfer,getpre,save_name,parse_name
import argparse


class Dire(core.dobj):
    suffix="node"
    tid=-1
    
    @classmethod
    def make_opt(cls,arg:argparse.ArgumentParser):
        note=arg.add_argument_group("%s"%cls.suffix)
        note.add_argument("-rename",dest="is_rename",action="store_true",default=False,help="rename current node")

    @classmethod
    def handle(cls,args):
        from filestore.filesystem import checkexists,transfer,getpre
        if args.is_rename==False:
            path=(args.path+'/'+args.name).strip('/')
        else:
            path=f"{args.path}/{args.name}"
        obj,_=checkexists(path)
        
        if obj==None and bool(args.is_rename)==False:
            pre,curname=getpre(path)
            pre[curname]=core.filetypes[args.type](name=curname)
        elif obj.suffix!=args.type:
            raise core.StoreError("%s already exists,and that its type is %s ,not %s"%(args.name,obj.suffix,args.type),core.StoreError.Exist)
        elif args.path!=None and args.is_rename==True:
            transfer(args.name,args.path)
            pass
        else:
            raise core.StoreError("%s already exists"%args.name,core.StoreError.Exist)


FILETYPES=[Dire]