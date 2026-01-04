import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib

data = pd.read_csv("dataset/liver.csv")

data['gender'] = data['gender'].map({'Male': 1, 'Female': 0})
data['ag_ratio'] = data['ag_ratio'].fillna(data['ag_ratio'].mean())

X = data.drop('is_patient', axis=1)
y = data['is_patient']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = RandomForestClassifier(
    n_estimators=300,
    max_depth=10,
    class_weight='balanced',
    random_state=42
)

model.fit(X_train, y_train)

joblib.dump(model, "model/liver_model.pkl")
print("Model trained and saved")
