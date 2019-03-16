# import numpy as np
# import matplotlib.pyplot as plt
# from sklearn.metrics import classification_report, \
#        confusion_matrix, \
#        accuracy_score
import os
import time
from collections import deque

import numpy as np
import pandas as pd
from sklearn import model_selection
from sklearn.tree import DecisionTreeClassifier

import sensors

# prepare configuration for cross validation test harness
seed = 100

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

# classifier
clf = DecisionTreeClassifier()

kfold = model_selection.KFold(n_splits=10, random_state=seed)
scoring = 'accuracy'

cv_results = model_selection.cross_val_score(clf, X, Y,
                                             cv=kfold,
                                             scoring=scoring)

clf.fit(X_train, y_train)

# Xnew = [[7380, 204, 14644, 69, -117, 191]]
s = sensors.Sensors()
start_time = None
elapsed_time = None
dq = deque()

try:
    while True:
        data = s.read()
        if data is None:
            continue
        elif start_time is None:
            start_time = time.time()
        elapsed_time = time.time() - start_time

        print("\r", end='')
        if elapsed_time is not None and start_time is not None:
            print("[%ds] " % (elapsed_time), end='')

        print(str(data) + " " * 5, end='')
        dq.append(
            {'time': elapsed_time, 'data': sensors.SensorData(*data.data())})
        # if time more than 1 second
        if dq and elapsed_time - dq[0]['time'] >= 1:
            save_data = data - dq.popleft()['data']

            # data_tobe_classified = pd.read_csv('new_data.csv',
            #                                 sep=',',
            #                                 header=None)

            y_pred = clf.predict(np.asarray([(list(save_data.data()))]))

            print("        Prediction: %s" % (y_pred) + " " * 5, end='')

    print("\r[%ds] " % (elapsed_time), end='')

    i += 1

except KeyboardInterrupt:
    print("Interrupted." + " " * 36)
