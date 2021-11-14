import csv
import errno
import os.path
import time
from datetime import datetime
import os

from pynput import mouse
from pynput import keyboard

# Subdirectory folders to save mouse/keystroke data in
data_folder = 'data/'
key_folder = 'key/'
mouse_folder = 'mouse/'
events_folder = 'events/'


# Time that app starts running (used in key and mouse file names)
start_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

global directory

# Complete file paths for mouse/keystroke data
key_filepath = ''
mouse_filepath = ''

# Start times for mouse and keystroke recording
start_mouse_time = time.time()
start_key_time = time.time()

# Mouse global variables
mouse_pressed = False

# Key global variables
keydata = 'a'

# Listeners
global m_listen
global k_listen


def create_events_folder(user_type):
    global directory
    folder_name = ''.join([user_type, '-', start_time])
    directory = os.path.join(data_folder, events_folder, folder_name)
    try:
        os.makedirs(directory)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise e
    return directory


def get_key_data_filepath():
    """
    Sets key_filepath to the complete file path of the key event data CSV file
    """
    global key_filepath, directory
    filename = 'key.csv'
    key_filepath = os.path.join(directory, filename)


def get_mouse_data_filepath():
    """
    Sets mouse_filepath to the complete file path of the mouse event data CSV file
    """
    global mouse_filepath
    filename = 'mouse.csv'
    mouse_filepath = os.path.join(directory, filename)


def write_key_header():
    with open(key_filepath, 'x') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Time', 'Key pressed', 'Key released'])


def write_mouse_header():
    with open(mouse_filepath, 'x') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['time', 'mouse_x', 'mouse_y', 'button', 'state'])


def write_key_row(timestamp, keypressed, keyreleased):
    with open(key_filepath, 'a') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow([timestamp, keypressed, keyreleased])


def write_mouse_row(timestamp, x, y, button, state):
    with open(mouse_filepath, 'a') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([timestamp, x, y, button, state])


def on_press(key):
    global keydata, start_key_time
    keydata = str(key).strip("'")
    current_time = round(time.time() - start_key_time, 5)
    write_key_row(current_time, keydata, 'None')


def on_release(key):
    global keydata, start_key_time
    keydata = str(key).strip("'")
    current_time = round(time.time() - start_key_time, 5)
    write_key_row(current_time, 'None', keydata)


def on_move(x, y):
    current_time = time.time() - start_mouse_time
    if mouse_pressed:
        write_mouse_row(current_time, x, y, 'NoButton', 'Drag')
    else:
        write_mouse_row(current_time, x, y, 'NoButton', 'Move')


def on_click(x, y, button, pressed):
    global mouse_pressed
    global start_mouse_time
    current_time = time.time() - start_mouse_time
    if pressed:
        write_mouse_row(current_time, x, y, button, 'Pressed')
        mouse_pressed = True
    else:
        write_mouse_row(current_time, x, y, button, 'Released')
        mouse_pressed = False


def stop_key_logging():
    print('Recording keystrokes stopped')
    if k_listen is not None:
        k_listen.stop()
        k_listen.join()


def stop_mouse_logging():
    print('Recording mouse stopped')
    global m_listen
    if m_listen is not None:
        m_listen.stop()
        m_listen.join()


def start_key_logging(user_type):
    print('Recording keystrokes started')
    global start_key_time, k_listen
    start_key_time = time.time()
    create_events_folder(user_type)

    get_key_data_filepath()
    write_key_header()

    k_listen = keyboard.Listener(on_press=on_press, on_release=on_release)
    k_listen.start()


def start_mouse_logging(user_type):
    print('Recording mouse started')
    global start_mouse_time, m_listen
    start_mouse_time = time.time()

    get_mouse_data_filepath()
    write_mouse_header()

    m_listen = mouse.Listener(on_move=on_move, on_click=on_click)
    m_listen.start()
