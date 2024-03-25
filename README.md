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