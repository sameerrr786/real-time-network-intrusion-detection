# Real-Time Network Intrusion Detection System

📡 **Real-Time Network Intrusion Detection System** is a machine learning-powered application designed to monitor and analyze network traffic in real-time. It detects and classifies various types of network intrusions, ensuring enhanced network security.

---

## Features

- **Real-Time Monitoring**: Captures live network traffic and processes it in real-time.
- **Intrusion Detection**: Uses a trained machine learning model to classify network traffic into categories such as:
  - 🟢 Legitimate Network Traffic
  - 🔴 DDoS Attack Detected
  - 🔴 Protocol Exploitation Detected
  - 🔴 Reconnaissance Detected
  - 🔴 Traffic Manipulation Detected
  - 🔴 Buffer Overflow Detected
- **Interactive Dashboard**: Visualize network traffic and predictions using an intuitive Streamlit-based UI.
- **Customizable**: Easily extendable to include additional features or integrate with other systems.

---

## Installation

### Prerequisites

- Python 3.8 or higher
- Git installed on your system

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/real-time-network-intrusion-detection.git
   cd real-time-network-intrusion-detection# real-time-network-intrusion-detection

 ## usage  
 Real-Time Monitoring:

Launch the app and navigate to the "Real-Time Monitoring" page.
View live network traffic statistics and predictions.
Advanced Analytics:

Explore detailed analytics and visualizations of network traffic.
Detection Results:

Review the predictions and take necessary actions based on the detected intrusions.

## project structure
real-time-network-intrusion-detection/
├── app.py                     # Streamlit app for the dashboard
├── train_model.py             # Script to train the ML model
├── real_time_stream.py        # Real-time packet processing
├── real_time_sniffer.py       # Packet sniffing and feature extraction
├── data/                      # Directory for the dataset
├── model/                     # Directory for the trained model and features
├── requirements.txt           # Python dependencies
└── README.md                  # Project documentation

## Technologies Used
Python: Core programming language
Scapy: For packet sniffing
XGBoost: Machine learning model for intrusion detection
Streamlit: Interactive dashboard for real-time monitoring
Plotly: Data visualization