import filestore.core as core
import os
import  core.config as Cfg

"""
作为文件父类
之后创建文件子类如 Fbat,Fsh等
"""
class File(core.fobj):
    suffix="bat"
    is_physical=True
    tid=1
    is_join_suff=True
    class Attr(core.Enum):
        commid=0
        runmid=1
        preid=2
        runpid=3
        icoid=4
        descid=5

    Attr_info={Attr.commid.value:core.attrInfo(name="command",type=core.attrType.str,arg="-com",desc="Command executed at runtime"),
            Attr.runmid.value:core.attrInfo(name="runmode",type=core.attrType.branch,arg="-start",desc="Whether to execute independently (0: console , 1: window&console , 2: window)"),
            Attr.preid.value:core.attrInfo(name="preboot",type=core.attrType.list,arg="-pre",desc="Environment configuration before command execution(Allow multiple)"),
            Attr.runpid.value:core.attrInfo(name="runpath",type=core.attrType.str,arg="-rpath",desc="Directory where the command is executed"),
            Attr.icoid.value:core.attrInfo(name="icopath",type=core.attrType.str,arg="-ico",desc="Icons of objects in the window"),
            Attr.descid.value:core.attrInfo(name="descript",type=core.attrType.str,arg="-desc",desc="Description of the current object"),}

    Needattr=[Attr.commid.value,Attr.runmid.value]
    

    Out_need_attr={Attr.descid.value}

    def checkExist(self,level=1):
        if  os.path.exists(os.path.join(Cfg.cfg.filestore.defpath,self.name+'.'+self.suffix))==False:
            if level==1:
                raise core.StoreError("The File object is invalid",core.StoreError.Exist)
            return False
        return True

    """
        EditComm
        EditIco
        EditDesc
        编辑bat文件指定内容
        Make
        编译bat文件开头结尾
    """
    def EditComm(self,file):
        get_arg="%*"
        if self.attr[self.Attr.runmid.value]==1:
            wmode=f'start "{self.name}" '
        elif self.attr[self.Attr.runmid.value]==2:
            wmode=f"explorer "
            get_arg=""
        else:
            wmode=""
            
        wdata=f"""set {self.Attr_info[self.Attr.runpid.value].name}={self.attr[self.Attr.runpid.value]}
set "{self.Attr_info[self.Attr.commid.value].name}={self.attr[self.Attr.commid.value]}"
set {self.Attr_info[self.Attr.runmid.value].name}={wmode}
"""
        file.write(wdata)
        return get_arg

    def Make(self):
        if self.is_join_suff:
            realpath=os.path.join(Cfg.cfg.filestore.defpath,self.name+'.'+self.suffix)
        else:
            realpath=os.path.join(Cfg.cfg.filestore.defpath,self.name)
        batf=open(realpath,'w')
        title="""@echo off
setlocal enabledelayedexpansion 
"""
        batf.write(title)
        get_arg=self.EditComm(batf)
        predata=""
        if type(self.attr[self.Attr.preid.value])==str:
            predata=self.attr[self.Attr.preid]
        elif type(self.attr[self.Attr.preid.value])==list:
            for i in self.attr[self.Attr.preid.value]:
                predata+=i+'\n'
        else:
            raise core.StoreError("preboot Expected str/bytes type",core.StoreError.VarType)
        if predata.strip()=="":
            predata=""
        

        bann=f"""set currpwd=%CD%
if not "%{self.Attr_info[self.Attr.runpid.value].name}%"=="" (cd /d %{self.Attr_info[self.Attr.runpid.value].name}%)
{predata}
%{self.Attr_info[self.Attr.runmid.value].name}% %{self.Attr_info[self.Attr.commid.value].name}% {get_arg}
if not "%{self.Attr_info[self.Attr.runpid.value].name}%"=="" (cd /d %currpwd%)
"""
        
        batf.write(bann)
        batf.write("endlocal")
        batf.close()
        pass

    """
        用于删除对象
    """
    def remove(self,key=None):
        if bool(key):
            raise core.StoreError("%s is File,not Dire"%self.name,core.StoreError.missing)
        if not self.checkExist():
            return;
        if self.is_join_suff:
            realpath=os.path.join(Cfg.cfg.filestore.defpath,self.name+'.'+File.suffix)
        else:
            realpath=os.path.join(Cfg.cfg.filestore.defpath,self.name)
        os.remove(realpath)
        return

FILETYPES=[File]

def CheckCONFIG():
    pass