var_name=r"tools"
root_path=r"B:\tools"

from winhelper.edit import *
from winhelper.func import *
from winhelper.env import *
from winhelper.out import *

import argparse
import colorama

colorama.init(autoreset=True)

ddict={}
tools_env=[root_path]
filelist={}

def help(parse : argparse.ArgumentParser):
    """ show """
    parse.add_argument('-c','--create',dest='is_creat',action='store_true', default=False,help="Construct system variables default:False")
    parse.add_argument('-help',dest='show_type',action='store_true', default=False,help="view type default:False")
    parse.add_argument('-hide',dest='is_hide',action='store_false', default=True,help="Show hide commands default:True")
    parse.add_argument('-out',dest='out_command',help="View the contents of the command")
    parse.add_argument('-oall',dest='out_comm_info',action='store_true',default=False,help="View the all contents of the command")
    parse.add_argument('-noc',dest='num_col',type=int,default=8,help="Number of columns")
    parse.add_argument('-win',dest="Is_Win",action='store_true',default=False,help="Using the Window Interface") # 还没实现

    """ search """
    parse.add_argument('-s','--search',dest='search_str',default='',help="Search specified string")
    parse.add_argument('-dire',dest='is_dire',action='store_true',default=False,help='Search specified type')
    
    """ command_data """
    parse.add_argument('-d','--direct',dest='direct',default='',help='Specify command')
    parse.add_argument('-r','--represent',dest='represent',default='',help="command note")
    parse.add_argument('-precom',dest='precom',help='Pre-executed commands to set the environment')
    parse.add_argument('-tardir',dest='target_dir',help="Specify target program directory")
    parse.add_argument('-start',dest='is_start',action='store_false', default=True,help="Do you want to use start to launch exe")
    
    """ command """
    parse.add_argument('-n','--name',dest='name',default='',help='Specify script name')
    parse.add_argument('-replace',dest='is_re',action='store_true',default=False,help="Replace the original command default:False")
    
    """ type """
    parse.add_argument('-t','--type',dest='type',default='',help='Type of command xx/xxx/xxxx')
    parse.add_argument('-redir',dest='redir',default='',help="Change type position")
    
    """ create type """
    parse.add_argument('-add',dest='add_dire',help='Added type')
    
    """ delete type/command """
    parse.add_argument('-del',dest='del_dire',help='Delete command or type')
    

def main():
    parse=argparse.ArgumentParser('help')
    help(parse)
    args=parse.parse_args()
    getdirlist(root_path,ddict,filelist,tools_env,var_name,is_creat=args.is_creat,is_hide=args.is_hide)
    if args.is_creat:
        setenv(root_path,ddict,filelist,tools_env,var_name)
    if args.show_type:
        parse.print_help()
        print("\n--------------- view Type ---------------\n")
        print(showdict(ddict,'',is_show_file=False)[1])
        exit(0)
    elif args.del_dire:
        delete(root_path,ddict,filelist,tools_env,var_name,args.del_dire)
    elif args.add_dire:
        create(root_path,ddict,filelist,tools_env,var_name,args.add_dire)
    elif args.redir:
        create(root_path,ddict,filelist,tools_env,var_name,args.name,args.redir)
    elif args.name:
        if (not (args.direct or args.type or args.is_re)):
            exit("When name exists, direct is required")
        addbat(root_path,ddict,filelist,tools_env,var_name,args.name,args.direct,args.type,args.precom,args.target_dir,args.represent,args.is_start,args.is_re)
    elif args.out_command:
        coms=showdict(root_path,ddict,filelist,tools_env,var_name,'',args.search_str,is_dire=True,hide=args.is_hide,num_col=args.num_col,Only_Name=True)[1]
        print(coms)
        OutCommands(root_path,ddict,filelist,tools_env,var_name,coms,args.out_command,args.out_comm_info)
    else:
        coms=showdict(root_path,ddict,filelist,tools_env,var_name,'',args.search_str,is_dire=args.is_dire,hide=args.is_hide,num_col=args.num_col)[1]
        out_command(coms.strip())

if __name__=='__main__':
    main()

