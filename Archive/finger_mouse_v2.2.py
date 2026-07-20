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

# Disable PyAutoGUI delay for real-time latency
pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False 

screen_width, screen_height = pyautogui.size()
cam_width, cam_height = 640, 480

# The "Active Zone" margin (Pixels from the edge of the camera)
margin = 100 

model_path = 'hand_landmarker.task'
if not os.path.exists(model_path):
    print("Downloading MediaPipe model...")
    url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
    urllib.request.urlretrieve(url, model_path)

base_options = python.BaseOptions(model_asset_path=model_path)
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    num_hands=1,
    min_hand_detection_confidence=0.7,
    min_hand_presence_confidence=0.7
)
detector = vision.HandLandmarker.create_from_options(options)

cap = cv2.VideoCapture(0)
cap.set(3, cam_width)
cap.set(4, cam_height)

prev_x, prev_y = 0, 0
smoothing_factor = 5
click_threshold = 40
left_clicked, right_clicked = False, False
click_lock = 0

# Debug Window Variables
show_debug = True
last_toggle_state = False

# Hardcoded connections to bypass Google's missing API
HAND_CONNECTIONS = [(0,1),(1,2),(2,3),(3,4),(0,5),(5,6),(6,7),(7,8),(5,9),(9,10),
                    (10,11),(11,12),(9,13),(13,14),(14,15),(15,16),(13,17),(17,18),(18,19),(19,20),(0,17)]

while True:
    success, img = cap.read()
    if not success: break
        
    img = cv2.flip(img, 1)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
    detection_result = detector.detect(mp_image)
    
    # --- GLOBAL HOTKEY LOGIC ---
    current_toggle_state = keyboard.is_pressed('ctrl+alt+d')
    if current_toggle_state and not last_toggle_state:
        show_debug = not show_debug
        if not show_debug:
            cv2.destroyAllWindows() # Close window cleanly
    last_toggle_state = current_toggle_state

    if detection_result.hand_landmarks:
        landmarks = detection_result.hand_landmarks[0]
        
        def get_px(landmark):
            return int(landmark.x * cam_width), int(landmark.y * cam_height)
            
        thumb_x, thumb_y = get_px(landmarks[4])
        index_x, index_y = get_px(landmarks[8])
        mid_x, mid_y = get_px(landmarks[12])
        mid_pip_x, mid_pip_y = get_px(landmarks[10])
        
        # --- DRAWING THE DEBUG MESH ---
        if show_debug:
            # Draw the Active Zone Rectangle
            cv2.rectangle(img, (margin, margin), (cam_width - margin, cam_height - margin), (255, 0, 255), 2)
            
            # Draw wireframe connections
            for connection in HAND_CONNECTIONS:
                pt1 = get_px(landmarks[connection[0]])
                pt2 = get_px(landmarks[connection[1]])
                cv2.line(img, pt1, pt2, (0, 255, 0), 2)
            
            # Draw highlighted nodes
            for i in range(21):
                cv2.circle(img, get_px(landmarks[i]), 4, (0, 0, 255), cv2.FILLED)
                
            # Draw interactive click lines
            color_left = (0, 255, 255) if left_clicked else (255, 0, 0)
            cv2.line(img, (thumb_x, thumb_y), (index_x, index_y), color_left, 3)
            
            color_right = (0, 255, 255) if right_clicked else (255, 0, 0)
            cv2.line(img, (thumb_x, thumb_y), (mid_x, mid_y), color_right, 3)

        # Map index finger using the Active Zone interpolation
        target_x = np.interp(index_x, (margin, cam_width - margin), (0, screen_width))
        target_y = np.interp(index_y, (margin, cam_height - margin), (0, screen_height))
        
        curr_x = prev_x + (target_x - prev_x) / smoothing_factor
        curr_y = prev_y + (target_y - prev_y) / smoothing_factor
        
        dist_left = math.hypot(index_x - thumb_x, index_y - thumb_y)
        dist_right = math.hypot(mid_x - thumb_x, mid_y - thumb_y)
        
        # Gestures and Actions
        if dist_left < click_threshold:
            if not left_clicked:
                pyautogui.click(button='left')
                left_clicked = True
                click_lock = 10 
        else:
            left_clicked = False
            
        if mid_y < mid_pip_y and dist_right < click_threshold:
            if not right_clicked:
                pyautogui.click(button='right')
                right_clicked = True
                click_lock = 10
        else:
            right_clicked = False
            
        if click_lock > 0:
            click_lock -= 1
        else:
            try:
                pyautogui.moveTo(int(curr_x), int(curr_y))
                prev_x, prev_y = curr_x, curr_y
            except Exception:
                pass
                
    if show_debug:
        cv2.imshow("Virtual Mouse Debug (Ctrl+Alt+D to hide)", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        # Keep OpenCV event loop running silently so it doesn't freeze
        cv2.waitKey(1)

cap.release()
cv2.destroyAllWindows()