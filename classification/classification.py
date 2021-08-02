import os

import numpy as np
from matplotlib import pyplot as plt
from numpy import interp
from sklearn import neighbors, svm
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_curve, auc
from sklearn.model_selection import StratifiedKFold

from statistics import mean
from statistics import stdev

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
    mu, sigma = 0, np.std(data)[:-1] * 10

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


def plot_roc_curve(tprs, aucs, classifier_name, type):

    mean_fpr = np.linspace(0, 1, 100)

    bot = '(Simple)' if type == 'simple' else '(Advanced)'
    title = ''.join(['ROC Curve for: ', classifier_name, ' ', bot])

    plt.plot([0, 1], [0, 1], linestyle='--', lw=2, color='r', label='Chance', alpha=.8)

    mean_tpr = np.mean(tprs, axis=0)
    mean_tpr[-1] = 1.0
    mean_auc = auc(mean_fpr, mean_tpr)
    std_auc = np.std(aucs)
    plt.plot(mean_fpr, mean_tpr, color='b', label=r'Mean ROC (AUC = %0.2f $\pm$ %0.2f)' % (mean_auc, std_auc), lw=2, alpha=.8)

    std_tpr = np.std(tprs, axis=0)
    tprs_upper = np.minimum(mean_tpr + std_tpr, 1)
    tprs_lower = np.maximum(mean_tpr - std_tpr, 0)
    plt.fill_between(mean_fpr, tprs_lower, tprs_upper, color='grey', alpha=.2, label=r'$\pm$ 1 std. dev.')
    plt.xlim([-0.05, 1.05])
    plt.ylim([-0.05, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title(title)
    plt.legend(loc="lower right")

    img = ''.join([classifier_name, '_', type, '.png'])
    plt.savefig(img)
    plt.show()


def perform_cross_validation(classifier, cv, X, y, type):
    if isinstance(classifier, svm.SVC):
        classifier.probability = True

    # Metrics
    accuracies = []
    precisions = []
    recalls = []
    f1_scores = []

    # Creating ROC Curve with Cross Validation
    tprs = []
    aucs = []
    mean_fpr = np.linspace(0, 1, 100)

    scalar = StandardScaler()
    pipeline = Pipeline([('transformer', scalar), ('estimator', classifier)])

    i = 0
    for train, test in cv.split(X, y):
        pipeline.fit(X.iloc[train], y.iloc[train])

        # Predictions for the metrics
        y_predictions = pipeline.predict(X.iloc[test])
        accuracies.append(accuracy_score(y.iloc[test], y_predictions))
        precisions.append(precision_score(y.iloc[test], y_predictions))
        recalls.append(recall_score(y.iloc[test], y_predictions))
        f1_scores.append(f1_score(y.iloc[test], y_predictions))

        # Probabilities for AUC curve
        probabilities = pipeline.predict_proba(X.iloc[test])
        # Compute ROC curve and AUC
        fpr, tpr, thresholds = roc_curve(y.iloc[test], probabilities[:, 1])
        tprs.append(interp(mean_fpr, fpr, tpr))

        tprs[-1][0] = 0.0
        roc_auc = auc(fpr, tpr)
        aucs.append(roc_auc)
        plt.plot(fpr, tpr, lw=1, alpha=0.3, label='ROC fold %d (AUC = %0.2f)' % (i, roc_auc))

        i += 1

    classifier_name = classifier.__class__.__name__
    plot_roc_curve(tprs, aucs, classifier_name, type)
    print_results(accuracies, precisions, recalls, f1_scores)


def print_results(accuracies, precisions, recalls, f1_scores):
    print('--------------------')
    print('Accuracy: {:0.2f}% \u00B1 {:0.2f}%'.format(mean(accuracies) * 100, stdev(accuracies) * 100))
    print('Precision: {:0.2f}% \u00B1 {:0.2f}%'.format(mean(precisions) * 100, stdev(precisions) * 100))
    print('Recall: {:0.2f}% \u00B1 {:0.2f}%'.format(mean(recalls) * 100, stdev(recalls) * 100))
    print('F1 score: {:0.2f}% \u00B1 {:0.2f}%'.format(mean(f1_scores) * 100, stdev(f1_scores) * 100))
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

    # Stratified k-fold cross validation with k=3
    cv = StratifiedKFold(n_splits=5, shuffle=True)

    for clf in classifiers:
        print('Results for classifier: {}'.format(str(clf)))
        print('===========================================================\n')

        # Simple bot results (human + simple data)
        print('Simple Bot Results')
        perform_cross_validation(clf, cv, X_simple, y_simple, 'simple')

        # Advanced bot results (human + advanced data)
        print('Advanced Bot Results')
        perform_cross_validation(clf, cv, X_advanced, y_advanced, 'advanced')


if __name__ == '__main__':
    main()
