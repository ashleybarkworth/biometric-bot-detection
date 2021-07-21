import csv
import os

data_directory = '../data/'
key_folder = 'key/'
events_folder = 'events/'
sessions_folder = 'sessions/'

simplebot_folder = 'simplebot/'
advancedbot_folder = 'advancedbot/'
human_folder = 'human/'

shifted = {'1': '!', '2': '@', '3': '#', 'a': 'A', 'b': 'B', 'c': 'C', 'p': 'P'}

unshifted = dict([reversed(i) for i in shifted.items()])


class bidict(dict):
    def __init__(self, *args, **kwargs):
        super(bidict, self).__init__(*args, **kwargs)
        self.inverse = {}
        for key, value in self.items():
            self.inverse.setdefault(value, []).append(key)

    def __setitem__(self, key, value):
        if key in self:
            self.inverse[self[key]].remove(key)
        super(bidict, self).__setitem__(key, value)
        self.inverse.setdefault(value, []).append(key)

    def __delitem__(self, key):
        self.inverse.setdefault(self[key], []).remove(key)
        if self[key] in self.inverse and not self.inverse[self[key]]:
            del self.inverse[self[key]]
        super(bidict, self).__delitem__(key)


def write_new_key_header(writer):
    header = ['Key pressed', 'Key released', 'Time', 'Hold Time', 'Consecutive Press Release']
    writer.writerow(header)


def create_new_key_file(rows, filepath):
    with open(filepath, 'w') as file:
        writer = csv.writer(file)
        write_new_key_header(writer)
        for row in rows:
            writer.writerow(row)


def not_a_typo(key_pressed, key_released):
    pressed_key = key_pressed != 'None' and 'Key.' in key_pressed or key_pressed in shifted.keys() or key_pressed in unshifted.keys()
    released_key = key_released != 'None' and 'Key.' in key_released or key_released in shifted.keys() or key_released in unshifted.keys()
    return pressed_key or released_key


def parse_key_file(subdirectory, filename):
    key_pressed_dict = {}
    last_pressed_time = 0
    # for up_up variable
    last_released_time = 0
    second_last_released_time = 0
    new_rows = []
    new_filename = 'new_mouse_data.csv'
    shift_is_pressed = False
    filepath = os.path.join(subdirectory, filename)

    with open(filepath) as csv_file:
        csv_reader = csv.DictReader(csv_file)
        rows = list(csv_reader)
        for i, row in enumerate(rows):
            row = rows[i]
            key_pressed = row['Key pressed']
            key_released = row['Key released'].replace("'", "")
            time = row['Time']
            hold_time = ''
            press_release = ''
            # Key press event
            if not_a_typo(key_pressed, key_released):
                if key_pressed != 'None' and 'Key.' in key_pressed or key_pressed in shifted.keys() or key_pressed in unshifted.keys():
                    last_pressed_time = time
                    key_pressed_dict[key_pressed] = float(time)
                    if key_pressed == 'Key.shift':
                        shift_is_pressed = True
                # Key Release event
                elif key_released != 'None':
                    check_for_key = key_released
                    # Key released is uppercase or symbol
                    if shift_is_pressed:
                        # It was typed as uppercase
                        if key_released in key_pressed_dict.keys():
                            check_for_key = key_released
                        # It was typed as lowercase
                        else:
                            check_for_key = unshifted[key_released]
                    # Key released is lowercase or number
                    else:
                        # It was typed as lowercase
                        if key_released in key_pressed_dict.keys():
                            check_for_key = key_released
                        # It was typed as uppercase
                        else:
                            check_for_key = shifted[key_released]

                    # Check when this key was pressed
                    press_time = key_pressed_dict[check_for_key]
                    hold_time = float(time) - float(press_time)
                    # Time between last press and current release
                    press_release = float(time) - float(last_pressed_time)

                    if key_released == 'Key.shift':
                        shift_is_pressed = False

                    if 'Key.' not in key_released:
                        if key_released in shifted.keys():
                            # Lowercase release: delete the uppercase entry
                            opposite_key = shifted[key_released]
                            key_pressed_dict.pop(opposite_key, None)
                        else:
                            # Uppercase release: delete lowercase entry
                            opposite_key = unshifted[key_released]
                            key_pressed_dict.pop(opposite_key, None)

                    # Delete entry from dictionary
                    key_pressed_dict.pop(key_released, None)

                new_row = [key_pressed, key_released, time, hold_time, press_release]
                new_rows.append(new_row)

    create_new_key_file(new_rows, filename)


def extract_key_features():
    key_events_folder = os.path.join(data_directory, key_folder, events_folder)
    # For each of the user type folders (advancedBot, human, simpleBot)
    for folder in os.listdir(key_events_folder):
        # Ensure it's a directory
        subdirectory = os.path.join(key_events_folder, folder)
        if os.path.isdir(subdirectory):
            # For each file in the user type folder
            for file in os.listdir(subdirectory):
                # Ensure it's a directory
                if not file.startswith('.'):
                    parse_key_file(subdirectory, file)
