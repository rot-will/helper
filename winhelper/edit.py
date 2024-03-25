from winhelper.func import *
from winhelper.env import *

import os
comm_orig=['@echo off','cd /d %sour_dir%','set sour_dir=%CD%','']
def editbat(root_path,name,cmd,path,precom,real_dir,represent,is_start):
    file_path=root_path+'\\'+path+'\\'+name+'.bat'
    bat_file=open(file_path,'wb')
    try:
        pad='%c% %*\r\n'
        cmd_line='set c='
        direct=comm_orig[0]+'\r\n'
        cd_dir=""
        return_dir=""
        des_line='set des=%s'%represent
        if real_dir:
            return_dir=comm_orig[1]+'\r\n'
            #cd_dir+=comm_orig[3]+'\r\n'+comm_orig[4]+'\r\n'
            cd_dir+=comm_orig[2]+'\r\n'
            cd_dir+='set real_dir="%s"'%real_dir+'\r\n'
            cd_dir+="cd /d %real_dir%"+'\r\n'
        if precom:
            precommand=precom
        else:
            precommand=""

        cmd=cmd.replace("'",'"')
        if os.path.isfile(cmd):
            if ' ' in cmd:
                pad='"%c%" %*\r\n'
            if is_start:
                pad='start "" "%c%" %*\r\n'
            cmd=os.path.realpath(cmd)
            cmd_line+=cmd
        else:
            if '%*' in cmd:
                pad='%c% \r\n'
            cmd_line+=cmd
        direct=direct+cd_dir+cmd_line+'\r\n'+precommand+'\r\n'+pad+return_dir+des_line
        direct=direct.strip()
        bat_file.write(direct.encode('gbk'))
    except Exception as e:
        bat_file.close()
        os.remove(file_path)
        return -1
    return 

def Sel_Path(Path_l):
    path_len=len(Path_l)
    if path_len==0:
        return False
    elif path_len==1:
        return Path_l[0]
    else:
        n=0
        for i in Path_l:
            print('[{}{}{}] {}{}{}'.format(ind_color,n,back_color,dire_color,i,back_color))
            n+=1
        ind=-1
        n=5
        while n>0:
            try:
                ind=int(input(ind_color+"Choose Path:"+back_color))
                if ind<0 or ind>=path_len:
                    n-=1
                    continue
                break
            except ValueError:
                n-=1
        if n==0:
            raise ValueError("Please enter the appropriate number  (base:0~9)")
        return Path_l[ind]

def getpaths(dire_={},name="",curr_dire=''):
    result=[]
    raw_name=name
    if '/' in name:
        ind=name.find('/')
        name_1=name.split('/')[1:]
        name=name[:ind]
    else:
        name_1=False
    for i in dire_:
        if dire_[i]==1:
            continue
        result+=getpaths(dire_[i],raw_name,curr_dire+'/'+i)
        if i==name:
            if name_1:
                dire_c=dire_[i]
                for j in name_1:
                    if dire_c.get(j)!=None:
                        dire_c=dire_c[j]
                    else:
                        dire_c=False
                        break
                if dire_c==False:
                    continue
            result.append(curr_dire+'/'+raw_name)
    return result
                


def addbat(root_path,ddict,filelist,name,cmd='',path='',precom='',real_dir='',represent='',is_start=True,is_re=False):
    path_1=Sel_Path(getpaths(ddict['/'],path))
    if path and path_1==False:
        exit("%s not found"%path)
    else:
        path=path_1
    if is_re:
        #if path and cmd:
        #    exit("Only command contents or command directories can be replaced")
        try:
            cmd_c,des,precom_,is_start_c,real_dir_c=get_cmd_info(filelist[name][0]+'\\'+name+'.bat')
        except KeyError:
            print("Not found %s \\ %s"%(name,path))
            exit(0)
        if is_start==True and is_start_c!=is_start:
            is_start=False
        elif is_start==False and is_start_c==is_start:
            is_start=True
        if not represent:
            represent=des
        if not cmd:
            cmd=cmd_c
        if real_dir==None:
            real_dir=real_dir_c
        if precom==None:
            precom=precom_
        else:
            precom=precom.replace('\\n','\r\n').replace("'",'"')
        if path:
            if os.path.isdir(root_path+'\\'+path):
                path+="\\"+name
            elif os.path.isfile(root_path+'\\'+path+'.bat'):
                exit("There are duplicate options")
            if not os.path.isfile(root_path+'\\'+path+'.bat'):
                os.rename(filelist[name][0]+'\\'+name+'.bat',root_path+'\\'+path+'.bat')
                return 0
        
        path=filelist[name][0][len(root_path)+1:]
    elif name in filelist:
        exit("There are duplicate options")
    status=editbat(root_path,name,cmd,path,precom,real_dir,represent,is_start)
    if status==-1 and is_re:
        editbat(root_path,cmd_c,path,precom_,real_dir_c,des,is_start_c)

def redir(root_path,source,target):
    if not source:
        exit("No type specified")
    if os.path.isdir(root_path+'\\'+target):
        exit(root_path+'/'+target+" already exists")
    else:
        os.rename(root_path+'\\'+source,root_path+'\\'+target)

def deldir(path): 
    cache=os.listdir(path)
    for i in cache:
        if os.path.isdir(path+'/'+i):
            deldir(path+'/'+i)
            os.rmdir(path+'/'+i)
        else:
            os.remove(path+'/'+i)

def delete(root_path,filelist,path):
    if os.path.isdir(root_path+'/'+path):
        deldir(root_path+'/'+path)
        os.rmdir(root_path+'/'+path)
    elif os.path.isfile(root_path+'/'+path+'.bat'):
        os.remove(root_path+'/'+path+'.bat')
    elif filelist[path]:
        os.remove(filelist[path][0]+'/'+path+'.bat')
    else:
        exit('The command or directory does not exist')


def setenv(tools_env,var_name):
    os.popen('@echo off && setx %s %s'%(var_name,';'.join(tools_env).strip(';')))
    print('[+] save success')

def movdir(path,redir):
    os.rename(path,redir)
            
            

def create(root_path,ddict,filelist,tools_env,var_name,path,redir=""):
    real_path=root_path
    if (redir!='' and os.path.isdir(real_path+'/'+redir) ) or (redir=='' and os.path.isdir(real_path+'/'+path)):
        exit("The specified destination is occupied by the directory")
    elif (redir=='' and os.path.isfile(real_path+'/'+path+'.bat')) or (redir!='' and os.path.isfile(real_path+'/'+redir+'.bat')):
        exit('The specified target is occupied by the command')
    if redir!='':
        for i in redir.split('/')[:-1]:
            real_path+='/'+i
            if not os.path.isdir(real_path):
                os.mkdir(real_path)
        movdir(root_path+'/'+path,root_path+'/'+redir)
    else:
        for i in path.split('/'):
            real_path+='/'+i
            if not os.path.isdir(real_path):
                os.mkdir(real_path)
    getdirlist(root_path,ddict,filelist,tools_env,is_creat=True)
    setenv(tools_env,var_name)