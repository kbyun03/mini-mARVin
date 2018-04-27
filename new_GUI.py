import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtCore import Qt
from pynput import keyboard

class App(QWidget):
    def __init__(self, OtherWindow):
    #def __init__(self):
        super().__init__()
        print("ths one is on github")
        self.setGeometry(100,100,440,800)

        #Assuming the world is 2m(width) by 1m(height)


        self.setWindowTitle("New GUI Interface Window")
        self.currentState = 0

        #self.directionCode =0
        self.flag = 0

        self.obstCounter = 0
        self.x = 20
        self.y = 710
        self.d = []

        #loading image for tank

        #self.tank = QtWidgets.QLabel(self)
        #self.tank.setPixmap(QtGui.QPixmap('smallcar.png'))
        #self.tank.move(self.x,self.y)
        #self.tank.adjustSize()

        self.image= QtGui.QImage('smallcar.png')
        self.rectImage = QtGui.QImage('rectOutline.png')

        self.pixmap = QtGui.QPixmap(self.image)
        self.pixmap_rect = QtGui.QPixmap(self.rectImage)

        self.tank = QtWidgets.QLabel(self)
        self.tank.setAlignment(QtCore.Qt.AlignCenter)
        self.tank.setPixmap(self.pixmap)
        self.tank.adjustSize()
        self.tank.move(self.x, self.y)


        self.boarder = QtWidgets.QLabel(self)
        self.boarder.setAlignment(QtCore.Qt.AlignCenter)
        self.boarder.setPixmap(self.pixmap_rect)
        self.boarder.adjustSize()

        self.showObstacle(205, 305)
        self.showObstacle(210,315)
        #self.showObstacle(20, 540)

        self.showObstacle(115,15)
        self.show()

    """
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
    """


    def moveCar(self, new_x, new_y):
        self.x += new_x
        self.y += new_y
        self.tank.move(self.x, self.y)

    def showTankPos(self):
        return [self.x, self.y]

    def detect(self, new_x, new_y, isDetected):
        print("detected function working")
        if isDetected == True:
            self.moveCar(new_x, new_y)

        else:
            print("detected function not working")



    def showObstacle(self, Obs_x, Obs_y):

        self.obstImage = QtGui.QImage('obsta_edited.png')
        self.pixmap_obst = QtGui.QPixmap(self.obstImage)
        self.d.append("O{0}".format(self.obstCounter))


        label = QtWidgets.QLabel(self)
        label.setPixmap(self.pixmap_obst)
        label.move(Obs_x, Obs_y)
        label.adjustSize()
        label.show()  # <---show QLabel

        self.d[self.obstCounter] = label
        self.obstCounter += 1
        print(self.d)
        #print("Obstacle Run")


    """

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
    """

    def rotate(self, angle):
        transform = QtGui.QTransform().rotate(angle)
        self.pixmap = self.pixmap.transformed(transform)
        self.tank.setPixmap(self.pixmap)


    def printStatement(self, message):
        print("this is from print Statement in GUI")
        print(message)

"""
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()

    sys.exit(app.exec_())
"""
