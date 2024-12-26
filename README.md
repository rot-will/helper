工具可以用来管理windows中的命令，根据自定义插件可以用于任何系统

## 迁移数据
### 3.x -> 4.0

1. 使用`python3 helper.py -export export.txt /`导出命令，之后使用4.0版本的helper执行导出的命令
2. 取消filestore/filesystem.py的第71-72行的注释，之后使用4.0版本随意创建一个节点，创建节点之后将71-72行注释或删除即可


## 参数详情
```shell
# 默认参数，可以使用 -t ??? 或 -dis ??? 指定输出或节点模块，同时使用-h可以获取对应模块的参数
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
pythonw helper.py -dis win # 显示无命令行窗口
```

## 节点与对象
由于本人英语不好，所以代码中存在部分node与note乱用的情况，实在抱歉
查看指定类型对象的创建参数
```shell
python3 helper.py -t ??? -h 
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
import filestore.core as core
class File(core.fobj):
    suffix="test" # 节点类型的名称，当创建节点会创建文件时，也是文件的后缀名 
    is_physical=True # 用于判断节点是否会创建文件
    tid=1 # 节点类型的唯一id 定义时请慎重
    is_join_suff=True # 判断节点创建的文件是否带有后缀

    class Attr(core.Enum):
        test=0
        # 储存属性id的枚举类型

    Attr_info={Attr.test.value:core.attrInfo(name="test",type=core.test.str,arg="-test",desc="test"),}
        # 属性信息

    Needattr=[Attr.test.value] # 必须存在的属性id列表
    

    Out_need_attr={Attr.descid.value} # 简单输出时的属性列表

    def Make(self):
        # 创建对象时的操作
        # 根据 self.attr 中的属性运行处理代码
    """
        用于删除对象
    """
    def remove(self,key=None):
        # 删除对象时的操作
        return

FILETYPES=[File]
import  core.config as Cfg
def CheckCONFIG():
    pass
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
