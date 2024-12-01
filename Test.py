import cv2
import mediapipe as mp
import tkinter as tk
from PIL import Image, ImageTk
import pygame

# MediaPipe initialization
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# Open webcam
cap = cv2.VideoCapture(0)
hands = mp_hands.Hands(max_num_hands=1)

# Initialize gesture counter and parameters
gesture_counter = 0
last_n_gestures = []  # Helps control speed along with n
n = 15  # Controls how fast the program changes the counter

# This is same as above but seperate for confirmation as we need it to be a different speed
last_n_victory_gestures = []  
n_v = 30

margin = 0.00  # More margin means more fingers must be up or down from the wrist

# Initial victory gesture frames requirement
initial_victory_frames = 30
initial_victory_counter = 0
initializing = True

# Global current floor variable
current_floor = 0
predicted_floor = 0

# Tkinter initialization
root = tk.Tk()
root.title("Gesture Recognition")
root.geometry("800x600")

# Create canvas for video feed
canvas = tk.Canvas(root, width=640, height=480)
canvas.pack()

# Gesture Counter Label
gesture_label = tk.Label(root, text=f"Gesture Counter: {gesture_counter}", font=("Helvetica", 16))
gesture_label.pack()

# Pygame mixer initialization
pygame.mixer.init()

class Hand:
    def __init__(self, hand_landmarks, margin):
        self.hand_landmarks = hand_landmarks
        self.margin = margin
        self.wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]

    def finger_pointing(self, finger_name, direction):
        finger_tip = self.hand_landmarks.landmark[getattr(mp_hands.HandLandmark, f"{finger_name}_TIP")]
        finger_dip = self.hand_landmarks.landmark[getattr(mp_hands.HandLandmark, f"{finger_name}_DIP")]
        finger_pip = self.hand_landmarks.landmark[getattr(mp_hands.HandLandmark, f"{finger_name}_PIP")]
        finger_mcp = self.hand_landmarks.landmark[getattr(mp_hands.HandLandmark, f"{finger_name}_MCP")]
        
        if direction == 'up':
            return (finger_tip.y < finger_dip.y and finger_dip.y < finger_pip.y and
                    finger_pip.y < finger_mcp.y and finger_mcp.y < self.wrist.y - self.margin)
        elif direction == 'down':
            return (finger_tip.y > finger_dip.y and finger_dip.y > finger_pip.y and
                    finger_pip.y > finger_mcp.y and finger_mcp.y > self.wrist.y + self.margin)

    def finger_up(self, finger_name):
        return self.finger_pointing(finger_name, 'up')

    def finger_down(self, finger_name):
        return self.finger_pointing(finger_name, 'down')

    def all_fingers_up_except_thumb(self):
        return (self.finger_up('INDEX_FINGER') and
                self.finger_up('MIDDLE_FINGER') and
                self.finger_up('RING_FINGER') and
                self.finger_up('PINKY'))

    def all_fingers_down_except_thumb(self):
        return (self.finger_down('INDEX_FINGER') and
                self.finger_down('MIDDLE_FINGER') and
                self.finger_down('RING_FINGER') and
                self.finger_down('PINKY'))

    def victory_gesture(self):
        return (self.finger_up('INDEX_FINGER') and
                self.finger_up('MIDDLE_FINGER') and
                not self.finger_up('RING_FINGER') and
                not self.finger_up('PINKY'))

def recognize_gesture(hand_landmarks):
    hand = Hand(hand_landmarks, margin)
    if hand.all_fingers_up_except_thumb():
        return "All Fingers Pointing Up"
    elif hand.all_fingers_down_except_thumb():
        return "All Fingers Pointing Down"
    elif hand.victory_gesture():
        return "Victory (OK)"
    elif hand.finger_up('INDEX_FINGER'):
        return "Index Finger Pointing Up"
    elif hand.finger_down('INDEX_FINGER'):
        return "Index Finger Pointing Down"
    else:
        return "Neutral"


def play_audio(file_name):
    try:
        pygame.mixer.music.load(file_name)
        pygame.mixer.music.play()
    except pygame.error as e:
        print(f"Error playing audio: {e}")


def update_frame():
    global gesture_counter, initializing, initial_victory_counter, current_floor, predicted_floor, last_n_gestures, last_n_victory_gestures

    success, image = cap.read()
    if not success:
        return

    # Flip and process the image
    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
    results = hands.process(image)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            gesture = recognize_gesture(hand_landmarks)

            if initializing:
                if gesture == "Victory (OK)":
                    initial_victory_counter += 1
                else:
                    initial_victory_counter = 0

                if initial_victory_counter >= initial_victory_frames:
                    initializing = False
                    initial_victory_counter = 0
                    current_floor += gesture_counter
                    play_audio('initialize.mp3')

                predicted_floor = current_floor + gesture_counter
                break

            # Handle victory gesture separately
            if gesture == "Victory (OK)":
                last_n_victory_gestures.append(gesture)
                if len(last_n_victory_gestures) > n_v:
                    last_n_victory_gestures.pop(0)

                if last_n_victory_gestures.count("Victory (OK)") == n_v:
                    current_floor += gesture_counter
                    gesture_counter = 0
                    initializing = True
                    play_audio('Confirm.mp3')
                    last_n_victory_gestures.clear()
            else:
                last_n_gestures.append(gesture)
                if len(last_n_gestures) > n:
                    last_n_gestures.pop(0)

                if last_n_gestures.count("All Fingers Pointing Up") == n:
                    gesture_counter += 10
                    play_audio('Floor_changing.mp3')
                    last_n_gestures.clear()

                elif last_n_gestures.count("All Fingers Pointing Down") == n:
                    gesture_counter -= 10
                    play_audio('Floor_changing.mp3')
                    last_n_gestures.clear()

                elif last_n_gestures.count("Index Finger Pointing Up") == n:
                    gesture_counter += 1
                    play_audio('Floor_changing.mp3')
                    last_n_gestures.clear()

                elif last_n_gestures.count("Index Finger Pointing Down") == n:
                    gesture_counter -= 1
                    play_audio('Floor_changing.mp3')
                    last_n_gestures.clear()

            predicted_floor = current_floor + gesture_counter

    # Convert the image to a format Tkinter understands
    img = Image.fromarray(image)
    imgtk = ImageTk.PhotoImage(image=img)
    canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
    canvas.imgtk = imgtk

    gesture_label.config(text=f"Gesture Counter: {gesture_counter}")
    root.after(10, update_frame)


update_frame()
root.mainloop()

cap.release()
cv2.destroyAllWindows()
