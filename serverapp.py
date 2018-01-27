from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QListWidget, \
                            QPushButton, QLabel, QLineEdit, QListWidgetItem, \
                            QTextEdit, QTabWidget, QHBoxLayout, \
                            QApplication, QGridLayout
import sys
from socket import socket
from threading import Thread, Timer
import pickle
import os
import time
import database
import hashlib
from random import randint
import copy


def clearLayout(layout):
    while layout.count():
        child = layout.takeAt(0)
        if child.widget() is not None:
            child.widget().deleteLater()
        elif child.layout() is not None:
            clearLayout(child.layout())


class User(QWidget):
    first = 1

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        mainlayout = QVBoxLayout()
        deletegroup = QGroupBox('Delete users')
        addgroup = QGroupBox('Add users')
        deletelay = QVBoxLayout()
        addlay = QVBoxLayout()
        self.list = QListWidget()
        self.refreshusers()
        self.delbtn = QPushButton('Delete user', self)
        self.delbtn.clicked.connect(self.delete)
        deletelay.addWidget(self.list)
        deletelay.addWidget(self.delbtn)
        deletegroup.setLayout(deletelay)
        loglay = QGridLayout()
        loglabel = QLabel('Login: ')
        self.logline = QLineEdit(self)
        loglay.addWidget(loglabel, 0, 0)
        loglay.addWidget(self.logline, 0, 1)
        passlabel1 = QLabel('Password: ')
        passlabel2 = QLabel('Repeat password: ')
        self.passline1 = QLineEdit(self)
        self.passline1.setEchoMode(QLineEdit.Password)
        self.passline2 = QLineEdit(self)
        self.passline2.setEchoMode(QLineEdit.Password)
        self.addstatus = QLabel()
        loglay.addWidget(passlabel1, 1, 0)
        loglay.addWidget(self.passline1, 1, 1)
        loglay.addWidget(passlabel2, 2, 0)
        loglay.addWidget(self.passline2, 2, 1)
        loglay.addWidget(self.addstatus)
        addlay.addLayout(loglay)
        addbtn = QPushButton('Add user')
        addbtn.clicked.connect(self.adduser)
        addlay.addWidget(addbtn)
        addgroup.setLayout(addlay)
        mainlayout.addWidget(deletegroup)
        mainlayout.addWidget(addgroup)
        self.setLayout(mainlayout)

    def refreshusers(self):
        self.list.clear()
        self.userlist = database.selectall()
        for i in self.userlist:
            a = QListWidgetItem(i[0])
            self.list.addItem(a)

    def delete(self):
        for i in self.list.selectedItems():
            a = i.text()
        database.deletebyname(a)
        self.refreshusers()

    def adduser(self):
        password1 = self.passline1.text()
        password2 = self.passline2.text()
        if password1 == password2:
            login = self.logline.text()
            password = hashlib.md5(password1.encode('utf-8')).hexdigest()
            database.insertuser(login, password)
            self.refreshusers()
            self.passline1.setText('')
            self.passline2.setText('')
            self.logline.setText('')
            self.addstatus.setText("<font color='blue'>User added</font>")
        else:
            self.addstatus.setText("<font color='red'>Check password</font>")


class Textmanage(QWidget):

    def __init__(self, parent=None):
        super(QWidget, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.textmanage = QVBoxLayout()
        textlabel = QLabel('Give title and add text')
        self.titletext = QLineEdit()
        self.filetext = QTextEdit()
        self.textstatus = QLabel()
        self.managebtn = QPushButton('Create file')
        self.managebtn.clicked.connect(self.manage)
        self.textmanage.addWidget(textlabel)
        self.textmanage.addWidget(self.titletext)
        self.textmanage.addWidget(self.filetext)
        self.textmanage.addWidget(self.textstatus)
        self.textmanage.addWidget(self.managebtn)
        self.setLayout(self.textmanage)

    def manage(self):
        title = self.titletext.text()
        filetext = self.filetext.toPlainText()
        if title != '' and filetext != '':
            filename = "text/{}.txt".format(title)
            file = open(filename, 'w')
            file.write(filetext)
            file.close()
            textstatus = "<font color='blue'>File created</font>"
            self.textstatus.setText(textstatus)
            self.titletext.setText('')
            self.filetext.setText('')
        else:
            textstatus = "<font color='red'>Enter title and text</font"
            self.textstatus.setText(textstatus)


class Main(QWidget):
    forcest = False
    first = 0
    clientresult = []
    sendtext = {}
    running = True
    conns = {}
    threads = []
    count = 0

    def __init__(self):
        super().__init__()
        self.startserver()

    def startserver(self):
        self.setGeometry(300, 60, 600, 600)
        tabwidget = QTabWidget()
        chat = QWidget()
        self.lay = QHBoxLayout()
        results = QWidget()
        resultslay = QVBoxLayout()
        self.resultlist = QListWidget()
        resultslay.addWidget(self.resultlist)
        results.setLayout(resultslay)
        startracer = QWidget()
        startlayout = QVBoxLayout()
        self.checkfilestatus = QTextEdit('')
        self.check = QPushButton('Check text')
        self.check.clicked.connect(self.checktext)
        self.listfiles = QListWidget()
        self.refreshfiles()
        self.selectstatus = QLabel()
        self.selecttext = QPushButton('Select text and start')
        self.randomtext = QPushButton('Select random file and start')
        self.stopracing = QPushButton('Stop the game')
        self.stopracing.setEnabled(False)
        self.stopracing.clicked.connect(self.forcestopping)
        self.selecttext.clicked.connect(self.selectnot)
        self.randomtext.clicked.connect(self.random)
        startlayout.addWidget(self.listfiles)
        startlayout.addWidget(self.checkfilestatus)
        startlayout.addWidget(self.selectstatus)
        startlayout.addWidget(self.check)
        startlayout.addWidget(self.selecttext)
        startlayout.addWidget(self.randomtext)
        startlayout.addWidget(self.stopracing)
        startracer.setLayout(startlayout)
        self.chatlay = QVBoxLayout()
        self.list = QListWidget(self)
        self.active = QListWidget(self)
        self.line = QLineEdit(self)
        self.send = QPushButton('Send', self)
        self.send.clicked.connect(self.sendmessage)
        self.chatlay.addWidget(self.active)
        self.chatlay.addWidget(self.list)
        self.chatlay.addWidget(self.line)
        self.chatlay.addWidget(self.send)
        chat.setLayout(self.chatlay)
        tabwidget.addTab(chat, 'Chat')
        tabwidget.addTab(Textmanage(self), 'Text manage')
        tabwidget.addTab(User(), 'User management')
        tabwidget.addTab(startracer, 'Start game')
        tabwidget.addTab(results, 'Results')
        if hasattr(self, 'socket'):
            self.socket.close()
            for i in self.conns.values():
                i.close()
        self.lay.addWidget(tabwidget)
        self.setLayout(self.lay)
        self.show()
        self.socket = socket()
        self.socket.bind(('0.0.0.0', 9090))
        self.socket.listen(5)
        Thread(target=self.acceptclients).start()
        Thread(target=self.activeusers).start()
        Thread(target=self.statistic).start()
        Thread(target=self.reftext).start()

    def forcestopping(self):
        self.forcest = True
        self.sendstop()

    def reftext(self):
        while True:
            time.sleep(9)
            self.refreshfiles()

    def statistic(self):
        while True:
            time.sleep(5)
            self.resultlist.clear()
            print(self.clientresult)
            stat = copy.deepcopy(self.clientresult)
            stat = sorted(stat)
            stat = stat[::-1]
            for i in stat:
                if type(i[0]) == str:
                    i[0], i[1] = i[1], i[0]
            print(stat)
            for i in stat:
                if type(i[1]) == str:
                    i[1], i[0] = i[0], i[1]
                i[1] = str(i[1]) + ' WPM'
                a = '  '.join(i)
                a = QListWidgetItem(a)
                self.resultlist.addItem(a)

    def selectnot(self):
        if len(self.listfiles.selectedItems()) > 0:
            self.first = 0
            self.forcest = False
            self.clientresult = []
            self.stopracing.setEnabled(True)
            for i in self.listfiles.selectedItems():
                i = i.text() + '.txt'
            direct = 'text/' + i
            self.sendtext[i] = open(direct).read()
            for i in self.conns.values():
                i.sendall(pickle.dumps(self.sendtext))

    def random(self):
        self.first = 0
        self.forcest = False
        self.clientresult = []
        l = os.listdir('text/')
        print(l)
        self.stopracing.setEnabled(True)
        d = randint(0, len(l) - 1)
        a, b = l[d].split('.')
        d = 'text/' + l[d]
        self.sendtext[a] = open(d).read()
        for i in self.conns.values():
            i.sendall(pickle.dumps(self.sendtext))

    def checktext(self):
        for i in self.listfiles.selectedItems():
            direct = 'text/' + i.text() + '.txt'
        text = open(direct).read()
        self.checkfilestatus.setText(text)

    def refreshfiles(self):
        self.listfiles.clear()
        for i in os.listdir('text/'):
            i = list(i.split('.'))[0]
            a = QListWidgetItem('{}'.format(i))
            self.listfiles.addItem(a)

    def activeusers(self):
        while self.running:
            self.active.clear()
            for i in self.conns.keys():
                a = QListWidgetItem(str(i))
                self.active.addItem(a)
            for i in self.conns.values():
                i.send(pickle.dumps(list(self.conns.keys())))
            time.sleep(5)

    def acceptclients(self):
        print('acceptclients runs')
        while self.running:
            try:
                conn, addr = self.socket.accept()
                print(addr)
                Thread(target=self.identifyclient, args=(conn,)).start()
            except:
                pass

    def identifyclient(self, conn):
        while self.running:
            try:
                req = conn.recv(1024)
                req = pickle.loads(req)
                print(req)
                if req[0] == 'Sign in':
                    ans = database.selectbyname(req[1], req[2])
                    print(ans)
                    if ans:
                        conn.send(pickle.dumps('okay'))
                        self.conns[req[1]] = conn
                        c = Thread(target=self.acceptmes, args=(conn, req[1]))
                        c.start()
                        break
                    else:
                        conn.send(pickle.dumps('Incorrect'))
                else:
                    if req[1] == "" and req[2] == "":
                        conn.send(pickle.dumps('Incorrect'))
                    else:
                        database.insertuser(req[1], req[2])
                        conn.send(pickle.dumps('okay'))
                        self.conns[req[1]] = conn
                        c = Thread(target=self.acceptmes, args=(conn, req[1]))
                        c.start()
                        break
            except:
                break

    def sendmessage(self):
        mymes = QListWidgetItem('You: {}'.format(self.line.text()))
        mymes.setTextAlignment(2)
        for i in self.conns.values():
            i.send(pickle.dumps('Admin: ' + self.line.text()))
        self.list.addItem(mymes)
        self.line.setText('')

    def sendstopping(self):
        t = Timer(10.0, self.sendstop)
        print('Timer')
        t.start()

    def sendstop(self):
        self.stopracing.setEnabled(False)
        print('sending to stop')
        for i in self.conns.values():
            i.sendall(pickle.dumps(['to stop']))
        time.sleep(2)
        if self.forcest:
            for i in self.conns.values():
                i.sendall(pickle.dumps(self.clientresult))

    def acceptmes(self, conn, name):
        while self.running:
            try:
                mes = conn.recv(2048)
                mes = pickle.loads(mes)
                print(mes)
                if type(mes) == list:
                    try:
                        self.clientresult.append(mes)
                        print(self.clientresult)
                        if self.first == 0 and not self.forcest:
                            Thread(target=self.sendstopping).start()
                        self.first += 1
                        if self.first == len(self.conns) and not self.forcest:
                            self.stopracing.setEnabled(False)
                            for i in self.conns.values():
                                i.sendall(pickle.dumps(self.clientresult))
                    except:
                        pass
                else:
                    mes = name + ': ' + mes
                    for i in self.conns.values():
                        if i != conn:
                            i.sendall(pickle.dumps(mes))
                    self.list.addItem(QListWidgetItem('{}'.format(mes)))
            except:
                self.conns.pop(name)
                break

    def closeEvent(self, event):
        os._exit(1)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Main()
    ex.show()
    sys.exit(app.exec_())
