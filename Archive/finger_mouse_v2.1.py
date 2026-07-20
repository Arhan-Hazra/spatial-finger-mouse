import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import pyautogui
import math
import urllib.request
import os

# Disable PyAutoGUI delay for real-time latency
pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False 

screen_width, screen_height = pyautogui.size()
cam_width, cam_height = 640, 480

# Auto-download the required MediaPipe model file
model_path = 'hand_landmarker.task'
if not os.path.exists(model_path):
    print("Downloading MediaPipe model file (this only happens once)...")
    url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
    urllib.request.urlretrieve(url, model_path)
    print("Download complete!")

# Initialize the new Tasks API
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

# Variables for smoothing and state machine
prev_x, prev_y = 0, 0
smoothing_factor = 5
click_threshold = 40
left_clicked = False
right_clicked = False
click_lock = 0

while True:
    success, img = cap.read()
    if not success:
        break
        
    # Flip horizontally for a natural mirror-image feel
    img = cv2.flip(img, 1)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Convert the OpenCV frame to a MediaPipe Image object
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
    
    # Detect landmarks using the Tasks API
    detection_result = detector.detect(mp_image)
    
    if detection_result.hand_landmarks:
        # Extract the first detected hand
        landmarks = detection_result.hand_landmarks[0]
        
        def get_px(landmark):
            return int(landmark.x * cam_width), int(landmark.y * cam_height)
            
        thumb_x, thumb_y = get_px(landmarks[4])
        index_x, index_y = get_px(landmarks[8])
        mid_x, mid_y = get_px(landmarks[12])
        mid_pip_x, mid_pip_y = get_px(landmarks[10])
        
        # Map the index finger to screen dimensions
        target_x = int(landmarks[8].x * screen_width)
        target_y = int(landmarks[8].y * screen_height)
        
        # Apply Exponential Moving Average (EMA) filter
        curr_x = prev_x + (target_x - prev_x) / smoothing_factor
        curr_y = prev_y + (target_y - prev_y) / smoothing_factor
        
        # Calculate Euclidean distances for gestures
        dist_left = math.hypot(index_x - thumb_x, index_y - thumb_y)
        dist_right = math.hypot(mid_x - thumb_x, mid_y - thumb_y)
        
        # -- GESTURE: Left Click (Index + Thumb) --
        if dist_left < click_threshold:
            if not left_clicked:
                pyautogui.click(button='left')
                left_clicked = True
                click_lock = 10 # Freeze cursor for 10 frames
        else:
            left_clicked = False
            
        # -- GESTURE: Right Click (Middle + Thumb) --
        if mid_y < mid_pip_y and dist_right < click_threshold:
            if not right_clicked:
                pyautogui.click(button='right')
                right_clicked = True
                click_lock = 10
        else:
            right_clicked = False
            
        # -- ACTION: Move Cursor --
        if click_lock > 0:
            click_lock -= 1
        else:
            try:
                pyautogui.moveTo(int(curr_x), int(curr_y))
                prev_x, prev_y = curr_x, curr_y
            except Exception:
                pass
                
    cv2.imshow("Virtual Mouse", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()