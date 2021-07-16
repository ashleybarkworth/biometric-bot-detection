import os

sessions_directory = '../data/sessions/'

class Rule:

    def __init__(self, feature, threshold):
        self.feature = feature
        self.threshold = threshold


def calculate_thresholds():
    features = ['num_actions', 'avg_inter_action_time', 'mm_avg_straightness', 'pc_avg_v', 'mm_avg_a', '']
    for folder in os.listdir(sessions_directory):
        subdirectory = os.path.join(sessions_directory, folder)


def main():
    calculate_thresholds()


if __name__ == '__main__':
    main()