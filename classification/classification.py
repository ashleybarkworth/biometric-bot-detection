import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.model_selection import train_test_split, cross_val_score, cross_validate

import pandas as pd

global files

features_directory = '../data/features/'


def get_data():
    global files
    # Retrieve all folders from features directory. Each user's data is in a separate folder.
    folders = [f for f in os.listdir(features_directory) if os.path.isdir(os.path.join(features_directory, f))]
    data = None
    classifications = []

    for folder in folders:
        # Retrieve
        key_data = pd.read_csv(os.path.join(features_directory, folder, 'key.csv'))
        mouse_data = pd.read_csv(os.path.join(features_directory, folder, 'mouse.csv'))
        # Combine key and mouse features from same user into one row
        merged_data = pd.concat([key_data, mouse_data], axis=1)
        # Determine classification of user from folder name and add to classifications
        classification = 'human' if 'human' in folder else 'bot'
        classifications.append(classification)
        # Merge feature row with existing data
        data = merged_data if data is None else pd.concat([data, merged_data], ignore_index=True)

    return data, classifications


def main():
    X, y = get_data()

    rfc = RandomForestClassifier()
    cv = cross_validate(rfc, X, y, cv=2)

    print(cv['test_score'])
    print(cv['test_score'].mean())

    print('done')


if __name__ == '__main__':
    main()
