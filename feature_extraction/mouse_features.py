import csv
import os

from feature_extraction.actions import ActionType, MouseEvent, MouseState, MouseAction
from feature_extraction.sessions import Session

data_directory = '../data/'
mouse_folder = 'mouse/'
events_folder = 'events/'
actions_folder = 'actions/'
sessions_folder = 'sessions/'


def interpolate_points(actions):
    for i, action in enumerate(actions):
        action = actions[i]
        if i > 0:
            prev_action_event = actions[i - 1].events[-1]
            last_x, last_y = prev_action_event.x, prev_action_event.y
            index = 0 if action.action_type.value == ActionType.MM.value else -4
            action.events[index].x, action.events[index].y = last_x, last_y
            if action.action_type.value != ActionType.MM.value:
                del action.events[-3]

    # Remove the first action that clicks 'Start' button (no movement recorded)
    return actions[1:]


def remove_point_drag_click(i, rows):
    # Returns True if rows[i] is a 'Drag' event between a mouse press and release
    if 0 < i < len(rows) - 1:
        event_state = rows[i]['state']
        prev_event_state = rows[i - 1]['state']
        next_event_state = rows[i + 1]['state']
        return event_state == 'Drag' and prev_event_state == 'Pressed' and next_event_state == 'Released'
    else:
        return False


def pre_process(rows):
    new_rows = [row for i, row in enumerate(rows) if not remove_point_drag_click(i, rows)]
    return new_rows


def parse_actions_from_events(subdirectory, usertype, filename):
    mouse_events = []
    actions = []

    filepath = os.path.join(subdirectory, filename)

    with open(filepath) as csv_file:
        csv_reader = csv.DictReader(csv_file)
        rows = list(csv_reader)
        processed_rows = pre_process(rows)
        prev_event = None
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
                    if len(mouse_events) > 0:
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
        actions = interpolate_points(actions)

    return actions


def write_action_csv_header(writer):
    header = ['action_type', 'duration', 'direction', 'trajectory', 'distance', 'straightness', 'num_points',
              'max_deviation', 'sum_of_angles', 'curvature', 'omega', 'vx', 'vy', 'v', 'a', 'j']
    writer.writerow(header)


def create_action_file(actions, folder, filename):
    filepath = os.path.join(data_directory, mouse_folder, actions_folder, folder, filename)
    with open(filepath, 'w') as file:
        writer = csv.writer(file)
        write_action_csv_header(writer)
        for action in actions:
            action_feature_row = action.calculate_features()
            writer.writerow(action_feature_row)


def create_session_file(session, folder, filename):
    session_feature_row = session.calculate_features()
    filepath = os.path.join(data_directory, mouse_folder, sessions_folder, folder, filename)
    with open(filepath, 'w') as file:
        writer = csv.writer(file)
        write_session_csv_header(writer)
        writer.writerow(session_feature_row)


def write_session_csv_header(writer):
    header = ['num_actions', 'avg_inter_action_time',
              'mm_avg_v', 'mm_sd_v',  # 'mm_max_v', 'mm_min_v',
              'mm_avg_a', 'mm_sd_a',  # 'mm_max_a', 'mm_min_a',
              'mm_avg_j', 'mm_sd_j',  # 'mm_max_j', 'mm_min_j',
              'mm_avg_duration', 'mm_sd_duration',  # 'mm_max_duration', 'mm_min_duration',
              # 'mm_avg_trajectory', 'mm_sd_trajectory',  # 'mm_max_trajectory', 'mm_min_trajectory',
              # 'mm_avg_distance', 'mm_sd_distance',  # 'mm_max_distance', 'mm_min_distance',
              'mm_avg_straightness', 'mm_sd_straightness',  # 'mm_max_straightness', 'mm_min_straightness',
              'mm_avg_num_points', 'mm_sd_num_points',  # 'mm_max_num_points', 'mm_min_num_points',
              'mm_avg_curvature', 'mm_sd_curvature',
              'mm_avg_angle_sum', 'mm_sd_angle_sum',  # 'mm_max_angle_sum', 'mm_min_angle_sum',
              'mm_avg_max_deviation', 'mm_sd_max_deviation',
              'pc_avg_v', 'pc_sd_v',  # 'pc_max_v', 'pc_min_v',
              'pc_avg_a', 'pc_sd_a',  # 'pc_max_a', 'pc_min_a',
              'pc_avg_j', 'pc_sd_j',  # 'pc_max_j', 'pc_min_j',
              'pc_avg_duration', 'pc_sd_duration',  # 'pc_max_duration', 'pc_min_duration',
              # 'pc_avg_trajectory', 'pc_sd_trajectory',  # 'pc_max_trajectory', 'pc_min_trajectory',
              # 'pc_avg_distance', 'pc_sd_distance',  # 'pc_max_distance', 'pc_min_distance',
              'pc_avg_straightness', 'pc_sd_straightness',  # 'pc_max_straightness', 'pc_min_straightness',
              'pc_avg_num_points', 'pc_sd_num_points',  # 'pc_max_num_points', 'pc_min_num_points',
              'pc_avg_curvature', 'pc_sd_curvature',
              'pc_avg_angle_sum', 'pc_sd_angle_sum',  # 'pc_max_angle_sum', 'pc_min_angle_sum',
              'pc_avg_max_deviation', 'pc_sd_max_deviation',
              'avg_click_time', 'pc_sd_click_time',  # 'max_click_time', 'min_click_time',
              'dd_avg_v', 'dd_sd_v',  # 'dd_max_v', 'dd_min_v',
              'dd_avg_a', 'dd_sd_a',  # 'dd_max_a', 'dd_min_a',
              'dd_avg_j', 'dd_sd_j',  # 'pc_max_j', 'pc_min_j',
              'dd_avg_duration', 'dd_sd_duration',  # 'dd_max_duration', 'dd_min_duration',
              # 'dd_avg_trajectory', 'dd_sd_trajectory', 'dd_max_trajectory', 'dd_min_trajectory',
              # 'dd_avg_distance', 'dd_sd_distance', 'dd_max_distance', 'dd_min_distance',
              'dd_avg_straightness', 'dd_sd_straightness',  # 'dd_max_straightness', 'dd_min_straightness',
              'dd_avg_num_points', 'dd_sd_num_points',  # 'dd_max_num_points', 'dd_min_num_points',
              'dd_avg_curvature', 'dd_sd_curvature',
              'dd_avg_angle_sum', 'dd_sd_angle_sum',  # 'dd_max_angle_sum', 'dd_min_angle_sum'
              'dd_mean_max_deviation', 'dd_sd_max_deviation']

    writer.writerow(header)


def extract_mouse_features():
    mouse_events_folder = os.path.join(data_directory, mouse_folder, events_folder)
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
