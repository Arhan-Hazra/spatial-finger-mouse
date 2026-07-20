import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import pyautogui
import math
import urllib.request
import os
import numpy as np
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

# --- NEW: Anti-Jitter and State Variables ---
prev_x, prev_y = 0, 0
smoothing_factor = 7 # Increased for smoother, heavier cursor feel
deadzone = 2 # Pixels cursor must move before updating (stops micro-shakes)

# --- NEW: Hysteresis & Buffer Variables ---
click_in = 25   # Distance to trigger a HOLD
click_out = 45  # Distance to TRIGGER a RELEASE
left_held, right_held = False, False

left_buffer = 0
right_buffer = 0
buffer_max = 3 # Frames the fingers must be apart before the code actually drops the click

show_debug = True
last_d_state = False
active_hand = "Right" 
last_h_state = False

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

    target_landmarks = None

    if detection_result.hand_landmarks:
        for idx in range(len(detection_result.hand_landmarks)):
            model_label = detection_result.handedness[idx][0].category_name
            physical_hand = "Right" if model_label == "Left" else "Left"
            if physical_hand == active_hand:
                target_landmarks = detection_result.hand_landmarks[idx]
                break

    if target_landmarks:
        def get_px(landmark):
            return int(landmark.x * cam_width), int(landmark.y * cam_height)
            
        thumb_x, thumb_y = get_px(target_landmarks[4])
        index_x, index_y = get_px(target_landmarks[8])
        mid_x, mid_y = get_px(target_landmarks[12])
        mid_pip_x, mid_pip_y = get_px(target_landmarks[10])
        
        if show_debug:
            critical_points = [4, 8, 10, 12]
            for pt in critical_points:
                cv2.circle(img, get_px(target_landmarks[pt]), 8, (0, 255, 0), cv2.FILLED)
                
            color_left = (0, 255, 255) if left_held else (255, 0, 0)
            cv2.line(img, (thumb_x, thumb_y), (index_x, index_y), color_left, 2)
            
            color_right = (0, 255, 255) if right_held else (255, 0, 0)
            cv2.line(img, (thumb_x, thumb_y), (mid_x, mid_y), color_right, 2)

        target_x = np.interp(index_x, (0, cam_width), (0, screen_width))
        target_y = np.interp(index_y, (0, cam_height), (0, screen_height))
        
        curr_x = prev_x + (target_x - prev_x) / smoothing_factor
        curr_y = prev_y + (target_y - prev_y) / smoothing_factor
        
        dist_left = math.hypot(index_x - thumb_x, index_y - thumb_y)
        dist_right = math.hypot(mid_x - thumb_x, mid_y - thumb_y)
        
        # --- LEFT CLICK (Hysteresis + Buffer) ---
        if dist_left < click_in:
            left_buffer = 0 # Reset buffer because we are confidently holding
            if not left_held:
                pyautogui.mouseDown(button='left')
                left_held = True
        elif dist_left > click_out:
            if left_held:
                left_buffer += 1 # Fingers are apart, start counting
                if left_buffer >= buffer_max: # Only release if apart for 3 frames
                    pyautogui.mouseUp(button='left')
                    left_held = False
                    left_buffer = 0
                
        # --- RIGHT CLICK (Hysteresis + Buffer) ---
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
            
        # --- MOVEMENT (With Deadzone) ---
        if abs(curr_x - prev_x) > deadzone or abs(curr_y - prev_y) > deadzone:
            try:
                pyautogui.moveTo(int(curr_x), int(curr_y))
                prev_x, prev_y = curr_x, curr_y
            except Exception:
                pass

    if show_debug:
        cv2.putText(img, f"Hand: {active_hand[0]}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
        cv2.imshow("Virtual Mouse Debug", img)
        if cv2.waitKey(1) & 0xFF == ord('q'): break
    else:
        cv2.waitKey(1)

if left_held: pyautogui.mouseUp(button='left')
if right_held: pyautogui.mouseUp(button='right')
cap.release()
cv2.destroyAllWindows()