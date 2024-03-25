from PySide6.QtWidgets import QApplication
import display.win.Main as Main
import core.init  
import display.win.api as api
        
class mapp(QApplication):
    def __init__(self,*args,**kargs):
        super().__init__(*args,**kargs)  # 用来处理参数

def init():
    api.init()

def show(args):
    core.init.init()
    app=mapp([]) 
    
    m=Main.MainWindow(app)
    m.show()    # 使窗口显示
    app.exec()  # 循环监听窗口时间，如果不执行则窗口会很快关闭

    