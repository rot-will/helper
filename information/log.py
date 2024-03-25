
import sys
import os
import threading
class logExce(Exception):
    init=0
    def __init__(self,message,id):
        super(logExce,self).__init__()
        self.message=message
        self.id=id
        pass
    pass

class Log():
    lock=threading.Lock()
    def __init__(self):
        self.handle=open(os.path.join(sys.path[0],'.help.log'),'a')
        pass
    def out(self,message,level,title):
        if title!='':
            title=title+':'
        message='[%d] %s'%(level,title)+message.strip()+'\n'
        with self.lock:
            self.write(message)
        
    def write(self,message):
        self.handle.write(message)
        print(message,end='')
        pass

    pass

loghandle:Log=None
def check_loginit():
    if loghandle==None:
        raise logExce("log system must be init",logExce.init)

def log(message:str,level=0,title=""):
    loghandle.out(message,level,title)


def init(handle=None):
    global loghandle
    if handle==None:
        loghandle=Log()
    else:
        loghandle=handle