import os
import statistics

from sklearn import neighbors, svm
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import make_scorer, accuracy_score, precision_score, recall_score, f1_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import cross_validate, KFold

import pandas as pd

global files

features_directory = '../data/features/'


def get_data_from_folders(data_folders):
    data = None
    classifications = []

    for folder in data_folders:
        # Retrieve key and mouse features for a single user
        key_data = pd.read_csv(os.path.join(features_directory, folder, 'key.csv'))
        mouse_data = pd.read_csv(os.path.join(features_directory, folder, 'mouse.csv'))
        # Combine key and mouse features from the user into one row
        merged_data = pd.concat([key_data, mouse_data], axis=1)
        # Determine classification of user from folder name and add to classifications
        classification = 'human' if 'human' in folder else 'bot'
        classifications.append(classification)
        # Merge feature row with existing data set
        data = merged_data if data is None else pd.concat([data, merged_data], ignore_index=True)

    return data, classifications


def get_data_for_advanced_bot():
    global files
    # Retrieve all folders from features directory. Each user's data is in a separate folder.
    folders = [f for f in os.listdir(features_directory) if os.path.isdir(os.path.join(features_directory, f))]

    human_folders = [f for f in folders if 'human' in f]
    advanced_bot_folders = [f for f in folders if 'advanced' in f]

    data_folders = human_folders + advanced_bot_folders
    return get_data_from_folders(data_folders)


def get_data_for_simple_bot():
    global files
    # Retrieve all folders from features directory. Each user's data is in a separate folder.
    folders = [f for f in os.listdir(features_directory) if os.path.isdir(os.path.join(features_directory, f))]

    human_folders = [f for f in folders if 'human' in f]
    simple_bot_folders = [f for f in folders if 'simple' in f]

    data_folders = human_folders + simple_bot_folders
    return get_data_from_folders(data_folders)


def print_results(results):
    # Print accuracy, precision, recall, and F1 score results from a classifier
    accuracy = statistics.mean([result['test_accuracy'].mean() for result in results])
    precision = statistics.mean([result['test_precision'].mean() for result in results])
    recall = statistics.mean([result['test_recall'].mean() for result in results])
    f1_score = statistics.mean([result['test_f1_score'].mean() for result in results])
    print('--------------------')
    print('Accuracy: {:0.2f}%'.format(accuracy * 100))
    print('Precision: {:0.2f}%'.format(precision * 100))
    print('Recall: {:0.2f}%'.format(recall * 100))
    print('F1 score: {:0.2f}%'.format(f1_score * 100))
    print('--------------------\n')


def main():

    # This contains the human and simple bot data
    X_simple, y_simple = get_data_for_simple_bot()

    # This contains the human and advanced bot data
    X_advanced, y_advanced = get_data_for_advanced_bot()

    # A list that we can add all the classifiers to, so that we can iterate through them for testing
    classifiers = []

    # Create the classifier algorithms (Random Forest/DT/SVM/KNN) here
    rfc = RandomForestClassifier(n_estimators=20)
    dt = DecisionTreeClassifier()
    SVM = svm.SVC(kernel='linear')
    knn = neighbors.KNeighborsClassifier(n_neighbors=3, weights='uniform')

    # Add the classifier to list here
    classifiers.append(rfc)
    classifiers.append(dt)
    classifiers.append(SVM)
    classifiers.append(knn)

    # These are the metrics for evaluating the classifiers
    scoring = {'accuracy': make_scorer(accuracy_score),
               'precision': make_scorer(precision_score, pos_label='bot'),
               'recall': make_scorer(recall_score, pos_label='bot'),
               'f1_score': make_scorer(f1_score, pos_label='bot')}

    # Number of times to repeat cross validation
    repeats = 5
    simple_results = []
    advanced_results = []

    for clf in classifiers:
        print('Results for classifier: {}'.format(str(clf)))
        print('===========================================================\n')

        for i in range(repeats):
            # This the cross validation performed to evaluate each of the classifiers.
            cv = KFold(n_splits=3, shuffle=True)

            simple_scores = cross_validate(clf, X_simple, y_simple, cv=cv, scoring=scoring)
            simple_results.append(simple_scores)

            advanced_scores = cross_validate(clf, X_advanced, y_advanced, cv=cv, scoring=scoring)
            advanced_results.append(advanced_scores)

        # Simple bot results (human + simple data)
        print('Simple Bot Results')
        print_results(simple_results)

        # Advanced bot results (human + advanced data)
        print('Advanced Bot Results')
        print_results(advanced_results)


if __name__ == '__main__':
    main()
