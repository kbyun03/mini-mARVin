#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
ZetCode PyQt5 tutorial 

This is a Tetris game clone.

Author: Jan Bodnar
Website: zetcode.com 
Last edited: August 2017
"""

from PyQt5.QtWidgets import QWidget,QLabel,QLineEdit, QHBoxLayout,QVBoxLayout,QMainWindow,QPushButton, QFrame, QDesktopWidget, QApplication
from PyQt5.QtCore import Qt, QIODevice, QByteArray, QBasicTimer, pyqtSignal, QDataStream, QSettings, QTimer
from PyQt5.QtGui import QPainter, QColor 
import sys, random
from PyQt5.QtNetwork import (QAbstractSocket, QHostInfo, QTcpSocket)
from pynput import keyboard
from threading import Thread, Lock
import socket

class MiniMarvin(QWidget):
    
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):

        self.blockSize = 0

        self.ipAddr = QLineEdit(self)

        self.ipAddrL = QLabel('IP Address: ',self)

        self.connectButton = QPushButton('Connect', self)
        self.connectButton.clicked.connect(self.socketConnect)

        self.statusLabel = QLabel("Not Connected")

        
        self.hbox = QHBoxLayout(self)
        self.hbox.addWidget(self.ipAddrL)
        self.hbox.addWidget(self.ipAddr)
        self.hbox.addWidget(self.connectButton)

        self.vbox = QVBoxLayout(self)
        self.vbox.addStretch(1)
        self.vbox.addLayout(self.hbox)
        self.setLayout(self.vbox)

        self.connected = False


        self.keylist = []
        self.lis = keyboard.Listener(on_press=self.on_press)
        
        
        self.resize(500,400)
        self.center()


        self.setWindowTitle('mini-mARVin')        
        self.show()
        self.mutex = Lock()

    def displayError(self, socketError):
        self.connected = False
        if socketError == QAbstractSocket.RemoteHostClosedError:
            pass
        else:
            print(self, "The following error occurred: %s." % self.tcpSocket.errorString())

        self.lis.stop()
        
    def center(self):
        '''centers the window on the screen'''
        
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-size.width())/2, 
            (screen.height()-size.height())/2)
        
    def socketConnect(self):
        if self.connected == False:
            self.blockSize = 0
            self.tcpSocket =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self.tcpSocket.connect((self.ipAddr.text(), 12000))
            except:
                print("Connection failed.")
            self.statusLabel.setText("Connected")
            self.connectButton.setText("Disconnect")
            self.connected = True;
            self.lis.start()
        else:
            self.tcpSocket.close()
            self.statusLabel.setText("Not Connected")
            self.connectButton.setText("Connect")
            self.connected = False;
            self.lis.stop()
        
    def on_press(self, key):
        try:
            message = ''
            if key.char == 'w':
                message = "F"
            elif key.char == 's':
                message = "B"
            elif key.char == 'd':
                message = "R"
            elif key.char == 'a':
                message = "L"
            elif key.char == 'q':
                message = "S"
            print("sending: " + message)
            # now use the QDataStream and write the byte array to it.
            # now send the QByteArray.
            self.tcpSocket.sendall(message.encode())
            
        except socket.error as msg:
            print ("excepton in sending data: " + str(msg))
            self.tcpSocket.close()
            self.connected = false
        
        if key == keyboard.Key.esc: return False #stop listener


    


if __name__ == '__main__':
    
    app = QApplication([])
    miniMarvin = MiniMarvin()    
    sys.exit(app.exec_())
