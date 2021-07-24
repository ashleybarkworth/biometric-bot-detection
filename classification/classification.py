import os
import random
import statistics

import numpy as np
from sklearn import neighbors, svm, model_selection
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import make_scorer, accuracy_score, precision_score, recall_score, f1_score, roc_curve, auc
from sklearn.model_selection import cross_validate, KFold
import matplotlib.pyplot as plt

import pandas as pd

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
        classification = 0 if 'human' in folder else 1
        classifications.append(classification)
        # Merge feature row with existing data set
        data = merged_data if data is None else pd.concat([data, merged_data], ignore_index=True)

    return data, classifications


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


def draw_auc_curve(classifiers, X, y, type):
    # Split data set into 60% for training and 40% for testing
    X_train, X_test, y_train, y_test = model_selection.train_test_split(X, np.ravel(y),
                                                                        test_size=0.5,
                                                                        shuffle=True)

    classifier_names = ['Random Forest', 'Decision Tree', 'SVM', 'K-Nearest Neighbor']

    # Loop through 4 classifiers (Random Forest/DT/SVM/KNN) and plot on the same figure
    for i, classifier in enumerate(classifiers):
        # For some reason only SVM needs this to be set to use predict_proba()
        if isinstance(classifier, svm.SVC):
            classifier.probability = True
        # Train classifier
        classifier.fit(X_train, y_train)
        # Get probabilities for test data
        y_predict_proba = classifier.predict_proba(X_test)
        probabilities = y_predict_proba[:, 1]
        # Obtain TPR/FPR
        fpr, tpr, _ = roc_curve(y_test, probabilities, pos_label=1)
        roc_auc = auc(fpr, tpr)
        color = ['lightblue', 'magenta', 'yellow', 'lime']
        # Plot TPR/FPR curve for the classifier
        plt.plot(fpr, tpr, color=color[i], lw=1, label=classifier_names[i] + ' (AUC = {:0.2f})'.format(roc_auc))

    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlim([-0.05, 1.05])
    plt.ylim([-0.05, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curve (' + type + ')')
    plt.legend(loc="lower right")

    image_name = type + '_auc' + '.png'
    plt.savefig(image_name)
    plt.show()


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
    rfc = RandomForestClassifier()
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
    repeats = 5
    simple_results = []
    advanced_results = []

    for clf in classifiers:
        print('Results for classifier: {}'.format(str(clf)))
        print('===========================================================\n')

        for i in range(repeats):
            # This the cross validation performed to evaluate each of the classifiers.
            cv = KFold(n_splits=2, shuffle=True)

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

    draw_auc_curve(classifiers, X_simple, y_simple, 'Simple')
    draw_auc_curve(classifiers, X_advanced, y_advanced, 'Advanced')


if __name__ == '__main__':
    main()
