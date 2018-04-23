import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt
from pynput import keyboard


class App(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setGeometry(100, 100, 1000, 800)
        self.setWindowTitle("New GUI Interface Window")
        self.obstCounter = 0
        self.x = 200
        self.y = 200
        self.d = []
        self.l2 = QtWidgets.QLabel(self)
        self.l2.setPixmap(QtGui.QPixmap('smallcar.png'))
        self.l2.move(self.x, self.y)
        self.l2.adjustSize()

        self.showObstacle(15, 15)
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
            # print("w")
            self.moveCar(0, -10)
        elif e.key() == Qt.Key_S:
            # print("S")
            self.moveCar(0, 10)
        elif e.key() == Qt.Key_D:
            # print("D")
            self.moveCar(10, 0)
        elif e.key() == Qt.Key_A:
            # print("A")
            self.moveCar(-10, 0)

    def moveCar(self, new_x, new_y):
        self.x += new_x
        self.y += new_y
        self.l2.move(self.x, self.y)

    def showObstacle(self, Obs_x, Obs_y):
        self.obstCounter += 1

        self.d.append(["O{0}".format(self.obstCounter), Obs_x, Obs_y])
        self.d[0][0] = QtWidgets.QLabel(self)
        self.d[0][0].setPixmap(QtGui.QPixmap("obsta_edited.png"))
        self.d[0][0].move(Obs_x, Obs_y)
        self.d[0][0].adjustSize()

        print("Obstacle Run")

    def detect(self):
        # this is where the sensor sends the data and checks where the obstacle is
        # for now it uses fake data
        cordinate = (205, 305)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()

    sys.exit(app.exec_())
