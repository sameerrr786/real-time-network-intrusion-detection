# train_model.py

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report
import joblib
import os
from xgboost import XGBClassifier

# Load the dataset
df = pd.read_csv('data/Network_Intrusion_Detection_Dataset.csv')

# Drop rows with missing values
df.dropna(inplace=True)

# Label encoding for categorical features
for col in df.select_dtypes(include=['object']).columns:
    df[col] = LabelEncoder().fit_transform(df[col])

# Split features and label
X = df.drop('Label', axis=1)
y = df['Label']

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Train model
clf = XGBClassifier(n_estimators=100, random_state=42, use_label_encoder=False, eval_metric='logloss')
clf.fit(X_train, y_train)

# Save model and feature1 names
os.makedirs('model', exist_ok=True)
joblib.dump(clf, 'model/model.pkl')
joblib.dump(X_train.columns.tolist(), 'model/features1.pkl')  # ✅ Save features

# Evaluate
y_pred = clf.predict(X_test)
print(classification_report(y_test, y_pred))
