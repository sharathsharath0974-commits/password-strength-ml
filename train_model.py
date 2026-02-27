import joblib
from sklearn.linear_model import LogisticRegression
import numpy as np

passwords = ["1234", "password", "abc123", "Strong@123", "Very$Strong#2026"]
labels = [0, 0, 0, 1, 1]

def features(p):
    return [
        len(p),
        sum(c.isdigit() for c in p),
        sum(c.isupper() for c in p),
        sum(c.islower() for c in p),
        sum(not c.isalnum() for c in p)
    ]

X = np.array([features(p) for p in passwords])
y = np.array(labels)

model = LogisticRegression()
model.fit(X, y)

joblib.dump(model, "password_model.pkl")
print("✔ ML model trained and saved")