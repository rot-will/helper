## 安装 ##
>python3 setup.py <tools_path> [tools_env]
## 帮助文档 ##
```
usage: help [-h] [-c] [-help] [-hide] [-out OUT_COMMAND] [-oall] [-noc NUM_COL] [-win] [-s SEARCH_STR] [-dire]
            [-d DIRECT] [-r REPRESENT] [-precom PRECOM] [-tardir TARGET_DIR] [-start] [-n NAME] [-replace] [-t TYPE]
            [-redir REDIR] [-add ADD_DIRE] [-del DEL_DIRE]

optional arguments:
  -h, --help            show this help message and exit               查看帮助文档 
  -c, --create          Construct system variables default:False      更新环境变量
  -help                 view type default:False                       查看帮助文档并且只显示目录
  -hide                 Show hide commands default:True               查看隐藏目录
  -out OUT_COMMAND      View the contents of the command              查看搜索到的命令的大概信息
                                                                    helper -out *
                                                                      查看所有命令的大概信息
  -oall                 View the all contents of the command          查看搜索到的命令的所有信息
                                                                    helper -out * -oall
                                                                      查看所有命令的所有信息
  -noc NUM_COL          Number of columns                             查看命令列表时每行显示数量
  -win                  Using the Window Interface(未实现)
  -s SEARCH_STR, --search SEARCH_STR                                  模糊搜索名称(默认搜索命令)
                        Search specified string                     helper -s xxx 
  -dire                 Search specified type                         指定搜索目录名称
                                                                    helper -s xxx -dire
  -d DIRECT, --direct DIRECT                                          指定命令中实际执行的命令
                        Specify command
  -r REPRESENT, --represent REPRESENT                                 指定命令的描述，使用helper -out xxx时会显示
                        command note
  -precom PRECOM        Pre-executed commands to set the environment  指定实际执行的命令之前执行的命令，用来设置一些环境
  -tardir TARGET_DIR    Specify target program directory              指定实际命令执行时所在的目录
  -start                Do you want to use start to launch exe        更改命令执行的方式 默认执行exe/bat时使用start xxx.bat
  -n NAME, --name NAME  Specify script name                           指定命令的名称
  -replace              Replace the original command default:False    更改命令的参数
  -t TYPE, --type TYPE  Type of command xx/xxx/xxxx                   指定命令所在的目录
  -redir REDIR          Change type position                          更改目录位置
  -add ADD_DIRE         Added type                                    添加目录
  -del DEL_DIRE         Delete command or type                        删除目录或命令
```

### 编辑 ###
>helper -add <direname>
```python
helper -add a
helper
"""
*- /
  *- \a/
"""
```
>helper -n <direname> -redir <new_direpath>
```python
helper -n a -redir b
helper
"""
*- /
  *- \b/
"""
```
>helper -del <comname/direname>
```python
helper -del b
helper
"""
*- /
"""
```
>helper -n <name> -d <command> [-t dire] [-r 描述] [-tardir 系统目录] [-start] [-replace]
```python
helper -add a
helper -add b
helper -n c -d dir -t a -r xxx     
        # 在这里使用当-d参数指定的是某个exe程序或者bat脚本时
        # 在这里加入-start可以设置exe或bat在命令行执行
        #   不加的话就是使用start执行
        # 当使用-start同时使用-replace时，可以转换start的模式
        #   如原先使用命令行执行，在同时使用-start,-replace时，就变成使用start执行
        #   但-start参数只对exe/bat有效
        # 在使用-replace时，不能同时使用-d与-t参数
        # 当创建命令时-d 与-t参数都是必要参数
helper
"""
*- /
  *- \a/
    +-- c
  *- \b/
"""
helper -n c -t b -replace
helper
"""
*- /
  *- \a/
  *- \b/
    +-- c
"""
helper -del b/c
helper
"""
*- /
  *- \a/
  *- \b/
"""
```
