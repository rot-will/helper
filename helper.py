import filestore.filesystem
import argparse
import core.config as config
import display 
import core.init as init

def make_type_help(types:dict):
    default=config.cfg.deftype
    help_d="Object type (default:%s"%default
    help_d+=' optional:'
    for i in types:
        help_d+=i+' '
    help_d=help_d.strip()+')'
    return help_d

def make_opt(arg:argparse.ArgumentParser):
    arg.add_argument("-h","--help",dest="help",default=False,action="store_true",help="Show this help message and exit")
    arg.add_argument("-n",dest="name",type=str,help="Specify the name of object/node")
    arg.add_argument("-t",dest="type",type=str,default=None,help=make_type_help(filestore.filesystem.core.filetypes))
    arg.add_argument("-p",dest="path",type=str,default=None,help="The location of the object/node")
    arg.add_argument("-d",'-del',dest="delete",type=str,default=None,help="Delete object/note (/???/???/???)")
    arg.add_argument("-clear",dest="clear",default=False,action="store_true",help="clear error objs")
    arg.add_argument("-remake",dest="remake",default=False,action="store_true",help="remake objs and clear error objs")
    arg.add_argument("-dis",dest='display',type=str,default='con',help="Select display mode (default: con  optional: con/win)")
    arg.add_argument("-export",dest="export",nargs=2,default=False,help="Export all objs in command form  (export_to_file,node_name)")

def print_help(args,arg:argparse.ArgumentParser):
    if args.type!=None:
        objtype=filestore.filesystem.core.filetypes[args.type]
        objtype.make_opt(arg)
        args=arg.parse_args()
    else:
        display.make_opt(arg)
    arg.print_help()
    pass

def main():
    init.init()
    arg=argparse.ArgumentParser(allow_abbrev=True,add_help=False)

    make_opt(arg)
    args=arg.parse_known_args()[0]
    if args.help==True:
        print_help(args,arg)
    elif args.clear==True:
        filestore.filesystem.clear_error()
    elif args.remake==True:
        filestore.filesystem.remake()
    elif args.export!=False:
        filestore.filesystem.export(args.export[0],args.export[1])
    elif bool(args.name):
        if bool(args.type)==False:
            type=config.cfg.deftype
        else:
            type=args.type
        objtype=filestore.filesystem.core.filetypes[type]
        objtype.make_opt(arg)
        args=arg.parse_args()
        args.type=type
        filestore.filesystem.make_filesystem(args,objtype)
    elif args.path!=None:
        filestore.filesystem.moveto(args.path)
    elif args.delete!=None:
        filestore.filesystem.remove(args.delete)
    else:
        display.make_opt(arg)
        args=arg.parse_args()
        display.show(args)
    pass

if __name__=='__main__':   
    main()