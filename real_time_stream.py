# real_time_stream.py

from scapy.all import sniff
from collections import defaultdict
import pandas as pd
import time
import joblib

# In-memory packet stats (reset each second)
packet_stats = defaultdict(lambda: {
    'Received Packets': 0,
    'Received Bytes': 0,
    'Sent Bytes': 0,
    'Sent Packets': 0,
    'Packets Looked Up': 0,
    'Packets Matched': 0,
    'Max Size': -1
})

# Load the trained model and feature names
clf = joblib.load('model/model.pkl')
feature_names = joblib.load('model/features1.pkl')

def process_packet(packet):
    if packet.haslayer("IP"):
        try:
            port = packet.sport if hasattr(packet, "sport") else 0
            size = len(packet)
            stats = packet_stats[port]
            stats['Received Packets'] += 1
            stats['Received Bytes'] += size
            stats['Sent Packets'] += 1
            stats['Sent Bytes'] += size
            stats['Packets Looked Up'] += 1
            stats['Packets Matched'] += 1
        except:
            pass

def real_time_data_stream():
    while True:
        packet_stats.clear()
        sniff(timeout=1, prn=process_packet, store=0)  # Capture for 1 second

        # Convert to DataFrame row format
        for port, stats in packet_stats.items():
            row = {
                'Port Number': port,
                'Received Packets': stats['Received Packets'],
                'Received Bytes': stats['Received Bytes'],
                'Sent Bytes': stats['Sent Bytes'],
                'Sent Packets': stats['Sent Packets'],
                'Packets Looked Up': stats['Packets Looked Up'],
                'Packets Matched': stats['Packets Matched'],
                'Max Size': stats['Max Size'],
            }

            # Convert row to DataFrame and ensure it matches the feature set
            row_df = pd.DataFrame([row], columns=feature_names).fillna(0)

            # Predict using the ML model
            prediction = clf.predict(row_df)
            row['Label'] = prediction[0]  # Add prediction to the row

            yield pd.Series(row)
