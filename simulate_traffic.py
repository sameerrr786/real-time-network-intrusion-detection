# simulate_traffic.py

import pandas as pd
import time
import random

def stream_data(file_path):
    df = pd.read_csv(file_path)
    df.dropna(inplace=True)

    for index, row in df.iterrows():
        yield row
        time.sleep(random.uniform(0.5, 2))  # Simulate delay
