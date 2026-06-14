# 🚗 Driver Drowsiness Detection & Alert Dashboard

A real-time IoT safety system that detects driver drowsiness using **computer vision** and streams live alerts to a web dashboard via **WebSockets**.

The system uses **OpenCV facial landmark detection** to compute the Eye Aspect Ratio (EAR) in real time. When EAR drops below a threshold (eyes closing), the system triggers instant drowsiness alerts — pushed to a live dashboard with audio SOS, alert history, and driver contact management.

---

## 🎯 What It Does

1. **Detects drowsiness** — a camera (Raspberry Pi or webcam) captures the driver's face. OpenCV extracts 68 facial landmarks and computes the Eye Aspect Ratio (EAR) each frame.
2. **Triggers alerts** — when EAR drops below the drowsiness threshold (sustained eye closure), the Flask backend fires an alert via Socket.IO.
3. **Live dashboard** — a real-time web interface shows live EAR values, alert history, driver contact details, and an audio SOS trigger.

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | Python, Flask, Socket.IO |
| **Computer Vision** | OpenCV, Facial Landmark Detection, EAR Algorithm |
| **Frontend** | HTML, CSS, JavaScript |
| **Real-Time Communication** | WebSockets (Socket.IO) |
| **Alert System** | Audio SOS trigger |
| **Hardware** | Raspberry Pi (or any webcam-equipped device) |

---

## 📁 Project Structure

```
driverdashboard/
├── server2.py             # Flask + Socket.IO backend (receives EAR data, pushes alerts)
├── index3.html            # Live dashboard interface
├── requirements.txt       # Python dependencies
├── css/                   # Dashboard styling
├── sounds/                # Audio files for SOS alert trigger
└── static/                # Static assets
```

---

## 🔑 Key Technical Decisions

**Why Eye Aspect Ratio (EAR)?**
EAR is a simple, effective metric: it's the ratio of vertical to horizontal eye distances from facial landmarks. Open eyes have EAR ≈ 0.3; closed eyes drop to ≈ 0.05. A sustained drop below a threshold reliably detects drowsiness without needing a trained ML model — making it fast enough for real-time use on low-power hardware like Raspberry Pi.

**Why Socket.IO instead of polling?**
The dashboard needs instant alerts. HTTP polling would either be too slow (missed alerts) or too frequent (server overload). Socket.IO provides persistent WebSocket connections for sub-second alert delivery. Rate throttling was added to handle high-frequency EAR data without overloading the server under continuous operation.

**Why a web dashboard instead of a mobile app?**
Accessibility — any device with a browser can monitor the driver. No installation, no platform dependency. The dashboard works on phones, tablets, and desktops equally.

---

## ⚙️ How to Run

### Prerequisites
```bash
pip install -r requirements.txt
```

### Start the server
```bash
python server2.py
```

### Open the dashboard
Navigate to `http://localhost:5000` (or the server's IP) in any browser.

### Connect a camera source
The system receives EAR data via REST API. Connect a Raspberry Pi or webcam running the OpenCV facial landmark detector, configured to POST EAR values to the server endpoint.

---

## 📊 Features

- **Live EAR monitoring** — real-time Eye Aspect Ratio values displayed on the dashboard
- **Instant drowsiness alerts** — WebSocket push notifications when EAR drops below threshold
- **Alert history** — timestamped log of all drowsiness events
- **Driver contact management** — store and display driver contact information
- **Audio SOS trigger** — emergency sound alert when drowsiness is detected
- **Rate throttling** — handles high-frequency data streams without server overload

---

## 💡 Possible Extensions

- Add a trained CNN eye-state classifier alongside the EAR threshold for higher accuracy
- Mobile push notifications via Twilio/FCM
- GPS integration for location-stamped alerts
- Multi-driver fleet monitoring dashboard
- Historical drowsiness pattern analysis

---

*IoT + Computer Vision project — real-time safety system using OpenCV, Flask, and WebSockets.*
