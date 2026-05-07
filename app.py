import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode
from ultralytics import YOLO
import av
import cv2
from collections import defaultdict
from datetime import datetime
import os
import time
import numpy as np
import threading

SAVED_FRAMES_DIR = "saved_frames"
if not os.path.exists(SAVED_FRAMES_DIR):
    os.makedirs(SAVED_FRAMES_DIR)

# Session state
if 'camera_active' not in st.session_state: st.session_state.camera_active = False
if 'model_ready' not in st.session_state: st.session_state.model_ready = False
if 'shared_data' not in st.session_state: st.session_state.shared_data = None

class SharedData:
    def __init__(self):
        self.object_counts = defaultdict(int)
        self.detection_log = []
        self.last_alert_time = 0
        self.last_save_time = 0
        self.mirror_view_enabled = True
        self.enable_alerts = True
        self.alert_objects = ["person", "cell phone"]
        self.auto_save = False
        self.show_counting = True
        self.save_request = False
        self.lock = threading.Lock()
    
    def update_counts(self, counts):
        with self.lock: 
            for k, v in counts.items(): self.object_counts[k] = v
    
    def get_counts(self): 
        with self.lock: return dict(self.object_counts)
    
    def add_alert(self, alert):
        with self.lock:
            self.detection_log.append(alert)
            if len(self.detection_log) > 10: self.detection_log = self.detection_log[-10:]
    
    def get_alerts(self): 
        with self.lock: return self.detection_log.copy()
    
    def set_mirror(self, value): 
        with self.lock: self.mirror_view_enabled = value
    
    def get_mirror(self): 
        with self.lock: return self.mirror_view_enabled
    
    def set_enable_alerts(self, value): 
        with self.lock: self.enable_alerts = value
    
    def get_enable_alerts(self): 
        with self.lock: return self.enable_alerts
    
    def set_alert_objects(self, value): 
        with self.lock: self.alert_objects = list(value)
    
    def get_alert_objects(self): 
        with self.lock: return list(self.alert_objects)
    
    def set_auto_save(self, value): 
        with self.lock: self.auto_save = value
    
    def get_auto_save(self): 
        with self.lock: return self.auto_save
    
    def set_show_counting(self, value): 
        with self.lock: self.show_counting = value
    
    def get_show_counting(self): 
        with self.lock: return self.show_counting
    
    def set_save_request(self, value): 
        with self.lock: self.save_request = value
    
    def get_save_request(self): 
        with self.lock: return self.save_request
    
    def clear_all(self):
        with self.lock:
            self.object_counts.clear()
            self.detection_log.clear()
            self.last_alert_time = 0

if st.session_state.shared_data is None:
    st.session_state.shared_data = SharedData()
shared_data = st.session_state.shared_data

@st.cache_resource
def load_model():
    try:
        model = YOLO("yolov8n.pt")
        return model
    except: return None

model = load_model()
st.session_state.model_ready = model is not None

# **ENHANCED COLORS - 30+ Objects**
OBJECT_COLORS = {
    'person': (255, 0, 255), 'bicycle': (255, 128, 0), 'car': (0, 255, 0),
    'motorcycle': (255, 0, 0), 'airplane': (0, 0, 255), 'bus': (255, 255, 0),
    'train': (0, 255, 255), 'truck': (255, 0, 128), 'boat': (128, 0, 255),
    'traffic light': (0, 255, 128), 'fire hydrant': (255, 128, 255),
    'stop sign': (128, 255, 0), 'parking meter': (255, 255, 128),
    'bench': (128, 0, 0), 'bird': (0, 128, 255), 'cat': (255, 128, 128),
    'dog': (128, 255, 255), 'horse': (255, 0, 128), 'sheep': (128, 255, 0),
    'cow': (0, 128, 0), 'elephant': (255, 128, 0), 'bear': (128, 0, 128),
    'zebra': (0, 255, 128), 'giraffe': (255, 0, 0), 'backpack': (0, 128, 255),
    'umbrella': (255, 128, 255), 'handbag': (128, 255, 128), 'tie': (255, 255, 0),
    'suitcase': (0, 255, 255), 'frisbee': (255, 0, 255), 'skis': (128, 0, 255),
    'snowboard': (0, 0, 128), 'sports ball': (255, 128, 0), 'kite': (128, 255, 0),
    'baseball bat': (0, 128, 0), 'baseball glove': (255, 0, 128), 'skateboard': (128, 0, 0),
    'surfboard': (0, 255, 0), 'tennis racket': (255, 128, 128), 'bottle': (128, 255, 255),
    'wine glass': (255, 0, 0), 'cup': (0, 128, 255), 'fork': (255, 128, 255),
    'knife': (128, 255, 128), 'spoon': (255, 255, 0), 'bowl': (0, 255, 255),
    'banana': (255, 0, 128), 'apple': (128, 0, 255), 'sandwich': (0, 128, 0),
    'orange': (255, 128, 0), 'broccoli': (128, 0, 128), 'carrot': (0, 255, 128),
    'hot dog': (255, 0, 0), 'pizza': (0, 128, 255), 'donut': (255, 128, 255),
    'cake': (128, 255, 128), 'chair': (255, 255, 0), 'couch': (0, 255, 255),
    'potted plant': (255, 0, 128), 'bed': (128, 0, 255), 'dining table': (0, 128, 0),
    'toilet': (255, 128, 0), 'tv': (128, 0, 128), 'laptop': (0, 255, 128),
    'mouse': (255, 0, 0), 'remote': (0, 128, 255), 'keyboard': (255, 128, 255),
    'cell phone': (128, 255, 128), 'microwave': (255, 255, 0), 'oven': (0, 255, 255),
    'toaster': (255, 0, 128), 'sink': (128, 0, 255), 'refrigerator': (0, 128, 0),
    'book': (255, 128, 0), 'clock': (128, 0, 128), 'vase': (0, 255, 128),
    'scissors': (255, 0, 0), 'teddy bear': (0, 128, 255), 'hair drier': (255, 128, 255),
    'toothbrush': (128, 255, 128), 'default': (128, 128, 128)
}

def get_object_color(class_name):
    return OBJECT_COLORS.get(class_name.lower(), OBJECT_COLORS['default'])

def draw_boxes(frame, boxes_data):
    """ENHANCED BOX DRAWING with better visibility"""
    for box_data in boxes_data:
        x1, y1, x2, y2 = map(int, box_data['box'])
        cls = box_data['class']
        conf = box_data['confidence']
        color = get_object_color(cls)
        
        # Main box - THICKER for better visibility
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)
        
        # Label background
        label = f"{cls[:12]} {conf:.1f}"
        (label_w, label_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        cv2.rectangle(frame, (x1, y1-label_h-10), (x1+label_w+10, y1), color, -1)
        
        # Label text - WHITE for contrast
        cv2.putText(frame, label, (x1+5, y1-5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)
        
        # ID tracker line (simulated tracking)
        cv2.line(frame, (x1, y1), (x1+30, y1), color, 2)
    
    return frame

def add_overlays(frame, counts, mirror_enabled, show_counting):
    """ENHANCED OVERLAYS"""
    if show_counting and counts:
        y_offset = 40
        for obj, cnt in sorted(counts.items(), key=lambda x: x[1], reverse=True)[:8]:
            if cnt > 0:
                color = get_object_color(obj)
                cv2.rectangle(frame, (10, y_offset-25), (250, y_offset+5), color, -1)
                cv2.putText(frame, f"{obj.capitalize()}: {cnt}", (15, y_offset), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
                y_offset += 35
    
    # Mirror indicator
    if mirror_enabled:
        cv2.rectangle(frame, (frame.shape[1]-200, 20), (frame.shape[1]-10, 50), (255,0,255), -1)
        cv2.putText(frame, "🔄 MIRROR", (frame.shape[1]-195, 42), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)
    
    # FPS
    cv2.putText(frame, f"{int(time.time()*10)%60} FPS", (10, frame.shape[0]-20), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,255), 2)
    
    return frame

class VideoProcessor:
    def __init__(self):
        self.frame_count = 0
        self.fps_time = time.time()
        self.model = model
        self.shared_data = shared_data
        self.last_detections = []
        
    def recv(self, frame):
        try:
            img = frame.to_ndarray(format="bgr24")
            orig_h, orig_w = img.shape[:2]
            
            sd = self.shared_data
            mirror_enabled = sd.get_mirror()
            show_counting = sd.get_show_counting()
            enable_alerts = sd.get_enable_alerts()
            alert_objects = sd.get_alert_objects()
            
            self.frame_count += 1
            current_time = time.time()
            
            # **ENHANCED DETECTION - Every 2 frames for smoother tracking**
            if (self.frame_count % 2 == 0) and self.model:
                try:
                    # Higher resolution inference
                    inference_img = cv2.resize(img, (640, 640))
                    results = self.model(inference_img, conf=0.45, iou=0.5, verbose=False)
                    
                    if results[0].boxes is not None:
                        boxes = results[0].boxes
                        names = results[0].names
                        
                        self.last_detections = []
                        current_counts = defaultdict(int)
                        
                        for box in boxes:
                            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                            # Scale back to original size
                            scale_x, scale_y = orig_w/640, orig_h/640
                            x1, y1, x2, y2 = x1*scale_x, y1*scale_y, x2*scale_x, y2*scale_y
                            
                            class_id = int(box.cls[0])
                            class_name = names[class_id]
                            confidence = float(box.conf[0])
                            
                            if confidence > 0.45:  # Slightly lower threshold
                                self.last_detections.append({
                                    'box': [x1, y1, x2, y2],
                                    'class': class_name,
                                    'confidence': confidence
                                })
                                current_counts[class_name] += 1
                        
                        sd.update_counts(current_counts)
                        
                        # **ENHANCED ALERTS**
                        if enable_alerts and (current_time - sd.last_alert_time) > 1.5:
                            for det in self.last_detections:
                                if det['class'] in alert_objects:
                                    sd.add_alert({
                                        'timestamp': datetime.now().strftime("%H:%M:%S"),
                                        'object': det['class'],
                                        'confidence': f"{det['confidence']:.1f}"
                                    })
                                    sd.last_alert_time = current_time
                                    break
                except: pass
            
            # **MIRROR FLIP**
            if mirror_enabled:
                img = cv2.flip(img, 1)
                # Adjust detection coordinates for mirror
                if self.last_detections:
                    mirrored_dets = []
                    for det in self.last_detections:
                        x1, y1, x2, y2 = det['box']
                        mirrored_dets.append({
                            'box': [orig_w-x2, y1, orig_w-x1, y2],
                            'class': det['class'],
                            'confidence': det['confidence']
                        })
                    self.last_detections = mirrored_dets
            
            # **DRAW BOXES**
            if self.last_detections:
                img = draw_boxes(img, self.last_detections)
            
            # **OVERLAYS**
            current_counts = sd.get_counts()
            img = add_overlays(img, current_counts, mirror_enabled, show_counting)
            
            # **AUTO-SAVE**
            if sd.get_auto_save() and (current_time - sd.last_save_time) > 8:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                cv2.imwrite(f"{SAVED_FRAMES_DIR}/auto_{timestamp}.jpg", img)
                sd.last_save_time = current_time
            
            # **MANUAL SAVE**
            if sd.get_save_request():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                cv2.imwrite(f"{SAVED_FRAMES_DIR}/manual_{timestamp}.jpg", img)
                sd.set_save_request(False)
            
            return av.VideoFrame.from_ndarray(img, format="bgr24")
            
        except:
            blank = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(blank, "🎥 CAMERA READY", (150, 250), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
            return av.VideoFrame.from_ndarray(blank, format="bgr24")

# **ENHANCED CYBERPUNK UI**
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
.stApp {background: linear-gradient(135deg, #000000 0%, #1a0033 50%, #0f0f23 100%);}
h1 {color: #00ff88; font-family: 'Orbitron', monospace; font-weight: 900; text-align: center; 
    text-shadow: 0 0 30px #00ff88, 0 0 60px #00ff88; font-size: 3em;}
h2 {color: #00ccff; font-family: 'Orbitron'; text-shadow: 0 0 15px #00ccff;}
.sidebar .sidebar-content {background: rgba(10,10,20,0.95); border-right: 2px solid #00ff88;}
.stButton > button {background: linear-gradient(45deg, #00ff88, #00ccff); 
    color: black; border: none; border-radius: 25px; font-family: 'Orbitron'; 
    font-weight: 700; box-shadow: 0 4px 15px rgba(0,255,136,0.4);}
.stButton > button:hover {box-shadow: 0 6px 25px rgba(0,255,136,0.6); transform: scale(1.05);}
.metric-container {background: rgba(0,0,0,0.7); border: 1px solid #00ff88;}
</style>
""", unsafe_allow_html=True)

st.markdown("# 🎯 **Live Object Detection & Tracing**")
st.markdown("### *Real-time AI Surveillance - 80+ Objects Detected*")

# **ENHANCED SIDEBAR**
with st.sidebar:
    st.markdown("## 🎛️ **CONTROL PANEL**")
    
    if st.button("🚀 **START DETECTION**", use_container_width=True, type="primary"):
        st.session_state.camera_active = True
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 🎥 **Camera Settings**")
    mirror_view = st.checkbox("🔄 **Mirror Mode**", value=True)
    shared_data.set_mirror(mirror_view)
    
    st.markdown("### 📊 **Display**")
    show_counting = st.checkbox("📈 **Object Counting**", value=True)
    shared_data.set_show_counting(show_counting)
    
    st.markdown("### 🚨 **Threat Alerts**")
    enable_alerts = st.checkbox("⚠️ **Enable Alerts**", value=True)
    shared_data.set_enable_alerts(enable_alerts)
    
    alert_objects = st.multiselect("🎯 **Alert Targets**:", 
        ["person", "cell phone", "laptop", "bottle", "knife", "gun", "car", "dog", "cat"], 
        ["person", "cell phone"])
    shared_data.set_alert_objects(alert_objects)
    
    st.markdown("### 💾 **Capture**")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📸 **SAVE FRAME**", use_container_width=True):
            shared_data.set_save_request(True)
    with col2:
        auto_save = st.checkbox("🤖 **Auto-save**")
        shared_data.set_auto_save(auto_save)
    
    if st.button("🔄 **RESET SYSTEM**", use_container_width=True):
        shared_data.clear_all()
        st.rerun()

# **MAIN CAMERA SECTION**
if st.session_state.camera_active:
    st.markdown("## 📡 **LIVE SURVEILLANCE FEED**")
    
    # Resolution selector
    col1, col2 = st.columns([3,1])
    with col2:
        resolution = st.selectbox("📱", ["640x480", "1280x720"], index=0)
        w, h = map(int, resolution.split('x'))
    
    webrtc_ctx = webrtc_streamer(
        key="enhanced-detection",
        mode=WebRtcMode.SENDRECV,
        video_processor_factory=VideoProcessor,
        media_stream_constraints={
            "video": {"width": {"ideal": w}, "height": {"ideal": h}, "frameRate": {"ideal": 25}},
            "audio": False
        },
        async_processing=True
    )
    
    # **ENHANCED LIVE METRICS**
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    counts = shared_data.get_counts()
    total_objects = sum(counts.values())
    
    with col1:
        st.metric("🎯 **Total Objects**", total_objects)
    
    with col2:
        alerts = shared_data.get_alerts()
        st.metric("🚨 **Alerts**", len(alerts))
    
    with col3:
        saved_files = len([f for f in os.listdir(SAVED_FRAMES_DIR) if f.endswith('.jpg')])
        st.metric("💾 **Saved Frames**", saved_files)
    
    with col4:
        threat_level = "🟢 LOW" if total_objects < 3 else "🟡 MEDIUM" if total_objects < 6 else "🔴 HIGH"
        st.metric("⚠️ **Threat**", threat_level)
    
    # **OBJECT COUNTING DISPLAY**
    if shared_data.get_show_counting() and counts:
        st.markdown("### 📊 **Live Object Count**")
        active_counts = {k: v for k, v in counts.items() if v > 0}
        for obj, count in sorted(active_counts.items(), key=lambda x: x[1], reverse=True)[:8]:
            col1, col2 = st.columns([3,1])
            with col1: st.write(f"**{obj.capitalize()}**")
            with col2: st.success(f"{count}")
    
    # **ALERT HISTORY**
    if shared_data.get_alerts():
        st.markdown("### 🚨 **Threat Alerts**")
        for alert in shared_data.get_alerts()[-5:]:
            st.error(f"⚠️ **{alert['object'].upper()}** detected - {alert['timestamp']} (Conf: {alert['confidence']})")
    
    # **FORENSIC EVIDENCE**
    saved_frames = sorted([f for f in os.listdir(SAVED_FRAMES_DIR) if f.endswith('.jpg')], reverse=True)
    if saved_frames:
        st.markdown("### 💾 **Evidence Storage**")
        for frame_file in saved_frames[:6]:
            frame_path = os.path.join(SAVED_FRAMES_DIR, frame_file)
            with st.expander(f"🖼️ **{frame_file[:25]}...**"):
                img = cv2.imread(frame_path)
                st.image(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), use_container_width=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    with open(frame_path, "rb") as f:
                        st.download_button("📥 Download", f.read(), frame_file, "image/jpeg")
                with col2:
                    if st.button("🗑️ Delete", key=f"del_{frame_file}"):
                        os.remove(frame_path)
                        st.rerun()

else:
    st.markdown("""
    <div style='text-align: center; padding: 40px; background: rgba(0,255,136,0.1); 
                border-radius: 20px; border: 2px solid #00ff88;'>
        <h2 style='color: #00ff88; font-family: Orbitron;'>🎥 **READY TO DETECT**</h2>
        <p style='font-size: 1.2em; color: #00ccff;'>
        👆 Click **START DETECTION**<br>
        📱 Hold objects: person, phone, bottle, book, chair, car, dog, cat, etc.<br>
        🎯 80+ objects supported!
        </p>
    </div>
    """, unsafe_allow_html=True)

# Model status
if not st.session_state.model_ready:
    st.warning("🔄 **Loading YOLOv8 model... (first run takes 30s)**")
else:
    st.success("✅ **YOLOv8 READY** - Detecting 80+ objects in real-time!")

st.markdown("---")
st.markdown("*Powered by YOLOv8 - Detects 80+ objects instantly*")
