import mediapipe as mp

mp_hands = mp.solutions.hands

#This class gets the cooadinations of each finger check wether or not that finger is poiting and if pointing up or down
# our gestures is based around how many fingers are up or down
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
