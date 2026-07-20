# 🖱️ Spatial Vision Mouse (with Dual-Hand Clutch & Kernel Injection)

A highly optimized, scale-invariant spatial computing mouse interface engineered for standard 2D webcams. Built using Python, OpenCV, and MediaPipe, this project bypasses the traditional limitations of 2D gesture tracking to deliver a precise, low-latency, drawing-capable desktop control engine.

---

## 🚀 Key Engineering Showcases

Unlike standard tutorial clones that rely on absolute pixel distances and laggy user-space mouse frameworks, this architecture solves the core physics and software limitations of 2D vision inputs:

*   **Kernel-Level Input Injection (`ctypes`):** Bypasses standard Windows user-space event throttling (`PyAutoGUI`). By injecting raw coordinate telemetry directly into `user32.dll`, the system achieves flawless line continuity during active click-and-drag operations (e.g., digital painting, window dragging).
*   **Mathematical Scale & Depth Invariance:** Eliminates distance dependency. The framework dynamically samples the Euclidean distance of the wrist-to-middle-knuckle vector ($\text{hand\_size}$). All pinch metrics are divided by this baseline, making click thresholds perfectly uniform whether your hand is 2 feet or 6 feet away from the lens.
*   **Dual-Hand Workspace Clutching:** Solves the physical Field of View (FoV) boundary problem. When the tracking hand reaches the edge of the camera frame, forming a fist with the secondary hand engages a **system clutch**, freezing the mouse state and allowing the user to reposition their tracking hand seamlessly.
*   **Synchronous Multi-Modal Optimization:** Integrates Hand Landmarking and Face Blendshapes (Eye Tracking) into a unified synchronous pipeline by running the Face Engine in a static `IMAGE` inline configuration, avoiding the thread deadlocks and frame drops typical of multi-threaded vision systems.

---

## 🛠️ System Architecture & Mechanics

### Core Gesture & Optimization Matrix

| Feature | The Engineering Hurdle | The Architectural Solution |
| :--- | :--- | :--- |
| **Drawing/Painting Support** | `PyAutoGUI` packet dropping during continuous hold clicks. | **Direct OS Kernel Injection** via `ctypes.windll.user32.SetCursorPos`. |
| **Depth Fluctuation** | Misfiring click states due to hand distance shifting. | **Vector Normalization** scaling distances dynamically against the hand bounding box. |
| **Workspace Clamping** | Running out of physical space inside the webcam box. | **Secondary Hand Mechanical Clutch** to decouple spatial mapping temporarily. |
| **Cursor Tremor / Jitter** | Raw sub-pixel camera noise causing jagged movement. | **Inline Smoothing Engine** paired with a calibrated dynamic deadzone. |
| **Multi-Task Latency** | High overhead from running both hand and face tracking. | **Synchronous Inline Stream Parsing** utilizing static image mode context switches. |

---

## 🎹 Global Control Triggers & Shortcuts

*   `Ctrl + Alt + D` : Toggle Real-Time Debug Camera Overlay (Automatically unloads from UI memory when hidden to save system CPU resources).
*   `Ctrl + Alt + H` : Instantly swap active tracking hand bias (Left-handed / Right-handed support).
*   `Left & Right Eye Blink Combo` : System desktop environment navigation commands.

---

## 📦 Installation & Setup

1. **Clone the Repository:**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git)
   cd YOUR_REPO_NAME
