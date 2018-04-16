import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QVBoxLayout, QSizePolicy, QMessageBox, QWidget, QPushButton
from PyQt5.QtGui import QIcon

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib.animation import FuncAnimation
from pynput import keyboard
import random


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.left = 50
        self.top = 50
        self.title = 'Moving'
        self.width = 840
        self.height = 600
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        print("other section runs")
        button = QPushButton('PyQt5 button', self)
        button.setToolTip('This s an example button')
        button.move(600, 0)
        button.resize(140, 100)

        m = PlotCanvas(self, width = 6, height = 5)
        
        self.show()


class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None, width=9, height=7.5, dpi=100):
        self.fig = plt.figure(figsize=(width, height), dpi=dpi)
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        self.k = ''
        self.x = 0
        self.y = 0
        self.ax = plt.axes(xlim = (-10,20), ylim = (-10,20))
        self.patch = plt.Circle((5,-5), 0.75, fc = 'y')
        self.result()

    def start(self):

        self.patch.center = (self.x,self.y)
        print("this section runs")
        self.ax.add_patch(self.patch)
        return self.patch,

    def animate(self, i):
        while (True):

            self.getData()
            self.patch.center = (self.x, self.y)

            return self.patch,

    def showAnimation(self):
        anim = animation.FuncAnimation(self.fig, self.animate,
                                       init_func=self.start,
                                       frames=360,
                                       interval=20,
                                       blit=True)
        lis = keyboard.Listener(on_press=self.on_press)
        lis.start()
        plt.show()
        return anim

    def on_press(self,key):

        try:
            self.k = key.char  # single-char keys
        except:
            self.k = key.name  # other keys
        if key == keyboard.Key.esc: return False  # stop listener

    def getData(self):
        if self.k == 'w':
            self.y = self.y + 0.1
            print('Key pressed: w')
            print(self.y)
        elif self.k == 's':
            self.y = self.y - 0.1
            print('Key pressed: s')
            print(self.y)
        elif self.k == 'a':
            self.x = self.x - 0.1
            print('Key pressed: k')
            print(self.x)
        elif self.k == 'd':
            self.x = self.x + 0.1
            print('Key pressed: d')
            print(self.x)

    def result(self):
        self.showAnimation()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
