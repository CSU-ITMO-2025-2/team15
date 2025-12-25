import pandas as pd
import pickle
from sklearn.model_selection import train_test_split

df = pd.read_csv('winequality-red.csv')
df.columns = ["fixed_acidity","volatile_acidity","citric_acid","residual_sugar","chlorides","free_sulfur_dioxide","total_sulfur_dioxide","density","pH","sulphates","alcohol","quality"]
X = df.drop(columns = 'quality')
y = df['quality']

X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.2)
from sklearn.ensemble import RandomForestClassifier
clf = RandomForestClassifier(n_estimators=100)
clf.fit(X_train,y_train)

filehandler = open(b"cfl.obj","wb")
pickle.dump(clf,filehandler)