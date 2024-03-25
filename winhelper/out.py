from winhelper.env import *
from winhelper.func import *

import sys,msvcrt
import colorama

file_color=colorama.Fore.LIGHTBLUE_EX
dire_color=colorama.Fore.LIGHTGREEN_EX
ind_color=colorama.Fore.LIGHTYELLOW_EX
back_color=colorama.Fore.RESET
wait=['< -- wait -- >\r','              \r']

def showdict(dir_dict,pad="",search_str="",is_show_file=True,is_dire=False,dire_in=-1,hide=True,num_col=0,Only_Name=False,Depth=0):
    n=0
    cache=''
    if Only_Name:
        if is_show_file:
            file_cache=[]
            dire_cache=[]
        else:
            file_cache={}
            dire_cache={}
    else:
        file_cache=""
        dire_cache=""
    file_num=0
    dire_for='\n{}'+"*- "+dire_color+'\\'*(Depth!=0)+'-'*(Depth-1)+'{}'+'-'*(Depth-1)+'/'*(Depth!=0)+back_color
    file_for='{}{}{} / '
    for i in dir_dict:
        if dir_dict[i]==1:
            if is_show_file and ((dire_in + is_dire)==-1 or (dire_in+is_dire)==2):
                i=i[:i.rfind('.')]
                if search_str and is_dire==False:
                    if search_str not in i:
                        continue
                if Only_Name==False and file_num>=num_col:
                    file_num=0
                    file_cache=file_cache[:-3]+'\n'+pad+" \\-  "
                file_num+=1
                if Only_Name:
                    file_cache.append(i)
                else:
                    file_cache+=file_for.format(file_color,i,back_color)
                n=n+1
        else:
            if ('hide' in i and hide) or ('real_hide' in i):
                continue
            n_1=0
            cache_1=''
            if is_dire:
                n_1,cache_1=showdict(dir_dict[i],pad+'  ',search_str,is_show_file,is_dire,(search_str in i or (dire_in==1)),hide,num_col,Only_Name,Depth+1)
            else:
                n_1,cache_1=showdict(dir_dict[i],pad+'  ',search_str,is_show_file,is_dire,-1,hide,num_col,Only_Name,Depth+1)
            if n_1!=0 or search_str=='':
                if Only_Name:
                    if is_show_file:
                        dire_cache+=cache_1
                    else:
                        dire_cache[i]=cache_1
                else:
                    dire_cache+=dire_for.format(pad,i)+cache_1
                #cache+="\n%s*- %s"%(pad,dire_color+i+back_color)+cache_1
                n=n+1
    if Only_Name==False:
        if file_cache=="":
            file_cache=''
        else:
            file_cache="\n"+pad+'+-- '+file_cache[:-3]
    if is_show_file:
        cache=file_cache+dire_cache
    else:
        cache=dire_cache
    return n,cache

def limit_out(row,rows):
    sys.stdout.flush()
    uchar=''
    if row>=rows:
        sys.stdout.write(wait[0])
        uchar=msvcrt.getch()
        sys.stdout.write(wait[1])
        if uchar == b' ':
            row=1
            rows=5
        elif uchar in [b'e',b'q',b'\x03',b'\x1a']:
            raise KeyError()
        else:
            row=1
            rows=1
    else:
        row+=1
    return row,rows


def out_command(coms,rows=20):
    coms=coms.splitlines()
    row=0
    curr_row=0
    for curr_row in coms:
        try:
            row,rows=limit_out(row,rows)
            print(curr_row)
        except:
            print(curr_row)
            return 0

def out_des_com(comm_list,cmd_width,des_width,rows=20):
    row=0
    print("command:")
    for i in comm_list:
        cmd=i[0].encode("gbk").ljust(cmd_width,b' ').decode('gbk')
        des=i[2].encode("gbk").ljust(des_width,b' ').decode('gbk')
        outdata="   %s : %s : %s"%(cmd,des,i[1])
        try:
            row,rows=limit_out(row,rows)
            print(outdata)
        except:
            return 0


def out_all_com(comm_list,rows=5):
    title=["Name",
           "Content of Execution",
           "Description",
           "Pre-executed command",
           "Actual execution directory",
           "Window program"]
    row=0
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
        try:
            row,rows=limit_out(row,rows)
            print(outdata)
        except:
            return 0
        pass

def OutCommands(filelist,coms,com_s,isall):
    out_comm_list=[]
    cmd_width=0
    des_width=0
    for i in coms:
        if filelist[i][1]==1:
            continue
        if com_s=='*' or com_s in i :
            cache=(get_OutCommand(filelist,i))
            if len(cache[0])>cmd_width:
                cmd_width=len(cache[0])
            if len(cache[2])>des_width:
                des_width=len(cache[2])
            out_comm_list.append(cache)
    if isall:
        out_all_com(out_comm_list)
    else:
        out_des_com(out_comm_list,cmd_width,des_width)
    
def get_OutCommand(filelist,com_n):
    comm_path=filelist[com_n][0]+'\\'+com_n+'.bat'
    cmd,des,precom,is_start,real_dir=get_cmd_info(comm_path)
    return [com_n,cmd,des,precom,real_dir,is_start]