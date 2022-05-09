# -*- coding: utf-8 -*-

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QWidget, QHBoxLayout
from PyQt5.QtGui import QPixmap, QPainter
import time
import json
import socket
import os
import threading

from attr import attr


thread_flag1 = False

class CommonHelper:
    def __init__(self):
        self.readQss()

    def readQss(style):
        with open(style, 'r') as f:
            return f.read()


class Widget(QWidget):
    def __init__(self): 
        super().__init__() 
        self.host='180.76.159.181'
        self.port=9999
        self.server = (self.host, self.port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.stop = True

        self.resize(363, 600)
        self.setFixedSize(self.width(), self.height())
        self.setWindowTitle("CQ")
        self.qss_path = './style.qss'
        self.qssStyle = CommonHelper.readQss(self.qss_path)

    def send(self, message):
        data = json.dumps(message).encode('utf-8')
        print(data)
        self.socket.sendto(data, self.server)

    def send_now(self, message, timeout = 5, need_timeout = True):
        socket.setdefaulttimeout(5) #设置连接超时
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #新建局部socket，单次通信使用
        data = json.dumps(message).encode('utf-8')
        print(data)
        sock.sendto(data, self.server)

        if need_timeout: sock.settimeout(timeout) #设置接收消息超时
        data = sock.recv(1024)
        with open('./data/recv.log', 'a+', encoding='utf-8') as fp:
            fp.write(data.decode('utf-8')+"\n")
            print(str(data,'utf-8'))
        sock.close()
        return str(data,'utf-8')

    def now_time(self):
        return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

    def recv(self):
        # sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        message= {'Attributes': 'start', 'time': time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))}
        data = json.dumps(message).encode('utf-8')
        print(str(data)+ '     recv')
        self.socket.sendto(data, self.server)
        with open('./data/recv.log', 'a+', encoding='utf-8') as fp:
                fp.write("现在开始监听, %s"%time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+"\n")
        while True:
            data = self.socket.recv(1024)
            if str(data, 'utf-8').split(' ')[0] == 'friendreply': 
                i = {"Attributes": "person", "time": self.now_time(), "userId": str(data, 'utf-8').split(' ')[1], "userIco": "./data/userIco/default.png"}
                with open('./data/friend.txt', 'a+', encoding='utf-8') as fp:
                    fp.write(json.dumps(i)+'\n')
                with open('./data/chat_friend.txt', 'a+', encoding='utf-8') as fp:
                    fp.write(json.dumps(i)+'\n')

            try: 
                dic = eval(str(data, 'utf-8'))
                if dic['Attributes'] == 'add_friend':
                    path = './data/new_friend.txt'
                    if not os.path.exists(path): open(path, 'w+', encoding='utf-8')
                    with open(path, 'a+', encoding='utf-8') as fp:
                        fp.write(str(data, 'utf-8')+"\n")
                        print(str(data, 'utf-8')+"       add_friend")
                if dic['Attributes'] == 'message':
                    if dic['mes_attrib'] == 'person':
                        path = './data/mes/%s.txt'%dic['userId']
                    else:
                        path = './data/mes/%s.txt'%dic['friend']
                    with open(path, 'a+', encoding='utf-8') as fp:
                        fp.write(str(data, 'utf-8')+"\n")
                        print(str(data, 'utf-8')+"       message")
                if dic['Attributes'] == 'create_group':
                    path1 = './data/group.txt'
                    path2 = './data/chat_friend.txt'
                    path3 = './data/new_group.txt'
                    if not os.path.exists(path3): open(path, 'w+', encoding='utf-8')
                    with open(path1, 'a+', encoding='utf-8') as fp:
                        fp.write(str(data, 'utf-8')+"\n")
                        print(str(data, 'utf-8')+"       create_group")
                    with open(path2, 'a+', encoding='utf-8') as fp:
                        fp.write(str(data, 'utf-8')+"\n")
                    with open(path3, 'a+', encoding='utf-8') as fp:
                        fp.write(str(data, 'utf-8')+"\n")
                        # print(str(data, 'utf-8')+"       create_group")
            except: pass

            with open('./data/recv.log', 'a+', encoding='utf-8') as fp:
                fp.write(data.decode('utf-8')+"\n\n\n")
                print(str(data, 'utf-8')+"       recv")

    def hint(self, widget, Hint = '提示', content = ''):
        QtWidgets.QMessageBox.about(widget, Hint, content)


class Login(Widget):
    def __init__(self):
        super().__init__() 
        self.new()

    def __init__(self, userName):
        super().__init__() 
        self.new()
        if userName != 0: 
            self.user.setText(userName)
            self.password.setFocus()

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None: 
        painter = QPainter(self)
        pixmap = QPixmap("./image/background.jpg")
        painter.drawPixmap(self.rect(), pixmap)

    def new(self):
        # self.qss_path = './style.qss'
        # self.qssStyle = CommonHelper.readQss(self.qss_path)
        # self.setObjectName("Widget")
        # self.setStyleSheet(self.qssStyle)

        self.enroll_btn = QtWidgets.QPushButton(self)
        self.enroll_btn.setText("注册")
        self.enroll_btn.setGeometry(QtCore.QRect(313, 540, 60, 29))
        self.enroll_btn.setObjectName("enroll_btn")
        self.enroll_btn.setStyleSheet(self.qssStyle)
        self.enroll_btn.clicked.connect(self.open_enroll)

        self.email_btn = QtWidgets.QPushButton(self)
        self.email_btn.setText("邮箱登录")
        self.email_btn.setGeometry(QtCore.QRect(220, 540, 93, 29))
        self.email_btn.setObjectName("enroll_btn")
        self.email_btn.setStyleSheet(self.qssStyle)
        self.email_btn.clicked.connect(self.click_email_btn)

        self.user = QtWidgets.QLineEdit(self)
        self.user.setPlaceholderText("用户名")
        self.user.setGeometry(QtCore.QRect(60, 210, 241, 31))
        self.user.setObjectName("user")
        self.user.setFocus()
        self.user.setStyleSheet(self.qssStyle)
        self.user.setMaxLength(5)

        self.password = QtWidgets.QLineEdit(self)
        self.password.setPlaceholderText("密码")
        self.password.setGeometry(QtCore.QRect(60, 290, 241, 31))
        self.password.setFrame(True)
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password.setObjectName("user")
        self.password.setStyleSheet(self.qssStyle)
        self.password.setMaxLength(12)

        self.login_btn = QtWidgets.QPushButton(self)
        self.login_btn.setText("登录")
        self.login_btn.setGeometry(QtCore.QRect(120, 370, 121, 121))
        self.login_btn.setAutoDefault(False)
        self.login_btn.setDefault(False)
        self.login_btn.setFlat(False)
        self.login_btn.setObjectName("login_btn")
        self.login_btn.setStyleSheet(self.qssStyle)
        self.login_btn.clicked.connect(self.open_home)

        self.avatar = QtWidgets.QLabel(self)
        self.avatar.setGeometry(QtCore.QRect(120, 50, 111, 101))
        self.avatar.setAlignment(QtCore.Qt.AlignCenter)
        self.avatar.setWordWrap(False)
        self.avatar.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse)
        self.avatar.setObjectName("avatar")
        self.avatar.setStyleSheet(self.qssStyle)
        self.avatar.setToolTip("用户头像")

    def open_enroll(self):
        self.enroll = Enroll()
        self.enroll.show()
        # self.enroll.socket = self.socket
        self.close()

    def open_home(self):
        #检测输入数据合法
        if self.user.text() == '':
            QtWidgets.QMessageBox.about(self, u'提示', u"用户名不能为空!")
            return
        if self.email_btn.text() == "邮箱登录" and self.password.text() == '':
            QtWidgets.QMessageBox.about(self, u'提示', u"密码不能为空!")
            return

        

        #构造登录数据
        Attributes = {"邮箱登录": "login_with_password", "密码登录": "login_with_email"}
        send_data = {"Attributes": Attributes[self.email_btn.text()], "time": time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())), 
                        "userId": self.user.text(), "password": self.password.text()}

        # QtCore.qDebug(json.dumps(send_data))
        
        if self.email_btn.text() == "邮箱登录": status_code = self.send_now(send_data)
        else: status_code = self.send_now(send_data, need_timeout=False)

        if status_code == 'Login success': 
            #存储用户信息
            userName = self.user.text()
            #打开聊天主页
            self.mess = Message(userName)
            self.mess.show()
            self.close()
        else:
            QtWidgets.QMessageBox.about(self, u'提示', status_code)

    def click_email_btn(self):
        if self.email_btn.text() == '邮箱登录':
            self.password.setText('')
            self.password.setEchoMode(QtWidgets.QLineEdit.Normal)
            self.password.setMaxLength(6)
            #self.password.setValidator(QtGui.QIntValidator())
            self.password.setPlaceholderText("验证码")
            self.email_btn.setText('密码登录')
        else:
            self.password.setText('')
            self.password.setEchoMode(QtWidgets.QLineEdit.Password)
            self.password.setPlaceholderText("密码")
            self.password.setMaxLength(12)
            self.email_btn.setText('邮箱登录')
        self.user.setFocus()




class Enroll(Login):
    def __init__(self):
        super().__init__(0) 
        self.new()

    def new(self):
        self.user = QtWidgets.QLineEdit(self)
        self.user.setGeometry(QtCore.QRect(60, 130, 241, 31))
        self.user.setObjectName("user")
        self.user.setStyleSheet(self.qssStyle)
        self.user.setFocus()
        self.user.setPlaceholderText("用户名")
        self.user.setMaxLength(5)

        self.email = QtWidgets.QLineEdit(self)
        self.email.setGeometry(QtCore.QRect(60, 210, 241, 31))
        self.email.setObjectName("user")
        self.email.setStyleSheet(self.qssStyle)
        self.email.setPlaceholderText("邮箱")
        my_regex = QtCore.QRegExp("^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$")
        my_validator = QtGui.QRegExpValidator(my_regex, self.email)
        self.email.setValidator(my_validator)

        self.password = QtWidgets.QLineEdit(self)
        self.password.setGeometry(QtCore.QRect(60, 290, 241, 31))
        self.password.setFrame(True)
        #self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password.setObjectName("user")
        self.password.setStyleSheet(self.qssStyle)
        self.password.setPlaceholderText("密码")
        self.password.setMaxLength(12)

        # self.ver_code = QtWidgets.QLineEdit(self)
        # self.ver_code.setGeometry(QtCore.QRect(60, 290, 241, 31))
        # self.ver_code.setFrame(True)
        # self.ver_code.setObjectName("user")
        # self.ver_code.setStyleSheet(self.qssStyle)
        # self.ver_code.setPlaceholderText("验证码")
        # self.ver_code.setMaxLength(6)
        # self.ver_code.setValidator(QtGui.QIntValidator())

        self.enroll_btn = QtWidgets.QPushButton(self)
        self.enroll_btn.setText("注册")
        self.enroll_btn.setGeometry(QtCore.QRect(120, 370, 121, 121))
        self.enroll_btn.setAutoDefault(False)
        self.enroll_btn.setDefault(False)
        self.enroll_btn.setFlat(False)
        self.enroll_btn.setObjectName("login_btn") #还是重用登录按钮的效果
        self.enroll_btn.setStyleSheet(self.qssStyle)
        self.enroll_btn.clicked.connect(self.click_enroll_btn)

    def click_enroll_btn(self):
        #检测输入数据合法
        if self.user.text() == '':
            QtWidgets.QMessageBox.about(self, u'提示', u"用户名不能为空!")
            return
        if self.email.text() == '':
            QtWidgets.QMessageBox.about(self, u'提示', u"邮箱不能为空!")
            return
        if self.password.text() == '':
            QtWidgets.QMessageBox.about(self, u'提示', u"密码不能为空!")
            return

        #构造注册数据
        send_data = {"Attributes": 'enroll', "time": time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())), 
                        "userId": self.user.text(), "email": self.email.text(), "password": self.password.text()}

        #send_data = json.dumps(send_data)
        # QtCore.qDebug(json.dumps(send_data))
        status_code = self.send_now(send_data)

        if status_code == 'succeed in registration': 
            QtWidgets.QMessageBox.about(self, u'提示', u"注册成功!")
            #返回登录页面
            self.login = Login(0)
            self.login.show()
            self.close()
        else:
            QtWidgets.QMessageBox.about(self, u'提示', "用户已存在！")


class Chat(Widget):
    mySignal_1 = QtCore.pyqtSignal()

    def __init__(self, object, last_widget):
        super().__init__() 
        self.myName = 'Chat'
        self.userName = last_widget.userName
        self.object = object
        self.last_widget = last_widget

        self.mySignal_1.connect(self.update)

        self.new()

    def new(self):
        global thread_flag1
        thread_flag1 = False
        self.topTitle = QtWidgets.QWidget(self)
        self.topTitle.setGeometry(QtCore.QRect(0, 0, 363, 40))
        self.topTitle.setObjectName("topTitle")
        self.topTitle.setStyleSheet(self.qssStyle)

        self.reback_btn = QtWidgets.QPushButton(self.topTitle)
        self.reback_btn.setGeometry(QtCore.QRect(0, 0, 30, 40))
        self.reback_btn.setText("<")
        self.reback_btn.setObjectName('add_btn')
        self.reback_btn.setStyleSheet(self.qssStyle)
        self.reback_btn.clicked.connect(self.click_reback_btn)

        self.title = QtWidgets.QLabel(self.topTitle)
        self.title.setGeometry(QtCore.QRect(150, 0, 60, 40))
        self.title.setText(self.object)
        self.title.setObjectName("titleText")
        self.title.setStyleSheet(self.qssStyle)

        self.tool_btn = QtWidgets.QPushButton(self.topTitle)
        self.tool_btn.setGeometry(QtCore.QRect(333, 5, 30, 30))
        self.tool_btn.setObjectName("tool_btn")
        self.tool_btn.setStyleSheet(self.qssStyle)

        self.wid = QtWidgets.QWidget(self)
        self.wid.setGeometry(QtCore.QRect(-13, 40, 420, 530))

        self.content = QtWidgets.QWidget(self)
        self.content.setMinimumSize(363, 1000)
        #self.content.setGeometry(QtCore.QRect(0, 0, 363, 515))

        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setWidget(self.content)
        self.scroll.verticalScrollBar().setValue(530)

        self.vbox = QtWidgets.QVBoxLayout()
        self.vbox.addWidget(self.scroll)
        self.wid.setLayout(self.vbox)

        self.mail = QtWidgets.QLineEdit(self)
        self.mail.setGeometry(QtCore.QRect(4, 560, 300, 35))
        self.mail.setObjectName("mail_input")
        self.mail.setStyleSheet(self.qssStyle)

        self.send = QtWidgets.QPushButton(self)
        self.send.setGeometry(QtCore.QRect(308, 560, 50, 35))
        self.send.setText("发送")
        self.send.setObjectName("send")
        self.send.setStyleSheet(self.qssStyle)
        self.send.clicked.connect(self.click_send_btn)

        self.show_mess()
        self.tr = threading.Thread(target=self.mes_update, args=(), daemon=True)
        self.tr.start()

    def show_mess(self):
        self.messages = Show_Inf('message', self)
        self.messages.setParent(self.content)
        self.messages.setGeometry(QtCore.QRect(2, 0, 361, 400))

    def click_reback_btn(self):
        global thread_flag1 
        thread_flag1 = True
        if self.last_widget.myName == 'Message':
            self.mess = Message(self.last_widget.userName)
            self.mess.show()
            self.close()
        else:
            self.mess = Contact(self.last_widget.userName)
            if not self.last_widget.now: self.mess.chosed(False)
            self.mess.show()
            self.close()

    def click_send_btn(self):
        #获取消息内容+目标对象
        #构造消息数据
        send_data = {"Attributes": 'message', "time": time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())), 
                        "userId": self.userName, "friend": self.object, "mes_attrib": "people", "mes_content": self.mail.text()}

        #更新聊天界面消息显示
        # QtCore.qDebug(json.dumps(send_data))
        status_code = self.send_now(send_data, need_timeout=False)
        if status_code == 'private message sent': 
            self.mail.setText('')
            #存消息记录
            with open('./data/mes/%s.txt'%self.object, 'a+', encoding='utf-8') as fp:
                fp.write(json.dumps(send_data)+'\n')
            self.messages.close()
            self.messages = Show_Inf('message', self)
            self.messages.setParent(self.content)
            self.messages.setGeometry(QtCore.QRect(2, 0, 361, 400))
            self.messages.show()
        else:
            #显示发送失败
            QtWidgets.QMessageBox.about(self, u'提示', u"发送失败!")
        
    def update(self):
        print('----------')
        self.messages.close()
        self.messages = Show_Inf('message', self)
        self.messages.setParent(self.content)
        self.messages.setGeometry(QtCore.QRect(2, 0, 361, 400))
        self.scroll.verticalScrollBar().setValue(530)
        self.messages.show()

    def mes_update(self):
        global thread_flag1
        while True:
            if thread_flag1: break
            #print file creation time
            FileName = './data/mes/%s.txt'%self.object
            #print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(os.stat(FileName).st_ctime)))
            #print file modified time
            # st_mtime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(os.stat(FileName).st_mtime))
            st_mtime = os.stat(FileName).st_mtime
            now_time = time.time()
            # print(now_time-st_mtime)
            if now_time-st_mtime < 0.9: self.mySignal_1.emit()
            time.sleep(0.5)


class Home(Widget):
    def __init__(self):
        super().__init__() 
        self.userName = ''
        
        self.topTitle = QtWidgets.QWidget(self)
        self.topTitle.setGeometry(QtCore.QRect(0, 0, 363, 40))
        self.topTitle.setObjectName("topTitle")
        self.topTitle.setStyleSheet(self.qssStyle)

        self.avatar = QtWidgets.QPushButton(self.topTitle)
        self.avatar.setGeometry(QtCore.QRect(0, 0, 150, 40))
        self.avatar.setObjectName("titleAvatar")
        self.avatar.setStyleSheet(self.qssStyle)
        self.avatar.setText("    "+"用户名")
        #self.avatar.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeading)
        self.avatar.clicked.connect(self.exit)

        self.title = QtWidgets.QLabel(self.topTitle)
        self.title.setGeometry(QtCore.QRect(150, 0, 100, 40))
        self.title.setObjectName("titleText")
        self.title.setStyleSheet(self.qssStyle)

        self.add_btn = QtWidgets.QPushButton(self.topTitle)
        self.add_btn.setGeometry(QtCore.QRect(303, 0, 60, 40))
        self.add_btn.setText("+")
        self.add_btn.setObjectName("add_btn")
        self.add_btn.setStyleSheet(self.qssStyle)
        menu = QtWidgets.QMenu()
        cre_menu = QtWidgets.QAction("创建群聊", menu)
        menu.addAction(cre_menu)
        cre_menu.triggered.connect(self.create_group)
        add_menu = QtWidgets.QAction("添加好友/群", menu)
        menu.addAction(add_menu)
        add_menu.triggered.connect(lambda:self.add_friend_and_group(self))
        self.add_btn.setMenu(menu)
        #self.add_btn.clicked.connect(Widget.close)
        #搜索好友，添加好友，搜索群聊，添加群聊功能

        self.wid = QtWidgets.QWidget(self)
        self.wid.setGeometry(QtCore.QRect(-13, 40, 420, 520))

        self.content = QtWidgets.QWidget(self)
        self.content.setGeometry(QtCore.QRect(0, 40, 363, 510))
        self.content.setMinimumSize(363, 1100)

        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setWidget(self.content)

        self.vbox = QtWidgets.QVBoxLayout()
        self.vbox.addWidget(self.scroll)
        self.wid.setLayout(self.vbox)

        self.search = QtWidgets.QLineEdit(self.content)
        self.search.setGeometry(QtCore.QRect(5, 5, 353, 30))
        self.search.setObjectName("search")
        self.search.setStyleSheet(self.qssStyle)
        self.search.setPlaceholderText("搜索")
        self.search.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        #搜索功能

        self.footer = QtWidgets.QWidget(self)
        self.footer.setGeometry(QtCore.QRect(0, 550, 363, 50))
        self.footer.setObjectName('footer')
        self.footer.setStyleSheet(self.qssStyle)

        self.information_btn = QtWidgets.QPushButton(self.footer)
        self.information_btn.setText("消息")
        self.information_btn.setObjectName('footer')
        self.information_btn.setStyleSheet(self.qssStyle)
        self.information_btn.clicked.connect(self.inf_btn)
        self.contact_btn = QtWidgets.QPushButton(self.footer)
        self.contact_btn.setText("联系人")
        self.contact_btn.setObjectName('footer')
        self.contact_btn.setStyleSheet(self.qssStyle)
        self.contact_btn.clicked.connect(self.con_btn)
        self.setup_btn = QtWidgets.QPushButton(self.footer)
        self.setup_btn.setText("设置")
        self.setup_btn.setObjectName('footer')
        self.setup_btn.setStyleSheet(self.qssStyle)
        self.setup_btn.clicked.connect(self.setu_btn)

        layout = QHBoxLayout()
        layout.addWidget(self.information_btn)
        layout.addWidget(self.contact_btn)
        layout.addWidget(self.setup_btn)
        self.footer.setLayout(layout)

    def setUserName(self, userName):
        self.userName = userName
        self.avatar.setText("  "+self.userName)

    def inf_btn(self):
        self.mess = Message(self.userName)
        self.mess.show()
        self.close()

    def con_btn(self):
        self.cont = Contact(self.userName)
        self.cont.show()
        self.close()

    def setu_btn(self):
        self.setup = Setup(self.userName)
        self.setup.show()
        self.close()
        
    def exit(self):
        self.login = Login(self.userName)
        self.login.show()
        self.close()

    def create_group(self):
        self.Create_Group = Home()
        self.Create_Group.myName = 'Create_Group'
        self.close()
        self.Create_Group.avatar.close()
        self.Create_Group.add_btn.close()
        self.Create_Group.footer.close()
        self.Create_Group.title.setText("创建群聊")
        self.Create_Group.wid.setGeometry(QtCore.QRect(-13, 40, 420, 542))

        self.Create_Group.reback_btn = QtWidgets.QPushButton(self.Create_Group)
        self.Create_Group.reback_btn.setGeometry(QtCore.QRect(0, 0, 30, 40))
        self.Create_Group.reback_btn.setText("<")
        self.Create_Group.reback_btn.setObjectName('add_btn')
        self.Create_Group.reback_btn.setStyleSheet(self.qssStyle)
        self.Create_Group.reback_btn.clicked.connect(lambda:self.search_inf_btn(self.Create_Group, self))

        self.Create_Group.sure_create = QtWidgets.QPushButton(self.Create_Group)
        self.Create_Group.sure_create.setGeometry(QtCore.QRect(0, 570, 363, 30))
        self.Create_Group.sure_create.setText("创建")
        self.Create_Group.sure_create.setObjectName('sure_create')
        self.Create_Group.sure_create.setStyleSheet(self.qssStyle)
        self.Create_Group.sure_create.clicked.connect(self.sure_btn)
        #创建群聊需要把选中的所有好友发送给服务器

        self.Create_Group.friend_btns = Show_Inf('chat_friend', self.Create_Group)
        self.Create_Group.friend_btns.setParent(self.Create_Group.content)
        self.Create_Group.friend_btns.setGeometry(QtCore.QRect(2, 45, 361, 400))
        # self.Create_Group.sure_create.clicked.connect(lambda:self.add_friend_and_group(self.Group_Inf))

        self.Create_Group.show()

    def sure_btn(self):
        # input_groupId = QWidget(self.Create_Group)
        # input_groupId.setGeometry(QtCore.QRect(100, 245, 200, 100))
        
        # input = QtWidgets.QLineEdit(input_groupId)
        # input.setGeometry(QtCore.QRect(0, 0, 200, 50))
        # input.setPlaceholderText('群名')
        # input.setFocus()

        # btn = QtWidgets.QPushButton(input_groupId)
        # btn.setGeometry(QtCore.QRect(0, 50, 200, 50))
        # btn.setText('确认')

        # input_groupId.show()


        chosed_list = []
        for i in self.Create_Group.friend_btns.friends_btn:
            if i == 0: continue
            if i.objectName() == 'myself_chosed': 
                chosed_list.append(i.text().strip())
        print(chosed_list)

        #创建数据,发送
        send_data = {'Attributes': 'create_group', 'time': self.now_time(), 'group_name': self.userName+''.join(chosed_list)[0:6],
        'userId': self.userName, 'members': chosed_list}
        res = self.send_now(send_data)

        #创建成功，返回消息界面
        if res == 'Group created successfully':
            self.hint(self.Create_Group, content='创建成功')
            self.Create_Group.close()
            self.show()

            with open('./data/group.txt', 'a+', encoding='utf-8') as fp:
                fp.write(json.dumps(send_data)+'\n')
            with open('./data/chat_friend.txt', 'a+', encoding='utf-8') as fp:
                fp.write(json.dumps(send_data)+'\n')
        else:
            self.hint(self.Create_Group, content=res)

    
    def add_friend_and_group(self, last_widget):
        self.setup = Setup(self.userName)
        last_widget.hide()
        #self.setup.title.setGeometry(QtCore.QRect())
        self.setup.avatar.close()
        self.setup.add_btn.close()
        self.setup.footer.close()
        self.setup.wid.setGeometry(QtCore.QRect(-13, 40, 420, 535))
        self.setup.title.setText("找人/找群")
        self.setup.find_people = QtWidgets.QPushButton(self.setup)
        self.setup.find_people.setText('找人')
        self.setup.find_people.setGeometry(QtCore.QRect(303, 570, 70, 29))
        self.setup.find_people.setObjectName("find_btn")
        self.setup.find_people.setStyleSheet(self.qssStyle)
        self.setup.find_people.clicked.connect(lambda:self.find_friend(self.setup, 0))

        self.setup.find_group = QtWidgets.QPushButton(self.setup)
        self.setup.find_group.setText('找群')
        self.setup.find_group.setGeometry(QtCore.QRect(230, 570, 73, 29))
        self.setup.find_group.setObjectName("find_btn")
        self.setup.find_group.setStyleSheet(self.qssStyle)
        self.setup.find_group.clicked.connect(lambda:self.find_friend(self.setup, 1))

        self.setup.reback_btn = QtWidgets.QPushButton(self.setup)
        self.setup.reback_btn.setGeometry(QtCore.QRect(0, 0, 30, 40))
        self.setup.reback_btn.setText("<")
        self.setup.reback_btn.setObjectName('add_btn')
        self.setup.reback_btn.setStyleSheet(self.qssStyle)
        self.setup.reback_btn.clicked.connect(lambda:self.search_inf_btn(self.setup, last_widget))

        # self.setup.friend_btns = Show_Inf('chat_friend', self)
        # self.setup.friend_btns.setParent(self.content)
        # self.setup.friend_btns.setGeometry(QtCore.QRect(2, 90, 361, 400))
        self.setup.show()

    def find_friend(self, last_widget, chose):
        attr = ['search_person', 'search_group']
        send_data = {'Attributes': attr[chose], 'time': self.now_time(), 'search_Id': last_widget.search.text()}

        # print(send_data)
        res = self.send_now(send_data)
        res = eval(res)
        data = []
        for i in res:
            dic = {'userId': i}
            data.append(dic)

        # print(data)
        last_widget.friend_btns = Show_Inf(data, self)
        last_widget.friend_btns.setParent(last_widget.content)
        last_widget.friend_btns.setGeometry(QtCore.QRect(2, 40, 361, 400))
        last_widget.friend_btns.show()



    def search_inf_btn(self, last_widget, last_last_widget):
        # self.mess = Message(self.userName)
        # self.mess.show()
        last_last_widget.show()
        last_widget.close()

class Message(Home):
    def __init__(self):
        super().__init__() 
        self.new()

    def __init__(self, userName):
        super().__init__() 
        self.myName = 'Message'
        self.setUserName(userName)
        # QtCore.qDebug(self.userName)
        self.new()

    def new(self):
        self.myself = QtWidgets.QPushButton(self.content)
        self.myself.setGeometry(QtCore.QRect(2, 40, 363, 50))
        self.myself.setObjectName("myself")
        self.myself.setStyleSheet(self.qssStyle)
        self.myself.setText("       "+self.userName)
        self.myself.clicked.connect(self.open_chat)
        self.information_btn.setObjectName('checked_btn')
        self.information_btn.setStyleSheet(self.qssStyle)

        self.friend_btns = Show_Inf('chat_friend', self)
        self.friend_btns.setParent(self.content)
        self.friend_btns.setGeometry(QtCore.QRect(2, 90, 361, 400))
        # self.scroll = QtWidgets.QScrollArea()
        # self.scroll.setWidget(self.content)

        # self.vbox = QtWidgets.QVBoxLayout()
        # self.vbox.addWidget(self.scroll)
        # self.wid.setLayout(self.vbox)


        #置顶，删除，标为未读

    def open_chat(self):
        self.chat = Chat(self.myself.text().strip(), self)
        self.chat.show()
        self.close()


class Contact(Home):
    def __init__(self):
        super().__init__() 
        self.new()

    def __init__(self, userName):
        super().__init__() 
        self.myName = 'Contact'
        self.setUserName(userName)
        # QtCore.qDebug(self.userName)
        self.new()

    def new(self):
        self.now = True
        self.title.setText("联系人")

        self.add_btn.setVisible(False)
        # self.bar1 = QtWidgets.QWidget(self.content)
        # self.bar1.setGeometry(QtCore.QRect(2, 40, 359, 30))
        # self.bar1.setObjectName('footer')
        # self.bar1.setStyleSheet(self.qssStyle)

        self.new_friend = QtWidgets.QPushButton(self.content)
        self.new_friend.setGeometry(QtCore.QRect(2, 40, 363, 30))
        self.new_friend.setText(" 新朋友")
        self.new_friend.setObjectName('new_friend')
        self.new_friend.setStyleSheet(self.qssStyle)
        self.new_friend.clicked.connect(self.open_new_friend)

        self.group_inf = QtWidgets.QPushButton(self.content)
        self.group_inf.setGeometry(QtCore.QRect(2, 70, 363, 30))
        self.group_inf.setText(" 群通知")
        self.group_inf.setObjectName('new_friend')
        self.group_inf.setStyleSheet(self.qssStyle)
        self.group_inf.clicked.connect(self.open_group_inf)

        self.bar2 = QtWidgets.QWidget(self.content)
        self.bar2.setGeometry(QtCore.QRect(2, 100, 359, 30))
        self.bar2.setObjectName('footer')
        self.bar2.setStyleSheet(self.qssStyle)

        self.friend = QtWidgets.QPushButton(self.bar2)
        self.friend.setGeometry(QtCore.QRect(0, 0, 40, 30))
        self.friend.setText("好友")
        self.friend.setObjectName('checked_cont')
        self.friend.setStyleSheet(self.qssStyle)
        self.friend.clicked.connect(lambda:self.chosed(True))
        
        self.group = QtWidgets.QPushButton(self.bar2)
        self.group.setGeometry(QtCore.QRect(40, 0, 40, 30))
        self.group.setText("群聊")
        self.group.setObjectName('unchecked_cont')
        self.group.setStyleSheet(self.qssStyle)
        self.group.clicked.connect(lambda:self.chosed(False))

        self.contact_btn.setObjectName('checked_btn')
        self.contact_btn.setStyleSheet(self.qssStyle)

        self.chosed(self.now)

        #好友群聊分开显示
    
    def open_chat(self):
        self.chat = Chat(self.default_friend.text().strip(), self)
        self.chat.show()
        self.close()

    def chosed(self, chosed):
        target = ''
        if chosed:
            # self.now = True
            self.friend.setObjectName('checked_cont')
            self.friend.setStyleSheet(self.qssStyle)
            self.group.setObjectName('unchecked_cont')
            self.group.setStyleSheet(self.qssStyle)

            self.default_friend = QtWidgets.QPushButton(self.content)
            self.default_friend.setGeometry(QtCore.QRect(2, 142, 361, 40))
            self.default_friend.setObjectName("myself")
            self.default_friend.setStyleSheet(self.qssStyle)
            self.default_friend.setText("      "+self.userName)
            self.default_friend.clicked.connect(self.open_chat)
            self.default_friend.show()

            target = 'friend'
        else:
            # self.now = False
            self.default_friend.close()
            self.friend.setObjectName('unchecked_cont')
            self.friend.setStyleSheet(self.qssStyle)
            self.group.setObjectName('checked_cont')
            self.group.setStyleSheet(self.qssStyle)

            target = 'group'

        # print(target)
        if not self.now: self.friend_btns.close()
        self.now = False
        self.friend_btns = Show_Inf(target, self)
        self.friend_btns.setParent(self.content)
        if target == 'group': self.friend_btns.setGeometry(QtCore.QRect(2, 142, 361, 400))
        else: self.friend_btns.setGeometry(QtCore.QRect(2, 182, 361, 400))
        self.friend_btns.show()

    def open_new_friend(self):
        self.New_Friend = Home()
        self.close()
        self.New_Friend.avatar.close()
        self.New_Friend.add_btn.close()
        self.New_Friend.footer.close()
        self.New_Friend.search.close()
        self.New_Friend.userName = self.userName
        self.New_Friend.title.setText("新朋友")
        self.New_Friend.wid.setGeometry(QtCore.QRect(-13, 40, 420, 570))

        self.New_Friend.reback_btn = QtWidgets.QPushButton(self.New_Friend)
        self.New_Friend.reback_btn.setGeometry(QtCore.QRect(0, 0, 30, 40))
        self.New_Friend.reback_btn.setText("<")
        self.New_Friend.reback_btn.setObjectName('add_btn')
        self.New_Friend.reback_btn.setStyleSheet(self.qssStyle)
        self.New_Friend.reback_btn.clicked.connect(lambda:self.reback(self.New_Friend))

        self.New_Friend.add = QtWidgets.QPushButton(self.New_Friend)
        self.New_Friend.add.setGeometry(QtCore.QRect(303, 0, 60, 40))
        self.New_Friend.add.setText("添加")
        self.New_Friend.add.setObjectName('titleText')
        self.New_Friend.add.setStyleSheet(self.qssStyle)
        self.New_Friend.add.clicked.connect(lambda:self.add_friend_and_group(self.New_Friend))
        # self.New_Friend.add.setObjectName("add_btn")
        # self.New_Friend.add.setStyleSheet(self.qssStyle)
        self.New_Friend.friend_btns = Show_Inf('new_friend', self.New_Friend)
        self.New_Friend.friend_btns.setParent(self.New_Friend.content)
        self.New_Friend.friend_btns.setGeometry(QtCore.QRect(2, 0, 361, 400))

        self.New_Friend.show()

    def open_group_inf(self):
        self.Group_Inf = Home()
        self.close()
        self.Group_Inf.avatar.close()
        self.Group_Inf.add_btn.close()
        self.Group_Inf.footer.close()
        self.Group_Inf.search.close()
        self.Group_Inf.title.setText("群通知")
        self.Group_Inf.wid.setGeometry(QtCore.QRect(-13, 40, 420, 570))

        self.Group_Inf.reback_btn = QtWidgets.QPushButton(self.Group_Inf)
        self.Group_Inf.reback_btn.setGeometry(QtCore.QRect(0, 0, 30, 40))
        self.Group_Inf.reback_btn.setText("<")
        self.Group_Inf.reback_btn.setObjectName('add_btn')
        self.Group_Inf.reback_btn.setStyleSheet(self.qssStyle)
        self.Group_Inf.reback_btn.clicked.connect(lambda:self.reback(self.Group_Inf))

        self.Group_Inf.add = QtWidgets.QPushButton(self.Group_Inf)
        self.Group_Inf.add.setGeometry(QtCore.QRect(303, 0, 60, 40))
        self.Group_Inf.add.setText("添加")
        self.Group_Inf.add.setObjectName('titleText')
        self.Group_Inf.add.setStyleSheet(self.qssStyle)
        self.Group_Inf.add.clicked.connect(lambda:self.add_friend_and_group(self.Group_Inf))

        self.Group_Inf.friend_btns = Show_Inf('new_group', self.Group_Inf)
        self.Group_Inf.friend_btns.setParent(self.Group_Inf.content)
        self.Group_Inf.friend_btns.setGeometry(QtCore.QRect(2, 0, 361, 400))

        self.Group_Inf.show()

    def reback(self, last_widgit):
        self.cont = Contact(self.userName)
        self.cont.show()
        last_widgit.close()

    

class Setup(Home):
    def __init__(self):
        super().__init__() 
        self.new()

    def __init__(self, userName):
        super().__init__() 
        self.setUserName(userName)
        # QtCore.qDebug(self.userName)
        self.new()

    def new(self):
        self.add_btn.setVisible(False)
        self.title.setText(" 设置")
        self.setup_btn.setObjectName('checked_btn')
        self.setup_btn.setStyleSheet(self.qssStyle)

        #设置头像
        #修改邮箱
        #修改密码

class New_Friend(Home):
    def __init__(self):
        super().__init__()


from random import choice, randint

class Show_Inf(Widget):
    def __init__(self, target, Self):
        super().__init__()
        self.Self = Self
        self.setFixedSize(self.width(), 1500)
        #self.setSizePolicy()
        if not isinstance(target, list): self.target_path = './data/%s.txt'%target
        # print(self.target_path)
        self.friends = []
        self.friends_btn = [0]*20
        self.target = target
        #QtCore.qDebug(self.target)
        if isinstance(self.target, list):
            # print("aaaa")
            self.friends = self.target
            self.make_widget()
        elif self.target == 'message':
            self.target_path = './data/mes/%s.txt'%Self.object
            #self.write_mess()
            self.read_file()
            self.show_mess()
        else:
            # self.write_file()
            self.read_file()
            self.make_widget()

    def make_widget(self):
        # print(self.friends)
        userId = 'userId'
        hight = 40
        space = '      '
        if self.target == 'new_group': userId = 'group_name'
        if self.target in ['friend', 'group']: 
            if self.target == 'group': userId = 'group_name'
            hight = 40
            space = '      '
        if self.target == 'chat_friend': 
            hight = 50
            space = '       '
        j = 0
        for i in self.friends:
            #QtCore.qDebug(str(j)+' '+i['userId'])
            self.friends_btn[j] = QtWidgets.QPushButton(self)
            self.friends_btn[j].setGeometry(QtCore.QRect(2, hight*j, 361, hight))
            # print(userId, i[userId])
            self.friends_btn[j].setText(space+i[userId])
            self.friends_btn[j].setObjectName('myself')
            self.friends_btn[j].setStyleSheet(self.qssStyle)
            self.friends_btn[j].clicked.connect(lambda:self.open_chat(self.sender()))
            if isinstance(self.target, list): self.friends_btn[j].setToolTip('是否添加好友,点击确认')
            if self.target == 'new_group': self.friends_btn[j].setToolTip('你已被邀请加入该群')
            j += 1

    def open_chat(self, object):
        if isinstance(self.target, list):
            # self.Self.send_now()
            send_data = {'Attributes': 'add_friend', 'time': self.now_time(), 
            'userId': self.Self.userName, 'add_Id': object.text().strip()}

            # print(send_data)
            self.send_now(send_data, need_timeout=False)
            return

        if self.target == 'new_friend' or self.target == 'new_group':
            # self.Self.confirm = QtWidgets.QWidget(self.Self)
            # self.Self.confirm.setGeometry(QtCore.QRect(150, 300, 100, 60))
            # self.Self.confirm.setObjectName('my_send')
            # self.Self.confirm.setStyleSheet(self.qssStyle)

            # self.Self.hint = QtWidgets.QLabel(self.Self.confirm)
            # self.Self.hint.setGeometry(QtCore.QRect(0, 0, 100, 30))
            # self.Self.hint.setText('是否同意请求：')

            # self.Self.agree = QtWidgets.QPushButton(self.Self.confirm)
            # self.Self.agree.setGeometry(QtCore.QRect(0, 30, 50, 30))
            # self.Self.agree.setText('同意')

            # self.Self.rejecg = QtWidgets.QPushButton(self.Self.confirm)
            # self.Self.rejecg.setGeometry(QtCore.QRect(50, 30, 50, 30))
            # self.Self.rejecg.setText('拒绝')
            # self.Self.confirm.show()
            id = {'new_group': 'group_name', 'new_friend': 'userId'}
            if self.target == 'new_friend':
                attr = {'new_group': 'people', 'new_friend': 'person'}
                res = QtWidgets.QMessageBox.question(self.Self, '提示', '是否同意请求？')
                if res == QtWidgets.QMessageBox.Yes:
                    reply = 'accepted'
                    #将该对象写入好友列表和联系人列表
                    i = {"Attributes": attr[self.target], "time": self.Self.now_time(), id[self.target]: object.text().strip(), "userIco": "./data/userIco/default.png"}
                    with open('./data/%s.txt'%self.target.strip('new_'), 'a+', encoding='utf-8') as fp:
                        fp.write(json.dumps(i)+'\n')
                    with open('./data/chat_friend.txt', 'a+', encoding='utf-8') as fp:
                        fp.write(json.dumps(i)+'\n')
                else:
                    reply = 'not accepted'
                attr = {'new_group': 'create_group', 'new_friend': 'add_friend'}
                send_data = {'Attributes': attr[self.target], 'time': self.now_time(), 'reply': reply,
                        id[self.target]: self.Self.userName, 'add_Id': object.text().strip()}
                self.send_now(send_data, need_timeout=False)
                #if i['userId'] == object.text().strip(): self.friends.remove(i)
            with open(self.target_path, 'w+', encoding='utf-8') as fp:
                for i in self.friends: 
                    print(i[id[self.target]], object.text().strip())
                    if i[id[self.target]] != object.text().strip():
                        fp.write(json.dumps(i)+'\n')
            self.close()
            self.new_widget = Show_Inf(self.target,self)
            self.new_widget.setParent(self.Self.content)
            self.new_widget.show()
            
            return
        if self.Self.myName != 'Create_Group':
        # QtCore.qDebug(object)
            self.chat = Chat(object.text().strip(), self.Self)
            self.chat.show()
            self.Self.close()
        else:
            # QtCore.qDebug(object.objectName())
            if object.objectName() == 'myself':
                object.setObjectName('myself_chosed')
            else:
                object.setObjectName('myself')
            object.setStyleSheet(self.qssStyle)
            object.show()

    def read_file(self):
        try:
            if not os.path.exists(self.target_path): open(self.target_path, 'w+', encoding='utf-8')
            with open(self.target_path, 'r', encoding='utf-8') as fp:
                line = fp.readline()
                # self.friends.append(json.loads(line.strip())) 
                while line:    
                    self.friends.append(json.loads(line.strip())) 
                    line = fp.readline()
        except:
            with open(self.target_path, 'w+', encoding='utf-8') as fp: pass

    def write_file(self):
        attr = ['person', 'people']
        if self.target == 'friend': attr[1] = 'person'
        if self.target == 'group': attr[0] = 'people'
        friends = []
        for i in range(20):
            friend = {'Attributes': choice(attr), 'userId': self.rand_str(), 'userIco': './data/userIco/default.png'}
            friends.append(friend)

        with open(self.target_path, 'w+', encoding='utf-8') as fp:
            for i in friends:
                fp.write(json.dumps(i)+'\n')

    def rand_str(self, len=5):
        string = ''
        for i in range(randint(1,len)):
            string += chr(randint(ord('a'), ord('z')))
        return string

    def write_mess(self):
        messages = []
        who = [self.Self.userName, self.Self.object]
        for i in range(20):
            one = choice(who)
            two = who[1] if one == who[0] else who[0]
            message = {'Attributes': 'message', 'time': time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),
             'userId': one, 'object': two, 'mes_attrib': 'person', 'mes_content': self.rand_str(20)}
            messages.append(message)

        with open(self.target_path, 'w+', encoding='utf-8') as fp:
            for i in messages:
                fp.write(json.dumps(i)+'\n')

    def show_mess(self):
        j = 0
        for i in self.friends[-20:]:
            self.friends_btn[j] = QtWidgets.QWidget(self)
            self.friends_btn[j].setGeometry(QtCore.QRect(2, 50*j, 361, 40))
            self.avatar = QtWidgets.QPushButton(self.friends_btn[j])
            self.content = QtWidgets.QLabel(self.friends_btn[j])
            if self.Self.userName == i['userId']: 
                self.content.setGeometry(QtCore.QRect(2, 0, 317, 40))
                self.avatar.setGeometry(QtCore.QRect(321, 0, 321, 40))
                self.content.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)
            else:
                self.content.setGeometry(QtCore.QRect(44, 0, 321, 40))
                self.avatar.setGeometry(QtCore.QRect(2, 0, 40, 40))

            self.content.setText("'"+i['userId']+"':"+i['mes_content'])
            self.content.setObjectName('my_send')
            self.content.setStyleSheet(self.qssStyle)
            self.avatar.setObjectName('myself')
            self.avatar.setStyleSheet(self.qssStyle)
            # self.friends_btn[j].clicked.connect(lambda:self.open_chat(self.sender().text().strip()))
            j += 1




