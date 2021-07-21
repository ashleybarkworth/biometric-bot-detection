import glob
import statistics

import pandas as pd
from sklearn.ensemble import IsolationForest
from os.path import join

global files

# Data containing activity from human users for training Isolation Forest
training_data = 'train/'

# Data used for testing our model (contains human + bot data)
test_data = 'test/'

global forest  # Isolation Forest model


def get_training_data():
    global files
    search_path = join(training_data, '*.csv')
    files = glob.glob(search_path)
    return pd.concat([pd.read_csv(f) for f in files], ignore_index=True)


def get_test_data():
    global files
    search_path = join(test_data, '*.csv')
    files = glob.glob(search_path)
    answers = [0 if 'human' in f else 1 for f in files]
    return pd.concat([pd.read_csv(f) for f in files], ignore_index=True), answers


def fit_tree_model(df):
    global forest
    max_features = 1.0
    n_estimators = 300
    max_samples = 'auto'
    contamination = float(0.0)
    forest = IsolationForest(max_features=max_features,
                             n_estimators=n_estimators,
                             max_samples=max_samples,
                             contamination=contamination)
    forest.fit(df)


def predict_anomalies(df):
    # Returns scores of -1 for anomalies and 1 for normal samples
    predictions = forest.predict(df)
    # Map predictions to 1 for anomalies and 0 for normal samples
    predictions = [1 if i == -1 else 0 for i in predictions]
    return predictions


def calculate_accuracy(predictions, answers):
    correct = 0
    if len(predictions) == len(answers):
        for i in range(len(predictions)):
            if predictions[i] == answers[i]:
                correct += 1
    return correct / len(answers)


def main():
    # Train Isolation Forest
    df_train = get_training_data()
    fit_tree_model(df_train)
    # Test Isolation Forest
    df_test, answers = get_test_data()
    predictions = predict_anomalies(df_test)
    accuracies = []
    for i in range(50):
        accuracies.append(calculate_accuracy(predictions, answers))
    avg_accuracy = statistics.mean(accuracies)

    print("{:.2%}".format(avg_accuracy))


if __name__ == '__main__':
    main()
