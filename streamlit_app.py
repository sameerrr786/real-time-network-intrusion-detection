# streamlit_app.py

import streamlit as st
import pandas as pd
import time
from collections import Counter
import matplotlib.pyplot as plt
from real_time_stream import real_time_data_stream
from utils import load_model, preprocess_row
import joblib

# Load expected feature names and model
feature_names = joblib.load("model/features.pkl")
model = load_model()

# Set Streamlit page configuration
st.set_page_config(page_title="Intrusion Detection Dashboard", layout="wide")
st.title("🛡️ Real-Time Intrusion Detection Dashboard")

# Create placeholders for dynamic updates
placeholder = st.empty()
alert_area = st.empty()

# Counters and log
attack_counter = Counter()
log_data = []

# Class label mapping
label_map = {
    0: "Normal",
    1: "DoS Attack",
    2: "Probe Attack",
    3: "R2L Attack",
    4: "U2R Attack"
}

# Start real-time packet streaming
data_gen = real_time_data_stream()

for row in data_gen:
    # Preprocess row and align with model features
    processed = preprocess_row(row)
    processed = processed.reindex(columns=feature_names, fill_value=0)

    # Optional debug info:
    # st.write("Missing columns:", set(feature_names) - set(processed.columns))
    # st.write("Extra columns:", set(processed.columns) - set(feature_names))

    prediction = model.predict(processed)[0]
    label = label_map.get(prediction, "Unknown")

    # Log the data row + prediction
    row_dict = row.to_dict()
    row_dict["Prediction"] = label
    log_data.append(row_dict)
    attack_counter[label] += 1

    # Show alert
    with alert_area.container():
        if prediction != 0:
            st.error(f"🚨 Intrusion Detected! Type: {label}")
        else:
            st.success("✅ Normal Traffic")

    # Display log and charts
    with placeholder.container():
        st.subheader("📋 Recent Traffic Log")
        df_log = pd.DataFrame(log_data[-10:])
        st.dataframe(df_log, use_container_width=True)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📊 Attack Type Distribution")
            fig, ax = plt.subplots(figsize=(4, 3))
            ax.bar(attack_counter.keys(), attack_counter.values(), color=["green", "red", "orange", "blue", "purple"])
            ax.set_ylabel("Count")
            ax.set_title("Live Detection Summary")
            plt.xticks(rotation=20)
            st.pyplot(fig)

        with col2:
            st.subheader("🧁 Attack vs Normal Ratio")
            fig2, ax2 = plt.subplots(figsize=(4, 3))
            ax2.pie(attack_counter.values(), labels=attack_counter.keys(), autopct='%1.1f%%',
                    colors=["green", "red", "orange", "blue", "purple"])
            ax2.set_title("Traffic Type Ratio")
            st.pyplot(fig2)

    time.sleep(1)
