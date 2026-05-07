# 🎯 Real-Time AI Object Detection & Tracking System

A powerful **real-time computer vision web app** built with **Streamlit + YOLOv8 + WebRTC**, capable of detecting and tracking **80+ objects live from a webcam feed** with alerts, counting, and evidence saving.

---

## 🚀 Features

### 📡 Live Object Detection
- Real-time webcam inference using **YOLOv8 (yolov8n.pt)**
- Detects **80+ COCO dataset objects**
- Bounding boxes with confidence scores
- Smooth frame processing using Streamlit WebRTC

### 📊 Object Tracking & Counting
- Live object counting per class
- On-screen overlay display
- Sidebar statistics dashboard

### 🚨 Smart Alert System
- Configurable alert targets (person, phone, car, etc.)
- Timestamped detection logs
- Last 10 alerts history tracking

### 💾 Frame Saving System
- Manual frame capture
- Auto-save mode every few seconds
- Local evidence storage (`saved_frames/`)
- Download & delete saved images

### 🎨 Modern UI
- Cyberpunk-style Streamlit interface
- Interactive sidebar control panel
- Real-time metrics dashboard
- Threat level indicator (Low / Medium / High)

### 🔄 Advanced Video Processing
- Mirror mode (flip view)
- FPS overlay
- Optimized inference (every 2 frames)
- Thread-safe shared state handling

---

## 🧠 Tech Stack

- **Python 3.9+**
- [Streamlit](https://streamlit.io/)
- [streamlit-webrtc](https://github.com/whitphx/streamlit-webrtc)
- [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics)
- OpenCV
- NumPy
- PyAV
- Threading

---

## 📦 Installation

### 1. Clone the repository
```bash
git clone https://github.com/your-username/object-detection-streamlit.git
cd object-detection-streamlit
2. Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
3. Install dependencies
pip install -r requirements.txt
📄 Requirements (requirements.txt)
streamlit
streamlit-webrtc
ultralytics
opencv-python
numpy
av
▶️ Run the App
streamlit run app.py
📷 How It Works
Click START DETECTION
Allow webcam access
The YOLOv8 model processes frames in real time
Objects are detected, counted, and displayed instantly
Alerts trigger when selected objects appear
Frames can be saved manually or automatically
⚙️ Configuration Options

In the sidebar:

🔄 Mirror Mode ON/OFF
📊 Object Counting display
🚨 Alert system toggle
🎯 Select alert objects
🤖 Auto-save frames
📁 Project Structure
.
├── app.py
├── saved_frames/
├── requirements.txt
└── README.md
🧪 Example Use Cases
Security surveillance system
AI-based monitoring dashboard
Smart classroom / attendance tracking
Object detection demo app
Computer vision learning project
⚠️ Notes
First run may take ~20–30 seconds to load YOLO model
Works best with a stable webcam
GPU is optional but improves performance

👨‍💻 Author

Built with ❤️ using YOLOv8 + Streamlit

⭐ If you like this project

Give it a star ⭐ on GitHub and share it with others!
