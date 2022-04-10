import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score
from xgboost import XGBClassifier

# the amount of previous matches that will be feed into the model
lookback = 12

# change the file path of your finalised data file
filepath = './data/' + str(lookback)
data = np.load(filepath +').npy')

# get the sample and target 
X = data[:,:-1]
y = data[:,-1]

# Split the data into train and test set for the xgboost
Xtrain, Xtest, yTrain, yTest = train_test_split(X, y, test_size=0.25, random_state=123)
eval_set = [(Xtest, yTest)]

# Training the XGBoost
model = XGBClassifier(use_label_encoder=False, n_estimators=450, max_depth=5, learning_rate=0.03, gamma=3)
model.fit(Xtrain, yTrain, early_stopping_rounds=50, eval_set=eval_set, eval_metric="logloss", verbose=True)

# Test the models accuracy
predictions = model.predict(Xtest)
predictions = [round(value) for value in predictions]
accuracy = accuracy_score(yTest, predictions)
print("Accuracy: %.2f%%" % (accuracy * 100.0))
