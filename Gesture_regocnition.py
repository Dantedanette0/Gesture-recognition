import cv2
import mediapipe as mp
import pygame

# MediaPipe initialization
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# Open webcam
cap = cv2.VideoCapture(0)
hands = mp_hands.Hands()

# counts how many n frames we held a gesture
gesture_counter = 0
last_n_gestures = []  #helps us control speed along with n
n = 30  # controls how fast the program changes the counter
margin = 0.0  # more margin means more fingers must be up or down from the wrist (can make detecting hand from afar wonky)

# Initial victory gesture frames requirement
initial_victory_frames = 30
initial_victory_counter = 0
initializing = True


# Global current floor variable
current_floor = 0
predicted_floor = 0

#responsible for getting the position of each part of the fingers and checking it against each other
class Hand:
    def __init__(self, hand_landmarks, margin):
        self.hand_landmarks = hand_landmarks
        self.margin = margin
        self.wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]

    #extract part of the finger from the landmark function given its name
    def finger_pointing(self, finger_name, direction):
        finger_tip = self.hand_landmarks.landmark[getattr(mp_hands.HandLandmark, f"{finger_name}_TIP")]
        finger_dip = self.hand_landmarks.landmark[getattr(mp_hands.HandLandmark, f"{finger_name}_DIP")]
        finger_pip = self.hand_landmarks.landmark[getattr(mp_hands.HandLandmark, f"{finger_name}_PIP")]
        finger_mcp = self.hand_landmarks.landmark[getattr(mp_hands.HandLandmark, f"{finger_name}_MCP")]
        
        #if parts of the finger are from up to down in order pointing up if in reverse order pointing down
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

while True:
    success, image = cap.read()
    if not success:
        continue

    # Flip the image so we don't see a mirrored version of ourselves
    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)

    # MediaPipe detects hands in each frame
    results = hands.process(image)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    # Resize window to make the initial screen bigger
    image = cv2.resize(image, (1280, 720))

    # If hand landmarks are detected, perform the following
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Draw landmarks
            mp_drawing.draw_landmarks(
                image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Recognize gesture
            gesture = recognize_gesture(hand_landmarks)

            # Initial gesture detection (30 frames of Victory gesture)
            if initializing:
                if gesture == "Victory (OK)":
                    initial_victory_counter += 1
                else:
                    initial_victory_counter = 0

                if initial_victory_counter >= initial_victory_frames:
                    initializing = False
                    initial_victory_counter = 0
                    current_floor += gesture_counter
                    pygame.mixer.init()
                    pygame.mixer.music.load('initialize.mp3')
                    pygame.mixer.music.play()

                predicted_floor = current_floor + gesture_counter
                cv2.putText(image, f"Show Victory Gesture to Start", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2, cv2.LINE_AA)
                cv2.putText(image, f"Current Floor: {current_floor}", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)

                cv2.imshow('MediaPipe Hands', image)

                if cv2.waitKey(1) & 0xFF in [ord('q'), 27]:
                    break
                continue

            # Append gesture to the last_n_gestures list
            last_n_gestures.append(gesture)
            if len(last_n_gestures) > n:
                last_n_gestures.pop(0)

            # Check if the last n frames were pointing up or down
            if last_n_gestures.count("All Fingers Pointing Up") == n:
                gesture_counter += 10
                pygame.mixer.music.load('Floor_changing.mp3')
                pygame.mixer.music.play()
                last_n_gestures.clear()

            elif last_n_gestures.count("All Fingers Pointing Down") == n:
                gesture_counter -= 10
                pygame.mixer.music.load('Floor_changing.mp3')
                pygame.mixer.music.play()
                last_n_gestures.clear()

            elif last_n_gestures.count("Victory (OK)") == n:
                    current_floor += gesture_counter
                    gesture_counter = 0
                    initializing = True
                    last_n_gestures.clear()
                    confirm_victory_counter = 0

            elif last_n_gestures.count("Index Finger Pointing Up") == n:
                gesture_counter += 1
                pygame.mixer.music.load('Floor_changing.mp3')
                pygame.mixer.music.play()
                last_n_gestures.clear()

            elif last_n_gestures.count("Index Finger Pointing Down") == n:
                gesture_counter -= 1
                pygame.mixer.music.load('Floor_changing.mp3')
                pygame.mixer.music.play()
                last_n_gestures.clear()

            # Predict the floor we are going to if confirmed
            predicted_floor = current_floor + gesture_counter

            # Display gesture, counter, current floor, and predicted floor
            cv2.putText(image, gesture, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.putText(image, f"Counter: {gesture_counter} (Show Victory Sign to Confirm Floor {predicted_floor})", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
            cv2.putText(image, f"Current Floor: {current_floor}", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
            cv2.putText(image, "Gesture List:", (10, 250), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(image, "Victory (OK): Confirm floor selection", (10, 300), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(image, "All Fingers Pointing Up: Increase counter by 10", (10, 350), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(image, "All Fingers Pointing Down: Decrease counter by 10", (10, 400), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(image, "Index Finger Pointing Up: Increase counter by 1", (10, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(image, "Index Finger Pointing Down: Decrease counter by 1", (10, 500), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)

    # Display landmarks of the hand
    cv2.imshow('MediaPipe Hands', image)

    # Close the program when 'q' or 'Esc' is pressed (waitKey checks if any key is pressed each frame)
    if cv2.waitKey(1) & 0xFF in [ord('q'), 27]:
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
