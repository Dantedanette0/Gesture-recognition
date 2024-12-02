import tkinter as tk

def setup_ui():
    # Tkinter initialization
    root = tk.Tk()
    root.title("Gesture Recognition")
    root.geometry("800x600")

    # Create canvas for video feed
    canvas = tk.Canvas(root, width=640, height=480)
    canvas.pack()

    # Gesture Counter Label
    gesture_label = tk.Label(root, text=f"Gesture Counter: 0", font=("Helvetica", 16))
    gesture_label.pack()

    # Current Floor Label
    current_floor_label = tk.Label(root, text=f"Current Floor: 0", font=("Helvetica", 16))
    current_floor_label.pack()

    return root, canvas, gesture_label, current_floor_label
