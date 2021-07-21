import csv
import os.path
import time
from datetime import datetime
from os.path import join

from pynput import mouse
from pynput import keyboard

# Subdirectory folders to save mouse/keystroke data in
data_directory = '../data/'
key_folder = 'key/'
mouse_folder = 'mouse/'
events_folder = 'events/'


# Time that app starts running (used in key and mouse file names)
start_time = datetime.now().strftime('%Y%m%d-%H%M%S')

# Complete file paths for mouse/keystroke data
key_filepath = ''
mouse_filepath = ''

# Start times for mouse and keystroke recording
start_mouse_time = time.time()
start_key_time = time.time()

# Mouse global variables
mouse_pressed = False

# Key global variables
p = []
r = []
count = 0
keydata = 'a'
kp_dict = {}
d = []

shifted = {
    '1': '!',
    '2': '@',
}

# Listeners
global m_listen
global k_listen


def get_directory(data_type, user_type):
    directory = ''
    data_type_directory = key_folder if data_type == 'key' else mouse_folder

    if user_type == 'simple':
        directory = join(data_directory, data_type_directory, events_folder, 'simplebot/')
    elif user_type == 'advanced':
        directory = join(data_directory, data_type_directory, events_folder, 'advancedbot/')
    elif user_type == 'human':
        directory = join(data_directory, data_type_directory, events_folder, 'human/')

    return directory


def get_key_data_filepath(user_type):
    """
    Sets key_filepath to the complete file path of the key event data CSV file
    :param user_type: human, simple, or advanced
    """
    global key_filepath
    filename = ''.join([start_time, '_', user_type, '.csv'])
    directory = get_directory('key', user_type)
    key_filepath = os.path.join(directory, filename)


def get_mouse_data_filepath(user_type):
    """
    Sets mouse_filepath to the complete file path of the mouse event data CSV file
    :param user_type: human, simple, or advanced
    """
    global mouse_filepath
    filename = ''.join([start_time, '_', user_type, '.csv'])
    directory = get_directory('mouse', user_type)
    mouse_filepath = os.path.join(directory, filename)


# def write_key_row(keypressed, keyreleased, timestamp, Hold_time, press_release):
#     with open(key_filepath, 'a') as f:
#         csv_writer = csv.writer(f)
#         csv_writer.writerow([keypressed, keyreleased, timestamp, Hold_time, press_release])


def write_key_row(keypressed, keyreleased, timestamp):
    with open(key_filepath, 'a') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow([keypressed, keyreleased, timestamp])


def write_mouse_row(timestamp, x, y, button, state):
    with open(mouse_filepath, 'a') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([timestamp, x, y, button, state])


def write_key_header():
    with open(key_filepath, 'x') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Time', 'Key pressed', 'Key released'])


def write_mouse_header():
    with open(mouse_filepath, 'x') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['time', 'mouse_x', 'mouse_y', 'button', 'state'])


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

    get_key_data_filepath(user_type)
    write_key_header()

    k_listen = keyboard.Listener(on_press=on_press, on_release=on_release)
    k_listen.start()


def start_mouse_logging(user_type):
    print('Recording mouse started')
    global start_mouse_time, m_listen

    start_mouse_time = time.time()

    get_mouse_data_filepath(user_type)
    write_mouse_header()

    m_listen = mouse.Listener(on_move=on_move, on_click=on_click)
    m_listen.start()
