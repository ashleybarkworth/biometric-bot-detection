import csv
import time
from datetime import datetime

from pynput import mouse
from pynput import keyboard

# Subdirectory folders to save mouse/keystroke data in
data_directory = '../data/'
key_folder = 'key/'
mouse_folder = 'mouse/'
events_folder = 'events/'

# Filenames to save mouse/keystroke data to
key_filename = datetime.now().strftime("%Y-%m-%d-%H-%M.csv")
mouse_filename = datetime.now().strftime("%Y-%m-%d-%H-%M.csv")

# Complete filepaths for mouse/keystroke data
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

# Listeners
global m_listen
global k_listen


def get_directory(data_type, user_type):

    directory = ''
    data_type_directory = key_folder if data_type == 'key' else mouse_folder

    if user_type == 'simple':
        directory = data_directory + data_type_directory + events_folder + 'simplebot/'
    elif user_type == 'advanced':
        directory = data_directory + data_type_directory + events_folder + 'advancedbot/'
    elif user_type == 'human':
        directory = data_directory + data_type_directory + events_folder + 'human/'

    return directory


def create_key_filename(user_type, start_time):
    """
    Generates a unique filename to store the keystroke activity for this recording sessions
    :param user_type: HUMAN, SIMPLE_BOT, or ADV_BOT
    :param start_time: Time that recording started
    :return: complete mouse_filename to write activity to
    """
    global key_filepath
    directory = get_directory('key', user_type)

    key_filepath = directory + key_filename


def create_mouse_filename(user_type, start_time):
    """
    Generates a unique filename to store the mouse activity for this recording sessions
    :param user_type: HUMAN, SIMPLE_BOT, or ADV_BOT
    :param start_time: Time that recording started
    :return: complete mouse_filename to write activity to
    """
    global mouse_filepath
    directory = get_directory('mouse', user_type)

    filename = ''.join([str(start_time).replace('.', ''), '.csv'])
    mouse_filepath = directory + mouse_filename


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
        csv_writer.writerow(['Key pressed', 'Key released', 'Time'])


def write_mouse_header():
    with open(mouse_filepath, 'x') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['time', 'mouse_x', 'mouse_y', 'button', 'state'])


def on_press(key):
    global keydata
    keydata = str(key)
    keydata = keydata.replace("'", "")
    counter_t = round(time.time() - start_key_time, 2)
    write_key_row(keydata, 'None', counter_t)


def on_release(key):

    counter_time = round(time.time() - start_key_time, 2)
    # r.append(counter_time)
    write_key_row('None', key, counter_time)

    # print('{0} released'.format(key))
    if key == keyboard.Key.esc:
        # Stop listener
        return False


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
    global k_listen
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

    create_key_filename(user_type, start_mouse_time)
    write_key_header()

    k_listen = keyboard.Listener(on_press=on_press, on_release=on_release)
    k_listen.start()


def start_mouse_logging(user_type):
    print('Recording mouse started')
    global start_mouse_time, m_listen

    start_mouse_time = time.time()

    create_mouse_filename(user_type, start_mouse_time)
    write_mouse_header()

    m_listen = mouse.Listener(on_move=on_move, on_click=on_click)
    m_listen.start()
