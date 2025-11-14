# ============================================================
# Driver Safety Monitor (with EAR Simulation + Real-time SocketIO)
# ============================================================

import eventlet
eventlet.monkey_patch()

import os
import time
import random
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO

# ---------------------------------------------
# APP INITIALIZATION
# ---------------------------------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = 'driver_safety_monitor_secret_key'

# Configure SocketIO for real-time updates
socketio = SocketIO(app,
                    cors_allowed_origins="*",
                    async_mode='eventlet',
                    logger=True,
                    engineio_logger=False)

# ---------------------------------------------
# GLOBAL STATE VARIABLES
# ---------------------------------------------
latest_eye = {
    "status": "open",
    "duration": 0.0,
    "alert_level": None,
    "alert_type": None,
    "alert_message": None,
    "sensitivity": 1.0,
    "ear_value": 0.0,       # 👁️ Eye Aspect Ratio
    "timestamp": datetime.now().strftime("%H:%M:%S")
}

eye_statistics = {
    "total_alerts": 0,
    "current_session_start": time.time(),
    "max_closure_time": 0,
    "alert_history": []
}

drivers_data = [
    {"id": 1, "name": "John Driver", "vehicle": "Truck A123", "status": "safe", "location": "Highway I-95", "phone": "+1-555-0101"},
    {"id": 2, "name": "Sarah Wilson", "vehicle": "Van B456", "status": "warning", "location": "Route 66", "phone": "+1-555-0102"},
    {"id": 3, "name": "Mike Johnson", "vehicle": "Car C789", "status": "danger", "location": "City Center", "phone": "+1-555-0103"}
]

# ---------------------------------------------
# STATIC AND WEB ROUTES
# ---------------------------------------------
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(os.path.join(app.root_path, 'static'), filename)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test', methods=['GET'])
def test_func():
    return jsonify({"ok": True}), 200


# ---------------------------------------------
# POST ENDPOINT FOR RASPBERRY PI (DATA RECEIVER)
# ---------------------------------------------
@app.route('/eye', methods=['POST'])
def eye_hook():
    """
    Receives data from Raspberry Pi — includes EAR + eye status.
    Expected JSON:
    {
        "status": "open"/"closed",
        "duration": <float>,
        "alert_level": "normal"/"warning"/"danger",
        "alert_type": "blink"/"drowsy"/etc,
        "alert_message": "Eyes closed too long",
        "sensitivity": <float>
    }
    """
    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "Invalid JSON"}), 400

    if not data or 'status' not in data:
        return jsonify({"error": "Missing 'status' in data"}), 400

    # Safely parse duration
    try:
        duration = float(data.get("duration", 0.0))
    except (ValueError, TypeError):
        duration = 0.0

    # 👁️ EAR simulation logic based on eye status
    status = data.get("status", "unknown").lower()

    if status == "closed":
        # Eyes closed → simulate EAR between 0.10–0.24
        ear_value = round(random.uniform(0.10, 0.24), 3)
    elif status == "open":
        # Eyes open → simulate EAR between 2.50–3.50
        ear_value = round(random.uniform(0.250, 0.350), 3)
    else:
        # Unknown → no valid EAR
        ear_value = 0.0

    # Update global state
    latest_eye.update({
        "status": status,
        "duration": duration,
        "alert_level": data.get("alert_level"),
        "alert_type": data.get("alert_type"),
        "alert_message": data.get("alert_message"),
        "sensitivity": data.get("sensitivity", 1.0),
        "ear_value": ear_value,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })

    # Update statistics
    update_statistics(data, ear_value)

    # Emit to all connected dashboards
    socketio.emit('eye_status', latest_eye)
    socketio.emit('statistics_update', eye_statistics)

    print(f"📩 EAR={ear_value:.3f} | Status={latest_eye['status']} | Duration={duration}")
    return jsonify({"ok": True}), 200


# ---------------------------------------------
# STATISTICS HANDLER
# ---------------------------------------------
def update_statistics(data, ear_value):
    """Update stats and alert history"""
    if data.get('alert_level') and data['alert_level'] != latest_eye.get('alert_level'):
        eye_statistics["total_alerts"] += 1

    if data.get('status') == 'closed' and data.get('duration', 0) > eye_statistics["max_closure_time"]:
        eye_statistics["max_closure_time"] = data['duration']

    history_entry = {
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "status": data.get('status'),
        "duration": data.get('duration', 0),
        "ear_value": ear_value,
        "alert_level": data.get('alert_level'),
        "alert_type": data.get('alert_type')
    }

    eye_statistics["alert_history"].append(history_entry)
    eye_statistics["alert_history"] = eye_statistics["alert_history"][-50:]


# ---------------------------------------------
# STATS & DRIVERS ROUTES
# ---------------------------------------------
@app.route('/statistics', methods=['GET'])
def get_statistics():
    return jsonify(eye_statistics), 200

@app.route('/reset_stats', methods=['POST'])
def reset_statistics():
    global eye_statistics
    eye_statistics = {
        "total_alerts": 0,
        "current_session_start": time.time(),
        "max_closure_time": 0,
        "alert_history": []
    }
    return jsonify({"ok": True}), 200

@app.route('/drivers', methods=['GET'])
def get_drivers():
    return jsonify(drivers_data), 200


# ---------------------------------------------
# SOCKET.IO EVENTS
# ---------------------------------------------
@socketio.on('connect')
def handle_connect():
    print(f"✅ Client connected: {request.sid}")
    socketio.emit('eye_status', latest_eye, room=request.sid)
    socketio.emit('statistics_update', eye_statistics, room=request.sid)
    socketio.emit('drivers_update', drivers_data, room=request.sid)

@socketio.on('disconnect')
def handle_disconnect():
    print(f"❌ Client disconnected: {request.sid}")

@socketio.on('sos_emergency')
def handle_sos(data):
    print(f"🚨 SOS Emergency received: {data}")
    socketio.emit('sos_alert', {
        'driver_id': data.get('driver_id'),
        'timestamp': data.get('timestamp'),
        'location': data.get('location'),
        'emergency': True
    })

@socketio.on('message')
def handle_message(data):
    print(f"💬 Message received: {data}")
    socketio.emit('message', data)


# ---------------------------------------------
# MAIN
# ---------------------------------------------
if __name__ == '__main__':
    print("🚀 Starting Driver Monitoring Dashboard with EAR simulation on http://0.0.0.0:5000")
    print("📡 Socket.IO server ready for connections")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
