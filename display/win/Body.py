from PySide6.QtWidgets import (QWidget,QPushButton,QLineEdit,QLabel,QVBoxLayout,QMenu,
        QSizePolicy,QHBoxLayout,
        QScrollArea,QDialog,QComboBox,QSpinBox,QListView,
        QCompleter)
from PySide6.QtCore import (Qt,Signal,QEvent,QPoint,QPropertyAnimation,QParallelAnimationGroup,
    QRegularExpression,QModelIndex,QMimeData,QStringListModel)

from PySide6.QtGui import (QDragEnterEvent, QDropEvent,QPainter,QColor,QMouseEvent,QAction,
    QResizeEvent,QRegularExpressionValidator,QKeyEvent,QDrag)
import display.win.api as api

class RenameWidget(QDialog):
    getText=lambda : ""
    def __init__(self,origin_name,*args,**kargs):
        super().__init__(*args,**kargs)
        self.setProperty("origin_name",origin_name)
        self.setupUi()
    
    def setupUi(self):
        
        self.setMinimumWidth(500)
        origin=self.property('origin_name')
        self.rejected.connect(lambda :self.setProperty("result","") if self.property("result")==None else None)
        self.setWindowIcon(api.application_ico)
        self.setWindowTitle(f"重命名   {origin}")
        oriname=QLabel(f"曾用名： {origin}")

        message=QLabel(f"")
        message.setStyleSheet("color: #ff2233;")
        self.message=message

        validator=QRegularExpressionValidator(QRegularExpression("[a-zA-Z0-9_]+"))
        
        line_input=QLineEdit()
        #line_input.setMask("")
        line_input.setValidator(validator)
        line_input.setPlaceholderText("新名称可以包括全部大小写字母加数字与英文下划线")
        
        self.getText=line_input.text

        line_button=QPushButton("确认")
        line_button.clicked.connect(self.check)
        input_lay=QHBoxLayout()
        input_lay.addWidget(line_input,1)
        
        input_lay.addWidget(line_button,0)
        layout=QVBoxLayout()
        layout.addWidget(oriname,0,Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(message,0,Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(input_lay)
        self.setLayout(layout)
        pass

    def result(self):
        if self.property("used"):
            self.message.setText("可能存在相同名称的节点或对象，请重新设置名称!!!")
            pass
        self.setProperty("result",None)
        self.setProperty("used",True)
        self.exec()
        return self.property("result")

    def check(self):
        result=self.getText()
        self.setProperty("result",result)
        self.close()

    def closeEvent(self, arg__1) -> None:
        if self.property("result")==None:
            self.setProperty("result","")
        return super().closeEvent(arg__1)

    @staticmethod
    def rename(origin_name,path,target_path):
        name=RenameWidget(origin_name)
        newname=name.result()
        status=False
        while (not status) and newname!="" and newname!=origin_name:
            status=api.rename(path,origin_name,target_path,newname)
            if status==True:
                return newname
            newname=name.text()
        return None

class RemoveDialog(QDialog):
    def __init__(self,name,*args,**kargs):
        super().__init__(*args,**kargs)
        self.setProperty("name",name)
        self.setupUi()
        
    def setupUi(self):
        self.setWindowTitle("确认删除")
        self.setWindowIcon(api.application_ico)
        name=self.property("name")
        info=QLabel(f"是否确认删除 {name} ?")

        yes=QPushButton()
        yes.setText("&Yes")
        yes.mousePressEvent=lambda e:(self.setProperty("result",True),self.close())
        no=QPushButton()
        no.setText("&No")
        no.mousePressEvent=lambda e:(self.setProperty("result",False),self.close())

        butt_lay=QHBoxLayout()
        butt_lay.addWidget(yes)
        butt_lay.addWidget(no)

        layout=QVBoxLayout()
        layout.addWidget(info,0,Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(butt_lay)
        self.setLayout(layout)
    


    def result(self):
        self.exec()
        return self.property("result")
    
    def closeEvent(self, arg__1):
        if self.property("result")==None:
            self.setProperty("result",False)
        return super().closeEvent(arg__1)
        
    @staticmethod
    def remove(path,name):
        ackremove=RemoveDialog(name)
        ack_result=ackremove.result()
        if ack_result==True:
            api.remove(path,name)

class strAttr(QWidget):
    def __init__(self,name,value=None,isneed=False,*args,**kargs):
        super().__init__(*args,**kargs)
        self.setProperty("name",name)
        if value==None:
            value=""
        self.setProperty("value",value)
        self.setProperty("isneed",isneed)
        self.setupUi()

    def setupUi(self):
        self.setFixedHeight(50)

        
        lineInput=QLineEdit()
        lineInput.setText(self.property("value"))
        self.valuewid=lineInput
        layout=QHBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        layout.setSpacing(3)
        layout.setContentsMargins(10,0,0,0)
        layout.addWidget(lineInput,0)
        self.setLayout(layout)
    
    def getValue(self):
        return self.property("name"),self.valuewid.text()
        pass
    def checkValue(self):
        if self.property("isneed")==False:
            return True
        return bool(self.valuewid.text())

class boolAttr(QWidget):
    def __init__(self,name,value=None,isneed=False,*args,**kargs):
        super().__init__(*args,**kargs)
        if value==None:
            value=0
        self.setProperty("name",name)
        self.setProperty("value",value)
        self.setProperty("isneed",isneed)
        self.setupUi()
        
    def setupUi(self):
        self.setFixedHeight(50)
        valueInput=QSpinBox()
        valueInput.setFixedWidth(200)
        valueInput.setValue(self.property("value"))
        self.valuewid=valueInput
        layout=QHBoxLayout()
        
        layout.setSpacing(3)
        layout.setContentsMargins(10,0,0,0)
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        #layout.addSpacing(2)
        layout.addWidget(valueInput)
        
        self.setLayout(layout)
        
    def getValue(self):
        return self.property("name"),int(self.valuewid.text())
    def checkValue(self):
        return True

class listAttrView(QListView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDragDropMode(QListView.InternalMove)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            
            if self.property("Dragindex")!=None:
                return
            index = self.indexAt(event.pos())
            if index.isValid():
                
                self.setProperty("Dragindex",index)
                #self.startDrag(Qt.DropAction.MoveAction|Qt.DropAction.CopyAction)
        #super().mousePressEvent(event)
    def mouseReleaseEvent(self, e: QMouseEvent) -> None:
        self.setProperty("Dragindex",None)
        return super().mouseReleaseEvent(e)
    def mouseMoveEvent(self, e) -> None:
        if self.property("Dragindex")!=None:
            self.startDrag(Qt.DropAction.MoveAction|Qt.DropAction.CopyAction)
    def startDrag(self, supportedActions) -> None:
        self.setProperty("Dragindex",None)
        
        index=self.property("Dragindex")
        if index==None:
            return
        
        mimedata=QMimeData()
        mimedata.setData("application/x-qabstractitemmodeldatalist",index.data().encode())
        drag=QDrag(self)
        drag.setMimeData(mimedata)
        drag.exec(supportedActions,Qt.DropAction.MoveAction)
        
    def dropEvent(self, event):
        dragindex=self.property("Dragindex")
        if dragindex==None:
            return
        pos=event.pos()
        curritem=self.indexAt(pos)
        pos.setY(pos.y()-4)
        
        if curritem!=self.indexAt(pos):
            curritem=self.model().index(curritem.row()-1,0,QModelIndex())

        self.model().move_options(dragindex,curritem)

    def InsertItem(self,ind,text):
        index=self.model().index(ind,0,QModelIndex())
        ind=self.model().insertItem(index,text)
        return ind
        pass

    def setItem(self,ind,data):
        index=self.model().index(ind,0,QModelIndex())
        ind=self.model().setItem(index,data)
        return ind
        pass

    def getItem(self,ind):
        index=self.model().index(ind,0,QModelIndex())
        return self.model().data(index)

class listAttrModel(QStringListModel):
    def __init__(self, data, *args, **kwargs):

        super().__init__(data, *args, **kwargs)


    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
         if role == Qt.ItemDataRole.DisplayRole:

             return self.stringList()[index.row()]
         elif role==Qt.ItemDataRole.DecorationRole:
             return super().data(index,role)
             pass
         return None

    def rowCount(self, parent=QModelIndex()):

        return len(self.stringList())

    def indexes_around(self, index):
        if index.row() < 5:
            start = 0
            end = 10
        elif index.row() > len(self.stringList) - 5:
            start = len(self.stringList) - 10
            end = len(self.stringList)
        else:
            start = index.row() - 5
            end = index.row() + 5
        return [self.index(i, 0, QModelIndex()) for i in range(start, end)]

    def move_options(self, source_index, destination_index):
        source_row = source_index.row()
        destination_row = destination_index.row()
        strlist=self.stringList()
        if source_row < destination_row:
            strlist.insert(destination_row, strlist.pop(source_row))
        else:
            strlist.insert(destination_row + 1, strlist.pop(source_row))
        self.setStringList(strlist)
        self.layoutChanged.emit()

    def insertItem(self,index,text):
        ind=index.row()
        items=self.stringList()
        
        if items[ind]=='':
            items[ind]=text
        else:
            ind=ind+1
            if items[ind]=='':
                items[ind]=text
            else:
                items.insert(ind,text)
        if items[-1]!='':
            items.append("")
        self.setStringList(items)
        self.layoutChanged.emit()
        return ind

    def setItem(self,index,text):
        ind=index.row()
        items=self.stringList()
        items[ind]=text
        if ind==self.rowCount()-1:
            items.append("")
        self.setStringList(items)
        
        self.layoutChanged.emit()
        return ind
        pass

class listAttrbox(QComboBox):
    def __init__(self,*args,**kargs):
        super().__init__(*args,**kargs)
    def mousePressEvent(self, e) -> None:
        #self.view().setProperty("Dragindex",None)
        return super().mousePressEvent(e)
    def toStart(self):
        index=self.model().index(0,0,QModelIndex())
        self.setCurrentIndex(index.row())

    def toEnd(self):
        count=self.model().rowCount()
        self.setCurrentIndex(count-1)
        pass

    def getValue(self):
        return self.model().stringList()
        
class listAttrInput(QLineEdit):
    keyPressSig=Signal(QKeyEvent)
    def __init__(self,*args,**kargs):
        super().__init__(*args,**kargs)
    
    def keyPressEvent(self, arg__1) -> None:
        self.keyPressSig.emit(arg__1)
        return super().keyPressEvent(arg__1)

class listAttr(QWidget):
    def __init__(self,name,value=None,isneed=False,*args,**kargs):
        super().__init__(*args,**kargs)
        self.setProperty("name",name)
        if value==None or value==[]:
            value=[""]
        elif value[-1]!='':
            value.append("")
            
        self.setProperty("value",value)
        self.setProperty("isneed",isneed)
        self.setupUi()

    def setupUi(self):
        self.setFixedHeight(35)
        model=listAttrModel(self.property("value"))
        listview=listAttrView()
        listview.setModel(model)
        self.view=listview
        viewbox=listAttrbox()
        
        viewbox.setView(listview)
        viewbox.setModel(model)
        viewbox.setFixedWidth(200)
        viewbox.currentIndexChanged.connect(self.indexChange)
        self.box=viewbox
        inputline=listAttrInput()
        inputline.keyPressSig.connect(self.InsertItem)
        self.inputline=inputline
        layout=QHBoxLayout()
        layout.addWidget(viewbox)
        layout.addWidget(inputline)
        layout.setSpacing(3)
        layout.setContentsMargins(10,0,0,0)
        self.setLayout(layout)
        self.box.toEnd()
        self.setProperty("permitChange",True)

    def InsertItem(self,event:QKeyEvent):
        if event.key()==Qt.Key.Key_Enter or event.key()==Qt.Key.Key_Return:
            self.setProperty("permitChange",False)
            data=self.inputline.text()
            if self.property('changeInd')!=None:
                ind=self.view.setItem(self.property('changeInd'),data)
                self.setProperty("changeInd",None)
                self.inputline.setText("")
            else:
                ind=self.view.InsertItem(self.box.currentIndex(),data)
                self.inputline.setText("")

            self.box.setCurrentIndex(ind)
            self.setProperty("permitChange",True)

        elif event.key()==Qt.Key.Key_Escape:
            
            self.setProperty("permitChange",False)
            if self.property("changeInd")!=None:
                text=self.view.getItem(self.property("changeInd"))
                self.inputline.setText(text)
            else:
                self.inputline.setText("")
            
            self.setProperty("permitChange",True)
        elif event.key()==Qt.Key.Key_Home:
            self.box.toStart()
            pass
        elif event.key()==Qt.Key.Key_End:
            self.box.toEnd()
            pass
        
            
    def indexChange(self,ind):
        if self.property("permitChange"):
            text=self.view.getItem(ind)
            self.inputline.setText(text)
            self.setProperty("changeInd",ind)
        pass

    def getValue(self):
        return self.property("name"),self.box.getValue()
    
    def checkValue(self):
        if self.property("isneed")==False:
            return True
        return bool(self.box.getValue())
        pass

typeAttrBox={
    str:strAttr,
    bool:boolAttr,
    list:listAttr
}

class attrName(QWidget):
    def __init__(self,name,isneed,*args,**kargs):
        super().__init__()
        self.setupUi(name,isneed)
    
    def setupUi(self,name,isneed):
        needLab=QLabel()
        needLab.setStyleSheet("color: #ff0000;")
        if isneed:
            needLab.setText('*')
        nameLab=QLabel(name)
        layout=QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        layout.addWidget(needLab)
        layout.addWidget(nameLab)
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.setLayout(layout)

class attrBox(QWidget):
    def __init__(self):
        super().__init__()
        self.typeLayout={}
        self.typeNeed={}
        self.setupUi()
        pass
    def setupUi(self):
        layout=QHBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(10,5,10,5)
        nameLay=QVBoxLayout()
        nameLay.setSpacing(0)
        attrLay=QVBoxLayout()
        attrLay.setSpacing(0)
        layout.addLayout(nameLay)
        layout.addLayout(attrLay)
        self.nameLay=nameLay
        self.attrLay=attrLay

        self.setLayout(layout)
        self.setProperty("typename","")
        pass

    def getAttrWid(self,name,attrinfo):
        attrtype,value,isneed=attrinfo
        nameLabel=attrName(name,isneed)
        
        if typeAttrBox.get(attrtype)!=None:
            wid=typeAttrBox[attrtype](name,value,isneed)
        else:
            wid=QWidget()
            wid.setFixedHeight(50)
        nameLabel.setVisible(False);
        wid.setVisible(False)
        height=wid.height()
        nameLabel.setFixedHeight(height)
        return (nameLabel,wid),height

    def changeView(self,name,attr):
        if (self.property("name")!=None):
            for name_,attr_ in self.typeLayout.get(self.property("name"))[0]:
                self.nameLay.removeWidget(name_)
                self.attrLay.removeWidget(attr_)
                name_.setVisible(False)
                attr_.setVisible(False)
        self.setProperty("name",name)
        if self.typeLayout.get(name)!=None:
            self.setupLay(name)
            return
        
        view_attrInfos=[]
        height=0
        for attrname in attr:
            line,lineHeight=self.getAttrWid(attrname,attr[attrname])
            height+=lineHeight
            view_attrInfos.append(line)

        self.typeLayout[name]=(view_attrInfos,height)
        self.setupLay((view_attrInfos,height))

    def setupLay(self,attrInfos):
        if type(attrInfos)==str:
            attrs,maxheight=self.typeLayout[attrInfos]
        else:
            attrs,maxheight=attrInfos
        
        # while self.nameLay.count():
        #     self.nameLay.removeItem(self.nameLay.itemAt(0))
        # while self.attrLay.count():
        #     self.attrLay.removeItem(self.attrLay.itemAt(0))
        for name,attr in attrs:
            self.nameLay.addWidget(name)
            self.attrLay.addWidget(attr)
            name.setVisible(True)
            attr.setVisible(True)
        self.setFixedHeight(maxheight)

    def checkValue(self):
        attrs,_=self.typeLayout[self.property("name")]
        for _,attrbox in attrs:
            if attrbox.checkValue()==False:
                return False
        return True
    def getAttrValue(self):
        attrs,_=self.typeLayout[self.property("name")]
        
        result={}
        for _,attrbox in attrs:
            attrname,attrvalue=attrbox.getValue()
            result[attrname]=attrvalue
        return result
    
    def paintEvent(self, event):
        rect=self.rect()
        rect.setWidth(rect.width())
        rect.setHeight(rect.height())
        painter=QPainter(self)
        painter.fillRect(rect,QColor('#f8f8f8'))

class PathInput(QLineEdit):
    fillSig=Signal(QKeyEvent)
    def __init__(self,*args,**kargs):
        super().__init__(*args,**kargs)
    def keyPressEvent(self, arg__1: QKeyEvent) -> None:
        super().keyPressEvent(arg__1)
        #self.fillSig.emit(arg__1)
        
class PathWidget(QWidget):
    def __init__(self,*args,**kargs):
        super().__init__(*args,**kargs)
        self.setupUi()
    def setupUi(self):
        layout=QHBoxLayout()
        pathLab=QLabel("路径：")
        pathVal=QRegularExpressionValidator(QRegularExpression("\/?([a-zA-Z0-9_]+\/)*([a-zA-Z0-9_]+\/*)"))
        pathInput=PathInput()
        pathInput.setValidator(pathVal)
        pathInput.setPlaceholderText("/???/???/???")
        pathInput.textChanged.connect(self.fillPath)
        
        pathComp=QCompleter(pathInput)
        pathComp.setModel(QStringListModel())
        #pathComp.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        pathInput.setCompleter(pathComp)
        pathComp.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        #pathSel=QPushButton("...")
        #pathSel.setFixedWidth(30)

        layout.addWidget(pathLab)
        layout.addWidget(pathInput)
        #layout.addWidget(pathSel)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(5)
        self.pathVal=pathInput
        self.setLayout(layout)

    def fillPath(self,event):
        parentList,fileList=api.getChildNode(self.pathVal.text())
        origin=self.pathVal.completer().model().stringList()
        if parentList==origin:
            return
        
        self.pathVal.completer().setModel(QStringListModel(fileList))
    def setText(self,text):
        self.pathVal.setText(text)
    
    def text(self):
        return self.pathVal.text()

class nameWidget(QWidget):
    def __init__(self,*args,**kargs):
        super().__init__()
        self.setupUi()
    
    def setupUi(self):
        layout=QHBoxLayout()
        nameLab=QLabel("名称：")
        nameVal=QRegularExpressionValidator(QRegularExpression("[a-zA-Z0-9_]+"))
        nameInput=QLineEdit()
        nameInput.setValidator(nameVal)
        nameInput.setPlaceholderText("仅允许大小写字母数字下划线")
        layout.addWidget(nameLab)
        layout.addWidget(nameInput)
        layout.setSpacing(5)
        layout.setContentsMargins(0,0,0,0)
        self.nameInput=nameInput
        self.setLayout(layout)
    
    def text(self):
        return self.nameInput.text()
        pass
    def setText(self,text):
        return self.nameInput.setText(text)
    pass

class ChildWidget(QDialog):
    def __init__(self,path,name=None,*args,**kargs):
        super().__init__(*args,**kargs)
        self.setProperty("path",path)
        self.setProperty("name",name)
        self.setupUi()
        pass

    def setupUi(self):
        self.setFixedWidth(700)
        self.setWindowTitle("helper")
        self.setWindowIcon(api.application_ico)
        typenames=api.getTypeNames()
        typeSelLay=QHBoxLayout()
        typeSelLay.setAlignment(Qt.AlignmentFlag.AlignLeft)
        typeSelLab=QLabel("选择类型: ")
        type_sel=QComboBox()
        type_sel.setFixedHeight(30)
        type_sel.setFixedWidth(100)
        for name in typenames:
            type_sel.addItem(name)
        type_sel.currentTextChanged.connect(self.changeView)
        typeSelLay.addWidget(typeSelLab)
        typeSelLay.addWidget(type_sel)

        self.typeSel=type_sel

        infoLay=QHBoxLayout()
        nameVal=nameWidget()
        nameVal.setFixedHeight(30)
        self.nameVal=nameVal

        pathVal=PathWidget()
        pathVal.setFixedHeight(30)
        self.pathVal=pathVal
        infoLay.addWidget(nameVal)
        infoLay.addSpacing(20)
        infoLay.addWidget(pathVal)

        childattr=attrBox()
        self.childattr=childattr


        submit=QPushButton("确认")
        submit.setFixedWidth(50)
        submit.clicked.connect(self.Submit)
        infoLab=QLabel()
        infoLab.setStyleSheet("color: #ff0000;")
        self.infoLab=infoLab
        buttomLay=QHBoxLayout()
        buttomLay.addWidget(infoLab)
        buttomLay.addWidget(submit,0,Qt.AlignmentFlag.AlignRight)
        
        layout=QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(20,20,20,20)
        layout.addLayout(typeSelLay)
        layout.addLayout(infoLay)
        #layout.addWidget(type_sel,0,Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)
        layout.addWidget(self.childattr)
        layout.addLayout(buttomLay)
        self.setLayout(layout)
        self.initWidget()
        #self.changeView()

    def Submit(self):
        if self.childattr.checkValue()==False:
            self.infoLab.setText("请检查参数是否正确填写")
            return
        self.setProperty("Submit",True)
        self.close()
        pass

    def initWidget(self):
        path=self.property("path")
        self.pathVal.setText(path)
        if self.property("name")==None:
            self.changeView()
            return
        name=self.property("name")
        self.nameVal.setText(name)
        typeName,attrs=api.getAttrFromPath(path,name)
        
        if attrs==None:
            return

        self.typeSel.setCurrentText(typeName)
        self.childattr.changeView(typeName,attrs)
        size=self.childattr.size()
        size.setHeight(size.height()+140)
        size.setWidth(size.width()+40)
        self.setFixedSize(size)

    def changeView(self):
        name=self.typeSel.currentText()
        ind=self.typeSel.currentIndex()
        typeattr=api.getTypeAttrFromName(name)
        if typeattr==None:
            self.typeSel.removeItem(ind)
            self.typeSel.setCurrentIndex(0)
            self.changeView()
            return;
        else:
            self.childattr.changeView(name,typeattr)

        size=self.childattr.size()
        size.setHeight(size.height()+145)
        size.setWidth(size.width()+40)
        self.setFixedSize(size)
    
    def setInfo(self,infoStatus):
        if infoStatus==1:
            self.infoLab.setText("类型错误")
        elif infoStatus==2:
            self.infoLab.setText("名称存在重复，请更改名称")
        elif infoStatus==3:
            self.infoLab.setText("参数错误")
        pass

    def getValue(self,infoStatus):
        self.setProperty("Submit",False)
        if self.property("used")==True:
            self.setInfo(infoStatus)
        else:
            self.setProperty("used",True)
        self.exec_()
        if self.property("Submit")==False:
            return None
        childType=self.typeSel.currentText()
        name=self.nameVal.text()
        path=self.pathVal.text()
        childAttr=self.childattr.getAttrValue()
        return childType,name,path,childAttr

    @staticmethod
    def addChild(path,name):
        direPath=f"{path}/{name}"
        childWidget=ChildWidget(direPath)
        status=-1
        while status!=0:
            result=childWidget.getValue(status)
            if result==None:
                return
            status=api.addCheckChildInfo(*result)
    
    @staticmethod
    def attrSet(path,name):
        childWidget=ChildWidget(path,name)
        status=-1
        while status!=0:
            result=childWidget.getValue(status)
            if result==None:
                return
            status=api.changeCheckChildInfo(path,name,*result)

        pass

class MoveChild(QDialog):
    def __init__(self,path,name,*args,**kargs):
        super().__init__(*args,**kargs)
        self.setProperty("path",path)
        self.setProperty("name",name)
        self.setupUi()
    def setupUi(self):
        layout=QVBoxLayout()

        originLay=QHBoxLayout()
        nameLay=QHBoxLayout()
        nameLab=QLabel("原名称")
        originName=QLabel(self.property("name"))
        nameLay.addWidget(nameLab)
        nameLay.addWidget(originName)

        pathLay=QHBoxLayout()
        pathLab=QLabel("原路径")
        originPath=QLabel(self.property("path"))
        pathLay.addWidget(pathLab)
        pathLay.addWidget(originPath)
        originLay.addLayout(nameLay)
        originLay.addLayout(pathLay)
        
        infoMsg=QLabel()
        infoMsg.setStyleSheet("color: #ff0000;")
        self.info=infoMsg
        targetLay=QHBoxLayout()
        tnameLay=QHBoxLayout()
        tnameLab=QLabel("目的名称")
        targetName=QLineEdit(self.property("name"))
        tnameLay.addWidget(tnameLab)
        tnameLay.addWidget(targetName)

        tpathLay=QHBoxLayout()
        tpathLab=QLabel("目的路径")
        targetPath=PathWidget()
        targetPath.setText(self.property("path"))
        tpathLay.addWidget(tpathLab)
        tpathLay.addWidget(targetPath)
        targetLay.addLayout(tnameLay)
        targetLay.addLayout(tpathLay)
        self.tname=targetName
        self.tpath=targetPath
        
        submit=QPushButton("确定")
        submit.clicked.connect(lambda e:(self.setProperty("canary",False),self.close()))

        layout.addLayout(originLay)
        layout.addWidget(infoMsg,0,Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(targetLay)
        layout.addWidget(submit,0,Qt.AlignmentFlag.AlignRight)
        self.setLayout(layout)

        #self.rejected.connect(lambda :)
        pass
    def getValue(self):
        self.setProperty("canary",True)
        if self.property("used")==True:
            self.info.setText("请检查名称与路径是否合法，名称不允许重复")
        else:
            self.setProperty("used",True)
        self.exec_()
        if self.property("canary")==True:
            return None,None
        return self.tpath.text(),self.tname.text()

        pass
    @staticmethod
    def moveChild(path,name):
        if path=='':
            path='/'
        movechild=MoveChild(path,name)
        
        status=False
        while status==False:
            tpath,tname=movechild.getValue()
            if tname==None:
                return
            status=api.rename(path,name,tpath,tname)
            pass

class Groupname(QLabel):
    leftpress=Signal()
    def __init__(self,group,*args,**kargs):
        super().__init__(*args,**kargs)
        self.setProperty("name",group.name)
        self.setProperty("path",group.path)
        self.setText(group.name)
        self.leaveEvent(None)
        self.setMouseTracking(True)
        self.customContextMenuRequested.connect(self.customContext)

    def mouseReleaseEvent(self, ev:QMouseEvent):
        if ev.button()==Qt.MouseButton.LeftButton:
            if self.rect().contains(ev.pos()):
                self.leftpress.emit()
        
    def mousePressEvent(self, ev: QMouseEvent) -> None:
        if ev.button()==Qt.MouseButton.LeftButton:
            self.setProperty("Drag",0)
        return super().mousePressEvent(ev)
    
    def mouseMoveEvent(self,ev):
        if self.property("Drag")==0:
            self.setProperty("Drag",1)
            self.startDrag(Qt.DropAction.MoveAction)
    
    def startDrag(self,action):
        self.setProperty("Drag",False)
        mimedata=QMimeData()
        name=self.property("name")
        path=self.property("path")
        mimedata.setData("helper/object", f"{path},{name}".encode('utf-8'))
        #mimedata.setData("text/plain",self.property("name").encode())
        drag=QDrag(self)
        drag.setMimeData(mimedata)
        drag.setHotSpot(QPoint(drag.pixmap().width()//2,drag.pixmap().height()))
        #drag.setHotSpot(event.pos() - self.rect().topLeft())
        drag.exec(action,Qt.DropAction.MoveAction)
    
    def dropEvent(self, event: QDropEvent) -> None:
        
        self.parent().dropEvent(event)
        super().dropEvent(event)
        
    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasFormat("helper/object"):
            event.accept()
        return super().dragEnterEvent(event)
    
    def enterEvent(self, event):
        stylesheet="""
        background: #dddddd;"""
        self.setStyleSheet(stylesheet)

    def leaveEvent(self, event):
        stylesheet="""
        background: #cccccc;"""
        self.setStyleSheet(stylesheet)



    def customContext(self,pos):
        menu=QMenu()
        innode=QAction("进入节点",menu)
        innode.triggered.connect(self.Innode)
        rename=QAction("重命名",menu)
        rename.triggered.connect(self.Rename)
        addchild=QAction("添加节点",menu)
        addchild.triggered.connect(self.Addchild)
        remove=QAction("删除",menu)
        remove.triggered.connect(self.Remove)
        move=QAction("转移",menu)
        move.triggered.connect(self.Move)
        menu.addActions([innode,rename,addchild,move,remove])
        #menu.setStyleSheet("background: #ffffff;")
        menu.exec_(self.mapToGlobal(pos))
        self.menu=menu

    def Innode(self):
        api.Restore(self.property("path"),self.property("name"))
        pass

    def Rename(self):
        origin_name=self.property("name")
        path=self.property("path")
        RenameWidget.rename(origin_name,path,path)
            

    def Addchild(self):
        ChildWidget.addChild(self.property("path"),self.property("name"))
    
    def Remove(self):
        RemoveDialog.remove(self.property("path"),self.property("name"))
        pass

    def Move(self):
        MoveChild.moveChild(self.property("path"),self.property("name"))
        pass
    
class Obj(QWidget):
    def __init__(self,obj,*args,**kargs):
        super().__init__(*args,**kargs)
        self.setProperty("name",obj.name)
        self.setProperty("path",obj.path)
        self.setProperty("type",obj.type)
        self.setAcceptDrops(True)
        #self.setDragEnabled(True)
        self.setupUi()
    
    def setupUi(self):
        self.setFixedSize(60,80)
        icon=QLabel(self.property("name"))
        icon.setAcceptDrops(True)
        icon.setFixedHeight(60)
        icon.setStyleSheet("background: #ff0000;")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon=icon
        name=QLabel(self.property("name"))
        name.setAcceptDrops(True)
        name.setStyleSheet("background: #ffffdd;")
        name.setFixedHeight(20)
        name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout=QVBoxLayout()
        layout.addWidget(icon,0,Qt.AlignmentFlag.AlignTop)
        layout.addWidget(name,0,Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(0)
        layout.setContentsMargins(0,0,0,0)
        self.setLayout(layout)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.customContext)
        
    def paintEvent(self, event):
        rect=self.rect()
        rect.setWidth(rect.width()-1)
        rect.setHeight(rect.height()-1)
        painter=QPainter(self)
        painter.drawRect(rect)
    
    def mousePressEvent(self, event):
        if event.button()==Qt.MouseButton.LeftButton:
            self.setProperty("Drag",True)
        return super().mousePressEvent(event)

    def mouseReleaseEvent(self,event):
        if event.button()==Qt.MouseButton.LeftButton:
            self.setProperty("Drag",False)
        return super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event) -> None:
        if self.property("Drag")==True:
            self.setProperty("Drag",False)
            self.startDrag(Qt.DropAction.MoveAction)
        return super().mouseMoveEvent(event)
    
    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasFormat("helper/object"):
            event.accept()
        return super().dragEnterEvent(event)
    
    def dropEvent(self, event: QDropEvent) -> None:
        path,name=event.mimeData().data("helper/object").toStdString().split(',')
        api.rename(path,name,self.property("path"),name)
        return super().dropEvent(event)
    
    def startDrag(self,action):
        self.setProperty("Drag",False)
        mimedata=QMimeData()
        name=self.property("name")
        path=self.property("path")
        mimedata.setData("helper/object", f"{path},{name}".encode('utf-8'))
        #mimedata.setData("text/plain",self.property("name").encode())
        drag=QDrag(self)
        drag.setMimeData(mimedata)
        drag.setHotSpot(QPoint(drag.pixmap().width()//2,drag.pixmap().height()))
        #drag.setHotSpot(event.pos() - self.rect().topLeft())
        drag.exec(action,Qt.DropAction.MoveAction)

        pass
    def customContext(self, pos) -> None:
        menu=QMenu(self)
        rename=QAction("重命名",menu)
        rename.triggered.connect(self.Rename)
        attrset=QAction("属性设置",menu)
        attrset.triggered.connect(self.Attrset)
        move=QAction("转移",menu)
        move.triggered.connect(self.Move)
        remove=QAction("删除",menu)
        remove.triggered.connect(self.Remove)
        menu.addActions([rename,attrset,move,remove])
        menu.exec_(self.mapToGlobal(pos))

    def Rename(self):
        origin_name=self.property("name")
        path=self.property("path")
        RenameWidget.rename(origin_name,path,path)

    def Remove(self):
        RemoveDialog.remove(self.property("path"),self.property("name"))
    
    def Attrset(self):
        ChildWidget.attrSet(self.property("path"),self.property("name"))
        pass

    def Move(self):
        MoveChild.moveChild(self.property("path"),self.property("name"))

class ChildGroup(QLabel):
    def __init__(self,group,*args,**kargs):
        
        super().__init__(*args,**kargs)
        self.setProperty("name",group.name)
        self.setProperty("path",group.path)
        self.setAcceptDrops(True)
        self.leaveEvent(None)
        self.setMouseTracking(True)
        self.setupUi()
        
    def setupUi(self):
        self.setFixedHeight(30)
        self.setText(self.property("name"))
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.customContext)
        pass

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        if event.button()==Qt.MouseButton.LeftButton:
            api.Restore(self.property("path"),self.property("name"))
        # return super().mouseDoubleClickEvent(event)
        return None;
    
    def mousePressEvent(self, ev: QMouseEvent) -> None:
        if ev.button()==Qt.MouseButton.LeftButton:
            self.setProperty("Drag",True)
        return super().mousePressEvent(ev)
    
    def mouseReleaseEvent(self, ev: QMouseEvent) -> None:
        if ev.button()==Qt.MouseButton.LeftButton:
            self.setProperty("Drag",False)
        return super().mouseReleaseEvent(ev)
    
    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        p_event=QMouseEvent(QEvent.Type.MouseMove,event.localPos(),event.button(),event.buttons(),event.modifiers(),event.device())
        self.parent().mouseMoveEvent(p_event)
        
        if self.property("Drag")==True:
            self.setProperty("Drag",False)
            self.startDrag(Qt.DropAction.MoveAction)
        return super().mouseMoveEvent(event)
    
    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasFormat("helper/object"):
            event.accept()
        return super().dragEnterEvent(event)
    
    def dropEvent(self, event: QDropEvent) -> None:
        path,name=event.mimeData().data("helper/object").toStdString().split(',')
        tp=self.property("path")
        tn=self.property("name")
        api.rename(path,name,f"{tp}/{tn}",name)
        super().dropEvent(event)
    def startDrag(self,action):
        self.setProperty("Drag",False)
        mimedata=QMimeData()
        name=self.property("name")
        path=self.property("path")
        mimedata.setData("helper/object", f"{path},{name}".encode('utf-8'))
        #mimedata.setData("text/plain",self.property("name").encode())
        drag=QDrag(self)
        drag.setMimeData(mimedata)
        #drag.setPixmap(self.icon.pixmap())
        drag.setHotSpot(QPoint(drag.pixmap().width()//2,drag.pixmap().height()))
        #drag.setHotSpot(event.pos() - self.rect().topLeft())
        drag.exec(action,Qt.DropAction.MoveAction)

    def enterEvent(self, event):
        stylesheet="""
        background: #dddddd;"""
        self.setStyleSheet(stylesheet)
    
    def leaveEvent(self, event):
        stylesheet="""
        background: #cccccc;"""
        self.setStyleSheet(stylesheet)

    def customContext(self,pos):
        menu=QMenu()
        #menu.setStyleSheet("background: #cccccc")
        innode=QAction("进入节点",menu)
        innode.triggered.connect(self.Innode)
        rename=QAction("重命名",menu)
        rename.triggered.connect(self.Rename)
        addchild=QAction("添加子节点",menu)
        addchild.triggered.connect(self.Addchild)
        move=QAction("转移",menu)
        move.triggered.connect(self.Move)
        remove=QAction("删除",menu)
        remove.triggered.connect(self.Remove)
        menu.addActions([innode,rename,addchild,move,remove])
        menu.exec_(self.mapToGlobal(pos))
        self.menu=menu
    
    def Innode(self):
        api.Restore(self.property("path"),self.property("name"))
        pass
    def Rename(self):
        origin_name=self.property("name")
        path=self.property("path")
        RenameWidget.rename(origin_name,path,path)

    def Addchild(self):
        ChildWidget.addChild(self.property("path"),self.property("name"))

    def Remove(self):
        RemoveDialog.remove(self.property("path"),self.property("name"))
    
    def Move(self):
        MoveChild.moveChild(self.property("path"),self.property("name"))

class Objbox(QWidget):
    def __init__(self,childs,*args,**kargs):
        super().__init__(*args,**kargs)
        self.setProperty("childs",childs)
        self.setupUi()
        
    def setupUi(self):
        self.setAcceptDrops(True)
        self.setMouseTracking(True)
        
        layout=QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(4,5,5,5)
        self.setLayout(layout)
        self.initBox()
        self.setBox()
        self.setProperty("Currwidth",self.width())
        

    def paintEvent(self, event):
        rect=self.rect()
        rect.setWidth(rect.width()-3)
        rect.setHeight(rect.height()-1)
        painter=QPainter(self)
        painter.fillRect(rect,QColor('#ddddff'))
        painter.drawRect(rect)

    def resizeEvent(self, event) -> None:
        
        self.setBox()

        return super().resizeEvent(event)
        
    #def mouseMoveEvent(self, event: QMouseEvent) -> None:
    #    p_event=QMouseEvent(QEvent.Type.MouseMove,event.localPos(),event.button(),event.buttons(),event.modifiers(),event.device())
    #    self.parent().mouseMoveEvent(p_event)
    #    return super().mouseMoveEvent(event)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasFormat("helper/object"):
            event.accept()
        return super().dragEnterEvent(event)

    def dropEvent(self, event: QDropEvent) -> None:
        self.parent().parent().parent().dropEvent(event)
        return super().dropEvent(event)
    
    def clearBox(self):
        
        while self.layout().count():
            self.layout().removeItem(self.layout().itemAt(0))

    def initBox(self):
        
        nodes=[]
        objs=[]
        obj_width=0
        obj_height=0
        node_height=0
        for i in self.property("childs"):
            if i.type in api.Node_type:
                node=ChildGroup(i,self)
                node_height=node.height()
                nodes.append(node)
            else:
                obj=Obj(i,self)
                obj_width=obj.width()
                obj_height=obj.height()
                objs.append(obj)
        
        self.setProperty("objs",objs)
        self.setProperty("objwidth",obj_width)
        self.setProperty("objheight",obj_height)
        self.setProperty("nodes",nodes)
        self.setProperty("nodeheight",node_height)

    def set_objarea(self,layout,objwidth):
        boxwidth=self.width()-5
        spacing=objwidth-1
        row_obj_num=boxwidth//objwidth
        while row_obj_num*(objwidth+spacing)>boxwidth:
            spacing-=1
            if spacing<=2:
                spacing=objwidth-1
                row_obj_num=row_obj_num-1
            

        objs=self.property("objs")
        
        hbox_len=(len(objs)+row_obj_num-1)//row_obj_num
        objarea_hei=hbox_len*(self.property("objheight")+5)
        
        hbox_left=(boxwidth-row_obj_num*(objwidth+spacing)+spacing-5)//2
        if hbox_left<0:
            hbox_left=0


        hbox=QHBoxLayout()
        
        hbox.setSpacing(spacing)
        hbox.setContentsMargins(hbox_left,0,0,0)
        hbox.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        for obj in objs:
            hbox.addWidget(obj)

            if hbox.count() >=row_obj_num:
                    layout.addLayout(hbox,0)
                    hbox=QHBoxLayout()
                    hbox.setSpacing(spacing)
                    hbox.setContentsMargins(hbox_left,0,0,0)
                    hbox.setAlignment(Qt.AlignmentFlag.AlignLeft)
        if hbox.count()!=0:
            layout.addLayout(hbox,0)
        return objarea_hei

    def setBox(self):
        self.clearBox()
        maxheight=10

        layout=self.layout()
        
        nodes=self.property("nodes")
        
        objwidth=self.property("objwidth")
        if objwidth!=0:
            maxheight+=self.set_objarea(layout,objwidth)
        

        maxheight+=len(nodes)*(self.property("nodeheight")+5)

        for node in nodes:
            #maxheight+=node.height()+5
            layout.addWidget(node,0)
        if maxheight<50:
            maxheight=50
        self.setFixedHeight(maxheight)
        self.setProperty("maxheight",maxheight+2)

class boxScroll(QScrollArea):
    def __init__(self,*args,**kargs):
        super().__init__(*args,**kargs)
        self.setMouseTracking(True)
    
    def resizeEvent(self, arg__1) -> None:
        width=self.width()
        if width!=self.widget().width():
            self.widget().setFixedWidth(width)
        return super().resizeEvent(arg__1)
        pass
    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        p_event=QMouseEvent(QEvent.Type.MouseMove,event.localPos(),event.button(),event.buttons(),event.modifiers(),event.device())
        self.parent().mouseMoveEvent(p_event)
        return super().mouseMoveEvent(event)
    
    def wheelEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            event.ignore()  # 忽略中键滚动事件，阻止其向上传递到上层控件
        else:
            super().wheelEvent(event)
    def dropEvent(self, event: QDropEvent) -> None:
        self.parent().dropEvent(event)
        return super().dropEvent(event)
        
class ObjGroup(QWidget):
    def __init__(self,group,*args,**kargs):
        super().__init__(*args,**kargs)
        self.setProperty("name",group.name)
        self.setProperty("path",group.path)
        self.setProperty("group",group)
        self.setProperty("isexpend",False)
        self.setAttribute(Qt.WidgetAttribute.WA_StaticContents)
        self.setupUi()
        pass

    def setupUi(self):
        self.setFixedHeight(27)
        self.setAcceptDrops(True)
        self.setMouseTracking(True)
        self.setSizePolicy(QSizePolicy.Policy.Ignored,QSizePolicy.Policy.Expanding)
        self.setupStyle()
        label_name=Groupname(self.property("group"))
        label_name.setProperty("class","group_name")
        label_name.setFixedHeight(25)
        label_name.leftpress.connect(self.expend)
        label_name.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.name=label_name
        box=Objbox(self.property("group").childs)
        self.setProperty("group",None)
        box.setProperty("isexpent",False)

        box_s=boxScroll()
        box_s.setWidget(box)
        box_s.setFixedHeight(0)
        box_s.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        box_s.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        box_s.hide()

        layout=QVBoxLayout()
        layout.addWidget(label_name,0,Qt.AlignmentFlag.AlignTop)
        layout.addWidget(box_s,0,Qt.AlignmentFlag.AlignBottom)
        self.box=box
        self.box_s=box_s
        

        layout.setSpacing(0)
        layout.setContentsMargins(1,1,1,1)
        self.setLayout(layout)
        
    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasFormat("helper/object"):
            event.accept()
        return super().dragEnterEvent(event)
    def setupStyle(self):
        
        stylesheet="""
        """
        self.setStyleSheet(stylesheet)
    
    def paintEvent(self, event):

        super().paintEvent(event)
        rect=self.rect()
        rect.setWidth(rect.width()-1)
        rect.setHeight(rect.height()-1)
        painter=QPainter(self)
        
        painter.fillRect(rect,QColor('#dddddd'))
        painter.drawRect(rect)
    
    def dropEvent(self, event: QDropEvent) -> None:
        path,name=event.mimeData().data("helper/object").toStdString().split(',')
        tp=self.property("path")
        tn=self.property("name")
        api.rename(path,name,f"{tp}/{tn}",name)
        return super().dropEvent(event)

    def expend(self,beforeExp=True):
        
        isexpend=self.property("isexpend")
        # if self.property("animation")!=None:
        #     self.property("animation").stop()
        #     self.property("animation").setParent(None)
        #     self.setProperty("animation",None)

        if isexpend==False:
            self.box_s.show()
            start=self.name.height()
            end=start+self.box.property("maxheight")+2
            # box_start=self.box_s.height()
            box_end=self.box.property("maxheight")
            self.box_s.setFixedHeight(box_end)
            # box_dur=300
            # me_dur=250


        elif isexpend==True:
            # start=self.height()
            end=self.name.height()+2
            # box_start=self.box.height()
            box_end=0
            self.box_s.hide();
            
            # box_dur=250
            # me_dur=300
        
        self.setProperty("isexpend",not isexpend)
        api.changeExpBox(self.property("name"),not isexpend)
        self.setFixedHeight(end)
        self.box_s.setFixedHeight(box_end)
        # if beforeExp:
        #     self.setFixedHeight(end)
        #     self.box_s.setFixedHeight(box_end)
        #     return
        
        # anigroup=QParallelAnimationGroup(self)
        # minani=QParallelAnimationGroup()
        # maxani=QParallelAnimationGroup()
        # min=QPropertyAnimation(self,b"minimumHeight")
        # min.setDuration(me_dur)
        # min.setStartValue(start)
        # min.setEndValue(end)
        
        # boxmin=QPropertyAnimation(self.box_s,b"minimumHeight")
        # boxmin.setDuration(box_dur)
        # boxmin.setStartValue(box_start)
        # boxmin.setEndValue(box_end)

        # max=QPropertyAnimation(self,b"maximumHeight")
        # max.setDuration(me_dur)
        # max.setStartValue(start)
        # max.setEndValue(end)

        # boxmax=QPropertyAnimation(self.box_s,b"maximumHeight")
        # boxmax.setDuration(box_dur)
        # boxmax.setStartValue(box_start)
        # boxmax.setEndValue(box_end)
        
        # minani.addAnimation(min)
        # minani.addAnimation(boxmin)
        
        # maxani.addAnimation(max)
        # maxani.addAnimation(boxmax)

        # anigroup.addAnimation(minani)
        # anigroup.addAnimation(maxani)
        
        # def finished():
        #     self.setProperty("animation",None)
        #     if isexpend==True:
        #         self.box_s.hide()
        #         #self.box_s.setFixedHeight(0)

        # anigroup.finished.connect(finished)
        # anigroup.start()
        
        # self.setProperty("animation",anigroup)

    def resizeEvent(self,event):
        if self.property("isexpend")==True and self.property("animation")==None:
            height=self.name.height()+self.box.property("maxheight")+2
            self.box_s.setFixedHeight(self.box.property("maxheight"))
            self.setFixedHeight(height)
        return super().resizeEvent(event)
    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button()==Qt.MouseButton.MiddleButton:
            api.Restore(self.property("path"),self.property("name"))
        # return super().mouseDoubleClickEvent(event)
        return None;
class Body(QWidget):
    def __init__(self,*args,**kargs):
        super().__init__(*args,**kargs)
        self.setupUi()
    
    def setupUi(self):
        self.setAcceptDrops(True)
        self.setMouseTracking(True)
        layout=QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(3)
        layout.setContentsMargins(0,5,0,0)
        self.setLayout(layout)
        self.setProperty("currwidth",self.width())
        self.setupStyle()
    
    def setupStyle(self):
        self.setStyleSheet("Body{background: ;}")
        
    def paintEvent(self,event):
        painter=QPainter(self)
        painter.fillRect(self.rect(),QColor('#b0b0b0'))
        pass

    def UnsetObj(self):
        while self.layout().count():
            item=self.layout().itemAt(0)
            if item.layout()!=None:
                self.layout().removeItem(item)

    def ClearChild(self):
        while self.layout().count():
            self.layout().removeItem(self.layout().itemAt(0))

        for child in self.children():
            
            if child!=self.layout():
                child.setParent(None)

    def resizeEvent(self, event: QResizeEvent) -> None:
        if event.size().width() != self.property("currwidth"):
            self.showObj()
        return super().resizeEvent(event)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasFormat("helper/object"):
            event.accept()
        return super().dragEnterEvent(event)
    
    def dropEvent(self, event: QDropEvent) -> None:
        path,name=event.mimeData().data('helper/object').toStdString().split(',')
        tp,tn=api.curr_path
        api.rename(path,name,f"{tp}/{tn}",name)
        return super().dropEvent(event)
    
    def showObj(self):
        objwidth=self.property("objwidth")
        if objwidth<=0:
            return
        objs=self.property("objs")
        spacing=objwidth-1
        row_obj_num=self.width()//objwidth
        while row_obj_num*(objwidth+spacing)>self.width():
            spacing-=1
            if spacing<=2:
                spacing=objwidth-1
                row_obj_num=row_obj_num-1
        if row_obj_num>len(objs):
            spacing=self.width()-len(objs)*(objwidth+5)
        hbox_left=(self.width()-row_obj_num*(objwidth+spacing)+spacing)//2
        if len(objs)<row_obj_num:
            hbox_left=10
            spacing=objwidth//len(objs)

        hbox=QHBoxLayout()
        hbox.setSpacing(spacing)
        hbox.setContentsMargins(hbox_left,0,0,0)
        hbox.setAlignment(Qt.AlignmentFlag.AlignLeft)
        linenum=0
        for obj in objs:
            hbox.addWidget(obj)
            if hbox.count() >=row_obj_num:
                    self.layout().insertLayout(linenum,hbox,0)
                    linenum+=1
                    hbox=QHBoxLayout()
                    hbox.setSpacing(spacing)
                    hbox.setContentsMargins(hbox_left,0,0,0)
                    hbox.setAlignment(Qt.AlignmentFlag.AlignLeft)
        if hbox.count()!=0:
            self.layout().insertLayout(linenum,hbox,0)

    def BuildLayout(self,childs):
        self.ClearChild()
        nodes=[]
        objs=[]
        objwidth=0
        for child in childs:
            # print(child.type,api.Node_type)
            if child.type in api.Node_type:
                isExpend=(child.name in api.expendBox)
                node=ObjGroup(child,self)
                if isExpend:
                    node.expend(isExpend)
                nodes.append(node)
            else:
                obj=Obj(child,self)
                objwidth=obj.width()
                objs.append(obj)
        self.setProperty("objwidth",objwidth)
        self.setProperty("objs",objs)
        for node in nodes:
            self.layout().addWidget(node,0,Qt.AlignmentFlag.AlignTop)
        self.showObj()
