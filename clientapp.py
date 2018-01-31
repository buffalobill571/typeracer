from PyQt5.QtWidgets import QWidget, QVBoxLayout, QListWidget, \
                            QPushButton, QLabel, QLineEdit, QListWidgetItem, \
                            QTextEdit, QApplication, QHBoxLayout
import sys
from PyQt5.QtMultimedia import QSound
from PyQt5.QtGui import QFont, QPalette, QBrush, QPixmap
from PyQt5.QtCore import Qt
from socket import socket
import threading
import pickle
import os
from time import time
import hashlib
import copy


def clearLayout(layout):
    while layout.count():
        child = layout.takeAt(0)
        if child.widget() is not None:
            child.widget().deleteLater()
        elif child.layout() is not None:
            clearLayout(child.layout())


def get_current_ip():
    import socket
    ip = (([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")] or [[(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) + ["no IP found"])[0]
    return ip


SERVER_ADDRESS = get_current_ip()
print(SERVER_ADDRESS)


def accept_broadcast():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.bind(('', 12345))
        m = s.recvfrom(1024)
        print(m)
        global SERVER_ADDRESS
        SERVER_ADDRESS = m[1][0]
    except:
        pass


class Main(QWidget):
    countlength = 0
    wordslist = []
    typing = ''
    typeracermode = False
    error = 'errorsound.mp3'
    success = 'success.wav'
    running = True
    length = 0
    threads = []
    count = 0
    counter = 0
    errorcount = 0
    name = None
    password = None
    trycount = 0
    before = ''

    def __init__(self):
        super().__init__()
        self.disp = QPushButton()
        self.disp.hide()
        self.disp.clicked.connect(self.displayall)
        self.initUI()

    def initUI(self):
        self.label = QLabel(self)
        pixmap = QPixmap('logo.png')
        pixmap = pixmap.scaledToWidth(200)
        self.label.setPixmap(pixmap)
        self.lay = QVBoxLayout()
        self.label.setAlignment(Qt.AlignCenter)
        self.hor = QHBoxLayout()
        # self.lay.setContentsMargins(-1,-1,-1,0)

        self.Hbox = QHBoxLayout()
        # self.Hbox.addStretch(1)

        # self.hor.setAlignment(Qt.AlignCenter)
        # self.lay.addLayout(self.hor)
        self.setStyleSheet('QWidget {background-color:white;border:none}')
        # self.label.setStyleSheet('Q {width:50px;height:auto}')

        self.height = 60
        self.trycount = 0
        self.setGeometry(300, 150, 400, 600)
        self.setWindowTitle('Welcome')
        self.nameline = QLineEdit()
        self.passwordline = QLineEdit()
        self.nameline.setPlaceholderText("Username...")
        self.passwordline.setPlaceholderText("Password...")

        self.passwordline.setEchoMode(QLineEdit.Password)
        self.nameline.setStyleSheet('QLineEdit {background-color:#EEE;height:40;border-radius:3px;font-family:Arial;padding:6px}')
        self.passwordline.setStyleSheet('QLineEdit {background-color:#EEE;height:40;border-radius:3px;font-family:Arial;padding:6px;}')
        self.status = QLabel()
        self.status.setStyleSheet("color:red")
        self.lay.addStretch(1)
        self.lay.addWidget(self.label)
        self.lay.addStretch(1)

        self.lay.addWidget(self.nameline)
        self.lay.addWidget(self.passwordline)
        self.lay.addWidget(self.status)
        self.lay.setAlignment(self.nameline, Qt.AlignBottom)

        self.lay.addLayout(self.Hbox)
        # self.lay.addStretch(1)


        self.signin = QPushButton('Sign in')
        self.signup = QPushButton('Sign up')
        self.signin.setStyleSheet('QPushButton {background-color:#4990E2;color:white;height:50;font-size:20px;border-radius:3px;font-family:Arial;}')
        self.signup.setStyleSheet('QPushButton {background-color:#7FDC89;color:white;height:50;font-size:20px;border-radius:3px;font-family:Arial;}')

        self.signin.clicked.connect(self.authentification)
        self.signup.clicked.connect(self.authentification)
        self.Hbox.addWidget(self.signin)
        self.Hbox.addWidget(self.signup)
        self.setLayout(self.lay)
        self.show()

    def authentification(self):

        sender = self.sender()
        self.name = self.nameline.text()
        password = self.passwordline.text()
        if self.name == "" and password == "":
            self.status.setText('Type something')
        else:
            self.password = hashlib.md5(password.encode('utf-8')).hexdigest()
            if self.trycount == 0:
                self.socket = socket()
                global SERVER_ADDRESS
                self.socket.connect((SERVER_ADDRESS, 9090))
                self.trycount += 1
            sendlist = [sender.text(), self.name, self.password]
            req = pickle.dumps(sendlist)
            self.socket.send(req)
            response = self.socket.recv(2048)
            response = pickle.loads(response)
            if response == 'okay':
                self.startserver()
                threading.Thread(target=self.accept).start()
            else:
                self.status.setText('Incorrect login or password')

    def startserver(self):
        self.setGeometry(300, 150, 500, 600)
        self.setWindowTitle('Chat')
        clearLayout(self.lay)
        online = QLabel('Online:')
        messages = QLabel('Messages:')
        self.list = QListWidget()
        self.list.setStyleSheet("QListWidget{border: none;border-radius:3px;background-color:#EEE}")
        self.active = QListWidget()
        self.active.setStyleSheet("QListWidget{border: none;border-radius:3px;background-color:#EEE;height:40}")
        self.line = QLineEdit()
        self.mesLine = QHBoxLayout()
        self.send = QPushButton('Send')
        self.send.setStyleSheet('background: #6d84b4;color: white;height:40;width:70px;border-radius:3px')
        self.mesLine.addWidget(self.line)
        self.mesLine.addWidget(self.send)
        self.send.clicked.connect(self.sendmessage)
        self.line.setStyleSheet("QLineEdit{border: none;border-radius:3px;background-color:#EEE;height:40}")
        self.line.setPlaceholderText("type something ...")
        self.startmode = QPushButton('Start typing')
        self.startmode.hide()
        self.startmode.clicked.connect(self.typeracer)
        self.lay.addWidget(online)
        self.lay.addWidget(self.active)
        self.lay.addWidget(messages)
        self.lay.addWidget(self.list)
        self.lay.addLayout(self.mesLine)

    def typeracer(self):
        self.setGeometry(300, 150, 400, 650)
        self.setWindowTitle('Typeracer')
        if hasattr(self, 'lay'):
            clearLayout(self.lay)
        else:
            self.lay = QVBoxLayout()
            self.setLayout(self.lay)
        if not self.typing:
            self.typing = "Hello WOT!!!"
        self.wordslist = list(self.typing.split())
        self.mainlist = list(self.typing)
        self.words = len(list(self.typing.split()))
        self.textline = QTextEdit()
        self.textline.setText("<font color='blue' size=8>{}</font>"
                              .format(self.typing))
        self.textline.setReadOnly(True)
        self.editline = QLineEdit()
        self.editline.setFixedSize(400, 70)
        font = self.editline.font()
        font.setPointSize(18)
        self.editline.setFont(font)
        self.editline.textChanged.connect(self.sec)
        self.stopbtn = QPushButton('Stop the game')
        self.stopbtn.clicked.connect(self.result)
        self.stopbtn.hide()
        self.lay.addWidget(self.textline)
        self.lay.addWidget(self.editline)
        self.lay.addWidget(self.stopbtn)
        self.firtime = time()

    def sec(self):
        text1 = self.editline.text()
        if len(self.before) < len(text1):
            if text1[-1] == self.mainlist[0]:
                self.counter += 1
                typed = self.typing[:self.counter]
                future = self.typing[self.counter:]
                text = '''<font color='blue' size=8>{}</font>
                          <font size=8>{}</font>'''.format(typed, future)
                self.textline.setText(text)
                if self.mainlist[0] == ' ':
                    self.editline.setText('')
                    self.before = ''
                else:
                    self.countlength += 1
                    self.before = text1
                self.mainlist = self.mainlist[1:]
                if not len(self.mainlist):
                    self.result()
            else:
                self.errorcount += 1
                self.before = text1
                QSound.play(self.success)
        else:
            self.before = text1

    def result(self):
        ch = 0
        w = 0
        for i in self.wordslist:
            if ch >= self.countlength:
                break
            ch += len(i)
            w += 1
        print(w)
        print(self.countlength)
        print(ch)
        clearLayout(self.lay)
        tosend = []
        self.time = time() - self.firtime
        h = round(self.time)
        self.time = self.time / 60
        self.time = round(w / self.time)
        tosend.append(self.time)
        tosend.append(self.name)
        h = str(h) + ' seconds'
        tosend.append(h)
        self.errorcount = str(self.errorcount) + ' errors'
        tosend.append(self.errorcount)
        QSound.play(self.success)
        self.socket.sendall(pickle.dumps(tosend))
        ss = []
        for i in tosend:
            i = str(i)
        label = QLabel('  '.join(ss))
        label2 = QLabel('Wait for others, it may take maximum 30 sec')
        self.lay.addWidget(label)
        self.lay.addWidget(label2)
        self.typing = []

    def sendmessage(self):
        mymes = QListWidgetItem('You: {}'.format(self.line.text()))
        mymes.setTextAlignment(2)
        self.socket.send(pickle.dumps(self.line.text()))
        self.list.addItem(mymes)
        self.line.setText('')

    def accept(self):
        while self.running:
            try:
                mes = self.socket.recv(4096)
                mes = pickle.loads(mes)
                print(mes)
                if type(mes) == list:
                    if type(mes[0]) == str:
                        if mes[0] == 'to stop':
                            self.stopbtn.click()
                        else:
                            self.active.clear()
                            for i in mes:
                                if i == self.name:
                                    i = 'You'
                                a = QListWidgetItem(str(i))
                                a.setTextAlignment(0x0004)
                                self.active.addItem(a)
                    else:
                        print(mes)
                        self.clientresult = mes
                        self.disp.click()
                elif type(mes) == dict:
                    self.typing = list(mes.values())[0]
                    self.startmode.click()
                elif mes == 'Admin: start':
                    self.startmode.click()
                else:
                    self.list.addItem(QListWidgetItem('{}'.format(mes)))
            except:
                pass

    def displayall(self):
        clearLayout(self.lay)
        listof = QListWidget()
        stat = copy.deepcopy(self.clientresult)
        stat = sorted(stat)
        stat = stat[::-1]
        for i in stat:
            if type(i[1]) == str:
                i[1], i[0] = i[0], i[1]
            i[1] = str(i[1]) + ' WPM'
            a = '  '.join(i)
            a = QListWidgetItem(a)
            listof.addItem(a)
        self.lay.addWidget(listof)
        goback = QPushButton('Back to chat')
        goback.clicked.connect(self.startserver)
        self.lay.addWidget(goback)
        self.counter = 0
        self.errorcount = 0
        self.countlength = 0
        self.before = ''
        self.typing = []

    def closeEvent(self, event):
        os._exit(1)


if __name__ == '__main__':
    threading.Thread(target=accept_broadcast).start()
    app = QApplication(sys.argv)
    ex = Main()
    sys.exit(app.exec_())

        pass


class Main(QWidget):
    countlength = 0
    wordslist = []
    typing = ''
    typeracermode = False
    error = 'errorsound.mp3'
    success = 'success.wav'
    running = True
    length = 0
    threads = []
    count = 0
    counter = 0
    errorcount = 0
    name = None
    password = None
    trycount = 0
    before = ''

    def __init__(self):
        super().__init__()
        self.disp = QPushButton()
        self.disp.hide()
        self.disp.clicked.connect(self.displayall)
        self.initUI()

    def initUI(self):
        self.label = QLabel(self)
        pixmap = QPixmap('logo.png')
        pixmap = pixmap.scaledToWidth(200)
        self.label.setPixmap(pixmap)
        self.lay = QVBoxLayout()
        self.label.setAlignment(Qt.AlignCenter)
        self.hor = QHBoxLayout()
        # self.lay.setContentsMargins(-1,-1,-1,0)
        
        self.Hbox = QHBoxLayout()
        # self.Hbox.addStretch(1)
        
        # self.hor.setAlignment(Qt.AlignCenter)
        # self.lay.addLayout(self.hor)
        self.setStyleSheet('QWidget {background-color:white;border:none}')
        # self.label.setStyleSheet('Q {width:50px;height:auto}')
        
        self.height = 60 
        self.trycount = 0
        self.setGeometry(300, 150, 400, 600)
        self.nameline = QLineEdit()
        self.passwordline = QLineEdit()
        self.nameline.setPlaceholderText("Username...")
        self.passwordline.setPlaceholderText("Password...")

        self.passwordline.setEchoMode(QLineEdit.Password)
        self.nameline.setStyleSheet('QLineEdit {background-color:#EEE;height:40;border-radius:3px;font-family:Arial;padding:6px}')
        self.passwordline.setStyleSheet('QLineEdit {background-color:#EEE;height:40;border-radius:3px;font-family:Arial;padding:6px;}')
        self.status = QLabel()
        self.status.setStyleSheet("color:red")
        self.lay.addStretch(1)
        self.lay.addWidget(self.label)
        self.lay.addStretch(1)
        
        self.lay.addWidget(self.nameline)
        self.lay.addWidget(self.passwordline)
        # self.lay.addWidget(self.status)
        self.lay.setAlignment(self.nameline, Qt.AlignBottom)
        
        self.lay.addLayout(self.Hbox)
        # self.lay.addStretch(1)
        
        
        self.signin = QPushButton('Sign in')
        self.signup = QPushButton('Sign up')
        self.signin.setStyleSheet('QPushButton {background-color:#4990E2;color:white;height:50;font-size:20px;border-radius:3px;font-family:Arial;}')
        self.signup.setStyleSheet('QPushButton {background-color:#7FDC89;color:white;height:50;font-size:20px;border-radius:3px;font-family:Arial;}')
        
        self.signin.clicked.connect(self.authentification)
        self.signup.clicked.connect(self.authentification)
        self.Hbox.addWidget(self.signin)
        self.Hbox.addWidget(self.signup)
        self.setLayout(self.lay)
        self.show()

    def authentification(self):
        
        sender = self.sender()
        self.name = self.nameline.text()
        password = self.passwordline.text()
        if self.name == "" and password == "":
            self.status.setText('Type something')
        else:
            self.password = hashlib.md5(password.encode('utf-8')).hexdigest()
            if self.trycount == 0:
                self.socket = socket()
                global SERVER_ADDRESS
                self.socket.connect((SERVER_ADDRESS, 9090))
                self.trycount += 1
            sendlist = [sender.text(), self.name, self.password]
            req = pickle.dumps(sendlist)
            self.socket.send(req)
            response = self.socket.recv(1024)
            response = pickle.loads(response)
            if response == 'okay':
                self.startserver()
                threading.Thread(target=self.accept).start()
            else:
                self.status.setText('Incorrect login or password')

    def startserver(self): 
        self.setGeometry(300, 150, 300, 450) 
        clearLayout(self.lay) 
        self.list = QListWidget() 
        self.list.setStyleSheet("border: none;border-radius:10px") 
        self.active = QListWidget() 
        self.active.setStyleSheet("border: none;border-radius:10px") 
        self.line = QLineEdit() 
        self.mesLine = QHBoxLayout() 
        self.send = QPushButton('Send') 
        self.send.setStyleSheet('background: #6d84b4;color: white') 
        self.mesLine.addWidget(self.line) 
        self.mesLine.addWidget(self.send) 
        self.send.clicked.connect(self.sendmessage) 
        self.line.setPlaceholderText("type something ...") 
        self.startmode = QPushButton('Start typing') 
        self.startmode.hide() 
        self.startmode.clicked.connect(self.typeracer) 
        self.lay.addWidget(self.active) 
        self.lay.addWidget(self.list) 
        self.lay.addLayout(self.mesLine)

    def typeracer(self):
        self.setGeometry(300, 150, 400, 650)
        if hasattr(self, 'lay'):
            clearLayout(self.lay)
        else:
            self.lay = QVBoxLayout()
            self.setLayout(self.lay)
        if not self.typing:
            self.typing = "Hello WOT!!!"
        self.wordslist = list(self.typing.split())
        self.mainlist = list(self.typing)
        self.words = len(list(self.typing.split()))
        self.textline = QTextEdit()
        self.textline.setText("<font color='blue' size=8>{}</font>"
                              .format(self.typing))
        self.textline.setReadOnly(True)
        self.editline = QLineEdit()
        self.editline.setFixedSize(400, 70)
        font = self.editline.font()
        font.setPointSize(18)
        self.editline.setFont(font)
        self.editline.textChanged.connect(self.sec)
        self.stopbtn = QPushButton('Stop the game')
        self.stopbtn.clicked.connect(self.result)
        self.stopbtn.hide()
        self.lay.addWidget(self.textline)
        self.lay.addWidget(self.editline)
        self.lay.addWidget(self.stopbtn)
        self.firtime = time()

    def sec(self):
        text1 = self.editline.text()
        if len(self.before) < len(text1):
            if text1[-1] == self.mainlist[0]:
                self.counter += 1
                typed = self.typing[:self.counter]
                future = self.typing[self.counter:]
                text = '''<font color='blue' size=8>{}</font>
                          <font size=8>{}</font>'''.format(typed, future)
                self.textline.setText(text)
                if self.mainlist[0] == ' ':
                    self.editline.setText('')
                    self.before = ''
                else:
                    self.countlength += 1
                    self.before = text1
                self.mainlist = self.mainlist[1:]
                if not len(self.mainlist):
                    self.result()
            else:
                self.errorcount += 1
                self.before = text1
                QSound.play(self.success)
        else:
            self.before = text1

    def result(self):
        ch = 0
        w = 0
        for i in self.wordslist:
            if ch >= self.countlength:
                break
            ch += len(i)
            w += 1
        print(w)
        print(self.countlength)
        print(ch)
        clearLayout(self.lay)
        tosend = []
        self.time = time() - self.firtime
        h = round(self.time)
        self.time = self.time / 60
        self.time = round(w / self.time)
        tosend.append(self.time)
        tosend.append(self.name)
        h = str(h) + ' seconds'
        tosend.append(h)
        self.errorcount = str(self.errorcount) + ' errors'
        tosend.append(self.errorcount)
        QSound.play(self.success)
        self.socket.sendall(pickle.dumps(tosend))
        ss = []
        for i in tosend:
            i = str(i)
        label = QLabel('  '.join(ss))
        label2 = QLabel('Wait for others, it may take maximum 30 sec')
        self.lay.addWidget(label)
        self.lay.addWidget(label2)
        self.typing = []

    def sendmessage(self):
        mymes = QListWidgetItem('You: {}'.format(self.line.text()))
        mymes.setTextAlignment(2)
        self.socket.send(pickle.dumps(self.line.text()))
        self.list.addItem(mymes)
        self.line.setText('')

    def accept(self):
        while self.running:
            try:
                mes = self.socket.recv(4096)
                mes = pickle.loads(mes)
                print(mes)
                if type(mes) == list:
                    if type(mes[0]) == str:
                        if mes[0] == 'to stop':
                            self.stopbtn.click()
                        else:
                            self.active.clear()
                            for i in mes:
                                if i == self.name:
                                    i = 'You'
                                a = QListWidgetItem(str(i))
                                self.active.addItem(a)
                    else:
                        print(mes)
                        self.clientresult = mes
                        self.disp.click()
                elif type(mes) == dict:
                    self.typing = list(mes.values())[0]
                    self.startmode.click()
                elif mes == 'Admin: start':
                    self.startmode.click()
                else:
                    self.list.addItem(QListWidgetItem('{}'.format(mes)))
            except:
                pass

    def displayall(self):
        clearLayout(self.lay)
        listof = QListWidget()
        stat = copy.deepcopy(self.clientresult)
        stat = sorted(stat)
        stat = stat[::-1]
        for i in stat:
            if type(i[1]) == str:
                i[1], i[0] = i[0], i[1]
            i[1] = str(i[1]) + ' WPM'
            a = '  '.join(i)
            a = QListWidgetItem(a)
            listof.addItem(a)
        self.lay.addWidget(listof)
        goback = QPushButton('Back to chat')
        goback.clicked.connect(self.startserver)
        self.lay.addWidget(goback)
        self.counter = 0
        self.errorcount = 0
        self.countlength = 0
        self.before = ''
        self.typing = []

    def closeEvent(self, event):
        os._exit(1)


if __name__ == '__main__':
    threading.Thread(target=accept_broadcast).start()
    app = QApplication(sys.argv)
    ex = Main()
    sys.exit(app.exec_())
