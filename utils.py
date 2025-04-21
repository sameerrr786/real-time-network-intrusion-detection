# utils.py

import joblib
import pandas as pd

def load_model():
    return joblib.load('model/model.pkl')

def preprocess_row(row):
    df = pd.DataFrame([row])

    # Convert categorical to numeric if any
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype('category').cat.codes

    # Drop the label column if it's there
    if 'Label' in df.columns:
        df = df.drop('Label', axis=1)

    return df
