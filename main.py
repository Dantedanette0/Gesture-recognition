import os
import sys
import cv2
import mediapipe as mp
import pygame
from UI import ElevatorUI
from gesture_handler import GestureHandler
import time

# MediaPipe initialization
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# Open webcam
cap = cv2.VideoCapture(0)
hands = mp_hands.Hands(max_num_hands=1)

margin = 0.05  # More margin means more fingers must be up or down from the wrist

# Initial victory gesture frames requirement
initial_victory_frames = 30
initial_victory_counter = 0
initializing = True

# Global current floor variable
current_floor = 0
predicted_floor = 0

# Pygame mixer initialization
pygame.mixer.init()

# Initialize UI
ui = ElevatorUI()

# Initialize GestureHandler
gesture_handler = GestureHandler(margin)

CONFIRM_AUDIO_PATH = os.path.join(getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__))), "audio/Confirm.mp3")
FLOOR_CHANGE_1X_AUDIO_PATH = os.path.join(getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__))), "audio/Floor_Change_1x.mp3")
FLOOR_CHANGE_10X_AUDIO_PATH = os.path.join(getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__))), "audio/Floor_Change_10x.mp3")

#draws the box around the hand , the text and its background above the box DO NOT CHANGE THE COORDINATES
def draw_detection_box(results, image, box_color, label_text, predicted_floor, show_floor=False):
    hand_landmarks_list = results.multi_hand_landmarks
    for i in range(len(hand_landmarks_list)):
        hand_landmarks = hand_landmarks_list[i]
        x_coordinates = [landmark.x for landmark in hand_landmarks.landmark]
        y_coordinates = [landmark.y for landmark in hand_landmarks.landmark]
        # Mirror the box coordinates as well so it matches the capture mirroring
        x_top_right = int(min(x_coordinates) * image.shape[1]) - 25
        y_top_right = int(min(y_coordinates) * image.shape[0]) - 25
        x_bottom_left = int(max(x_coordinates) * image.shape[1]) + 25
        y_bottom_left = int(max(y_coordinates) * image.shape[0]) + 25
        box_width = x_bottom_left - x_top_right

        #we are drawing the text and the rectangles in scale of each other so they dont get out 
        cv2.rectangle(image, (x_top_right, y_top_right), (x_bottom_left, y_bottom_left), box_color, thickness=10)
        cv2.rectangle(image, (x_top_right, y_top_right), (x_bottom_left, y_bottom_left), (0, 0, 0), thickness=3)
        if gesture_handler.initializing:
            cv2.rectangle(image, (x_top_right - 3, y_top_right - 30), (x_top_right + 100 + box_width, y_top_right), (0, 0, 0), thickness=-1)
            cv2.putText(image, label_text, (x_top_right + 5, y_top_right - 5), cv2.FONT_HERSHEY_TRIPLEX, color=box_color, fontScale=1)
        # Draw the predicted floor above the gesture label only if we are able to change the floor
        if show_floor:
            # Draw black box background for predicted floor
            cv2.rectangle(image, (x_top_right - 3, y_top_right - 60), (x_top_right + 175 + box_width, y_top_right - 30), (0, 0, 0), thickness=-1)
            cv2.putText(image, f"You are going to floor: {predicted_floor}", (x_top_right + 5, y_top_right - 35), cv2.FONT_HERSHEY_TRIPLEX, color=box_color, fontScale=min(box_width / 250, 0.75))
    return image

def update():
    # Initialize predicted_floor with the current calculation
    predicted_floor = gesture_handler.current_floor + gesture_handler.gesture_counter
    
    # Capture image from webcam
    success, image = cap.read()
    if not success:
        return
    
    # Flip and process the image so we don't see a mirrored version of ourselves
    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
    results = hands.process(image)

    # Add initializing text to the image
    if gesture_handler.initializing:
        # Make the text flash by alternating visibility based on time
        if int(time.time() * 2) % 1 == 0:
            cv2.putText(image, "Show Peace Sign", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 0), 2, cv2.LINE_AA)
    else:
        cv2.putText(image, "Selecting Floor", (200, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,(0, 255, 0), 2)
  

    # State-specific box colors and labels
    state_config = {
        "Victory (OK)": {"box_color": (255,255,0), "label_text": "Victory (OK)"},
        "All Fingers Pointing Up": {"box_color": (50,205,50), "label_text": "All Fingers Pointing Up"},
        "All Fingers Pointing Down": {"box_color": (255,0,0), "label_text": "All Fingers Pointing Down"},
        "Index Finger Pointing Up": {"box_color": (0, 255, 0), "label_text": "Index Finger Pointing Up"},
        "Index Finger Pointing Down": {"box_color": (220,20,60), "label_text": "Index Finger Pointing Down"},
        "idle": {"box_color": (169, 169, 169), "label_text": "Idle"}  
    }

    current_state = "idle"
    show_floor = False

    # If hands are detected, process the landmarks
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Draw the landmarks on the fingers and also get their position
            mp_drawing.draw_landmarks(
                image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Recognize gesture from landmarks
            gesture = gesture_handler.recognize_gesture(hand_landmarks)

            # Handle initializing phase
            if gesture_handler.initializing:
                if gesture == "Victory (OK)":
                    gesture_handler.handle_initializing(gesture)
                    predicted_floor = gesture_handler.current_floor + gesture_handler.gesture_counter
                    # Show instructions during initialization
                    current_state = "Victory (OK)"
                else:
                    current_state = "idle"
                break

            # Handle gestures while changing floors
            if not gesture_handler.initializing:
                if gesture == "All Fingers Pointing Up":
                    gesture_handler.handle_gesture(gesture_handler.all_fingers_up_data, FLOOR_CHANGE_10X_AUDIO_PATH)
                    current_state = "All Fingers Pointing Up"
                    show_floor = True

                elif gesture == "All Fingers Pointing Down":
                    gesture_handler.handle_gesture(gesture_handler.all_fingers_down_data, FLOOR_CHANGE_10X_AUDIO_PATH)
                    current_state = "All Fingers Pointing Down"
                    show_floor = True

                elif gesture == "Index Finger Pointing Up":
                    gesture_handler.handle_gesture(gesture_handler.index_finger_up_data, FLOOR_CHANGE_1X_AUDIO_PATH)
                    current_state = "Index Finger Pointing Up"
                    show_floor = True

                elif gesture == "Index Finger Pointing Down":
                    gesture_handler.handle_gesture(gesture_handler.index_finger_down_data, FLOOR_CHANGE_1X_AUDIO_PATH)
                    current_state = "Index Finger Pointing Down"
                    show_floor = True

                elif gesture == "Victory (OK)":
                    # Confirm the current floor selection
                    gesture_handler.handle_gesture(gesture_handler.victory_gesture_data, CONFIRM_AUDIO_PATH)
                    current_state = "Victory (OK)"
                    show_floor = True

                # Update predicted floor
                predicted_floor = gesture_handler.current_floor + gesture_handler.gesture_counter

        # Draw detection box around the detected hand
        box_color = state_config[current_state]["box_color"]
        label_text = state_config[current_state]["label_text"]
        image = draw_detection_box(results, image, box_color, label_text, predicted_floor, show_floor=show_floor)

    # Update UI elements
    ui.update_video(image)
    ui.update_floor_display(gesture_handler.current_floor, predicted_floor)
    
    # Schedule the next update
    ui.root.after(10, update)

    # Inside the update function, after gesture handling
    if gesture_handler.initializing or gesture_handler.is_first_initialization:
        # Hide instructions during very first initialization
        ui.hide_instructions()
    elif not gesture_handler.initializing:
        # Show instructions right after initialization
        if not ui.floor_selected:
            ui.show_instructions()
        
        # Reset floor_selected when starting a new gesture sequence
        if gesture_handler.initial_victory_counter >= 0:
            ui.floor_selected = False
            ui.show_instructions()

# Start the UI
ui.start(update)

# The cleanup code should be called when the window is closed
cap.release()
cv2.destroyAllWindows()