import cv2
import mediapipe as mp
import tkinter as tk
import pygame
from PIL import Image, ImageTk

# TODO: Use different sound effects for up versus down gestures
# TODO: Use different sound effects (higher pitch versus lower pitch) for higher speed and lower speed respectively
# TODO: Make UI prettier in general

# Initialize MediaPipe components
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# Initialize pygame for sound effects
pygame.mixer.init()

# Initialize webcam capture
cap = cv2.VideoCapture(0)
hands = mp_hands.Hands(max_num_hands=1)

# Initialize counters and parameters
gesture_counter = 0
last_n_gestures = []  # List to track recent gestures
n = 15  # Number of frames to determine a consistent gesture
margin = 0  # Margin for finger position detection
initial_victory_frames = 30  # Frames required for initial victory gesture
initial_victory_counter = 0
initializing = True
current_floor = 0
predicted_floor = 0

# Add these constants near the top
PADDING = 10
BG_COLOR = "#f0f0f0"
PRIMARY_COLOR = "#2c3e50"
ACCENT_COLOR = "#3498db"

# Initialize Tkinter window and components
root = tk.Tk()
root.title("Gesture Recognition")
root.configure(bg=BG_COLOR)
root.geometry("1024x768")  # Larger default size
root.minsize(800, 600)    # Minimum window size

# Create main frames for better organization
left_frame = tk.Frame(root, bg=BG_COLOR)
left_frame.pack(side=tk.LEFT, padx=PADDING, pady=PADDING, fill=tk.BOTH, expand=True)

right_frame = tk.Frame(root, bg=BG_COLOR)
right_frame.pack(side=tk.RIGHT, padx=PADDING, pady=PADDING, fill=tk.BOTH, expand=True)

# Video frame with border
video_container = tk.Frame(left_frame, bg=ACCENT_COLOR, padx=2, pady=2)
video_container.pack(padx=PADDING, pady=PADDING, expand=True)
video_frame = tk.Label(video_container)
video_frame.pack(expand=True)

# Status section
status_frame = tk.Frame(right_frame, bg=BG_COLOR)
status_frame.pack(fill=tk.X, padx=PADDING*2, pady=PADDING)

gesture_label = tk.Label(
    status_frame,
    text="Waiting for gesture...",
    font=("Helvetica", 16),
    bg=BG_COLOR,
    fg=PRIMARY_COLOR,
    pady=5,
    wraplength=300  # Allow text to wrap
)
gesture_label.pack(fill=tk.X)

predicted_floor_label = tk.Label(
    status_frame,
    text="Predicted Floor: 0",
    font=("Helvetica", 16, "bold"),
    bg=BG_COLOR,
    fg=ACCENT_COLOR,
    pady=5,
    wraplength=300
)
predicted_floor_label.pack(fill=tk.X)

floor_label = tk.Label(
    status_frame,
    text="Current Floor: 0",
    font=("Helvetica", 16),
    bg=BG_COLOR,
    fg=PRIMARY_COLOR,
    pady=5,
    wraplength=300
)
floor_label.pack(fill=tk.X)

# Instructions section with controlled size and better alignment
instructions_frame = tk.Frame(
    right_frame,
    bg=BG_COLOR,
    relief=tk.GROOVE,
    borderwidth=2,
    width=400,  # Increased width
    height=300  # Increased height
)
instructions_frame.pack(fill=tk.X, padx=PADDING*2, pady=PADDING)
instructions_frame.pack_propagate(False)

instructions_title = tk.Label(
    instructions_frame,
    text="Gesture Instructions",
    font=("Helvetica", 14, "bold"),
    bg=BG_COLOR,
    fg=PRIMARY_COLOR,
    pady=5
)
instructions_title.pack(anchor="n")

instruction_text = """
✌️   Victory (OK): Confirm floor selection
🖐️   All Fingers Up: +5 floors
👇   All Fingers Down: -5 floors
☝️   Index Up: +1 floor
👎   Index Down: -1 floor
"""

instructions_detail = tk.Label(
    instructions_frame,
    text=instruction_text,
    font=("Helvetica", 12),
    bg=BG_COLOR,
    fg=PRIMARY_COLOR,
    justify=tk.LEFT,
    anchor="w",
    wraplength=350,  # Added wraplength to prevent text cutoff
    padx=20,
    pady=10
)
instructions_detail.pack(fill=tk.BOTH, anchor="w", expand=True)


class Hand:
    """Class to handle hand landmark detection and gesture recognition."""
    
    def __init__(self, hand_landmarks, margin):
        self.hand_landmarks = hand_landmarks
        self.margin = margin
        self.wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]

    def finger_pointing(self, finger_name, direction):
        """Determine if a finger is pointing in the specified direction."""
        finger_tip = self.hand_landmarks.landmark[getattr(mp_hands.HandLandmark, f"{finger_name}_TIP")]
        finger_dip = self.hand_landmarks.landmark[getattr(mp_hands.HandLandmark, f"{finger_name}_DIP")]
        finger_pip = self.hand_landmarks.landmark[getattr(mp_hands.HandLandmark, f"{finger_name}_PIP")]
        finger_mcp = self.hand_landmarks.landmark[getattr(mp_hands.HandLandmark, f"{finger_name}_MCP")]
        
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
        """Check if a specific finger is pointing up."""
        return self.finger_pointing(finger_name, 'up')

    def finger_down(self, finger_name):
        """Check if a specific finger is pointing down."""
        return self.finger_pointing(finger_name, 'down')

    def all_fingers_up_except_thumb(self):
        """Check if all fingers except thumb are pointing up."""
        return (self.finger_up('INDEX_FINGER') and
                self.finger_up('MIDDLE_FINGER') and
                self.finger_up('RING_FINGER') and
                self.finger_up('PINKY'))

    def all_fingers_down_except_thumb(self):
        """Check if all fingers except thumb are pointing down."""
        return (self.finger_down('INDEX_FINGER') and
                self.finger_down('MIDDLE_FINGER') and
                self.finger_down('RING_FINGER') and
                self.finger_down('PINKY'))

    def victory_gesture(self):
        """Check if hand is making a victory gesture."""
        return (self.finger_up('INDEX_FINGER') and
                self.finger_up('MIDDLE_FINGER') and
                not self.finger_up('RING_FINGER') and
                not self.finger_up('PINKY'))


def recognize_gesture(hand_landmarks):
    """Recognize the current hand gesture."""
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


def update_frame():
    """Update the video frame and process hand gestures."""
    global gesture_counter, initializing, initial_victory_counter, current_floor, predicted_floor, last_n_gestures

    success, image = cap.read()
    if not success:
        return

    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
    results = hands.process(image)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
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
                    pygame.mixer.music.load('initialize.mp3')
                    pygame.mixer.music.play()

                gesture_label.config(text="Show Victory Gesture to Start")
                break

            last_n_gestures.append(gesture)
            if len(last_n_gestures) > n:
                last_n_gestures.pop(0)

            # Process gestures and update counters
            if last_n_gestures.count("All Fingers Pointing Up") == n:
                gesture_counter += 5
                pygame.mixer.music.load('Floor_changing.mp3')
                pygame.mixer.music.play()
                last_n_gestures.clear()
            
            elif last_n_gestures.count("All Fingers Pointing Down") == n:
                gesture_counter -= 5
                pygame.mixer.music.load('Floor_changing.mp3')
                pygame.mixer.music.play()
                last_n_gestures.clear()
            
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
            
            elif last_n_gestures.count("Victory (OK)") == n:
                current_floor += gesture_counter
                gesture_counter = 0
                initializing = True
                pygame.mixer.music.load('initialize.mp3')
                pygame.mixer.music.play()
                last_n_gestures.clear()

            # Update display
            predicted_floor = current_floor + gesture_counter
            gesture_label.config(text=f"Current Gesture: {gesture}")
            # counter_label.config(text=f"Counter: {gesture_counter}")
            floor_label.config(text=f"Current Floor: {current_floor}")
            predicted_floor_label.config(text=f"Predicted Floor: {predicted_floor}")

    # Update video display
    img = Image.fromarray(image)
    imgtk = ImageTk.PhotoImage(image=img)
    video_frame.imgtk = imgtk
    video_frame.configure(image=imgtk)
    
    root.after(10, update_frame)


# Start the application
update_frame()
root.mainloop()

# Clean up resources
cap.release()
cv2.destroyAllWindows() 