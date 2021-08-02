import csv
import os
import statistics

shifted = {'1': '!', '2': '@', '3': '#', 'a': 'A', 'b': 'B', 'c': 'C', 'p': 'P'}
unshifted = dict([reversed(i) for i in shifted.items()])


def create_key_feature_file(features_directory, folder, feature_row):
    filepath = os.path.join(features_directory, folder, 'key.csv')

    header = ['Total time taken', 'Average hold time', 'Max hold time', 'Min hold time', 'SD hold time',
              'Average CPR time', 'Max CPR time', 'Min CPR time', 'SD CPR time',
              'Average Release Latency', 'Max Release Latency', 'Min Release Latency', 'SD Release Latency',
              'Average Press Latency', 'Max Press Latency', 'Min Press Latency', 'SD Press Latency']

    with open(filepath, 'w') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerow(feature_row)


def not_a_typo(key_pressed, key_released):
    # This checks that for a specific event, either the key pressed contains an important character or the key released
    # contains an important character. 'Important' characters are Key.shift or one of the characters in '123CAPabc!'.
    pressed_key = key_pressed != 'None' and 'Key.shift' in key_pressed or key_pressed in shifted.keys() or key_pressed in unshifted.keys()
    released_key = key_released != 'None' and 'Key.shift' in key_released or key_released in shifted.keys() or key_released in unshifted.keys()
    return pressed_key or released_key


def parse_key_file(filepath):
    key_pressed_dict = {}
    last_pressed_time = 0
    shift_is_pressed = False

    total_time_taken = 0
    hold_times = []
    cpr_times = []
    released_times = []
    pressed_times = []

    with open(filepath) as csv_file:
        csv_reader = csv.DictReader(csv_file)
        rows = list(csv_reader)
        for i, row in enumerate(rows):
            row = rows[i]
            key_pressed = row['Key pressed']
            key_released = row['Key released'].replace("'", "")
            time = float(row['Time'])

            hold_time = ''
            press_release = ''
            released_key_time = ''
            pressed_key_time = ''

            # Character must either be Key.shift or one of the characters in '123CAPabc!'
            if not_a_typo(key_pressed, key_released):
                # Key press event
                if key_pressed != 'None':
                    # Ignore shift character for feature calculation, but set flag that caps is on
                    if key_pressed == 'Key.shift':
                        shift_is_pressed = True
                    else:
                        key_pressed_dict[key_pressed] = time
                        last_pressed_time = time
                        pressed_key_time = time
                # Key Release event
                elif key_released != 'None':
                    # Ignore shift character for feature calculation, but set flag that caps is off
                    if key_released == 'Key.shift':
                        shift_is_pressed = False
                    else:
                        check_for_key = key_released
                        released_key_time = time
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
                        # Time between pressing this character and current release
                        hold_time = time - press_time
                        # Time between last press (any character) and current release
                        press_release = time - last_pressed_time

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

                if hold_time:
                    hold_times.append(hold_time)

                if press_release:
                    cpr_times.append(press_release)

                if pressed_key_time:
                    pressed_times.append(pressed_key_time)

                if released_key_time:
                    released_times.append(released_key_time)

        # Total time taken to type 10 words
        total_time_taken = float(rows[-1]['Time']) - float(rows[0]['Time'])

    # Times between key releases
    release_latency = [released_times[i + 1] - released_times[i] for i in range(len(released_times) - 1)]
    # Times between key presses
    press_latency = [pressed_times[i + 1] - pressed_times[i] for i in range(len(pressed_times) - 1)]

    # Average/Maximum/Minimum/Std.Dev. hold times
    avg_hold_time, max_hold_time, min_hold_time, sd_hold_time = statistics.mean(hold_times), max(hold_times), min(hold_times), statistics.stdev(hold_times)
    # Average/Maximum/Minimum/Std.Dev. consecutive press release times
    avg_cpr_time, max_cpr_time, min_cpr_time, sd_cpr_time = statistics.mean(cpr_times), max(cpr_times), min(cpr_times), statistics.stdev(cpr_times)
    # Average/Maximum/Minimum/Std.Dev. release latency times
    avg_released_time, max_released_time, min_released_time, sd_released_time = statistics.mean(release_latency), max(release_latency), min(release_latency), statistics.stdev(release_latency)
    # Average/Maximum/Minimum/Std.Dev. press latency times
    avg_press_time, max_press_time, min_press_time, sd_press_time = statistics.mean(press_latency), max(press_latency), min(press_latency), statistics.stdev(press_latency)

    # Values of the features that are written to new CSV
    feature_row = [total_time_taken, avg_hold_time, max_hold_time, min_hold_time, sd_hold_time,
                   avg_cpr_time, max_cpr_time, min_cpr_time, sd_cpr_time,
                   avg_released_time, max_released_time, min_released_time, sd_released_time,
                   avg_press_time, max_press_time, min_press_time, sd_press_time]

    return feature_row


def extract_key_features(events_directory, features_directory, folder):
    key_filepath = os.path.join(events_directory, folder, 'key.csv')
    feature_row = parse_key_file(key_filepath)
    create_key_feature_file(features_directory, folder, feature_row)

