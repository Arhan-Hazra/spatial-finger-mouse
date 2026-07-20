import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import pyautogui
import math
import urllib.request
import os
import keyboard

# Pipeline Configuration
pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False 

screen_width, screen_height = pyautogui.size()
cam_width, cam_height = 640, 480

model_path = 'hand_landmarker.task'
if not os.path.exists(model_path):
    print("Downloading MediaPipe model...")
    url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
    urllib.request.urlretrieve(url, model_path)

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

# --- TOUCHPAD ENGINE VARIABLES ---
current_mouse_pos = pyautogui.position()
virtual_x, virtual_y = current_mouse_pos.x, current_mouse_pos.y

prev_index_x, prev_index_y = None, None
smoothing_factor = 4 
deadzone = 4 
base_sensitivity = 3.5 

# Hysteresis & Buffer Variables
click_in = 25   
click_out = 45  
left_held, right_held = False, False
left_buffer, right_buffer = 0, 0
buffer_max = 3 

# Toggles and States
show_debug = True
last_d_state = False
active_hand = "Right" 
last_h_state = False
was_clutched = False

def is_fist(landmarks):
    """Calculates if the hand is folded into a fist"""
    folded_fingers = 0
    tips = [8, 12, 16, 20]
    knuckles = [5, 9, 13, 17]
    
    for tip, knuckle in zip(tips, knuckles):
        dist_tip_to_wrist = math.hypot(landmarks[tip].x - landmarks[0].x, landmarks[tip].y - landmarks[0].y)
        dist_knuckle_to_wrist = math.hypot(landmarks[knuckle].x - landmarks[0].x, landmarks[knuckle].y - landmarks[0].y)
        
        if dist_tip_to_wrist < dist_knuckle_to_wrist:
            folded_fingers += 1
            
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

    active_landmarks = None
    clutch_landmarks = None

    if detection_result.hand_landmarks:
        for idx in range(len(detection_result.hand_landmarks)):
            model_label = detection_result.handedness[idx][0].category_name
            physical_hand = "Right" if model_label == "Left" else "Left"
            
            if physical_hand == active_hand:
                active_landmarks = detection_result.hand_landmarks[idx]
            elif physical_hand == clutch_hand:
                clutch_landmarks = detection_result.hand_landmarks[idx]

    # --- 1. CLUTCH LOGIC ---
    clutch_engaged = False
    if clutch_landmarks:
        # FIXED: Removed .landmark
        if is_fist(clutch_landmarks):
            clutch_engaged = True
            
        if show_debug:
            def get_px(landmark): return int(landmark.x * cam_width), int(landmark.y * cam_height)
            # FIXED: Removed .landmark
            cv2.circle(img, get_px(clutch_landmarks[0]), 15, (255, 0, 255), 3)

    if clutch_engaged:
        was_clutched = True
        if show_debug:
            cv2.putText(img, "CLUTCH ENGAGED (FROZEN)", (cam_width//2 - 200, cam_height//2), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)
    else:
        if was_clutched:
            prev_index_x, prev_index_y = None, None
            was_clutched = False

    # --- 2. ACTIVE HAND LOGIC ---
    if active_landmarks:
        def get_px(landmark):
            return int(landmark.x * cam_width), int(landmark.y * cam_height)
            
        # FIXED: Removed .landmark
        thumb_x, thumb_y = get_px(active_landmarks[4])
        index_x, index_y = get_px(active_landmarks[8])
        mid_x, mid_y = get_px(active_landmarks[12])
        mid_pip_x, mid_pip_y = get_px(active_landmarks[10])
        
        if show_debug:
            critical_points = [4, 8, 10, 12]
            for pt in critical_points:
                # FIXED: Removed .landmark
                cv2.circle(img, get_px(active_landmarks[pt]), 8, (0, 255, 0), cv2.FILLED)
                
            color_left = (0, 255, 255) if left_held else (255, 0, 0)
            cv2.line(img, (thumb_x, thumb_y), (index_x, index_y), color_left, 2)
            
            color_right = (0, 255, 255) if right_held else (255, 0, 0)
            cv2.line(img, (thumb_x, thumb_y), (mid_x, mid_y), color_right, 2)

        if not clutch_engaged:
            # --- RELATIVE MOVEMENT LOGIC ---
            if prev_index_x is None:
                prev_index_x, prev_index_y = index_x, index_y
                curr_index_x, curr_index_y = index_x, index_y
            else:
                curr_index_x = prev_index_x + (index_x - prev_index_x) / smoothing_factor
                curr_index_y = prev_index_y + (index_y - prev_index_y) / smoothing_factor
                
                dx = curr_index_x - prev_index_x
                dy = curr_index_y - prev_index_y
                speed = math.hypot(dx, dy)
                
                accel = 1.0
                if speed > 2.0: accel = 1.0 + (speed / 4.0) 
                    
                move_x = dx * base_sensitivity * accel
                move_y = dy * base_sensitivity * accel
                
                if abs(move_x) > deadzone or abs(move_y) > deadzone:
                    virtual_x += move_x
                    virtual_y += move_y
                    
                    virtual_x = max(0, min(screen_width, virtual_x))
                    virtual_y = max(0, min(screen_height, virtual_y))
                    
                    try:
                        pyautogui.moveTo(int(virtual_x), int(virtual_y))
                    except Exception: pass
                        
                prev_index_x, prev_index_y = curr_index_x, curr_index_y

            # --- CLICKS ---
            dist_left = math.hypot(index_x - thumb_x, index_y - thumb_y)
            dist_right = math.hypot(mid_x - thumb_x, mid_y - thumb_y)
            
            if dist_left < click_in:
                left_buffer = 0 
                if not left_held:
                    pyautogui.mouseDown(button='left')
                    left_held = True
            elif dist_left > click_out:
                if left_held:
                    left_buffer += 1 
                    if left_buffer >= buffer_max: 
                        pyautogui.mouseUp(button='left')
                        left_held = False
                        left_buffer = 0
                    
            if mid_y < mid_pip_y and dist_right < click_in:
                right_buffer = 0
                if not right_held:
                    pyautogui.mouseDown(button='right')
                    right_held = True
            elif dist_right > click_out:
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