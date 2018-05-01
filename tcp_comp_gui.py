#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
ZetCode PyQt5 tutorial 

This is a Tetris game clone.

Author: Jan Bodnar
Website: zetcode.com 
Last edited: August 2017
"""
from new_GUI import App
from PyQt5.QtWidgets import QWidget,QLabel,QLineEdit, QHBoxLayout,QVBoxLayout,QMainWindow,QPushButton, QFrame, QDesktopWidget, QApplication
from PyQt5.QtCore import Qt, QIODevice, QByteArray, QBasicTimer, pyqtSignal, QDataStream, QSettings, QTimer
from PyQt5.QtGui import QPainter, QColor
from PyQt5.Qt import QStackedLayout

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

        
        self.vbox = QVBoxLayout(self)
        self.vbox.addWidget(self.ipAddrL)
        self.vbox.addWidget(self.ipAddr)
        self.vbox.addWidget(self.connectButton)
        self.vbox.addWidget(self.statusLabel)

        self.setLayout(self.vbox)

        self.connected = False


        self.keylist = []
        
        
        self.resize(500,400)
        self.center()


        self.setWindowTitle('mini-mARVin')

        self.show()

    def openWindow(self):

        self.window = QMainWindow()
        self.myGui = App(self.window)

        self.stacked_layout = QStackedLayout()
        self.stacked_layout.addWidget(self.myGui)


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
        if (self.connected == False):
            self.blockSize = 0
            self.tcpSocket =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self.tcpSocket.connect((self.ipAddr.text(), 12000))
                self.statusLabel.setText("Connected")
                self.connectButton.setText("Disconnect")
                self.connected = True
                self.openConnection = True
                self.openWindow()
                self.lis = keyboard.Listener(on_press=self.on_press)
                self.lis.start()
                self.receiveThread = ReceiveThread(self)
                self.receiveThread.start()
            except socket.error as eMsg:
                print("Connection failed." + eMsg)

            #hi
        elif (self.connected == True):
            self.tcpSocket.close()
            self.statusLabel.setText("Not Connected")
            self.connectButton.setText("Connect")
            self.connected = False
            self.lis.stop()
            self.receiveThread.join()

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
            self.tcpSocket.sendall(message.encode())

            
        except socket.error as msg:
            print ("excepton in sending or receiving data: " + str(msg))
            self.tcpSocket.close()
            self.statusLabel.setText("Not Connected")
            self.connectButton.setText("Connect")
            self.connected = False
            self.lis.stop()
            self.recieveThread.join()
        
        if key == keyboard.Key.esc: return False #stop listener

class ReceiveThread(Thread):
    def __init__(self, mainSelf):
        Thread.__init__(self)
        self.window = mainSelf.window
        self.mainSelf = mainSelf
        self.tcpSocket = mainSelf.tcpSocket
        
    def run(self):
        while(1):
            msgStr = ''
            try:
                print("trying to receive thread")
                msg = self.tcpSocket.recv(4096)
                msgStr = str(msg.decode())
                print(msgStr)
                    #Assuming format is following
                    #msg = 'MARV [12,20] ; OBST [20,30] [30,40] ; HEAD 90'

                seg = msgStr.split(' ')

                for i in range(0,len(seg)):
                    if seg[i] == 'MARV':
                        curPos= seg[i+1]
                        posSeg = curPos.split(',')
                        curPosList = []
                        curPosList.append(int(posSeg[0][1:(len(posSeg[0]))]))
                        curPosList.append(int(posSeg[1][0:(len(posSeg[1])-1)]))
                        self.mainSelf.myGui.moveCar(curPosList)
                    elif seg[i] == 'HEAD':
                        angle = seg[i+1]
                        
                        self.mainSelf.myGui.rotate(float(angle))
                    elif seg[i] == 'OBST':
                        j = i

                        ObstPos = seg[j + 1]
                        posSeg = ObstPos.split(',')
                        obstPosList = []
                        obstPosList.append(float(posSeg[0][1:(len(posSeg[0]))]))
                        obstPosList.append(float(posSeg[1][0:(len(posSeg[1]) - 1)]))
                        print("ObstPos: " + str(ObstPos))
                        print("curPosList passed to showObstacle: " + str(obstPosList))
                        self.mainSelf.myGui.showObstacle(obstPosList, curPosList)



            except socket.error as eMsg:
                print('exception in tcpSocket.recv(): ' + str(eMsg))
                break




if __name__ == '__main__':
    
    app = QApplication([])
    miniMarvin = MiniMarvin()    
    sys.exit(app.exec_())
