import cv2
import mediapipe as mp
import pygame
from elevator_ui import ElevatorUI

class Hand:
    """Class to handle hand landmark detection and gesture recognition."""
    def __init__(self, hand_landmarks, margin, mp_hands):
        self.hand_landmarks = hand_landmarks
        self.margin = margin
        self.mp_hands = mp_hands
        self.wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]

    def finger_pointing(self, finger_name, direction):
        """Determine if a finger is pointing in the specified direction."""
        finger_tip = self.hand_landmarks.landmark[getattr(self.mp_hands.HandLandmark, f"{finger_name}_TIP")]
        finger_dip = self.hand_landmarks.landmark[getattr(self.mp_hands.HandLandmark, f"{finger_name}_DIP")]
        finger_pip = self.hand_landmarks.landmark[getattr(self.mp_hands.HandLandmark, f"{finger_name}_PIP")]
        finger_mcp = self.hand_landmarks.landmark[getattr(self.mp_hands.HandLandmark, f"{finger_name}_MCP")]
        
        if direction == 'up':
            return (finger_tip.y < finger_dip.y and 
                   finger_dip.y < finger_pip.y and
                   finger_pip.y < finger_mcp.y and 
                   finger_mcp.y < self.wrist.y - self.margin)
        elif direction == 'down':
            return (finger_tip.y > finger_dip.y and 
                   finger_dip.y > finger_pip.y and
                   finger_pip.y > finger_mcp.y and 
                   finger_mcp.y > self.wrist.y + self.margin)

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

class ElevatorController:
    def __init__(self):
        # Initialize MediaPipe
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_hands = mp.solutions.hands
        
        # Initialize camera and hands
        self.cap = cv2.VideoCapture(0)
        self.hands = self.mp_hands.Hands(max_num_hands=1)
        
        # Initialize pygame for sound
        pygame.mixer.init()
        
        # Initialize counters and parameters
        self.gesture_counter = 0
        self.last_n_gestures = []
        self.last_n_victory_gestures = []
        self.n = 15
        self.n_v = 30
        self.margin = 0
        self.initial_victory_frames = 30
        self.initial_victory_counter = 0
        self.initializing = True
        self.current_floor = 0
        self.predicted_floor = 0
        
        # Initialize UI
        self.ui = ElevatorUI()

    def recognize_gesture(self, hand_landmarks):
        """Recognize the current hand gesture."""
        hand = Hand(hand_landmarks, self.margin, self.mp_hands)
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

    def play_sound(self, sound_file):
        """Play a sound effect."""
        try:
            pygame.mixer.music.load(sound_file)
            pygame.mixer.music.play()
        except pygame.error as e:
            print(f"Error playing audio: {e}")

    def update_frame(self):
        """Main update loop"""
        success, image = self.cap.read()
        if not success:
            return

        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
        results = self.hands.process(image)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(image, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                gesture = self.recognize_gesture(hand_landmarks)
                
                if self.initializing:
                    if gesture == "Victory (OK)":
                        self.initial_victory_counter += 1
                    else:
                        self.initial_victory_counter = 0

                    if self.initial_victory_counter >= self.initial_victory_frames:
                        self.initializing = False
                        self.initial_victory_counter = 0
                        self.current_floor += self.gesture_counter
                        self.play_sound('initialize.mp3')

                    self.ui.update_gesture_label("Show Victory Gesture to Start")
                    break

                # Handle victory gesture separately
                if gesture == "Victory (OK)":
                    self.last_n_victory_gestures.append(gesture)
                    if len(self.last_n_victory_gestures) > self.n_v:
                        self.last_n_victory_gestures.pop(0)

                    if self.last_n_victory_gestures.count("Victory (OK)") == self.n_v:
                        self.current_floor += self.gesture_counter
                        self.gesture_counter = 0
                        self.initializing = True
                        self.play_sound('Confirm.mp3')
                        self.last_n_victory_gestures.clear()
                else:
                    self.last_n_gestures.append(gesture)
                    if len(self.last_n_gestures) > self.n:
                        self.last_n_gestures.pop(0)

                    # Handle different gestures
                    if self.last_n_gestures.count("All Fingers Pointing Up") == self.n:
                        self.gesture_counter += 10
                        self.play_sound('Floor_changing.mp3')
                        self.last_n_gestures.clear()
                    
                    elif self.last_n_gestures.count("All Fingers Pointing Down") == self.n:
                        self.gesture_counter -= 10
                        self.play_sound('Floor_changing.mp3')
                        self.last_n_gestures.clear()
                    
                    elif self.last_n_gestures.count("Index Finger Pointing Up") == self.n:
                        self.gesture_counter += 1
                        self.play_sound('Floor_changing.mp3')
                        self.last_n_gestures.clear()
                    
                    elif self.last_n_gestures.count("Index Finger Pointing Down") == self.n:
                        self.gesture_counter -= 1
                        self.play_sound('Floor_changing.mp3')
                        self.last_n_gestures.clear()

                # Update display
                self.predicted_floor = self.current_floor + self.gesture_counter
                self.ui.update_gesture_label(f"Current Gesture: {gesture}")
                self.ui.update_floor_display(self.current_floor, self.predicted_floor)

        # Update video display
        self.ui.update_video(image)
        self.ui.root.after(10, self.update_frame)

    def run(self):
        """Start the application"""
        self.ui.start(self.update_frame)
        
    def cleanup(self):
        """Clean up resources"""
        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    app = ElevatorController()
    try:
        app.run()
    finally:
        app.cleanup() 