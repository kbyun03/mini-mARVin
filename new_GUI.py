import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtCore import Qt
from pynput import keyboard

class App(QWidget):
    def __init__(self, OtherWindow):
    #def __init__(self):
        super().__init__()
        print("ths one is on github!!")
        self.setGeometry(100,100,400,720)
        # 715 x 385 => 720x  390
        #Assuming the world is 147m(height) by 77m(height)

        self.pixbycm_height = 630/147
        self.pixbycm_width = 320/77


        self.setWindowTitle("New GUI Interface Window")
        self.currentAngle = 0

        self.obstCounter = 0
        self.x = 10
        self.y = 650
        self.d = []

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
        self.createObstacle()
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
        self.x = new_x * self.pixbycm_width + 10
        self.y = 650 - (new_y * self.pixbycm_height)
        self.tank.move(self.x, self.y)
        print(self.showTankPos())
        if self.showTankPos() == [20, 590]:
            print("show Obstacle is called")
            self.showObstacle(20,round(-15 * self.pixbycm_height,2) + 590)
        elif self.showTankPos() == [60, 590]:
            print("show obstacle is called again")
            self.showObstacle(90,590)


    def showTankPos(self):
        return [self.x, self.y]

    def detect(self, new_x, new_y, isDetected):
        print("detected function working")
        if isDetected == True:
            self.moveCar(new_x, new_y)

        else:
            print("detected function not working")



    def createObstacle(self):

        self.obstImage = QtGui.QImage('obsta_edited.png')
        self.pixmap_obst = QtGui.QPixmap(self.obstImage)

        for i in range(0,80):
            self.d.append(["O{0}".format(i), []])
            label = QtWidgets.QLabel(self)
            label.setPixmap(self.pixmap_obst)
            label.move(9999, 9999)
            label.adjustSize()
            self.d[i][0] = label

        """
        self.d.append(["O{0}".format(self.obstCounter), []])
        label = QtWidgets.QLabel(self)
        label.setPixmap(self.pixmap_obst)
        label.move(9999, 9999)
        label.adjustSize()
        label.show()
        self.d[self.obstCounter][0] = label
        """

        print(self.d)


    def showObstacle(self,x ,y):
        print("test if there is already another obstacle")
        print([x,y])
        print(self.d[self.obstCounter][1])
        if self.obstCounter != 0:
            for i in range(0,self.obstCounter):
                if [x,y] == self.d[i][1]:
                    print("The Obstacle is already there")
                    return


        print("The Obstacle is not there")
        self.d[self.obstCounter][0].move(x, y)
        self.d[self.obstCounter][1].append(x)
        self.d[self.obstCounter][1].append(y)
        print(self.d)
        print(self.d[self.obstCounter])
        self.d[self.obstCounter][0].show()
        print(self.obstCounter)
        self.obstCounter += 1





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
