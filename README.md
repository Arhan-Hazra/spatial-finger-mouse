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
git clone https://github.com/Arhan-Hazra/spatial-finger-mouse.git
cd spatial-finger-mouse
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

- ✅ Scale-invariant gesture recognition (makes the mouse more adaptable to each people)
- ✅ Kernel-level mouse injection
- ✅ Continuous drawing support
- ✅ Dual-hand clutch mechanism
- ✅ Dynamic gesture normalization
- ✅ Eye blink desktop switch (double blink to go to right desktop, triple blink to go to left desktop)
- ✅ Left & right hand support
- ✅ Low-latency cursor smoothing
- ✅ Automatic MediaPipe model download

---

---

# 📈 Version History & Evolution

## v1.0 — The Beginning
- Basic webcam mouse pointer following using hand tracking.

---

## v2.x — The Tracking & Stabilization Era

### v2.1
- Established the core tracking baseline using the Google MediaPipe Tasks API.
- Implemented an Exponential Moving Average (EMA) smoothing filter.
- Added a strict 10-frame click freeze lock (`click_lock`) for stable clicking.

### v2.2
- Introduced an active viewport margin (`margin = 100`) with `np.interp()` mapping.
- Built a custom hardcoded hand wireframe mesh (`HAND_CONNECTIONS`).
- Added the global debug hotkey:

```
Ctrl + Alt + D
```

### v2.3
- Upgraded the pipeline to support simultaneous dual-hand tracking.
- Reduced confidence thresholds to 50% to improve folded-finger detection.
- Added runtime dominant-hand swapping:

```
Ctrl + Alt + H
```

- Replaced the heavy wireframe overlay with a lightweight **"Just Dots"** diagnostic mode.

### v2.4
- Replaced discrete clicks with persistent `mouseDown()` / `mouseUp()` logic.
- Added native drag-and-drop support.
- Removed movement freeze during click-hold.

### v2.5
- Designed a complete hysteresis & debounce framework.
- Added independent engage/release thresholds:

```
click_in  = 25
click_out = 45
```

- Introduced a 3-frame release memory buffer.
- Added a 2-pixel movement deadzone to eliminate micro-jitter.

---

## v3.x — The Touchpad & Geometric Scaling Engine

### v3.1
- Rebuilt the cursor engine into a relative touchpad architecture (`dx`, `dy`).
- Added dynamic acceleration based on hand velocity.

### v3.2 – v3.3
- Developed the Dual-Hand Mechanical Clutch.
- Added secondary-hand fist detection (`is_fist()`).
- Allowed users to temporarily disengage cursor mapping and reset workspace position naturally.

### v3.4
- Introduced Mathematical Scale & Depth Invariance.
- Normalized every gesture against the dynamic hand reference vector (`hand_size`).
- Eliminated dependency on camera distance.

### v3.5
- Changed cursor anchor from the index fingertip to the middle-finger MCP joint.
- Eliminated cursor drift during pinch gestures.
- Tightened release ratio tolerance to improve hold reliability.

### v3.6
- Added threaded audio feedback using `winsound`.
- Implemented confirmation/error tones.
- Wrapped the application in graceful `KeyboardInterrupt` cleanup with a proper `finally` block.

---

## v4.x — Multi-Modal Synchronization & OS Integration *(Current)*

### v4.1 – v4.2
- Replaced terminal configuration with a complete **Tkinter Setup Wizard**.
- Built an interactive calibration overlay.
- Added a rolling 1-second sampling queue to automatically determine personalized gesture thresholds.

### v4.3
- Designed an experimental 3-finger / 4-finger gesture engine.
- Added native Windows Virtual Desktop navigation.

```
Ctrl + Win + Left
Ctrl + Win + Right
```

### v4.4
- Replaced finger swipes with MediaPipe Face Blendshape tracking.
- Developed synchronized double-blink and triple-blink gesture recognition.
- Added a hidden developer unlock sequence:

```
Ctrl + Alt + Shift + = + Home
```

### v4.5 – v4.6
- Eliminated frame drops by converting the Face Engine into a synchronous inline `IMAGE` pipeline.
- Refactored clutch mechanics so active drag operations continue seamlessly while clutching.

### v4.7 
- Solved PyAutoGUI line stuttering during continuous drawing.
- Integrated direct Windows cursor injection using:

```python
ctypes.windll.user32.SetCursorPos()
```

- Cursor movement automatically switches to kernel-level injection whenever a gesture click is active, enabling smooth digital drawing and CAD workflows without discontinuities.

### v4.8
Unified every subsystem into the final production architecture. Integrated direct Windows kernel-level cursor injection (`user32.SetCursorPos`) for uninterrupted drawing, completed the Tkinter calibration wizard, finalized scale-invariant gesture recognition, dual-hand clutch mechanics, Face Blendshape eye tracking, blink-based desktop navigation, touchpad acceleration, low-latency smoothing, audio feedback, automatic MediaPipe model downloading, runtime hand swapping, and graceful resource cleanup.

### v4.9 (Current Stable Main)
Completed the project's final input engine overhaul, introducing reliable continuous drawing support across graphics applications. Improved overall cursor responsiveness, click-and-drag stability, and application compatibility while maintaining the existing low-latency gesture pipeline. With drawing, desktop navigation, calibration, dual-hand clutching, and eye tracking now working together, the system reaches its first fully feature-complete milestone.

---

### 🔮 Planned for v5.x

- Configurable gesture profiles
- Multi-monitor awareness
- Custom macro gesture recording
- Scroll & zoom gesture engine
- Plugin architecture
- Linux support through native X11/Wayland injection
- GPU-accelerated processing pipeline
- Collaborations are welcome!!

# 👨‍💻 Developed & Maintained By

**Arhan Hazra**

Built with 💻, ☕, and an unhealthy amount of OpenCV debugging.
