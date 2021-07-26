import os
import statistics

import numpy as np
from sklearn import neighbors, svm
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import make_scorer, accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import cross_validate, StratifiedKFold

import pandas as pd

features_directory = '../data/features/'


def add_noise(data):
    # Get random 10% of data to add noise to
    part_10 = data.sample(frac=0.1)
    # Get the remaining 90% of data
    rest_part_10 = data.drop(part_10.index)

    # Get all columns from the 10% data set (except for the class label) so noise can be added to each value
    clean_signal = part_10.drop('class', axis=1)
    # Get the class labels (to add back in after adding noise)
    classes = part_10['class']

    # Get [row, column] dimensions of the 10% features data set (needed for adding random noise to each value)
    shape = clean_signal.shape
    # Mean, standard deviation of Gaussian (i.e. normal) distribution
    mu, sigma = 0, np.std(data)[:-1] * 5

    # Generate random noise from Gaussian distribution (generates random noise for each value)
    noise = np.random.normal(mu, sigma, [shape[0], shape[1]])
    # Add random noise to the 10% data set
    signal = clean_signal.add(noise)
    # Add 'class' column back to array
    signal['class'] = classes

    # Recombine 10% and 90% data sets
    noisy_data = pd.concat([signal, rest_part_10], ignore_index=True)
    return noisy_data


def get_data_from_folders(data_folders):
    data = None

    for folder in data_folders:
        # Retrieve key and mouse features for a single user
        key_data = pd.read_csv(os.path.join(features_directory, folder, 'key.csv'))
        mouse_data = pd.read_csv(os.path.join(features_directory, folder, 'mouse.csv'))
        # Combine key and mouse features from the user into one row
        merged_data = pd.concat([key_data, mouse_data], axis=1)
        # Determine classification of user from folder name and add to classifications
        classification = 0 if 'human' in folder else 1
        # Add classification as a new column to the feature row
        merged_data['class'] = classification
        # Merge feature row with existing data set
        data = merged_data if data is None else pd.concat([data, merged_data], ignore_index=True)

    # data['class'] = classifications
    noisy_data = add_noise(data)

    classifications = noisy_data['class']
    noisy_data = noisy_data.drop('class', axis=1)

    return noisy_data, classifications


def get_data_for_advanced_bot():
    # Retrieve all folders from features directory. Each user's data is in a separate folder.
    folders = [f for f in os.listdir(features_directory) if os.path.isdir(os.path.join(features_directory, f))]

    human_folders = [f for f in folders if 'human' in f]
    advanced_bot_folders = [f for f in folders if 'advanced' in f]

    data_folders = human_folders + advanced_bot_folders
    return get_data_from_folders(data_folders)


def get_data_for_simple_bot():
    # Retrieve all folders from features directory. Each user's data is in a separate folder.
    folders = [f for f in os.listdir(features_directory) if os.path.isdir(os.path.join(features_directory, f))]

    human_folders = [f for f in folders if 'human' in f]
    simple_bot_folders = [f for f in folders if 'simple' in f]

    data_folders = human_folders + simple_bot_folders
    return get_data_from_folders(data_folders)


def print_results(results):
    # Print accuracy, precision, recall, and F1 score results from a classifier
    accuracy_avg = statistics.mean([result['test_accuracy'].mean() for result in results])
    accuracy_sd = statistics.stdev([result['test_accuracy'].mean() for result in results])

    precision_avg = statistics.mean([result['test_precision'].mean() for result in results])
    precision_sd = statistics.stdev([result['test_precision'].mean() for result in results])

    recall_avg = statistics.mean([result['test_recall'].mean() for result in results])
    recall_sd = statistics.stdev([result['test_recall'].mean() for result in results])

    f1_score_avg = statistics.mean([result['test_f1_score'].mean() for result in results])
    f1_score_sd = statistics.stdev([result['test_f1_score'].mean() for result in results])

    print('--------------------')
    print('Accuracy: {:0.2f}% \u00B1 {:0.2f}%'.format(accuracy_avg * 100, accuracy_sd * 100))
    print('Precision: {:0.2f}% \u00B1 {:0.2f}%'.format(precision_avg * 100, precision_sd * 100))
    print('Recall: {:0.2f}% \u00B1 {:0.2f}%'.format(recall_avg * 100, recall_sd * 100))
    print('F1 score: {:0.2f}% \u00B1 {:0.2f}%'.format(f1_score_avg * 100, f1_score_sd * 100))
    print('--------------------\n')


def main():
    # This contains the human and simple bot data
    X_simple, y_simple = get_data_for_simple_bot()

    # This contains the human and advanced bot data
    X_advanced, y_advanced = get_data_for_advanced_bot()

    # A list that we can add all the classifiers to, so that we can iterate through them for testing
    classifiers = []

    # Create the classifier algorithms (Random Forest/DT/SVM/KNN) here
    rfc = RandomForestClassifier(n_estimators=150)
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
               'precision': make_scorer(precision_score, pos_label=1),
               'recall': make_scorer(recall_score, pos_label=1),
               'f1_score': make_scorer(f1_score, pos_label=1)}

    # Number of times to repeat cross validation
    repeats = 10
    # Stores results. There should be (repeats * n_splits) results after repeated cross validation completes
    simple_results = []
    advanced_results = []

    for clf in classifiers:
        print('Results for classifier: {}'.format(str(clf)))
        print('===========================================================\n')

        for i in range(repeats):
            scalar = StandardScaler()
            pipeline = Pipeline([('transformer', scalar), ('estimator', clf)])

            # Stratified k-fold cross validation with k=3
            cv = StratifiedKFold(n_splits=3, shuffle=True)

            simple_scores = cross_validate(pipeline, X_simple, y_simple, cv=cv, scoring=scoring)
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
