from PySide6.QtWidgets import (QWidget,QLineEdit,QLabel,QHBoxLayout,QVBoxLayout,QScrollArea,QGroupBox,
            QSizePolicy,QPushButton)
from PySide6.QtCore import Qt,Signal
from PySide6.QtGui import QCloseEvent, QPixmap,QPainter,QColor,QFont
from PySide6.QtGui import QMouseEvent
import display.win.api as api

class stroption(QWidget):
    def __init__(self,name,value,valueType='Any',*args,**kargs):
        super().__init__(*args,**kargs)
        self.setProperty("type",valueType)
        self.setupUi(name,value)

    def setupUi(self,name,value):
        self.setProperty("name",name)
        layout=QHBoxLayout()
        nameLab=QLabel(name)
        valueInput=QLineEdit()
        valueInput.setText(str(value))
        self.valueInput=valueInput
        nameLab.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
        layout.addWidget(nameLab)
        layout.addWidget(valueInput)
        layout.setContentsMargins(0,0,0,0)
        self.setLayout(layout)
    def getValue(self):
        return (self.property("name"),self.valueInput.text(),self.property("type"))
        pass

class OptionBox(QGroupBox):
    def __init__(self,name,group,*args,**kargs):
        super().__init__(name,*args,**kargs)
        self.setProperty("name",name)
        self.Options=[]
        self.setupUi(group)
    def setupUi(self,group):
        self.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Fixed)
        
        groupLay=QVBoxLayout()
        for name in group:
            valueType,value=group[name]
            lab=stroption(name,value,valueType)
            self.Options.append(lab)
            groupLay.addWidget(lab)
        self.setLayout(groupLay)
        return self

    def getValue(self):
        result={}
        for option in self.Options:
            name,value,type=option.getValue()
            result[name]=(type,value)
        return self.property("name"),result
        pass

class optionWid(QWidget):
    def __init__(self,*args,**kargs):
        super().__init__(*args,**kargs)
        self.Groups={}
        self.setupUi()
    
    def setupUi(self):
        layout=QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop|Qt.AlignmentFlag.AlignLeft)
        layout.setSpacing(2)
        layout.setContentsMargins(3,3,3,3)
        self.setLayout(layout)
        pass

    def makeGroup(self,options):
        group=[]
        for name in options:
            if type(options[name])==dict:
                group.append(OptionBox(name,options[name]))

            else:
                valueType,value=options[name]
                lab=stroption(name,value,valueType)
                group.append(lab)

        return group

        pass
    def addOptions(self,ind,options):
        group=self.makeGroup(options)
        self.Groups[ind]=group
    
    def erasureBox(self):
        while self.layout().count():
            self.layout().removeItem(self.layout().itemAt(0))
        for child in self.children():
            
            if child!=self.layout():
                child.setParent(None)

    def setOption(self,ind):
        self.erasureBox()
        group=self.Groups[ind]
        for subopt in group:
            self.layout().addWidget(subopt)
        pass

    def getGroupOptions(self):
        result={}
        for ind in self.Groups:
            group={}
            for option in self.Groups[ind]:
                if type(option)==OptionBox:
                    name,value=option.getValue()
                    group[name]=value
                else:
                    name,value,Type=option.getValue()
                    group[name]=(Type,value)
            result[ind]=group
        return result
        
        pass

class groupName(QLabel):
    selectSig=Signal(int)
    def __init__(self,index,name,*args,**kargs):
        
        super().__init__(*args,**kargs)
        self.setProperty("index",index)
        self.setProperty("name",name)
        self.setText(name)
    
    def mousePressEvent(self, ev: QMouseEvent) -> None:
        if ev.button()==Qt.MouseButton.LeftButton:
            self.selectSig.emit(self.property("index"))
        return super().mousePressEvent(ev)

    def name(self):
        return self.property("name")
    
class GroupnameBox(QWidget):
    selectSig=Signal(int)
    def __init__(self,*args,**kargs):
        super().__init__(*args,**kargs)
        self.groups={}
        self.currentGroup=None
        self.setupUi()

    
    def setupUi(self):
        layout=QVBoxLayout()
        layout.setSpacing(3)
        layout.setContentsMargins(3,3,3,3)
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)
        self.setLayout(layout)
        pass

    def addOption(self,ind,name):
        if self.currentGroup==None:
            self.currentGroup=ind
        group=groupName(ind,name)
        group.selectSig.connect(self.selectIndex)
        self.groups[ind]=group
        self.layout().addWidget(group)
    
    def selectIndex(self,ind):
        self.selectSig.emit(ind)
    
    def setSelStyle(self,ind=None):
        if ind==None:
            pass
        else:
            pass
        pass
    def getNames(self):
        result={}
        for ind in self.groups:
            result[ind]=self.groups[ind].name()
        return result

class Option(QWidget):
    close_signal=Signal()
    def __init__(self,*args,**kargs):
        super().__init__(*args,**kargs)
        self.setupUi()
    def setupUi(self):
        self.setMinimumWidth(500)
        self.setMinimumHeight(500)
        self.setWindowTitle("选项")
        self.setWindowIcon(api.application_ico)
        opGroupBox=GroupnameBox()
        opGroupBox.setFixedWidth(60)
        self.opGroupBox=opGroupBox
        groupArea=QScrollArea()
        groupArea.setFixedWidth(60)
        groupArea.setWidget(opGroupBox)
        groupArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        groupArea.setWidgetResizable(True)

        opBox=optionWid()
        self.opBox=opBox
        opArea=QScrollArea()
        opArea.setWidget(opBox)
        opArea.setWidgetResizable(True)
        opArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        opGroupBox.selectSig.connect(opBox.setOption)
        submit=QPushButton("&submit")
        cancel=QPushButton("&cancel")
        cancel.clicked.connect(self.cancel)
        submit.clicked.connect(self.submitConfig)
        layout=QVBoxLayout()
        layout.setContentsMargins(3,3,3,3)

        grouplay=QHBoxLayout()
        grouplay.addWidget(groupArea)
        grouplay.addWidget(opArea)
        grouplay.setSpacing(2)
        #grouplay.setContentsMargins(3,3,3,3)
        buttLay=QHBoxLayout()
        buttLay.setAlignment(Qt.AlignmentFlag.AlignRight)
        buttLay.addWidget(cancel)
        buttLay.addWidget(submit)
        buttLay.setContentsMargins(0,0,0,0)
        
        layout.addLayout(grouplay)
        layout.addLayout(buttLay)

        self.setLayout(layout)
        self.setGroup()

    def setGroup(self):
        groups=api.getConfigGroup()
        
        for ind,value in enumerate(groups):
            name,group=value
            self.opGroupBox.addOption(ind,name)
            
            self.opBox.addOptions(ind,group)
        self.opGroupBox.selectIndex(0)
    
    def submitConfig(self):
        groups=self.opBox.getGroupOptions()
        groupnames=self.opGroupBox.getNames()
        cfgDict={}
        for ind in groupnames:
            cfgDict[groupnames[ind]]=groups[ind]
        status=api.setConfigFromDict(cfgDict)
        if status==True:
            self.close()

        pass

    def cancel(self):
        self.close()
    def closeEvent(self, event) -> None:
        self.close_signal.emit()
        return super().closeEvent(event)
    pass

class TopButton(QWidget):
    def __init__(self,hover_color:str,*args,**kargs):
        super().__init__(*args,**kargs)
        self.setupUi(hover_color=hover_color)
    
    def setupUi(self,**kargs):
        self.setMaximumHeight(27)
        self.setMinimumHeight(27)
        self.setupStyle(**kargs)
        layout=QHBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.setSpacing(0)
        layout.setContentsMargins(0,0,0,0)

        self.setLayout(layout)

        
        pass
    def setupStyle(self,**kargs):
        stylesheet=f"""
QLabel.butt{{
    padding:2px;
}}
QLabel.butt:hover{{
    background: {kargs['hover_color']}
    }}
"""
        self.setStyleSheet(stylesheet)

    def addButton(self,imgpath):
        top_butt=QLabel()
        top_butt.setPixmap(QPixmap(imgpath))
        top_butt.setScaledContents(True)
        top_butt.setProperty('class','butt')
        top_butt.setMaximumHeight(27)
        top_butt.setMaximumWidth(27)
        self.layout().addWidget(top_butt)
        return top_butt

class SearchInput(QLineEdit):
    def __init__(self,*args,**kargs):
        
        super().__init__()
        self.setProperty("path","")
        self.setProperty("rule","")
    
    def makeInfo(self):
        text=self.text()
        splitLine=text.split(':')
        if len(splitLine)==1:
            splitLine.append('')
        key=['path','rule']
        for ind,value in enumerate(splitLine):
            self.setProperty(key[ind],value)
            
    def keyPressEvent(self, keyEvent) -> None:
        if keyEvent.key() ==Qt.Key.Key_Return or keyEvent.key()==Qt.Key.Key_Enter:
            self.makeInfo()
            api.Search(self.property("path"),self.property("rule"))
        elif  keyEvent.key()==Qt.Key.Key_Escape:
            self.setContent()
        return super().keyPressEvent(keyEvent)
    
    def setContent(self):
        text=""
        key=['rule']
        for property in key:
            if text!="":
                text=":"+self.property(property)  
            elif self.property(property)!="":
                text=":"+self.property(property)
        text=self.property("path")+text
        self.setText(text)

    def setPath(self,text):
        self.setProperty("path",text)
        self.setContent()
        
    
class Search(QWidget):

    def __init__(self,*args,**kargs):
        super().__init__(*args,**kargs)
        self.setupUi()

    def setupUi(self):
        self.setupStyle()
        
        input=SearchInput()
        input.setObjectName("search")
        input.setPlaceholderText("请输入要搜索的对象名称")
        search_font=QFont("宋体",12,1)
        input.setFont(search_font)
        self.input=input

        layout=QHBoxLayout()
        layout.addWidget(input)
        
        layout.setSpacing(0)
        layout.setContentsMargins(2,2,2,2)
        self.setLayout(layout)

    def setupStyle(self):
        stylesheet="""
SearchInput#search{
    border: none;
    border-bottom: none;
    margin-left:2px;
    height:20px;
    color: #888888;
    background: #f8f8f8;
    
}
QLabel#search_ico{
    padding: 2px;
}

Search{
    background: #f8f8f8;
}
"""
        self.setStyleSheet(stylesheet)
        pass

    def setPath(self,path):
        self.input.setPath(path)

    def paintEvent(self,event):
        painter=QPainter(self)
        painter.fillRect(self.rect(),QColor('#f8f8f8'))

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self.input.setFocus()

class TopInfo(QWidget):
    def __init__(self,*args,**kargs):
        super().__init__(*args,**kargs)
        self.setupUi()
    
    def setupUi(self):
        obj_num=QLabel(u"对象数量：")
        obj_num.setAlignment(Qt.AlignmentFlag.AlignRight)
        node_num=QLabel(u"节点数量：")
        node_num.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.obj_num=QLabel("/")
        self.node_num=QLabel("/")

        obj_lay=QHBoxLayout()
        obj_lay.addWidget(obj_num,1)
        obj_lay.addWidget(self.obj_num,2)
        node_lay=QHBoxLayout()
        node_lay.addWidget(node_num,1)
        node_lay.addWidget(self.node_num,2)

        layout=QVBoxLayout()
        #layout.addLayout(curr_lay)
        layout.addLayout(obj_lay)
        layout.addLayout(node_lay)
        self.setLayout(layout)
        
        pass

    def setinfo(self,objnum,nodenum):
        self.obj_num.setText(str(objnum))
        self.node_num.setText(str(nodenum))

class Top(QWidget):
    setinfo_sig=Signal(str,str)
    def __init__(self,*args,**kargs):
        super().__init__(*args,**kargs)
        self.setupUi()
    
    def setupUi(self):
        self.Option_win=None
        self.setupStyle()

        self.toplay=TopButton("#37f6b0")
        opt_butt=self.toplay.addButton("./option.png")
        opt_butt.mouseReleaseEvent=self.option_show
        
        search=Search()
        self.search=search
        info=TopInfo()
        self.setinfo_sig.connect(info.setinfo)
        layout=QVBoxLayout()
        layout.addWidget(self.toplay,0,Qt.AlignmentFlag.AlignTop)
        layout.addWidget(info)
        layout.addWidget(search,0,Qt.AlignmentFlag.AlignBottom)
        layout.setSpacing(0)
        layout.setContentsMargins(0,0,0,0)
        self.setLayout(layout)

    def setupStyle(self):
        self.setMinimumHeight(130)
        self.setMaximumHeight(130)
        self.setWindowFlags(self.windowFlags()|Qt.WindowType.FramelessWindowHint)
        stylesheet="""
"""
        self.setStyleSheet(stylesheet)

    
    def paintEvent(self,event):
        painter=QPainter(self)
        painter.fillRect(self.rect(),QColor('#37f6b0'))


    def option_show(self,event:QMouseEvent):
        if self.Option_win!=None:
            self.Option_win.activateWindow()
            return
        self.Option_win=Option()
        self.Option_win.close_signal.connect(self.option_close)
        self.Option_win.show()
        pass

    def option_close(self):
        if self.Option_win!=None:
            self.Option_win.close()
            self.Option_win=None
        pass


    def setinfo(self,name,objnum,nodenum):
        self.search.setPath(name)
        self.setinfo_sig.emit(objnum,nodenum)
        