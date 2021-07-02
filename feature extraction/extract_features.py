import csv

from actions import MouseEvent, MouseState, MouseAction, ActionType


def read_file(filename):
    mouse_events = []
    actions = []
    with open(filename) as csv_file:
        csv_reader = csv.DictReader(csv_file)
        rows = list(csv_reader)
        for i, row in enumerate(rows):
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
                next_event = rows[i + 1]
                # Check if next event is a mouse drag, in which case create Mouse Move action
                # and start new Drag and Drop action
                if MouseState(next_event['state']) == MouseState.DRAGGED:
                    actions.append(MouseAction(ActionType.MM, mouse_events))
                    mouse_events = [mouse_event]
                else:
                    mouse_events.append(mouse_event)
            # Mouse movement (either mouse held down or not)
            else:
                mouse_events.append(mouse_event)

            prev_event = mouse_event

    actions[:] = [action for action in actions if len(action.events) >= 4]
    create_action_file(actions)


def create_action_file(actions):
    with open('./data/action_features.csv', 'w+', ) as file:
        writer = csv.writer(file)
        write_csv_header(writer)
        for action in actions:
            action_feature_row = action.calculate_features()
            writer.writerow(action_feature_row)


def write_csv_header(writer):
    header = ["action_type", "elapsed_time", "trajectory", "direction", "straightness", "num_points",
              "max_deviation", "sum_of_angles", "mean_curv", "sd_curv", "max_curv", "min_curv",
              "mean_omega", "sd_omega", "max_omega", "min_omega", "mean_vx", "sd_vx", "max_vx", "min_vx",
              "mean_vy", "sd_vy", "max_vy", "min_vy", "mean_v", "sd_v", "max_v", "min_v",
              "mean_a", "sd_a", "max_a", "min_a", "mean_j", "sd_j", "max_j", "min_j",
              "distance", "beginning_acceleration_time"]
    writer.writerow(header)


read_file('./data/events.csv')
