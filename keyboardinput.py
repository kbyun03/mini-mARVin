import numpy as np
from matplotlib import pyplot as plt
from matplotlib import animation
import _thread
from pynput import keyboard
import time
from random import randint
fig = plt.figure()
fig.set_dpi(100)
fig.set_size_inches(8, 6.5)
k = ''

x = 0
y = 0

ax = plt.axes(xlim=(0, 10), ylim=(0, 10))
patch = plt.Circle((5, -5), 0.75, fc='y')

def on_press(key):
    global x, y, k
    try: k = key.char # single-char keys
    except: k = key.name # other keys
    if key == keyboard.Key.esc: return False # stop listener

def getData():
    global y, x, k
    if k == 'w':
        y = y +0.1
        print('Key pressed: w')
        print(y)
    elif k == 's':
        y = y - 0.1
        print('Key pressed: s')
        print(y)
    elif k == 'a':
        x = x - 0.1
        print('Key pressed: k')
        print(x)
    elif k == 'd':
        x = x + 0.1
        print('Key pressed: d')
        print(x)
    result = [x,y]
    return result


def init():
    global x, y
    patch.center = (x, y)
    print("this section run")
    ax.add_patch(patch)
    return patch,

def animate(i):

    while (True):
        global x, y, k
        x, y = patch.center
        [x,y] = getData()
        patch.center = (x, y)

        return patch,


def showAnimation():
    anim = animation.FuncAnimation(fig, animate,
                                   init_func=init,
                                   frames=360,
                                   interval=20,
                                   blit=True)

    plt.show()

    return anim

try:
    lis = keyboard.Listener(on_press=on_press)
    lis.start() # start to listen on a separate thread

except:
    print("error")

while 1:
    test1 = showAnimation()