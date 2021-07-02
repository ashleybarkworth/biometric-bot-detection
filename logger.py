import csv
import time

from pynput import mouse

mouse_pressed = False
filename = 'data/events.csv'
start = time.time()


def write_row(timestamp, x, y, button, state):
    with open(filename, 'a') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([timestamp, x, y, button, state])


def write_header():
    with open(filename, 'w+') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['time', 'mouse_x', 'mouse_y', 'button', 'state'])


def on_move(x, y):
    current_time = time.time() - start
    if mouse_pressed:
        write_row(current_time, x, y, 'NoButton', 'Drag')
    else:
        write_row(current_time, x, y, 'NoButton', 'Move')


def on_click(x, y, button, pressed):
    global mouse_pressed
    global start
    current_time = time.time() - start
    if pressed:
        write_row(current_time, x, y, button, "Pressed")
        mouse_pressed = True
    else:
        write_row(current_time, x, y, button, "Released")
        mouse_pressed = False


def start_recording():
    print("recording started")
    global start
    start = time.time()
    write_header()
    m_listen = mouse.Listener(on_move=on_move, on_click=on_click)
    m_listen.start()
