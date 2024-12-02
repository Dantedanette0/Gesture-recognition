import pygame
from hand import Hand

class GestureHandler:
    def __init__(self, margin):
        self.margin = margin
        self.gesture_counter = 0
        self.initial_victory_counter = 0
        self.initializing = True
        self.current_floor = 0

        # Gesture data definitions   (name of the sign - number of frames that is has to remain active for the program to accept it 
        # - numbers of floors it changes each time you detect it - wether or not it can change the current floor)
        self.victory_gesture_data = self.handle_gesture_counter("Victory (OK)", 30, 0, update_floor=True)
        self.all_fingers_up_data = self.handle_gesture_counter("All Fingers Pointing Up", 20, 10)
        self.all_fingers_down_data = self.handle_gesture_counter("All Fingers Pointing Down", 20, -10)
        self.index_finger_up_data = self.handle_gesture_counter("Index Finger Pointing Up", 15, 1)
        self.index_finger_down_data = self.handle_gesture_counter("Index Finger Pointing Down", 15, -1)

    #This has to recognize gestures in this order otherwise the app will break DO NOT TOUCH
    def recognize_gesture(self, hand_landmarks):
        hand = Hand(hand_landmarks, self.margin)

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

    def play_audio(self, file_name):
        try:
            pygame.mixer.music.load(file_name)
            pygame.mixer.music.play()
        except pygame.error as e:
            print(f"Error playing audio: {e}")

    def handle_gesture_counter(self, gesture_name, threshold, increment, update_floor=False):
        return {
            "gesture_list": [],
            "gesture_name": gesture_name,
            "threshold": threshold,
            "increment": increment,
            "update_floor": update_floor
        }

    def handle_gesture(self, gesture, gesture_data, audio_file):
        gesture_list = gesture_data['gesture_list']
        gesture_name = gesture_data['gesture_name']
        threshold = gesture_data['threshold']
        increment = gesture_data['increment']
        update_floor = gesture_data['update_floor']

        # as long as we can detect the gesture for each frame append to this list if it goes above threshold (speed) then we confirm its detection
        gesture_list.append(gesture_name)
        if len(gesture_list) > threshold:
            gesture_list.pop(0)

        # as long as we hit the threshold play its audio and increment gesture counter once done update floor if the gesture lets you change it.
        # If floor is changed it means elevator has moved and once again we need confirmation
        if gesture_list.count(gesture_name) == threshold:
            if update_floor:
                self.current_floor += self.gesture_counter
                self.gesture_counter = 0
                self.initializing = True
            else:
                self.gesture_counter += increment
            self.play_audio(audio_file)
            gesture_list.clear()

    # the intilize state of the app is different thats why we handle this particular gesture a bit differently (it opens and closes the gesture logic rules)
    def handle_initializing(self, gesture):

        if gesture == "Victory (OK)":
            self.initial_victory_counter += 1
        else:
            self.initial_victory_counter = 0

        if self.initial_victory_counter >= 30:
            self.initializing = False
            self.initial_victory_counter = 0
            self.current_floor += self.gesture_counter
            self.play_audio('initialize.mp3')
