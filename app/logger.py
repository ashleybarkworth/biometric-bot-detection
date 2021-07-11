import csv
import time
from pynput import mouse

mouse_pressed = False
filepath = ''
start = time.time()


def create_file_name(data_directory, user_type, start_time):
    """
    Generates a unique filename to store the mouse/keyboard activity for this recording sessions
    :param data_directory: filepath of data directory for activity data
    :param user_type: HUMAN, SIMPLE_BOT, or ADV_BOT
    :param start_time: Time that recording started
    :return: complete filepath to write activity to
    """
    global filepath
    directory = ''
    if user_type == 'simple':
        directory = data_directory + 'simplebot/'
    elif user_type == 'advanced':
        directory = data_directory + 'advancedbot/'
    elif user_type == 'human':
        directory = data_directory + 'human/'

    filename = ''.join([str(start_time).replace('.', ''), '.csv'])
    filepath = directory + filename


def write_row(timestamp, x, y, button, state):
    with open(filepath, 'a') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([timestamp, x, y, button, state])


def write_header():
    with open(filepath, 'x') as csv_file:
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
        write_row(current_time, x, y, button, 'Pressed')
        mouse_pressed = True
    else:
        write_row(current_time, x, y, button, 'Released')
        mouse_pressed = False


def start_recording(data_directory, user_type):
    print('Recording started')
    global start
    start = time.time()

    create_file_name(data_directory, user_type, start)
    write_header()

    m_listen = mouse.Listener(on_move=on_move, on_click=on_click)
    m_listen.start()
