import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtCore import Qt
from pynput import keyboard

class App(QWidget):
    def __init__(self, OtherWindow):
        super().__init__()
        print("ths one is on github")
        self.setGeometry(100,100,800,600)
        #Assuming the world is 2m(width) by 1m(height)


        self.setWindowTitle("New GUI Interface Window")
        self.currentState = 0

        #self.directionCode =0

        self.obstCounter = 0
        self.x = 200
        self.y = 200
        self.d = []

        #loading image for tank

        #self.tank = QtWidgets.QLabel(self)
        #self.tank.setPixmap(QtGui.QPixmap('smallcar.png'))
        #self.tank.move(self.x,self.y)
        #self.tank.adjustSize()

        self.image= QtGui.QImage('smallcar.png')

        self.pixmap = QtGui.QPixmap(self.image)

        self.tank = QtWidgets.QLabel(self)
        self.tank.setAlignment(QtCore.Qt.AlignCenter)
        self.tank.setPixmap(self.pixmap)
        self.tank.adjustSize()
        self.tank.move(self.x, self.y)
        self.showObstacle(205, 305)



        self.show()

    def keyPressEvent(self, e):
        def isPrintable(key):
            printable = [
                Qt.Key_W,
                Qt.Key_S,
                Qt.Key_D,
                Qt.Key_A,
                            ]
            if key in printable:
                return True
            else:
                return False
        control = False

        if e.key() == Qt.Key_W:
            #print("w")

            self.changeHeading(0)
            self.moveCar(0,-10)

        elif e.key() == Qt.Key_S:
            #print("S")

            self.changeHeading(2)
            self.moveCar(0,10)


        elif e.key() == Qt.Key_D:
            #print("D")

            self.changeHeading(1)
            self.moveCar(10,0)

        elif e.key() == Qt.Key_A:
            #print("A")

            self.changeHeading(3)
            self.moveCar(-10,0)


    def moveCar(self, new_x, new_y):
        self.x += new_x
        self.y += new_y
        self.tank.move(self.x, self.y)

    def showObstacle(self, Obs_x, Obs_y):
        self.obstCounter += 1

        self.d.append(["O{0}".format(self.obstCounter), Obs_x, Obs_y])
        self.d[0][0] =QtWidgets.QLabel(self)
        self.d[0][0].setPixmap(QtGui.QPixmap("obsta_edited.png"))
        self.d[0][0].move(Obs_x, Obs_y)
        self.d[0][0].adjustSize()


        print("Obstacle Run")

    def changeHeading(self, directionCode):
        #direction data from IMU
        #this is temporary code
        print("current state : " + str(self.currentState) + " directionCode : " + str(directionCode))
        if self.currentState == directionCode:
            print("currentState == Directioncode")
        elif self.currentState - directionCode == -1 or self.currentState - directionCode == 3:
            print("rotate 90 degrees")
            transform = QtGui.QTransform().rotate(90)
            self.pixmap = self.pixmap.transformed(transform)
            self.tank.setPixmap(self.pixmap)
        elif self.currentState - directionCode == -2 or self.currentState - directionCode == 2:
            print("rotate 180 degree")
            transform = QtGui.QTransform().rotate(180)
            self.pixmap = self.pixmap.transformed(transform)
            self.tank.setPixmap(self.pixmap)
        elif self.currentState - directionCode == -3 or self.currentState - directionCode == 1:
            print("rotate 270 degree")
            transform = QtGui.QTransform().rotate(270)
            self.pixmap = self.pixmap.transformed(transform)
            self.tank.setPixmap(self.pixmap)
        self.currentState = directionCode

    def printStatement(self, message):
        print("this is from print Statement in GUI")
        print(message)
