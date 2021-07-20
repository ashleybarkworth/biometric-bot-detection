import csv
import os

from actions import MouseEvent, MouseState, MouseAction, ActionType
from featureExtraction.sessions import Session

data_directory = '../data/'

key_folder = 'key/'
mouse_folder = 'mouse/'

events_folder = 'events/'
actions_folder = 'actions/'
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


def smooth_bot_point_clicks(actions):

    for i, action in enumerate(actions):

        action = actions[i]
        if i > 0:
            prev_action_event = actions[i - 1].events[-1]
            last_x, last_y = prev_action_event.x, prev_action_event.y
            index = 0 if action.action_type.value == ActionType.MM.value else -4
            action.events[index].x, action.events[index].y = last_x, last_y
            if action.action_type.value != ActionType.MM.value:
                del action.events[-3]
            print('done')

    return actions



def point_drag(i, rows):
    # Remove single 'Drag' events between mouse press and release ()
    return 0 < i < len(rows) - 1 and rows[i]['state'] == 'Drag' \
           and rows[i - 1]['state'] == 'Pressed' \
           and rows[i + 1]['state'] == 'Released'


def pre_process(rows):
    new_rows = [row for i, row in enumerate(rows) if not point_drag(i, rows)]
    return new_rows


def parse_actions_from_events(subdirectory, usertype, filename):
    mouse_events = []
    actions = []

    filepath = os.path.join(subdirectory, filename)

    with open(filepath) as csv_file:
        csv_reader = csv.DictReader(csv_file)
        rows = list(csv_reader)
        processed_rows = pre_process(rows)
        for i, row in enumerate(processed_rows):
            time = row['time']
            x = row['mouse_x']
            y = row['mouse_y']
            button = row['button']
            state = row['state']

            mouse_event = MouseEvent(time, x, y, button, state)

            if mouse_event.state == MouseState.RELEASED:
                # Point and Click Action
                if prev_event is not None and prev_event.state == MouseState.PRESSED:
                    mouse_events.append(mouse_event)
                    actions.append(MouseAction(ActionType.PC, mouse_events))
                    mouse_events = []
                # Drag and Drop Action
                if prev_event is not None and prev_event.state == MouseState.DRAGGED:
                    mouse_events.append(mouse_event)
                    actions.append(MouseAction(ActionType.DD, mouse_events))
                    mouse_events = []
            elif mouse_event.state == MouseState.PRESSED:
                next_event = processed_rows[i + 1]
                # Check if next event is a mouse drag, in which case create Mouse Move action
                # and start_time new Drag and Drop action
                if MouseState(next_event['state']) == MouseState.DRAGGED:
                    actions.append(MouseAction(ActionType.MM, mouse_events))
                    mouse_events = [mouse_event]
                else:
                    mouse_events.append(mouse_event)
            # Mouse movement (either mouse held down or not)
            else:
                mouse_events.append(mouse_event)

            prev_event = mouse_event

    if usertype == 'simplebot':
        # pc_actions = [action for action in actions if action.action_type.value == ActionType.PC.value]
        actions = smooth_bot_point_clicks(actions)

    return actions


def create_action_file(actions, folder, filename):
    filepath = os.path.join(data_directory, mouse_folder, actions_folder, folder, filename)
    with open(filepath, 'w') as file:
        writer = csv.writer(file)
        write_action_csv_header(writer)
        for action in actions:
            action_feature_row = action.calculate_features()
            writer.writerow(action_feature_row)


def write_action_csv_header(writer):
    header = ['action_type', 'duration', 'direction', 'trajectory', 'distance', 'straightness', 'num_points',
              'max_deviation', 'sum_of_angles', 'curvature', 'omega', 'vx', 'vy', 'v', 'a', 'j']
    writer.writerow(header)


def write_new_mouse_header(writer):
    header = ['Key pressed', 'Key released', 'Time', 'Hold Time', 'Consecutive Press Release']
    writer.writerow(header)


def create_new_key_file(rows, filepath):
    with open(filepath, 'w') as file:
        writer = csv.writer(file)
        write_new_mouse_header(writer)
        for row in rows:
            writer.writerow(row)


def create_session_file(session, folder, filename):
    session_feature_row = session.calculate_features()
    filepath = os.path.join(data_directory, mouse_folder, sessions_folder, folder, filename)
    with open(filepath, 'w') as file:
        writer = csv.writer(file)
        write_session_csv_header(writer)
        writer.writerow(session_feature_row)


def write_session_csv_header(writer):
    header = ['num_actions', 'pc_mean_inter_action_time', # 'pc_sd_inter_action_time',
              'mm_mean_inter_action_time', # 'mm_sd_inter_action_time',
              'dd_mean_inter_action_time', # 'dd_sd_inter_action_time',
              'mm_avg_v',  # 'mm_sd_v',  # 'mm_max_v', 'mm_min_v',
              # 'mm_avg_a', 'mm_sd_a',  # 'mm_max_a', 'mm_min_a',
              'mm_avg_j', # 'mm_sd_j',  # 'mm_max_j', 'mm_min_j',
              'mm_avg_duration', # 'mm_sd_duration',  # 'mm_max_duration', 'mm_min_duration',
              # 'mm_avg_trajectory', 'mm_sd_trajectory', 'mm_max_trajectory', 'mm_min_trajectory',
              # 'mm_avg_distance', 'mm_sd_distance', 'mm_max_distance', 'mm_min_distance',
              'mm_avg_straightness', # 'mm_sd_straightness',  # 'mm_max_straightness', 'mm_min_straightness',
              # 'mm_avg_num_points', 'mm_sd_num_points',  # 'mm_max_num_points', 'mm_min_num_points',
              # 'mm_avg_curvature', 'mm_sd_curvature',
              # 'mm_avg_angle_sum', 'mm_sd_angle_sum',  # 'mm_max_angle_sum', 'mm_min_angle_sum',
              # 'mm_mean_max_deviation', 'mm_sd_max_deviation',
              # 'pc_avg_v', 'pc_sd_v',  # 'pc_max_v', 'pc_min_v',
              # 'pc_avg_a', 'pc_sd_a',  # 'pc_max_a', 'pc_min_a',
              # 'pc_avg_j', 'pc_sd_j',  # 'pc_max_j', 'pc_min_j',
              'pc_avg_duration', # 'pc_sd_duration',  # 'pc_max_duration', 'pc_min_duration',
              # 'pc_avg_distance', 'pc_sd_distance', 'pc_max_distance', 'pc_min_distance',
              'pc_avg_straightness', # 'pc_sd_straightness',  # 'pc_max_straightness', 'pc_min_straightness',
              # 'pc_avg_num_points', 'pc_sd_num_points',  # 'pc_max_num_points', 'pc_min_num_points',
              # 'pc_avg_curvature', 'pc_sd_curvature',
              # 'pc_avg_angle_sum', 'pc_sd_angle_sum',  # 'pc_max_angle_sum', 'pc_min_angle_sum',
              # 'pc_mean_max_deviation', 'pc_sd_max_deviation',
              'avg_click_time', # 'pc_sd_click_time',  # 'max_click_time', 'min_click_time',
              'avg_approach_time', # 'pc_sd_approach_time',  # 'max_approach_time', 'min_approach_time',
              # 'dd_avg_v', 'dd_sd_v',  # 'dd_max_v', 'dd_min_v',
              # 'dd_avg_a', 'dd_sd_a',  # 'dd_max_a', 'dd_min_a',
              # 'dd_avg_j', 'dd_sd_j',  # 'pc_max_j', 'pc_min_j',
              'dd_avg_duration', # 'dd_sd_duration',  # 'dd_max_duration', 'dd_min_duration',
              # 'dd_avg_trajectory', 'dd_sd_trajectory', 'dd_max_trajectory', 'dd_min_trajectory',
              # 'dd_avg_distance', 'dd_sd_distance', 'dd_max_distance', 'dd_min_distance',
              'dd_avg_straightness'] #'dd_sd_straightness']  # 'dd_max_straightness', 'dd_min_straightness',
              # 'dd_avg_num_points', 'dd_sd_num_points',  # 'dd_max_num_points', 'dd_min_num_points',
              # 'dd_avg_curvature', 'dd_sd_curvature']
    # 'dd_avg_angle_sum', 'dd_sd_angle_sum',  # 'dd_max_angle_sum', 'dd_min_angle_sum'
    # 'dd_mean_max_deviation', 'dd_sd_max_deviation']

    writer.writerow(header)


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
            print(i)
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


def extract_mouse_features():
    mouse_events_folder = os.path.join(data_directory, mouse_folder, events_folder)
    # mouse_actions_folder = os.path.join(data_directory, mouse_folder, actions_folder)
    # # For each of the user type folders (advancedBot, human, simpleBot)
    # search_paths = [os.path.join(data_directory, events_folder, user_folder, '/*.csv') for user_folder in
    #                 [human_folder, simplebot_folder, advancedbot_folder]]
    # files = [f for f in glob.glob(search_path)]
    for folder in os.listdir(mouse_events_folder):
        # Ensure it's a directory
        subdirectory = os.path.join(mouse_events_folder, folder)
        if os.path.isdir(subdirectory):
            # For each file in the user type folder
            for file in os.listdir(subdirectory):
                if not file.startswith('.'):
                    actions = parse_actions_from_events(subdirectory, folder, file)
                    create_action_file(actions, folder, file)
                    session = Session(file, actions, folder)
                    create_session_file(session, folder, file)


def main():
    extract_key_features()
    extract_mouse_features()


if __name__ == '__main__':
    main()
