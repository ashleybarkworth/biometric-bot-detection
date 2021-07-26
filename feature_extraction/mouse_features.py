import csv
import os

from feature_extraction.mouse_actions import ActionType, MouseEvent, MouseState, MouseAction
from feature_extraction.mouse_sessions import Session


def smooth_bot_actions(actions):
    for i, action in enumerate(actions):
        action = actions[i]
        if i > 0:
            prev_action_event = actions[i - 1].events[-1]
            last_x, last_y, last_time = prev_action_event.x, prev_action_event.y, prev_action_event.time
            index = 0 if action.action_type.value == ActionType.MM.value else -4
            action.events[index].x, action.events[index].y = last_x, last_y

    # Remove the first action that clicks 'Start' button (no movement recorded)
    return actions[1:]


def drag_between_point_click(i, rows):
    # Returns True if rows[i] is a 'Drag' event between a mouse press and release
    if 0 < i < len(rows) - 1:
        event_state = rows[i]['state']
        prev_event_state = rows[i - 1]['state']
        next_event_state = rows[i + 1]['state']
        return event_state == 'Drag' and prev_event_state == 'Pressed' and next_event_state == 'Released'
    else:
        return False


def parse_mouse_file(filepath):
    mouse_events = []
    actions = []

    with open(filepath) as csv_file:
        csv_reader = csv.DictReader(csv_file)
        rows = list(csv_reader)
        processed_rows = [row for i, row in enumerate(rows) if not drag_between_point_click(i, rows)]
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

    if 'simple' in filepath or 'advanced' in filepath:
        actions = smooth_bot_actions(actions)

    # Remove actions with less than 2 events
    actions = [action for action in actions if len(action.events) >= 2]

    for action in actions:
        action.calculate_features()

    return actions


def create_session_feature_file(features_directory, folder, feature_row, action_type):
    filepath = os.path.join(features_directory, folder, 'mouse.csv')
    with open(filepath, 'w') as file:
        writer = csv.writer(file)
        write_session_csv_header(writer, action_type)
        writer.writerow(feature_row)


def write_session_csv_header(writer, action_type):
    mm_header = ['mm_avg_v', 'mm_sd_v', 'mm_max_v', 'mm_min_v',
                 'mm_avg_a', 'mm_sd_a', 'mm_max_a', 'mm_min_a',
                 'mm_avg_j', 'mm_sd_j', 'mm_max_j', 'mm_min_j',
                 'mm_avg_duration', 'mm_sd_duration', 'mm_max_duration', 'mm_min_duration',
                 'mm_avg_straightness', 'mm_sd_straightness', 'mm_max_straightness', 'mm_min_straightness',
                 'mm_avg_num_points', 'mm_sd_num_points', 'mm_max_num_points', 'mm_min_num_points',
                 'mm_avg_curvature', 'mm_sd_curvature', 'mm_max_curvature', 'mm_min_curvature',
                 'mm_avg_angle_sum', 'mm_sd_angle_sum', 'mm_max_angle_sum', 'mm_min_angle_sum',
                 'mm_avg_max_deviation', 'mm_sd_max_deviation', 'mm_max_max_deviation', 'mm_min_max_deviation']

    pc_header = ['pc_avg_v', 'pc_sd_v', 'pc_max_v', 'pc_min_v',
                 'pc_avg_a', 'pc_sd_a', 'pc_max_a', 'pc_min_a',
                 'pc_avg_j', 'pc_sd_j', 'pc_max_j', 'pc_min_j',
                 'pc_avg_duration', 'pc_sd_duration', 'pc_max_duration', 'pc_min_duration',
                 'pc_avg_straightness', 'pc_sd_straightness', 'pc_max_straightness', 'pc_min_straightness',
                 'pc_avg_num_points', 'pc_sd_num_points', 'pc_max_num_points', 'pc_min_num_points',
                 'pc_avg_curvature', 'pc_sd_curvature', 'pc_max_curvature', 'pc_min_curvature',
                 'pc_avg_angle_sum', 'pc_sd_angle_sum', 'pc_max_angle_sum', 'pc_min_angle_sum',
                 'pc_avg_max_deviation', 'pc_sd_max_deviation', 'pc_max_max_deviation', 'pc_min_max_deviation',
                 'pc_avg_click_time', 'pc_sd_click_time', 'pc_max_click_time', 'pc_min_click_time']

    dd_header = ['dd_avg_v', 'dd_sd_v', 'dd_max_v', 'dd_min_v',
                 'dd_avg_a', 'dd_sd_a', 'dd_max_a', 'dd_min_a',
                 'dd_avg_j', 'dd_sd_j', 'pc_max_j', 'pc_min_j',
                 'dd_avg_duration', 'dd_sd_duration', 'dd_max_duration', 'dd_min_duration',
                 'dd_avg_straightness', 'dd_sd_straightness', 'dd_max_straightness', 'dd_min_straightness',
                 'dd_avg_num_points', 'dd_sd_num_points', 'dd_max_num_points', 'dd_min_num_points',
                 'dd_avg_curvature', 'dd_sd_curvature', 'dd_max_curvature', 'dd_min_curvature',
                 'dd_avg_angle_sum', 'dd_sd_angle_sum', 'dd_max_angle_sum', 'dd_min_angle_sum',
                 'dd_avg_max_deviation', 'dd_sd_max_deviation', 'dd_max_max_deviation', 'dd_min_max_deviation']

    header = ['num_actions', 'total_duration']

    if action_type == 'mm':
        header += mm_header
    elif action_type == 'pc':
        header += pc_header
    elif action_type == 'dd':
        header += dd_header
    else:
        header += mm_header + pc_header + dd_header

    writer.writerow(header)


def get_usertype(folder):
    if 'human' in folder:
        usertype = 'human'
    elif 'simple' in folder:
        usertype = 'simple'
    else:
        usertype = 'advanced'
    return usertype


def extract_mouse_features(events_directory, features_directory, folder, action_type):
    mouse_filepath = os.path.join(events_directory, folder, 'mouse.csv')
    actions = parse_mouse_file(mouse_filepath)
    usertype = get_usertype(folder)
    session = Session(actions, usertype)
    session_feature_row = session.calculate_features(action_type)
    create_session_feature_file(features_directory, folder, session_feature_row, action_type)
