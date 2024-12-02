import cv2
import mediapipe as mp
import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
import pygame
from hand import Hand
from UI import ElevatorUI
from gesture_handler import GestureHandler

# MediaPipe initialization
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# Open webcam
cap = cv2.VideoCapture(0)
hands = mp_hands.Hands(max_num_hands=1)

margin = 0.00  # More margin means more fingers must be up or down from the wrist

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

    # Gesture state tracking
    gesture_active = False
    going_down = False

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
                gesture_handler.handle_initializing(gesture)
                predicted_floor = gesture_handler.current_floor + gesture_handler.gesture_counter
                # Hide instructions during initialization
                ui.update_gesture_label(f"Initializing... Gesture Counter: {gesture_handler.gesture_counter}", initializing=True)
                break

            # Handle gestures and set gesture_active if floor is changing
            if gesture == "Victory (OK)":
                gesture_handler.handle_gesture(gesture, gesture_handler.victory_gesture_data, 'Confirm.mp3')

            elif gesture == "All Fingers Pointing Up":
                gesture_handler.handle_gesture(gesture, gesture_handler.all_fingers_up_data, '10_floors.mp3')
                gesture_active = True
                going_down = False  # Floor is going up

            elif gesture == "All Fingers Pointing Down":
                gesture_handler.handle_gesture(gesture, gesture_handler.all_fingers_down_data, '10_floors.mp3')
                gesture_active = True
                going_down = True  # Floor is going down

            elif gesture == "Index Finger Pointing Up":
                gesture_handler.handle_gesture(gesture, gesture_handler.index_finger_up_data, 'Floor_changing.mp3')
                gesture_active = True
                going_down = False  # Floor is going up

            elif gesture == "Index Finger Pointing Down":
                gesture_handler.handle_gesture(gesture, gesture_handler.index_finger_down_data, 'Floor_changing.mp3')
                gesture_active = True
                going_down = True  # Floor is going down

            # Update predicted floor
            predicted_floor = gesture_handler.current_floor + gesture_handler.gesture_counter

    # Update UI elements
    ui.update_video(image)
    ui.update_floor_display(gesture_handler.current_floor, predicted_floor)
    # Update gesture label and manage instructions visibility based on initializing state
    ui.update_gesture_label(f"Gesture Counter: {gesture_handler.gesture_counter}", gesture_active=gesture_active, going_down=going_down, initializing=gesture_handler.initializing)
    
    # Schedule the next update
    ui.root.after(10, update)

# Start the UI
ui.start(update)

# The cleanup code should be called when the window is closed
cap.release()
cv2.destroyAllWindows()
