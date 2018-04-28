import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtCore import Qt
from pynput import keyboard

class App(QWidget):
    #def __init__(self, OtherWindow):
    def __init__(self):
        super().__init__()
        print("ths one is on github!!")
        self.setGeometry(100,100,440,800)

        #Assuming the world is 147m(height) by 77m(height)

        self.pixbycm_height = 800/147
        self.pixbycm_width = 440/77


        self.setWindowTitle("New GUI Interface Window")
        self.currentAngle = 0

        self.obstCounter = 0
        self.x = 20
        self.y = 710
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


    def moveCar(self, curPos):
        new_x = curPos[0]
        new_y = curPos[1]
        self.x += new_x
        self.y += new_y
        self.tank.move(self.x, self.y)
        print(self.showTankPos())

        #for testing show obstacle method /// comment it out later
        if self.showTankPos() == [20, 590]:
            print("show Obstacle is called")
            self.showObstacle(20,round(-15 * self.pixbycm_height,2) + 590)
        elif self.showTankPos() == [60, 590]:
            print("show obstacle is called again")
            self.showObstacle(90,590)

    def showTankPos(self):
        return [self.x, self.y]



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



        #print(self.d)


    def showObstacle(self,ObstPos):
        print("test if there is already another obstacle")
        x = ObstPos[0]
        y = ObstPos[1]
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
        #print(self.d)
        print(self.d[self.obstCounter])
        self.d[self.obstCounter][0].show()
        print(self.obstCounter)
        self.obstCounter += 1


    def rotate(self, angle):
        if self.currentAngle == angle:
            print("current angle and received angle are same")
            return
        else:
            if (abs(angle) == 180):
                angle = 180;
            elif(angle < -45 and angle >= -135):
                angle = 90
            elif(angle < -135 or angle >= 130):
                angle = 180
            elif(angle <45 and angle >= -45):
                #dont rotate
                return
            elif(angle> 45 and angle <= 135):
                angle = 270

        self.currentAngle = angle


        transform = QtGui.QTransform().rotate(angle)
        self.pixmap = self.pixmap.transformed(transform)
        self.tank.setPixmap(self.pixmap)


    def printStatement(self, message):
        print("this is from print Statement in GUI")
        print(message)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()

    sys.exit(app.exec_())

