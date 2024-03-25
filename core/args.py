from typing import Any


class ArgError(Exception):
    Argname=0
    def __init__(self,*args,**kargs):
        super(ArgError,self).__init__()
        self.ErrorMessage=args[0]
        self.Errorid=args[1]
    pass
class args:
    def __init__(self,d_args:dict|None=None):
        if d_args==None:
            return
        else:
            for key in d_args:
                if type(key)!=str:
                    raise ArgError("Error initializing args: key's type not str",ArgError.Argname)
                if type(d_args[key])==dict:
                    value=args(d_args[key])
                    setattr(self,key,value)
                else:
                    setattr(self,key,d_args[key])
    def __setitem__(self, __name: str, __value: Any) -> None:
        self.__setattr__(__name,__value)
    def __getattribute__(self, __name: str) -> Any:
        try:
            return super().__getattribute__(__name)
        except:
            return None