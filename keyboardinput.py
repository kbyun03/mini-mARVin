from pynput import keyboard

def on_key_release(key):
    print('Released Key %s' %key)

def on_key_listen(key):
    print('Pressed Key %s' %key)
with keyboard.Listener(on_release = on_key_release, on_press = on_key_listen) as listener:
    listener.join()
