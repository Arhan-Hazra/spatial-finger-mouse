# 🖱️ Spatial Vision Mouse (with Dual-Hand Clutch & Kernel Injection)

A highly optimized, scale-invariant spatial computing mouse interface engineered for standard 2D webcams. Built using **Python**, **OpenCV**, and **MediaPipe**, this project bypasses the traditional limitations of 2D gesture tracking to deliver a precise, low-latency, drawing-capable desktop control engine.

---

# 🚀 Key Engineering Showcases

Unlike standard tutorial clones that rely on absolute pixel distances and laggy user-space mouse frameworks, this architecture solves the core physics and software limitations of 2D vision inputs.

### 🖥️ Kernel-Level Input Injection (`ctypes`)
Bypasses standard Windows user-space event throttling (`PyAutoGUI`). By injecting raw coordinate telemetry directly into `user32.dll`, the system achieves flawless line continuity during active click-and-drag operations (digital painting, window dragging, CAD work, etc.).

### 📏 Mathematical Scale & Depth Invariance
Eliminates distance dependency. The framework dynamically samples the Euclidean distance of the wrist-to-middle-knuckle vector (`hand_size`). All gesture measurements are normalized against this baseline, producing identical click thresholds regardless of whether the user's hand is 2 feet or 6 feet away from the camera.

### ✋🤚 Dual-Hand Workspace Clutching
Solves the physical webcam Field-of-View limitation. When the tracking hand reaches the camera boundary, forming a fist with the secondary hand engages a virtual clutch that freezes cursor movement, allowing the tracking hand to reposition naturally before resuming control.

### ⚡ Synchronous Multi-Modal Optimization
Runs Hand Landmark detection and Face Blendshape (Eye Blink) recognition inside a unified synchronous processing pipeline. By utilizing MediaPipe Face Landmarker in static `IMAGE` mode for inline inference, the system avoids the thread contention, synchronization issues, and latency spikes common in multi-threaded computer vision applications.

---

# 🛠️ System Architecture

## Core Gesture & Optimization Matrix

| Feature | Engineering Challenge | Architectural Solution |
|----------|-----------------------|------------------------|
| **Drawing/Painting Support** | PyAutoGUI drops packets during continuous click-and-drag. | **Direct Windows Input Injection** using `ctypes.windll.user32.SetCursorPos`. |
| **Depth Fluctuation** | Gesture thresholds change as hand distance varies. | **Dynamic Vector Normalization** against the hand reference vector. |
| **Workspace Clamping** | Limited webcam field of view restricts cursor travel. | **Secondary-Hand Clutch Mechanism** allowing seamless hand repositioning. |
| **Cursor Tremor / Jitter** | Camera noise causes unstable cursor movement. | **Inline Smoothing Engine** with calibrated deadzone filtering. |
| **Multi-Task Latency** | Running hand + face tracking simultaneously increases processing overhead. | **Synchronous Inline Stream Parsing** utilizing static image mode context switching. |

---

# 🎹 Global Shortcuts

| Shortcut | Action |
|----------|--------|
| **Ctrl + Alt + D** | Toggle the real-time debug camera overlay. The UI is completely unloaded when hidden to reduce CPU utilization. |
| **Ctrl + Alt + H** | Instantly swap dominant tracking hand (Left / Right-handed mode). |
| **Left + Right Eye Blink** | Trigger desktop navigation commands. |

---

# 📦 Installation

## 1. Prerequisites

- Windows operating system
- Python 3.10+
- Webcam

> **Note:** Windows is currently required because cursor injection is performed through the Windows `user32.dll` API using `ctypes`.

---

## 2. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME
```

---

## 3. Install Dependencies

```bash
pip install opencv-python mediapipe pyautogui keyboard
```

---

## 4. Run the Application

```bash
python main.py
```

---

## 🤖 Automatic Model Download

On the first launch, the application automatically downloads the required MediaPipe models into the project directory:

- `hand_landmarker.task`
- `face_landmarker.task`

These models are retrieved directly from Google's official MediaPipe model repository.

---

# 🧠 Technologies Used

- Python
- OpenCV
- Google MediaPipe Tasks API
- ctypes (Windows API)
- PyAutoGUI
- Keyboard
- NumPy

---

# 📌 Highlights

- ✅ Scale-invariant gesture recognition
- ✅ Kernel-level mouse injection
- ✅ Continuous drawing support
- ✅ Dual-hand clutch mechanism
- ✅ Dynamic gesture normalization
- ✅ Eye blink desktop shortcuts
- ✅ Left & right hand support
- ✅ Low-latency cursor smoothing
- ✅ Automatic MediaPipe model download

---

# 👨‍💻 Developed By

**Arhan Hazra**

Built with 💻, ☕, and an unhealthy amount of OpenCV debugging.
