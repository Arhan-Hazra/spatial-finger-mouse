import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import pyautogui
import math
import urllib.request
import os
import keyboard
import winsound
import threading
import time
import tkinter as tk
from tkinter import messagebox
import webbrowser

# [ HEADING: GLOBAL IDENTIFIER ]
_dev_signature_alpha = "MOUSE POINTER ~ MADE BY ARHAN"

def play_sound(event_type):
    def beep():
        if event_type == "clutch":
            winsound.Beep(900, 100)  
            winsound.Beep(1200, 100) 
        elif event_type == "lost":
            winsound.Beep(800, 120)  
            winsound.Beep(500, 150)
    threading.Thread(target=beep, daemon=True).start()

def run_cv2_configurator(mode, detector, cap, cam_width, cam_height):
    cv2.namedWindow("Configurator")
    next_clicked = False
    
    def mouse_cb(event, x, y, flags, param):
        nonlocal next_clicked
        if event == cv2.EVENT_LBUTTONDOWN:
            if cam_width - 150 < x < cam_width - 30 and cam_height - 80 < y < cam_height - 30:
                next_clicked = True
    cv2.setMouseCallback("Configurator", mouse_cb)

    history = []
    _loop_auth = "MOUSE POINTER ~ MADE BY ARHAN"

    while not next_clicked:
        success, img = cap.read()
        if not success: break
        
        img = cv2.flip(img, 1)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
        detection_result = detector.detect(mp_image)
        
        if detection_result.hand_landmarks:
            landmarks = detection_result.hand_landmarks[0]
            def get_px(landmark): return int(landmark.x * cam_width), int(landmark.y * cam_height)
            
            wrist = get_px(landmarks[0])
            mid_knuckle = get_px(landmarks[9])
            thumb_tip = get_px(landmarks[4])
            index_tip = get_px(landmarks[8])
            mid_tip = get_px(landmarks[12])
            
            hand_size = math.hypot(mid_knuckle[0] - wrist[0], mid_knuckle[1] - wrist[1])
            if hand_size == 0: hand_size = 1
            
            if mode == 'index':
                dist = math.hypot(index_tip[0] - thumb_tip[0], index_tip[1] - thumb_tip[1])
                pt1, pt2 = thumb_tip, index_tip
                lbl = "Index-Thumb Ratio"
            else:
                dist = math.hypot(mid_tip[0] - thumb_tip[0], mid_tip[1] - thumb_tip[1])
                pt1, pt2 = thumb_tip, mid_tip
                lbl = "Mid-Thumb Ratio"
                
            ratio = dist / hand_size
            
            curr_time = time.time()
            history = [(t, r) for t, r in history if curr_time - t <= 1.0]
            history.append((curr_time, ratio))
            
            max_val = max([r for t, r in history])
            min_val = min([r for t, r in history])
            
            cv2.circle(img, pt1, 10, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, pt2, 10, (255, 0, 255), cv2.FILLED)
            cv2.line(img, pt1, pt2, (0, 255, 255), 3)
            cv2.line(img, wrist, mid_knuckle, (255, 255, 0), 2)
            
            cv2.putText(img, f"{lbl}: {ratio:.2f}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 3)
            cv2.putText(img, f"1s MAX: {max_val:.2f}", (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.putText(img, f"1s MIN: {min_val:.2f}", (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

        status_text = f"Measuring: {'Index' if mode == 'index' else 'Middle'} & Thumb"
        cv2.putText(img, status_text, (20, cam_height - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

        cv2.rectangle(img, (cam_width - 150, cam_height - 80), (cam_width - 30, cam_height - 30), (0, 200, 0), cv2.FILLED)
        cv2.putText(img, "NEXT >", (cam_width - 140, cam_height - 45), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        cv2.imshow("Configurator", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    cv2.destroyWindow("Configurator")


class SetupWizard:
    def __init__(self, detector, cap, cam_width, cam_height):
        self.root = tk.Tk()
        self._win_title = "MOUSE POINTER ~ MADE BY ARHAN"
        self.root.title(self._win_title)
        
        # UI FIX: No geometry set means the window auto-resizes to fit text perfectly
        self.root.geometry("")
        
        self.detector = detector
        self.cap = cap
        self.cam_width = cam_width
        self.cam_height = cam_height
        self.left_ratio_final = 0.20
        self.right_ratio_final = 0.20
        
        self.page_intro()
        self.root.mainloop()

    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def page_intro(self):
        self.clear()
        # Added extra padding to give the auto-sized window some breathing room
        frame = tk.Frame(self.root, padx=40, pady=40)
        frame.pack()
        tk.Label(frame, text="Welcome to the Virtual Mouse Calibration!", font=("Helvetica", 18, "bold")).pack(pady=10)
        tk.Label(frame, text="A quirky, scale-invariant, dual-hand clutch masterpiece.", font=("Helvetica", 13)).pack(pady=5)
        tk.Label(frame, text="Let's get your hands calibrated for absolute precision.", font=("Helvetica", 13)).pack(pady=5)
        tk.Button(frame, text="Next >", command=self.page_instructions, font=("Helvetica", 13), bg="lightblue", width=15).pack(pady=20)

    def page_instructions(self):
        self.clear()
        frame = tk.Frame(self.root, padx=40, pady=40)
        frame.pack()
        tk.Label(frame, text="Why do we need to configure?", font=("Helvetica", 18, "bold")).pack(pady=10)
        
        instructions = (
            "1. Everyone's hands are different sizes.\n"
            "2. Webcam focal lengths and distortions vary.\n"
            "3. Scale-Invariance requires personalized tip-to-hand ratios.\n\n"
            "WHAT TO DO:\n"
            "On the next screens, pinch your fingers normally and comfortably.\n"
            "Pay close attention to your '1s MAX' and '1s MIN' values.\n"
            "Remember a comfortable middle ratio for both gestures!"
        )
        tk.Label(frame, text=instructions, font=("Helvetica", 12), justify="left").pack(pady=10)
        tk.Button(frame, text="Next >", command=self.page_config_index, font=("Helvetica", 13), bg="lightblue", width=15).pack(pady=20)

    def page_config_index(self):
        self.root.withdraw()
        run_cv2_configurator("index", self.detector, self.cap, self.cam_width, self.cam_height)
        self.root.deiconify()
        self.page_config_middle()

    def page_config_middle(self):
        self.root.withdraw()
        run_cv2_configurator("middle", self.detector, self.cap, self.cam_width, self.cam_height)
        self.root.deiconify()
        self.page_input()

    def page_input(self):
        self.clear()
        frame = tk.Frame(self.root, padx=40, pady=40)
        frame.pack()
        tk.Label(frame, text="Confirm Your Values", font=("Helvetica", 18, "bold")).pack(pady=10)
        
        self.left_var = tk.StringVar(value="0.20")
        self.right_var = tk.StringVar(value="0.20")
        self.sync_var = tk.BooleanVar(value=False)
        
        input_grid = tk.Frame(frame)
        input_grid.pack(pady=10)
        
        tk.Label(input_grid, text="Left Click (Index) Ratio:", font=("Helvetica", 13)).grid(row=0, column=0, pady=10, padx=10, sticky="e")
        left_entry = tk.Entry(input_grid, textvariable=self.left_var, font=("Helvetica", 13), width=10)
        left_entry.grid(row=0, column=1, pady=10)
        
        tk.Label(input_grid, text="Right Click (Middle) Ratio:", font=("Helvetica", 13)).grid(row=1, column=0, pady=10, padx=10, sticky="e")
        self.right_entry = tk.Entry(input_grid, textvariable=self.right_var, font=("Helvetica", 13), width=10)
        self.right_entry.grid(row=1, column=1, pady=10)
        
        # UI FIX: Custom scaled text-toggle instead of OS Checkbutton
        self.check_lbl = tk.Label(frame, text="[ ] ARE BOTH SAME VALUE?", font=("Helvetica", 14, "bold"), fg="#0055ff", cursor="hand2")
        self.check_lbl.pack(pady=15)
        
        def toggle_sync(event=None):
            current = not self.sync_var.get()
            self.sync_var.set(current)
            self.check_lbl.config(text="[X] ARE BOTH SAME VALUE?") if current else self.check_lbl.config(text="[ ] ARE BOTH SAME VALUE?")
            if current:
                self.right_var.set(self.left_var.get())
                self.right_entry.config(state='disabled')
            else:
                self.right_entry.config(state='normal')
                
        self.check_lbl.bind("<Button-1>", toggle_sync)
        self.left_var.trace_add("write", lambda *args: toggle_sync() if self.sync_var.get() and not self.sync_var.get() else (self.right_var.set(self.left_var.get()) if self.sync_var.get() else None))
        
        tk.Button(frame, text="Next >", command=self.page_ready, font=("Helvetica", 13), bg="lightblue", width=15).pack(pady=20)

    def page_ready(self):
        self.clear()
        try:
            self.left_ratio_final = float(self.left_var.get())
            self.right_ratio_final = float(self.right_var.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers!")
            self.page_input()
            return
            
        frame = tk.Frame(self.root, padx=40, pady=20)
        frame.pack()
        tk.Label(frame, text="ARE YOU READY FOR THE PROTOTYPE?", font=("Helvetica", 16, "bold")).pack(pady=10)
        
        feat_frame = tk.Frame(frame)
        feat_frame.pack(pady=5)
        tk.Label(feat_frame, text="Active Features:", font=("Helvetica", 14, "bold", "underline")).pack(anchor="w", pady=5)
        features = [
            "• Scale-Invariant 3D Tracking",
            "• Left & Right Click (Full Hold & Drag Support)",
            "• Dual-Hand Clutch Mechanism (Fist to freeze pointer)",
            "• Anti-Jitter Touchpad Acceleration Engine",
            "• Advanced Gestures (3 & 4 Finger Windows Navigation)",
            "• Auto-Hidden Camera (Saves CPU resources)",
            "• Shortcut: Ctrl+Alt+D (Toggle Camera) | Ctrl+Alt+H (Swap Hand)"
        ]
        for f in features:
            tk.Label(feat_frame, text=f, font=("Helvetica", 12)).pack(anchor="w")

        caution = "CAUTION - THIS IS A 2D CAMERA BASED FINGER-MOUSE ADAPTATION\nSO THIS MAY NOT BE AS ACCURATE AS OTHER 3D VISION COUNTERPARTS"
        tk.Label(frame, text=caution, font=("Helvetica", 10, "bold"), fg="#d9534f", justify="center").pack(pady=15)
        
        tk.Button(frame, text="Continue", command=self.root.destroy, font=("Helvetica", 14, "bold"), bg="lightgreen", width=25).pack(pady=10)
        
        def open_mail(e): webbrowser.open("mailto:rahanrazah@gmail.com")
        contact_lbl = tk.Label(frame, text="Contact?", font=("Helvetica", 11, "underline"), fg="blue", cursor="hand2")
        contact_lbl.pack(pady=5)
        contact_lbl.bind("<Button-1>", open_mail)

_core_logic_tag = "MOUSE POINTER ~ MADE BY ARHAN"

def is_fist(landmarks):
    folded_fingers = 0
    tips, knuckles = [8, 12, 16, 20], [5, 9, 13, 17]
    for tip, knuckle in zip(tips, knuckles):
        dist_tip = math.hypot(landmarks[tip].x - landmarks[0].x, landmarks[tip].y - landmarks[0].y)
        dist_knuckle = math.hypot(landmarks[knuckle].x - landmarks[0].x, landmarks[knuckle].y - landmarks[0].y)
        if dist_tip < dist_knuckle: folded_fingers += 1
    return folded_fingers >= 3

if __name__ == "__main__":
    _startup_sig = "MOUSE POINTER ~ MADE BY ARHAN"
    
    pyautogui.PAUSE = 0
    pyautogui.FAILSAFE = False 
    screen_width, screen_height = pyautogui.size()
    cam_width, cam_height = 640, 480

    model_path = 'hand_landmarker.task'
    if not os.path.exists(model_path):
        print("Downloading MediaPipe model...")
        urllib.request.urlretrieve("https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task", model_path)

    base_options = python.BaseOptions(model_asset_path=model_path)
    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        num_hands=2, 
        min_hand_detection_confidence=0.5,
        min_hand_presence_confidence=0.5,
        min_tracking_confidence=0.5
    )
    detector = vision.HandLandmarker.create_from_options(options)
    
    cap = cv2.VideoCapture(0)
    cap.set(3, cam_width)
    cap.set(4, cam_height)

    wizard = SetupWizard(detector, cap, cam_width, cam_height)
    
    left_ratio_in = wizard.left_ratio_final
    right_ratio_in = wizard.right_ratio_final
    left_ratio_out = left_ratio_in + 0.04
    right_ratio_out = right_ratio_in + 0.04

    current_mouse_pos = pyautogui.position()
    virtual_x, virtual_y = current_mouse_pos.x, current_mouse_pos.y

    prev_x, prev_y = None, None
    smoothing_factor = 4 
    deadzone = 4 
    base_sensitivity = 3.5 

    left_held, right_held = False, False
    left_buffer, right_buffer = 0, 0
    buffer_max = 3 

    # GESTURE ENGINE VARIABLES
    swipe_cooldown = 0
    gesture_start_x, gesture_start_y = None, None

    show_debug = False 
    last_d_state, last_h_state = False, False
    active_hand = "Right" 
    was_clutched = False
    hand_was_present = False 

    print("\nVirtual Mouse is LIVE in the background. Press Ctrl+C in terminal to exit.")

    try:
        while True:
            success, img = cap.read()
            if not success: break
                
            img = cv2.flip(img, 1) 
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
            detection_result = detector.detect(mp_image)
            
            current_d_state = keyboard.is_pressed('ctrl+alt+d')
            if current_d_state and not last_d_state:
                show_debug = not show_debug
                if not show_debug: cv2.destroyAllWindows() 
            last_d_state = current_d_state

            current_h_state = keyboard.is_pressed('ctrl+alt+h')
            if current_h_state and not last_h_state:
                active_hand = "Left" if active_hand == "Right" else "Right"
            last_h_state = current_h_state

            clutch_hand = "Left" if active_hand == "Right" else "Right"
            active_landmarks, clutch_landmarks = None, None

            if detection_result.hand_landmarks:
                for idx in range(len(detection_result.hand_landmarks)):
                    model_label = detection_result.handedness[idx][0].category_name
                    physical_hand = "Right" if model_label == "Left" else "Left"
                    if physical_hand == active_hand: active_landmarks = detection_result.hand_landmarks[idx]
                    elif physical_hand == clutch_hand: clutch_landmarks = detection_result.hand_landmarks[idx]

            clutch_engaged = False
            if clutch_landmarks:
                if is_fist(clutch_landmarks): clutch_engaged = True
                if show_debug:
                    def get_px(landmark): return int(landmark.x * cam_width), int(landmark.y * cam_height)
                    cv2.circle(img, get_px(clutch_landmarks[0]), 15, (255, 0, 255), 3)

            if clutch_engaged:
                if not was_clutched: play_sound("clutch") 
                was_clutched = True
                if show_debug: cv2.putText(img, "CLUTCH ENGAGED", (150, cam_height//2), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)
            else:
                if was_clutched:
                    prev_x, prev_y = None, None
                    was_clutched = False

            if active_landmarks:
                hand_was_present = True 
                def get_px(landmark): return int(landmark.x * cam_width), int(landmark.y * cam_height)
                    
                wrist = get_px(active_landmarks[0])
                mid_knuckle = get_px(active_landmarks[9])
                thumb_tip = get_px(active_landmarks[4])
                index_tip = get_px(active_landmarks[8])
                mid_tip = get_px(active_landmarks[12])
                mid_pip = get_px(active_landmarks[10])
                
                hand_size = math.hypot(mid_knuckle[0] - wrist[0], mid_knuckle[1] - wrist[1])
                if hand_size == 0: hand_size = 1

                # --- 3 & 4 FINGER GESTURE ENGINE ---
                fingers_up_count = 0
                tips, pips = [8, 12, 16, 20], [6, 10, 14, 18]
                for tip, pip in zip(tips, pips):
                    # In MediaPipe, smaller Y means higher on screen
                    if active_landmarks[tip].y < active_landmarks[pip].y: 
                        fingers_up_count += 1
                
                if show_debug:
                    cv2.putText(img, f"Fingers Up: {fingers_up_count}", (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 165, 0), 2)
                    cv2.circle(img, mid_knuckle, 12, (255, 165, 0), cv2.FILLED) 
                    for pt in [4, 8, 10, 12]: cv2.circle(img, get_px(active_landmarks[pt]), 8, (0, 255, 0), cv2.FILLED)
                    cv2.line(img, thumb_tip, index_tip, (0, 255, 255) if left_held else (255, 0, 0), 2)
                    cv2.line(img, thumb_tip, mid_tip, (0, 255, 255) if right_held else (255, 0, 0), 2)

                if swipe_cooldown > 0:
                    swipe_cooldown -= 1
                    gesture_start_x, gesture_start_y = None, None
                    
                elif fingers_up_count >= 3:
                    # Freeze normal mouse operations and handle the swipe
                    if gesture_start_x is None:
                        gesture_start_x, gesture_start_y = active_landmarks[0].x, active_landmarks[0].y
                    else:
                        dx = active_landmarks[0].x - gesture_start_x
                        dy = active_landmarks[0].y - gesture_start_y
                        swipe_thresh = 0.15 # 15% of the screen width/height to trigger
                        
                        if fingers_up_count == 4:
                            if dx > swipe_thresh: 
                                pyautogui.hotkey('ctrl', 'win', 'right')
                                swipe_cooldown = 40
                            elif dx < -swipe_thresh:
                                pyautogui.hotkey('ctrl', 'win', 'left')
                                swipe_cooldown = 40
                            elif dy < -swipe_thresh: # Swipe Up
                                pyautogui.hotkey('win', 'down')
                                swipe_cooldown = 40
                        elif fingers_up_count == 3:
                            if dy > swipe_thresh: # Swipe Down
                                pyautogui.hotkey('win', 'd')
                                swipe_cooldown = 40
                
                # --- STANDARD MOVEMENT & CLICKS ---
                elif not clutch_engaged:
                    gesture_start_x = None # Reset swipe anchor
                    movement_pt = mid_knuckle
                    
                    if prev_x is None:
                        prev_x, prev_y = movement_pt[0], movement_pt[1]
                        curr_x, curr_y = movement_pt[0], movement_pt[1]
                    else:
                        curr_x = prev_x + (movement_pt[0] - prev_x) / smoothing_factor
                        curr_y = prev_y + (movement_pt[1] - prev_y) / smoothing_factor
                        
                        dx, dy = curr_x - prev_x, curr_y - prev_y
                        speed = math.hypot(dx, dy)
                        
                        accel = 1.0 + (speed / 4.0) if speed > 2.0 else 1.0
                        move_x, move_y = dx * base_sensitivity * accel, dy * base_sensitivity * accel
                        
                        if abs(move_x) > deadzone or abs(move_y) > deadzone:
                            virtual_x = max(0, min(screen_width, virtual_x + move_x))
                            virtual_y = max(0, min(screen_height, virtual_y + move_y))
                            try: pyautogui.moveTo(int(virtual_x), int(virtual_y))
                            except Exception: pass
                                
                        prev_x, prev_y = curr_x, curr_y

                    dist_left_ratio = math.hypot(index_tip[0] - thumb_tip[0], index_tip[1] - thumb_tip[1]) / hand_size
                    dist_right_ratio = math.hypot(mid_tip[0] - thumb_tip[0], mid_tip[1] - thumb_tip[1]) / hand_size
                    
                    if dist_left_ratio < left_ratio_in:
                        left_buffer = 0 
                        if not left_held:
                            pyautogui.mouseDown(button='left')
                            left_held = True
                    elif dist_left_ratio > left_ratio_out:
                        if left_held:
                            left_buffer += 1 
                            if left_buffer >= buffer_max: 
                                pyautogui.mouseUp(button='left')
                                left_held = False
                                left_buffer = 0
                            
                    if mid_tip[1] < mid_pip[1] and dist_right_ratio < right_ratio_in:
                        right_buffer = 0
                        if not right_held:
                            pyautogui.mouseDown(button='right')
                            right_held = True
                    elif dist_right_ratio > right_ratio_out:
                        if right_held:
                            right_buffer += 1
                            if right_buffer >= buffer_max:
                                pyautogui.mouseUp(button='right')
                                right_held = False
                                right_buffer = 0
            else:
                prev_x = None
                gesture_start_x = None
                if hand_was_present:
                    play_sound("lost")
                    hand_was_present = False

            if show_debug:
                _debug_overlay_tag = "MOUSE POINTER ~ MADE BY ARHAN"
                cv2.putText(img, f"Active: {active_hand[0]}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
                cv2.imshow("Virtual Mouse Debug", img)
                if cv2.waitKey(1) & 0xFF == ord('q'): break
            else:
                cv2.waitKey(1)

    except KeyboardInterrupt:
        print("\n[Shutting down gracefully...]")

    finally:
        try:
            if left_held: pyautogui.mouseUp(button='left')
            if right_held: pyautogui.mouseUp(button='right')
            cap.release()
            cv2.destroyAllWindows()
        except: 
            pass
        os._exit(0)