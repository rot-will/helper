from PySide6.QtWidgets import QWidget,QLabel,QVBoxLayout,\
    QHBoxLayout,QDialog,QSystemTrayIcon,QMenu,QScrollArea
from PySide6.QtGui import QIcon,QPixmap,QAction
from PySide6.QtCore import Qt
import display.win.api as api
from display.win import Top,Body
import os
class msg(QDialog):
    def __init__(self,text):
        super().__init__()
        self.setProperty("text",text)
        self.setAttribute(Qt.WidgetAttribute.WA_StaticContents)
        self.setupUi()

    def setupUi(self):
        self.setFixedWidth(200)
        self.setFixedHeight(50)
        self.setWindowTitle(self.property("text"))
        self.setWindowIcon(api.application_ico)
        info=QLabel()
        info.setText(self.property("text"))
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout=QHBoxLayout()
        layout.addWidget(info,0,Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)

        self.setModal(True)
    


class MainButton(QLabel):
    def __init__(self,name,ico,*args,**kargs):
        super().__init__(*args,**kargs)
        self.setProperty("icopath",ico)
        self.setProperty("name",name)
        self.setupUi()
        self.leaveEvent(None)

    def setupUi(self):
        if self.property("icopath") !=None:
            self.setPixmap(QPixmap(self.property("icopath")))
        else:
            self.setText(self.property("name"))
    def enterEvent(self, event):
        stylesheet="""
        background: #cccccc;"""
        self.setStyleSheet(stylesheet)
    
    def leaveEvent(self, event):
        stylesheet="""
        background: #dddddd;"""
        self.setStyleSheet(stylesheet)
    pass

class Buttonbox(QWidget):
    def __init__(self,*args,**kargs):
        super().__init__(*args,**kargs)
        self.setupUi()
    
    def setupUi(self):
        layout=QHBoxLayout()
        left=QHBoxLayout()
        right=QHBoxLayout()
        left.setSpacing(3)
        left.setAlignment(Qt.AlignmentFlag.AlignLeft)
        right.setSpacing(3)
        right.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addLayout(left,0)
        layout.addLayout(right,0)
        layout.setContentsMargins(2,2,2,2)
        #layout.setAlignment(Qt.AlignmentFlag.AlignAbsolute)
        self.setLayout(layout)
        self.right=right
        self.left=left

        self.setFixedHeight(34)
    
    def addbutt(self,name,ico,align):
        button=MainButton(name,ico)
        butt_size=self.height()-4
        button.setFixedSize(butt_size,butt_size)
        if align==Qt.AlignmentFlag.AlignLeft:
            self.left.addWidget(button,0)
        else:
            self.right.addWidget(button,0)
        return button

class MainWindow(QWidget): # 创建窗口类，继承基础窗口类
    def __init__(self,app):
        super().__init__()  # 调用父类的构造函数
        self.setupUi(app)

    def setupUi(self,app):
        api.windows_dire=os.path.dirname(__file__);
        api.application_ico=QIcon(api.windows_dire+"/icon.ico")
        self.setWindowIcon(api.application_ico)
        self.setWindowTitle("helper")
        self.setMaximumWidth(450)
        self.setMinimumWidth(350)
        self.setMinimumHeight(600)
        
        self.tray=self.setupTray(app)

        top=Top.Top()
        api.topinfo=top.setinfo
        api.sort_mode=self.Getsort_mode
        api.view_mode=self.Getview_mode
        self.top=top
        self.setProperty("sortmode",api.sortMode.Nonsort)
        self.setProperty("viewmode",api.ViewMode.Tree)
        button=Buttonbox()
        toroot=button.addbutt("toroot",None,Qt.AlignmentFlag.AlignLeft)
        retparent=button.addbutt("return",None,Qt.AlignmentFlag.AlignLeft)
        refresh=button.addbutt("refersh",None,Qt.AlignmentFlag.AlignLeft)
        viewmode=button.addbutt("viewmode",None,Qt.AlignmentFlag.AlignRight)
        sortview=button.addbutt("sort",None,Qt.AlignmentFlag.AlignRight)
        newchild=button.addbutt("child",None,Qt.AlignmentFlag.AlignRight)

        retparent.mousePressEvent=self.Retparent
        toroot.mousePressEvent=self.Toroot
        refresh.mousePressEvent=self.Referse
        sortview.mousePressEvent=self.Sortview
        newchild.mousePressEvent=self.NewChild
        viewmode.mousePressEvent=self.viewMode



        body=Body.Body()
        api.rebuild=body.BuildLayout
        api.Restore()

        body_s=QScrollArea()
        body_s.setWidgetResizable(True)
        body_s.setWidget(body)
        
        #bottom=Bottom.Bottom()
        
        layout=QVBoxLayout()
        layout.addWidget(top,0,Qt.AlignmentFlag.AlignTop)
        layout.addWidget(button,0,Qt.AlignmentFlag.AlignTop)

        layout.addWidget(body_s,1)
        #layout.addWidget(bottom,0,Qt.AlignmentFlag.AlignBottom)
        layout.setSpacing(0)
        layout.setContentsMargins(0,0,0,0)
        self.setLayout(layout)
        self.setStyleSheet("mwindow{background: #fff0f0;}")
    
    def setupTray(self,app):
        tray=QSystemTrayIcon(api.application_ico,parent=app)
        menu=QMenu()

        restore=QAction("exit",menu)
        restore.triggered.connect(lambda :(self.top.option_close(),app.quit()))
        menu.addAction(restore)
        
        tray.setContextMenu(menu)
        tray.activated.connect(self.display)
        tray.show()
        return tray
    
    def closeEvent(self, event) -> None:
        self.hide()
        self.tray.show()
        event.ignore()
        
    def display(self,reason):
        if reason==QSystemTrayIcon.ActivationReason.Trigger:
            if self.isHidden():
                self.show()
            else:
                self.activateWindow()
    
    def Toroot(self,event):
        if event.button()==Qt.MouseButton.LeftButton:
            api.Restore("","")
    def Retparent(self,event):
        if event.button() == Qt.MouseButton.LeftButton:
            api.Restore(api.curr_path[0])

    def Referse(self,event):
        if event.button()==Qt.MouseButton.LeftButton:
            m=msg("正在刷新，请稍后...")
            m.show()
            api.referse()
            m.close()

    def viewMode(self,event):
        if event.button()==Qt.MouseButton.LeftButton:
            curr_mode=self.Getview_mode()
            if curr_mode==api.ViewMode.List:
                self.setProperty("viewmode",api.ViewMode.Tree)
            elif curr_mode==api.ViewMode.Tree:
                self.setProperty("viewmode",api.ViewMode.List)
            pass
            api.Restore()
        pass
    
    def Sortview(self,event):
        if event.button()==Qt.MouseButton.LeftButton:
            curr_mode=self.Getsort_mode()
            if curr_mode==api.sortMode.Nonsort:
                self.setProperty("sortmode",api.sortMode.Order)
            elif curr_mode==api.sortMode.Order:
                self.setProperty("sortmode",api.sortMode.Invert)
            else:
                self.setProperty("sortmode",api.sortMode.Nonsort)
            api.Restore()
    def NewChild(self,event):
        if event.button()==Qt.MouseButton.LeftButton:
            path=api.curr_path[0]
            name=api.curr_path[1]
            Body.ChildWidget.addChild(path,name)
        pass
    def Getsort_mode(self):
        return self.property("sortmode")
    def Getview_mode(self):
        return self.property("viewmode")

    def quit(self):
        super().close()
