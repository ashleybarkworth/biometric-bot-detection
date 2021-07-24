import argparse
import errno
import os

from feature_extraction import mouse_features, key_features

events_directory = '../data/events'
features_directory = '../data/features/'


def create_feature_folder(folder):
    directory = os.path.join(features_directory, folder)
    try:
        os.makedirs(directory)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise e


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--actionType', default='all')
    args = parser.parse_args()
    action_type = args.actionType

    folders = [f for f in os.listdir(events_directory) if os.path.isdir(os.path.join(events_directory, f))]
    for folder in folders:
        create_feature_folder(folder)
        key_features.extract_key_features(events_directory, features_directory, folder)
        mouse_features.extract_mouse_features(events_directory, features_directory, folder, action_type)


if __name__ == '__main__':
    main()
