import tkinter as tk
from PIL import Image, ImageTk

class ElevatorUI:
    def __init__(self):
        # Constants
        self.PADDING = 10
        self.BG_COLOR = "#f0f0f0"
        self.PRIMARY_COLOR = "#2c3e50"
        self.ACCENT_COLOR = "#3498db"
        
        self.instruction_text = """
        Gestures:
        • Victory Sign (✌️) - Initialize/Confirm floor selection
        • All fingers up (✋) - Add 5 floors
        • All fingers down (🤚) - Subtract 5 floors
        • Index finger up (☝️) - Add 1 floor
        • Index finger down (👇) - Subtract 1 floor

        Hold gesture steady for a moment to register.
        """
        
        # Initialize window
        self.root = tk.Tk()
        self.root.title("Gesture Recognition")
        self.root.configure(bg=self.BG_COLOR)
        self.root.geometry("1024x768")
        self.root.minsize(800, 600)
        
        self._setup_ui()
    
    def _setup_ui(self):
        # Main frame
        self.main_frame = tk.Frame(self.root, bg=self.BG_COLOR)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=self.PADDING, pady=self.PADDING)

        # Floor display frame
        self._setup_floor_display()
        
        # Video and instructions container
        self._setup_video_and_instructions()
        
        # Status frame
        self._setup_status_frame()

    def _setup_floor_display(self):
        floor_display_frame = tk.Frame(self.main_frame, bg=self.BG_COLOR)
        floor_display_frame.pack(fill=tk.X, pady=(0, self.PADDING))

        self.floor_label = tk.Label(
            floor_display_frame,
            text="Current Floor: 0",
            font=("Helvetica", 20, "bold"),
            bg=self.BG_COLOR,
            fg=self.PRIMARY_COLOR,
        )
        self.floor_label.pack()

        self.predicted_floor_label = tk.Label(
            floor_display_frame,
            text="Predicted Floor: 0",
            font=("Helvetica", 20, "bold"),
            bg=self.BG_COLOR,
            fg=self.ACCENT_COLOR,
        )
        self.predicted_floor_label.pack()

    def _setup_video_and_instructions(self):
        container = tk.Frame(self.main_frame, bg=self.BG_COLOR)
        container.pack(expand=True, fill=tk.BOTH)

        # Video frame - removed background color, added border
        video_container = tk.Frame(container, highlightbackground=self.ACCENT_COLOR, 
                                 highlightthickness=2, bg=self.BG_COLOR)
        video_container.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        self.video_frame = tk.Label(video_container)
        self.video_frame.pack(expand=True)

        # Instructions frame
        self._setup_instructions(container)

    def _setup_instructions(self, parent):
        instructions_frame = tk.Frame(
            parent,
            bg=self.BG_COLOR,
            relief=tk.GROOVE,
            borderwidth=2,
            width=200
        )
        instructions_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(self.PADDING, 0))
        instructions_frame.pack_propagate(False)

        instructions_title = tk.Label(
            instructions_frame,
            text="Instructions",
            font=("Helvetica", 14, "bold"),
            bg=self.BG_COLOR,
            fg=self.PRIMARY_COLOR,
        )
        instructions_title.pack(pady=(5, 0))

        instructions_detail = tk.Label(
            instructions_frame,
            text=self.instruction_text,
            font=("Helvetica", 10),
            bg=self.BG_COLOR,
            fg=self.PRIMARY_COLOR,
            justify=tk.LEFT,
            wraplength=180
        )
        instructions_detail.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

    def _setup_status_frame(self):
        status_frame = tk.Frame(self.main_frame, bg=self.BG_COLOR)
        status_frame.pack(fill=tk.X, pady=self.PADDING)

        status_label = tk.Label(
            status_frame,
            text="Status",
            font=("Helvetica", 16, "bold"),
            bg=self.BG_COLOR,
            fg=self.PRIMARY_COLOR,
        )
        status_label.pack()

        self.gesture_label = tk.Label(
            status_frame,
            text="Waiting for gesture...",
            font=("Helvetica", 14),
            bg=self.BG_COLOR,
            fg=self.PRIMARY_COLOR,
        )
        self.gesture_label.pack()

    def update_video(self, image):
        """Update the video frame with a new image"""
        img = Image.fromarray(image)
        imgtk = ImageTk.PhotoImage(image=img)
        self.video_frame.imgtk = imgtk
        self.video_frame.configure(image=imgtk)

    def update_floor_display(self, current_floor, predicted_floor):
        """Update the floor display labels"""
        self.floor_label.config(text=f"Current Floor: {current_floor}")
        self.predicted_floor_label.config(text=f"Predicted Floor: {predicted_floor}")

    def update_gesture_label(self, text):
        """Update the gesture label text"""
        self.gesture_label.config(text=text)

    def start(self, update_callback):
        """Start the UI with the given update callback"""
        self.root.after(10, update_callback)
        self.root.mainloop()