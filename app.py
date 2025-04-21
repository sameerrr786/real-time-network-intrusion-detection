import streamlit as st
import pandas as pd
from scapy.all import sniff
from collections import defaultdict
import time
import random
import joblib
import plotly.express as px

st.set_page_config(page_title="Real-Time Packet Monitor", layout="wide")
st.title("📡 Real-Time Network Feature Dashboard")

# Initialize session state to store stats
if "packet_stats" not in st.session_state:
    st.session_state.packet_stats = defaultdict(lambda: {
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
            'Connection Point': random.randint(0, 10),
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

# Define label mapping
label_mapping = {
    0: "🟢 LEGITIMATE NETWORK TRAFFIC",
    1: "🔴 DDoS ATTACK DETECTED",
    2: "🔴 PROTOCOL EXPLOITATION DETECTED",
    3: "🔴 RECONNAISSANCE DETECTED",
    4: "🔴 TRAFFIC MANIPULATION DETECTED",
    5: "🔴 BUFFER OVERFLOW DETECTED"
}

# Add a filter to only process TCP packets
def process_packet(packet):
    if packet.haslayer("IP") and packet.haslayer("TCP"):
        try:
            port = packet.sport if hasattr(packet, "sport") else 0
            size = len(packet)
            stats = st.session_state.packet_stats[port]['curr']
            stats['Received Packets'] += 1
            stats['Received Bytes'] += size
            stats['Sent Packets'] += 1
            stats['Sent Bytes'] += size
            stats['Total Load/Rate'] += random.randint(0, 100)
            stats['Unknown Load/Rate'] += random.randint(0, 100)
            stats['Latest bytes counter'] = size
            stats['Packets Looked Up'] += 1
            stats['Packets Matched'] += 1
        except Exception as e:
            st.error(f"Packet processing error: {e}")

# Update the sniff timeout to 5 seconds
sniff(timeout=5, prn=process_packet)

# Convert to DataFrame
rows = []

for port, values in st.session_state.packet_stats.items():
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
        'Delta Received Packets': curr['Received Packets'] - prev.get('Received Packets', 0),
        'Delta Received Bytes': curr['Received Bytes'] - prev.get('Received Bytes', 0),
        'Delta Sent Bytes': curr['Sent Bytes'] - prev.get('Sent Bytes', 0),
        'Delta Sent Packets': curr['Sent Packets'] - prev.get('Sent Packets', 0),
        'Delta Port alive Duration (S)': round(duration - prev.get('Port alive Duration (S)', 0), 2),
        'Delta Packets Rx Dropped': curr['Packets Rx Dropped'] - prev.get('Packets Rx Dropped', 0),
        ' Delta Packets Tx Dropped': curr['Packets Tx Dropped'] - prev.get('Packets Tx Dropped', 0),
        'Delta Packets Rx Errors': curr['Packets Rx Errors'] - prev.get('Packets Rx Errors', 0),
        'Delta Packets Tx Errors': curr['Packets Tx Errors'] - prev.get('Packets Tx Errors', 0),
        'Connection Point': curr['Connection Point'],
        'Total Load/Rate': curr['Total Load/Rate'],
        'Total Load/Latest': curr['Total Load/Rate'],
        'Unknown Load/Rate': curr['Unknown Load/Rate'],
        'Unknown Load/Latest': curr['Unknown Load/Rate'],
        'Latest bytes counter': curr['Latest bytes counter'],
        'is_valid': curr['is_valid'],
        'Table ID': curr['Table ID'],
        'Active Flow Entries': curr['Active Flow Entries'],
        'Packets Looked Up': curr['Packets Looked Up'],
        'Packets Matched': curr['Packets Matched'],
        'Max Size': curr['Max Size'],
        'Label': None
    }

    # Convert row to DataFrame and ensure it matches the feature set
    row_df = pd.DataFrame([row], columns=feature_names).fillna(0)

    # Predict using the ML model
    prediction = clf.predict(row_df)
    row['Label'] = label_mapping[prediction[0]]  # Map prediction to description

    values['prev'] = curr.copy()
    rows.append(row)

df = pd.DataFrame(rows)
st.dataframe(df, use_container_width=True)

# Display predictions below the real-time data
st.subheader("Predicted Features")
st.write(df[['Port Number', 'Label']])  # Show only relevant columns with mapped labels

# Add visualization
st.subheader("Prediction Visualization")
if not df.empty:
    label_counts = df['Label'].value_counts().reset_index()
    label_counts.columns = ['Label', 'Count']

    # Create a bar chart using Plotly
    fig = px.bar(
        label_counts,
        x='Label',
        y='Count',
        color='Label',
        title="Distribution of Predicted Labels",
        labels={'Label': 'Predicted Label', 'Count': 'Number of Predictions'},
        color_discrete_sequence=px.colors.qualitative.Set1
    )
    st.plotly_chart(fig, use_container_width=True, key=f"prediction_visualization_{time.time()}")
else:
    st.info("No data available for visualization.")

# Add custom CSS for styling
st.markdown("""
    <style>
    /* Main background and text colors */
    .main {
        background-color: #1e1e2f;
        color: #ffffff;
    }

    /* Sidebar styling */
    .css-1d391kg {
        background-color: #2c2c3e;
        color: #ffffff;
    }

    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #00c8ff !important;
        font-family: 'Arial', sans-serif;
    }

    /* Dataframe styling */
    .stDataFrame {
        background-color: #2c2c3e;
        color: #ffffff;
        border: 1px solid #00c8ff;
    }

    /* Buttons */
    .stButton>button {
        background-color: #00c8ff;
        color: #ffffff !important;
        border: 1px solid #00c8ff;
        border-radius: 5px;
        font-size: 16px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #ffffff;
        color: #00c8ff !important;
    }

    /* Metrics */
    .css-1xarl3l {
        background-color: #2c2c3e;
        border: 1px solid #00c8ff;
        border-radius: 5px;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background-color: #2c2c3e;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1e1e2f;
        color: #ffffff !important;
        border: 1px solid #00c8ff;
        border-radius: 5px;
    }

    /* Footer */
    footer {
        color: #ffffff !important;
        border-top: 1px solid #00c8ff;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# Add a styled header
st.markdown("""
    <div style="background-color: #2c2c3e; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
        <h1 style="text-align: center; color: #00c8ff;">📡 Real-Time Network Feature Dashboard</h1>
        <p style="text-align: center; color: #ffffff;">Monitor and analyze network traffic in real-time with AI-powered predictions.</p>
    </div>
""", unsafe_allow_html=True)

# Add metrics at the top
st.markdown("<h2 style='color: #00c8ff;'>📊 Key Metrics</h2>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
col1.metric("Active Ports", len(st.session_state.packet_stats))
col2.metric("Total Packets", sum(stats['curr']['Received Packets'] for stats in st.session_state.packet_stats.values()))
col3.metric("Unique Labels", len(label_mapping))

# Display predictions below the real-time data
st.markdown("<h2 style='color: #00c8ff;'>📋 Real-Time Data Table</h2>", unsafe_allow_html=True)
st.dataframe(df, use_container_width=True)

# Add visualization
st.markdown("<h2 style='color: #00c8ff;'>📈 Prediction Visualization</h2>", unsafe_allow_html=True)
if not df.empty:
    label_counts = df['Label'].value_counts().reset_index()
    label_counts.columns = ['Label', 'Count']

    # Create a bar chart using Plotly
    fig = px.bar(
        label_counts,
        x='Label',
        y='Count',
        color='Label',
        title="Distribution of Predicted Labels",
        labels={'Label': 'Predicted Label', 'Count': 'Number of Predictions'},
        color_discrete_sequence=px.colors.qualitative.Set1
    )
    st.plotly_chart(fig, use_container_width=True, key=f"prediction_visualization_{time.time()}")
else:
    st.info("No data available for visualization.")

# Add a footer
st.markdown("""
    <footer style="background-color: #2c2c3e; padding: 10px; border-radius: 5px; margin-top: 20px; text-align: center;">
        <p style="color: #ffffff;">© 2025 Real-Time Network Monitor | Powered by Streamlit</p>
    </footer>
""", unsafe_allow_html=True)

# Refresh every second
time.sleep(1)
st.rerun()

# Add a new page for navigation
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/network-protection.png", width=100)
    st.markdown("## Navigation")
    page = st.selectbox("Choose a page", ["Real-Time Monitoring", "Advanced Analytics", "Detection Result"])


