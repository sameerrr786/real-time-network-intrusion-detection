from scapy.all import sniff
from collections import defaultdict
import pandas as pd
import time
import random
import joblib

# Initialize stats per port
packet_stats = defaultdict(lambda: {
    'prev': {},
    'curr': {
        'Received Packets': 0,
        'Received Bytes': 0,
        'Sent Bytes': 0,
        'Sent Packets': 0,
        'Port alive Start': time.time(),
        'Packets Rx Dropped': 0,
        'Packets Tx Dropped': 0,
        'Packets Rx Errors': 0,
        'Packets Tx Errors': 0,
        'Connection Point': random.randint(0, 10),  # Simulated
        'Total Load/Rate': 0,
        'Total Load/Latest': 0,
        'Unknown Load/Rate': 0,
        'Unknown Load/Latest': 0,
        'Latest bytes counter': 0,
        'is_valid': 1,
        'Table ID': 0,
        'Active Flow Entries': random.randint(1, 10),
        'Packets Looked Up': 0,
        'Packets Matched': 0,
        'Max Size': -1,
    }
})

# Load the trained model and feature names
clf = joblib.load('model/model.pkl')
feature_names = joblib.load('model/features1.pkl')

def process_packet(packet):
    if packet.haslayer("IP"):
        try:
            port = packet.sport if hasattr(packet, "sport") else 0
            size = len(packet)

            stats = packet_stats[port]['curr']
            stats['Received Packets'] += 1
            stats['Received Bytes'] += size
            stats['Sent Packets'] += 1
            stats['Sent Bytes'] += size

            # Simulate load counters
            stats['Total Load/Rate'] += random.randint(0, 100)
            stats['Unknown Load/Rate'] += random.randint(0, 100)
            stats['Latest bytes counter'] = size
            stats['Packets Looked Up'] += 1
            stats['Packets Matched'] += 1

        except Exception as e:
            print(f"Error: {e}")

# Sniffing phase
print("Sniffing packets for 10 seconds...")
sniff(timeout=10, prn=process_packet)
print("Sniffing complete.")

# Build the final DataFrame
rows = []

for port, values in packet_stats.items():
    curr = values['curr']
    prev = values['prev']

    duration = time.time() - curr['Port alive Start']
    
    row = {
        'Port Number': port,
        'Received Packets': curr['Received Packets'],
        'Received Bytes': curr['Received Bytes'],
        'Sent Bytes': curr['Sent Bytes'],
        'Sent Packets': curr['Sent Packets'],
        'Port alive Duration (S)': round(duration, 2),
        'Packets Rx Dropped': curr['Packets Rx Dropped'],
        'Packets Tx Dropped': curr['Packets Tx Dropped'],
        'Packets Rx Errors': curr['Packets Rx Errors'],
        'Packets Tx Errors': curr['Packets Tx Errors'],
        
        # Deltas (simulated or computed)
        'Delta Received Packets': curr['Received Packets'] - prev.get('Received Packets', 0),
        'Delta Received Bytes': curr['Received Bytes'] - prev.get('Received Bytes', 0),
        'Delta Sent Bytes': curr['Sent Bytes'] - prev.get('Sent Bytes', 0),
        'Delta Sent Packets': curr['Sent Packets'] - prev.get('Sent Packets', 0),
        'Delta Port alive Duration (S)': round(duration - prev.get('Port alive Duration (S)', 0), 2),
        'Delta Packets Rx Dropped': curr['Packets Rx Dropped'] - prev.get('Packets Rx Dropped', 0),
        ' Delta Packets Tx Dropped': curr['Packets Tx Dropped'] - prev.get('Packets Tx Dropped', 0),
        'Delta Packets Rx Errors': curr['Packets Rx Errors'] - prev.get('Packets Rx Errors', 0),
        'Delta Packets Tx Errors': curr['Packets Tx Errors'] - prev.get('Packets Tx Errors', 0),

        # Remaining fields
        'Connection Point': curr['Connection Point'],
        'Total Load/Rate': curr['Total Load/Rate'],
        'Total Load/Latest': curr['Total Load/Rate'],  # assuming same for now
        'Unknown Load/Rate': curr['Unknown Load/Rate'],
        'Unknown Load/Latest': curr['Unknown Load/Rate'],
        'Latest bytes counter': curr['Latest bytes counter'],
        'is_valid': curr['is_valid'],
        'Table ID': curr['Table ID'],
        'Active Flow Entries': curr['Active Flow Entries'],
        'Packets Looked Up': curr['Packets Looked Up'],
        'Packets Matched': curr['Packets Matched'],
        'Max Size': curr['Max Size'],
        'Label': None  # For prediction mode
    }

    # Convert row to DataFrame and ensure it matches the feature set
    row_df = pd.DataFrame([row], columns=feature_names).fillna(0)

    # Predict using the ML model
    prediction = clf.predict(row_df)
    row['Label'] = prediction[0]  # Add prediction to the row

    # Update prev for delta tracking next round
    values['prev'] = curr.copy()
    rows.append(row)

# Convert to DataFrame
df = pd.DataFrame(rows)
print("\n📊 Real-time Feature Snapshot with Predictions:\n")
print(df.head())
