import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import pyautogui
import math
import urllib.request
import os
import keyboard

# --- TERMINAL CONFIGURATION ---
print("--- Launching Scale-Invariant Virtual Mouse ---")
try:
    left_ratio_in = float(input("Enter Left Click Ratio (Index-Thumb) [e.g., 0.15]: "))
    right_ratio_in = float(input("Enter Right Click Ratio (Middle-Thumb) [e.g., 0.15]: "))
except ValueError:
    print("Invalid input. Defaulting to 0.15")
    left_ratio_in = 0.15
    right_ratio_in = 0.15

# Automatically calculate the release thresholds for hysteresis
left_ratio_out = left_ratio_in + 0.15
right_ratio_out = right_ratio_in + 0.15

# Pipeline Configuration
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

# --- ENGINE VARIABLES ---
current_mouse_pos = pyautogui.position()
virtual_x, virtual_y = current_mouse_pos.x, current_mouse_pos.y

prev_index_x, prev_index_y = None, None
smoothing_factor = 4 
deadzone = 4 
base_sensitivity = 3.5 

left_held, right_held = False, False
left_buffer, right_buffer = 0, 0
buffer_max = 3 

show_debug = True
last_d_state, last_h_state = False, False
active_hand = "Right" 
was_clutched = False

def is_fist(landmarks):
    folded_fingers = 0
    tips, knuckles = [8, 12, 16, 20], [5, 9, 13, 17]
    for tip, knuckle in zip(tips, knuckles):
        dist_tip = math.hypot(landmarks[tip].x - landmarks[0].x, landmarks[tip].y - landmarks[0].y)
        dist_knuckle = math.hypot(landmarks[knuckle].x - landmarks[0].x, landmarks[knuckle].y - landmarks[0].y)
        if dist_tip < dist_knuckle: folded_fingers += 1
    return folded_fingers >= 3

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

    # --- CLUTCH LOGIC ---
    clutch_engaged = False
    if clutch_landmarks:
        if is_fist(clutch_landmarks): clutch_engaged = True
        if show_debug:
            def get_px(landmark): return int(landmark.x * cam_width), int(landmark.y * cam_height)
            cv2.circle(img, get_px(clutch_landmarks[0]), 15, (255, 0, 255), 3)

    if clutch_engaged:
        was_clutched = True
        if show_debug: cv2.putText(img, "CLUTCH ENGAGED", (150, cam_height//2), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)
    else:
        if was_clutched:
            prev_index_x, prev_index_y = None, None
            was_clutched = False

    # --- ACTIVE HAND LOGIC ---
    if active_landmarks:
        def get_px(landmark): return int(landmark.x * cam_width), int(landmark.y * cam_height)
            
        wrist = get_px(active_landmarks[0])
        mid_knuckle = get_px(active_landmarks[9])
        thumb_tip = get_px(active_landmarks[4])
        index_tip = get_px(active_landmarks[8])
        mid_tip = get_px(active_landmarks[12])
        mid_pip = get_px(active_landmarks[10])
        
        # Calculate Hand Size for Ratio Mapping
        hand_size = math.hypot(mid_knuckle[0] - wrist[0], mid_knuckle[1] - wrist[1])
        if hand_size == 0: hand_size = 1
        
        if show_debug:
            for pt in [4, 8, 10, 12]: cv2.circle(img, get_px(active_landmarks[pt]), 8, (0, 255, 0), cv2.FILLED)
            cv2.line(img, thumb_tip, index_tip, (0, 255, 255) if left_held else (255, 0, 0), 2)
            cv2.line(img, thumb_tip, mid_tip, (0, 255, 255) if right_held else (255, 0, 0), 2)

        if not clutch_engaged:
            if prev_index_x is None:
                prev_index_x, prev_index_y = index_tip[0], index_tip[1]
                curr_index_x, curr_index_y = index_tip[0], index_tip[1]
            else:
                curr_index_x = prev_index_x + (index_tip[0] - prev_index_x) / smoothing_factor
                curr_index_y = prev_index_y + (index_tip[1] - prev_index_y) / smoothing_factor
                
                dx, dy = curr_index_x - prev_index_x, curr_index_y - prev_index_y
                speed = math.hypot(dx, dy)
                
                accel = 1.0 + (speed / 4.0) if speed > 2.0 else 1.0
                move_x, move_y = dx * base_sensitivity * accel, dy * base_sensitivity * accel
                
                if abs(move_x) > deadzone or abs(move_y) > deadzone:
                    virtual_x = max(0, min(screen_width, virtual_x + move_x))
                    virtual_y = max(0, min(screen_height, virtual_y + move_y))
                    try: pyautogui.moveTo(int(virtual_x), int(virtual_y))
                    except Exception: pass
                        
                prev_index_x, prev_index_y = curr_index_x, curr_index_y

            # --- SCALE-INVARIANT CLICKS ---
            dist_left_ratio = math.hypot(index_tip[0] - thumb_tip[0], index_tip[1] - thumb_tip[1]) / hand_size
            dist_right_ratio = math.hypot(mid_tip[0] - thumb_tip[0], mid_tip[1] - thumb_tip[1]) / hand_size
            
            # Left Click
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
                    
            # Right Click
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
        prev_index_x = None

    if show_debug:
        cv2.putText(img, f"Active: {active_hand[0]}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
        cv2.imshow("Virtual Mouse Debug", img)
        if cv2.waitKey(1) & 0xFF == ord('q'): break
    else:
        cv2.waitKey(1)

if left_held: pyautogui.mouseUp(button='left')
if right_held: pyautogui.mouseUp(button='right')
cap.release()
cv2.destroyAllWindows()