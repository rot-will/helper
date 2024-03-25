经过迭代之后，现在的helper工具不仅仅能用来管理windows中的命令，根据自定义插件可以用于任何系统，也可以用来管理文档等各种功能
不过这只是我认为的，有任何意见与问题请您将其提出来
## 参数详情
```shell
usage: helper.py [-h] [-n NAME] [-t TYPE] [-p PATH] [-d DELETE] [-clear] [-dis DISPLAY] [-row ROWNUM] [-s SEARCH]
                  [-sd SEARCH_NOTE] [-out] [-all]

options:
  -h, --help            Show this help message and exit
  -n NAME               Specify the name of object/node
  -t TYPE               Object type (default:bat optional:bat node)
  -p PATH               The location of the object/note
  -d DELETE, -del DELETE
                        Delete object/note (/???/???/???)
  -clear                clear error objs
  -dis DISPLAY          Select display mode (default: con optional: con/win)

Console:
  -row ROWNUM           Number of objects displayed in a row
  -s SEARCH             Search for objects that protect the specified string
  -sd SEARCH_NOTE       Search for note that protect the specified string
  -out                  Show only the required attributes
  -all                  Show All Attributes
```

## 显示方式更改

以命令行方式显示节点与对象
```shell
python3 helper.py -dis con 
python3 helper.py -dis con -h #查看命令行显示参数
```

以窗口形式显示节点与对象(尚未开发完全)
```shell
python3 helper.py -dis win
python3 helper.py -dis win -h #查看窗口显示参数

```

## 节点与对象
由于本人英语不好，所以代码中存在部分node与note乱用的情况
查看指定类型对象的创建参数
```shell
python3 helper.py -t ... -h 
```

默认仅支持增加与删除，其他操作以插件为准，目前插件系统还为开发完全
```shell
python3 helper.py -t node -n name -p a/b/c/
python3 helper.py -t node -d /a/b/c/name
```



## 插件编写
编写的插件放入 `filestore/store/`
插件模板
```python
class File(core.fobj):
    suffix="bat" # 插件名称，也用于文件后缀
    tid=1 # 插件id，需要手动设置，不能与其他插件冲突

    class Attr:
        ... # 设置属性id

    Id_Attr={attrid:"attrname"} #设置属性id与属性名称的映射
    
    Needattr=[attrid,..] # 设置必要的属性
    
    Attr_types={attrid:attrtype} #设置属性id对应的属性类型

    Out_need_attr={attrid} # 设置简单输出时输出的属性

    @staticmethod
    def make_opt(arg:argparse.ArgumentParser):
        ... # 设置自定义插件的命令行参数

    @staticmethod
    def handle(args):
      ... # 根据args中的值进行增改操作，然后使用__init__函数应用属性的更改
            
    def __init__(self,*args,**kargs):
        # 一般通过handle调用，

    
    def remove(self,key=None):
        # 当前节点被删除时进行的操作
        return

    def Parse(self,file:core.fileio):
        # 解析存档文件中当前类型的对象

    def Save(self,file:core.fileio):
        file.WriteByte(self.tid)
        # 讲当前对象保存到存档文件中

    def export(self,file:core.fileio,path:str):
        # 导出当前对象的生成参数
    
    def getAttr(self):
        result={}
        for i in self.attr:
            result[self.Id_Attr[i]]=(self.Attr_types[i],self.attr[i])
        return result
    
    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return str(self)
FILETYPES=[...] # 指定导出的对象类
import  core.config as Cfg
def CheckCONFIG():
    #检查需要的参数是否设置完全
    #全局配置储存在 Cfg.cfg中
    
```

## 配置文件编写
```
{大类名称} 
[子类名称]
属性名称:类型=值
属性名称=值
```

访问属性的方式为`Cfg.cfg.大类名称.子类名称.属性名称`
当类型为空时值为字符串类型，当类型==int时值为整数类型
