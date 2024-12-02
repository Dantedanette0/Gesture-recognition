import cv2
import mediapipe as mp
import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
import pygame
from hand import Hand
from UI import setup_ui
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

# Setup the UI
tk_root, canvas, gesture_label, current_floor_label = setup_ui()

# Initialize GestureHandler
gesture_handler = GestureHandler(margin)

while True:

    #opens the camera and starts capturing
    success, image = cap.read()
    if not success:
        break
    # Flip and process the image so we dont see a mirrored version of our selves
    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
    results = hands.process(image)

    #if you see hands do what ever is below
    if results.multi_hand_landmarks:

        # draw the land marks on the fingers and also get their position
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            gesture = gesture_handler.recognize_gesture(hand_landmarks)

            # this where the app doing the first confirmation and also where we set current floor    
            if gesture_handler.initializing:
                gesture_handler.handle_initializing(gesture)
                predicted_floor = gesture_handler.current_floor + gesture_handler.gesture_counter
                break

            # Handle gestures
            if gesture == "Victory (OK)":
                gesture_handler.handle_gesture(gesture, gesture_handler.victory_gesture_data, 'Confirm.mp3')

            elif gesture == "All Fingers Pointing Up":
                gesture_handler.handle_gesture(gesture, gesture_handler.all_fingers_up_data, '10_floors.mp3')

            elif gesture == "All Fingers Pointing Down":
                gesture_handler.handle_gesture(gesture, gesture_handler.all_fingers_down_data, '10_floors.mp3')

            elif gesture == "Index Finger Pointing Up":
                gesture_handler.handle_gesture(gesture, gesture_handler.index_finger_up_data, 'Floor_changing.mp3')

            elif gesture == "Index Finger Pointing Down":
                gesture_handler.handle_gesture(gesture, gesture_handler.index_finger_down_data, 'Floor_changing.mp3')

            predicted_floor = gesture_handler.current_floor + gesture_handler.gesture_counter


    # Convert the image to a format Tkinter understands
    img = Image.fromarray(image)
    imgtk = ImageTk.PhotoImage(image=img)
    canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
    canvas.imgtk = imgtk

    gesture_label.config(text=f"Gesture Counter: {gesture_handler.gesture_counter}")
    current_floor_label.config(text=f"Current Floor: {gesture_handler.current_floor} | Predicted Floor: {predicted_floor}")

    tk_root.update_idletasks()
    tk_root.update()

cap.release()
cv2.destroyAllWindows()
