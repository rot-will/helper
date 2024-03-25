from winhelper.env import *
from winhelper.func import *

import sys,msvcrt
import colorama

file_color=colorama.Fore.LIGHTBLUE_EX
dire_color=colorama.Fore.LIGHTGREEN_EX
ind_color=colorama.Fore.LIGHTYELLOW_EX
back_color=colorama.Fore.RESET
wait=['< -- wait -- >\r','              \r']

class Outline:
    def __init__(self,threshold_r,span=5):
        self.line=0
        self.threshold=threshold_r
        if span<1:
            self.span=5
        else:
            self.span=span
    
    def limit(self):
        if self.threshold==-1:
            return
        sys.stdout.flush()
        uchar=''
        if self.line>=self.threshold:
            sys.stdout.write(wait[0])
            uchar=msvcrt.getch()
            sys.stdout.write(wait[1])
            if uchar == b' ':
                self.line=1
                self.threshold=self.span
            elif uchar in [b'e',b'q',b'\x03',b'\x1a']:
                raise KeyError()
            else:
                self.line=1
                self.threshold=1
        else:
            self.line+=1

    def print(self,outdata):
        try:
            self.limit()
            print(outdata)
        except:
            return -1

def showdict(dir_dict,search_str="",is_show_file=True,is_dire=False,dire_in=False,hide=True,Depth=0,Only_file=False,objlist=[]):
    #n=0
    dir_list=[]
    for i in dir_dict:
        if dir_dict[i]==1:
            if is_show_file:
                if ((is_dire == False) and (search_str in i)) or ((dire_in+is_dire)==2):
                    objlist.append((i[:-4],Depth*2,-1))
        else:
            dir_list.append(i)

    for i in dir_list:
        if ('hide' in i and hide) or ('real_hide' in i):
            continue
        tdire_in=dire_in
        tobjlist=[]
        if is_dire :
            if search_str in i:
                tdire_in=True
        showdict(dir_dict[i],search_str=search_str,is_show_file=is_show_file,\
                 is_dire=is_dire,dire_in=tdire_in,hide=hide,Depth=Depth+1,\
                    Only_file=Only_file,objlist=tobjlist)
        if search_str and len(tobjlist) == 0:
            continue
        if Only_file==False:
            objlist.append((i,Depth*2,Depth))
        objlist+=tobjlist
    return objlist



def out_command(coms,rows=20,cols=8,span=8):
    out=Outline(rows,span)
    tcols=0
    for name,pad,nType in coms:
        if nType!=-1:
            if tcols!=0:
                if out.print(outdata)==-1:
                    return 0
                tcols=0
            if nType>0:
                outdata=f"{' '*pad}*- {dire_color}\\{'-'*nType}{name}{'-'*nType}/{back_color}"
            else:
                outdata=f"{' '*pad}*- {dire_color}{name}{back_color}"
        else:
            if tcols==0:
                outdata=f"{' '*pad}+-- {file_color}{name}{back_color}"
                tcols=cols-1
            else:
                outdata=f"{outdata} / {file_color}{name}{back_color}"
                tcols-=1
        if tcols==0:
            if out.print(outdata)==-1:
                return 0
            outdata=""
    if tcols!=0:
        out.print(outdata)
def out_des_com(comm_list,cmd_width,des_width,rows=20,span=8):
    print("command:")
    out=Outline(rows,span)
    for i in comm_list:
        cmd=i[0].encode("gbk").ljust(cmd_width,b' ').decode('gbk')
        des=i[2].encode("gbk").ljust(des_width,b' ').decode('gbk')
        outdata="   %s : %s : %s"%(cmd,des,i[1])
        if out.print(outdata)==-1:
            return 0


def out_all_com(comm_list,rows=5,span=8):
    title=["Name",
           "Content of Execution",
           "Description",
           "Pre-executed command",
           "Actual execution directory",
           "Window program"]
    
    out=Outline(rows,span)
    for i in comm_list:
        outdata=""
        pad=""
        align=4
        for j,v in enumerate(i):
            if type(v)!=bool and not v:
                continue
            if j==3:
                data=v.splitlines()
                outdata+='%s%s : %s\r\n'%(pad,title[j].ljust(align,' '),data[0])
                for k in data[1:]:
                    outdata+="%s%s   %s\r\n"%(pad,' '.ljust(align,' '),k)
                
            else:
                outdata+="%s%s : %s\r\n"%(pad,title[j].ljust(align,' '),v)
            pad='  '
            align=26
        if out.print(outdata)==-1:
            return 0
        pass

def OutCommands(filelist,coms,com_s,isall,rows=20,span=8):
    out_comm_list=[]
    cmd_width=0
    des_width=0
    for i in coms:
        name=i[0]
        if filelist[name].hide:
            continue
        if com_s=='*' or com_s in name :
            cache=(get_OutCommand(filelist,name))
            if len(cache[0])>cmd_width:
                cmd_width=len(cache[0])
            if len(cache[2])>des_width:
                des_width=len(cache[2])
            out_comm_list.append(cache)
    if isall:
        out_all_com(out_comm_list,rows,span)
    else:
        out_des_com(out_comm_list,cmd_width,des_width,rows,span)
    
def get_OutCommand(filelist,com_n):
    comm_path=filelist[com_n]
    cmd,des,precom,is_start,real_dir=get_cmd_info(comm_path)
    return [com_n,cmd,des,precom,real_dir,is_start]