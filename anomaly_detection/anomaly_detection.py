# import numpy as np
import glob
import shap
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
# import seaborn as sns
from os.path import join

global files

data = join('../data/mouse/sessions/')

global forest  # Isolation Forest model
global clf  # Local Outlier Factor model


def combine_session_data():
    global files
    search_path = join(data, '**/*.csv')
    files = glob.glob(search_path)
    return pd.concat([pd.read_csv(f) for f in files], ignore_index=True)


def fit_tree_model(df):
    global forest
    max_features = 1.0
    n_estimators = 200
    max_samples = 'auto'
    contamination = float(0.2)
    forest = IsolationForest(max_features=max_features,
                             n_estimators=n_estimators,
                             max_samples=max_samples,
                             contamination=contamination)
    forest.fit(df)


def fit_local_outlier_model(df):
    global clf
    n_neighbors = 1
    contamination = float(0.2)
    clf = LocalOutlierFactor(n_neighbors=n_neighbors,
                             contamination=contamination)
    clf.fit(df)


def find_anomalies(df):
    # df['scores'] = forest.decision_function(df)
    df['anomaly_value'] = forest.predict(df)


def predict_anomalies(df):
    tree_pred = forest.predict(df)
    clf_pred = clf.fit_predict(df)
    print('done')


def fit_models(df):
    fit_tree_model(df)
    shap.TreeExplainer(forest)
    fit_local_outlier_model(df)


def main():
    df = combine_session_data()
    fit_models(df)
    predict_anomalies(df)


if __name__ == '__main__':
    main()
