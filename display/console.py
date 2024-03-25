import core.config as config
import filestore.filesystem
from filestore.filesystem import search,get_objs,clear_empty,get_attr,get_need_attr,get_maxpad

pad='\t'
padnum=1
attrpad='\t'
attrpadnum=1
def checkConfig():
    defcfg={'pad': {'chr': (config.CfgObj.int,32), 'num': (config.CfgObj.int,2)}, 
                'attrpad': {'chr': (config.CfgObj.int,32), 'num': (config.CfgObj.int,4)}}
    config.checkConfig('console',defcfg)

    pass

def init():
    global pad,padnum,attrpad,attrpadnum
    checkConfig()

    pad=chr(config.cfg.console.pad.chr)
    padnum=config.cfg.console.pad.num
    attrpad=chr(config.cfg.console.attrpad.chr)
    attrpadnum=config.cfg.console.attrpad.num

def make_opt(arg):
    console=arg.add_argument_group("Console")
    console.add_argument("-row",dest="rownum",type=int,default=6,help="Number of objects displayed in a row")

    """
        树形搜索
    """
    console.add_argument("-s",dest="search",type=str,default=None,help="Search for objects that protect the specified string")
    console.add_argument("-sd",dest="search_note",type=str,default=None,help="Search for note that protect the specified string")

    """
        显示object属性的方式
    """
    console.add_argument("-out",dest="out_obj",action="store_true",default=False,help="Show only the required attributes")
    console.add_argument("-all",dest="out_all",action="store_true",default=False,help="Show All Attributes")

def outformat(objs,depth,isnote):
    if isnote==True:
        data=pad*padnum*depth+'+- %s'%objs
    else:
        data=pad*padnum*(depth+1)+'--: '+' / '.join(objs)
        
    print(data)
    pass

def tree(notes,rownum):
    i=0
    stack=[]
    curr=notes
    currsubnote=0
    outformat(curr.name,len(stack),True)
    while True:
        i=0
        subnotes=[]
        objs=[]
        while i<len(curr):
            if curr[i].tid==0:
                subnotes.append(curr[i])
            else:
                objs.append(curr[i].name)
                if len(objs)>=rownum:
                    outformat(objs,len(stack),False)
                    objs=[]

            i+=1
        if len(objs)>0:
            outformat(objs,len(stack),False)
        if len(subnotes)==0 and len(stack)!=0:
            curr,subnotes,currsubnote=stack.pop()
        if currsubnote < len(subnotes):
            stack.append((curr,subnotes,currsubnote+1))
        else:
            while len(stack)>0 and currsubnote >= len(subnotes):
                curr,subnotes,currsubnote=stack.pop()
            if currsubnote< len(subnotes):
                stack.append((curr,subnotes,currsubnote+1))
        if currsubnote>=len(subnotes):
            break
        outformat(subnotes[currsubnote].name,len(stack),True)
            
        curr=subnotes[currsubnote]
        currsubnote=0

def getmax_keylen(attrs):
    keylen=0
    for i in attrs:
        if len(i) > keylen:
            keylen=len(i)
    return keylen

def outmulattr(attrs):
    keylen=getmax_keylen(attrs)
    for i in attrs:
        if bool(attrs[i])==False:
            continue
        print(attrpad*attrpadnum+"%s:%s"%(i.ljust(keylen,' '),attrs[i]))
    pass

def outattr(name:str,attrs:dict,pad_=0):
    if len(attrs)==1:
        value=list(attrs.values())[0]
        if bool(value)==False:
            value="<empty>"
        print("%s: %s"%(name.ljust(pad_,' '),value))
    else:
        print("%s: "%name)
        outmulattr(attrs)
    pass

def req_attr(objs):
    pad_=get_maxpad(objs)
    for i in objs:
        outattr(i.name,get_need_attr(i),pad_)

def all_attr(objs):
    for i in objs:
        outattr(i.name,get_attr(i))
    pass

def show(args):
    curr_notes=search(filestore.filesystem.fileroot,args.search)
    if args.search_note!=None:
        curr_notes=search(curr_notes,args.search_note,True)
    if args.search_note!=None or args.search!=None:
        curr_notes=clear_empty(curr_notes)
    if args.out_obj!=False:
        objs=get_objs(curr_notes)
        req_attr(objs)
    elif args.out_all!=False:
        objs=get_objs(curr_notes)
        all_attr(objs)
    else:
        tree(curr_notes,args.rownum)