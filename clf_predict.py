#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import time
from collections import deque

import numpy as np
import pandas as pd
from sklearn import model_selection
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis

import sensors

class Predict():

    # Xnew = [[7380, 204, 14644, 69, -117, 191]]
    start_time = None
    elapsed_time = None
    dq = deque()
    # classifier
    clf = LinearDiscriminantAnalysis()

    def __init__(self):

        X = []
        Y = []
        for filename in os.listdir('data'):
            data = pd.read_csv('data/'+filename, sep=',', header=None, index_col=0)
            # print(data)
            for i in data.index.unique():
                # Index is activity ID
                # Y.append(i)
                # X.append(data.loc[i].values[:250]) #TODO: Change this maximum value to some better dataset
                for coords in data.loc[i].values:
                    Y.append(i)
                    X.append(coords)

        # Split data
        X_train, X_test, y_train, y_test = model_selection.train_test_split(
            X, Y,
            test_size=0.3,
            random_state=100)

        self.clf.fit(X_train, y_train)

    def predict(self, data: sensors.SensorData):
        if data is None:
            return None
        elif self.start_time is None:
            self.start_time = time.time()
        self.elapsed_time = time.time() - self.start_time

        print("\r", end='')
        if self.elapsed_time is not None and self.start_time is not None:
            print("[%ds] " % (self.elapsed_time), end='')

        print(str(data) + " " * 5, end='')
        self.dq.append(
            {'time': self.elapsed_time, 'data': sensors.SensorData(*data.data())})
        # if time more than 1 second
        if self.dq and self.elapsed_time - self.dq[0]['time'] >= 1:
            save_data = data - self.dq.popleft()['data']

            # data_tobe_classified = pd.read_csv('new_data.csv',
            #                                 sep=',',
            #                                 header=None)

            return self.clf.predict(np.asarray([(list(save_data.data()))]))

def main():
    p = Predict()
    s = sensors.Sensors()
    try:
        while True:
            data = s.read()
            y_pred = p.predict(data)
            if y_pred is None:
                continue

            print("        Prediction: %s" % (y_pred) + " " * 5, end='')

        print("\r[%ds] " % (p.elapsed_time), end='')

    except KeyboardInterrupt:
        print("Interrupted." + " " * 36)


if __name__ == "__main__":
    main()
