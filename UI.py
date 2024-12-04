import tkinter as tk
from PIL import Image, ImageTk

class ElevatorUI:
    def __init__(self):
        # Constants
        self.PADDING = 10
        self.BG_COLOR = "#f8f9fa"
        self.PRIMARY_COLOR = "#343a40"
        self.ACCENT_COLOR = "#007bff"
        self.GESTURE_ACTIVE_COLOR_UP = "#28a745"  # Green color for gesture active state (floor going up)
        self.GESTURE_ACTIVE_COLOR_DOWN = "#dc3545"  # Red color for gesture active state (floor going down)
        self.GESTURE_ACTIVE_COLOR_EXTRA = "#ffc107"  # Yellow color for extra gesture active state
        self.INITIALIZING_TEXT_COLOR = "#ff8c00"  # Orange color for initializing message
        
        self.INSTRUCTIONS = [
            "Victory Sign (✌️): Initialize/Confirm floor selection",
            "Index Finger Up (☝️): Add 1 floor",
            "Index Finger Down (🖐): Subtract 1 floor",
            "Whole Hand Up (🖐): Add 10 floors",
            "Whole Hand Down (✋): Subtract 10 floors",
            "Note: Hold gesture steady for a moment to register"
        ]
        
        # Add initialization state
        self.is_initialized = False
        self.floor_selected = False
        
        # Initialize window
        self.root = tk.Tk()
        self.root.title("Gesture Recognition Elevator UI")
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

        # Floor label
        self.floor_label = tk.Label(
            floor_display_frame,
            text="Current Floor: 0",
            font=("Helvetica", 24, "bold"),
            bg=self.BG_COLOR,
            fg=self.PRIMARY_COLOR,
        )
        self.floor_label.pack(pady=(0, 5))

        # Predicted floor label - made it less prominent
        self.predicted_floor_label = tk.Label(
            floor_display_frame,
            text="Predicted Floor: 0",
            font=("Helvetica", 18),
            bg=self.BG_COLOR,
            fg=self.ACCENT_COLOR,
        )
        self.predicted_floor_label.pack()

    def _setup_video_and_instructions(self):
        container = tk.Frame(self.main_frame, bg=self.BG_COLOR)
        container.pack(expand=True, fill=tk.BOTH)

        # Video frame - improved style
        self.video_container = tk.Frame(
            container,
            highlightbackground=self.ACCENT_COLOR,
            highlightthickness=2,
            bg=self.BG_COLOR
        )
        self.video_container.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=(0, self.PADDING))
        self.video_frame = tk.Label(self.video_container)
        self.video_frame.pack(expand=True, padx=self.PADDING, pady=self.PADDING)

        # Overlay text on video frame for initialization instructions
        self.overlay_label = tk.Label(
            self.video_frame,
            text="",
            font=("Helvetica", 24, "bold"),
            bg=self.BG_COLOR,
            fg=self.INITIALIZING_TEXT_COLOR
        )
        self.overlay_label.place(relx=0.5, rely=0.1, anchor=tk.CENTER)

        # Instructions frame
        self.INSTRUCTIONS_frame = self._setup_instructions(container)

    def _setup_instructions(self, parent):
        self.INSTRUCTIONS_frame = tk.Frame(
            parent,
            bg=self.BG_COLOR,
            relief=tk.RIDGE,
            borderwidth=3,
            width=250
        )
        # Don't pack the frame initially
        self.INSTRUCTIONS_frame.pack_propagate(False)

        self.INSTRUCTIONS_title = tk.Label(
            self.INSTRUCTIONS_frame,
            text="Instructions",
            font=("Helvetica", 16, "bold"),
            bg=self.BG_COLOR,
            fg=self.PRIMARY_COLOR,
        )
        self.INSTRUCTIONS_title.pack(pady=(10, 5))

        # Create separate frames for each instruction
        for instruction in self.INSTRUCTIONS:
            instruction_frame = tk.Frame(
                self.INSTRUCTIONS_frame,
                bg=self.BG_COLOR,
                relief=tk.RIDGE,
                borderwidth=1
            )
            instruction_frame.pack(fill=tk.X, padx=10, pady=5)

            instruction_label = tk.Label(
                instruction_frame,
                text=instruction,
                font=("Arial", 14),
                bg=self.BG_COLOR,
                fg="#2c3e50",
                wraplength=200,
                anchor=tk.W,
                justify=tk.LEFT
            )
            instruction_label.pack(fill=tk.X, padx=5, pady=5)

        return self.INSTRUCTIONS_frame

    def _setup_status_frame(self):
        status_frame = tk.Frame(self.main_frame, bg=self.BG_COLOR)
        status_frame.pack(fill=tk.X, pady=self.PADDING)


    def update_video(self, image, initializing=False):
        """Update the video frame with a new image, add initialization message if initializing"""
        img = Image.fromarray(image)
        imgtk = ImageTk.PhotoImage(image=img)
        self.video_frame.imgtk = imgtk
        self.video_frame.configure(image=imgtk)

        # Hide instructions during initialization
        if initializing:
            self.hide_instructions()

    def update_floor_display(self, current_floor, predicted_floor):
        """Update the floor display labels"""
        self.floor_label.config(text=f"Current Floor: {current_floor}")
        self.predicted_floor_label.config(text=f"Predicted Floor: {predicted_floor}")
        
        # Reset floor_selected when starting a new selection
        if current_floor != predicted_floor:
            self.floor_selected = False
        
        # Hide instructions when a floor selection is confirmed
        if current_floor != 0 and predicted_floor == current_floor:
            self.floor_selected = True
            self.hide_instructions()

    def update_gesture_label(self, text, gesture_active=False, going_down=False, initializing=False, extra_gesture=False):
        """Update the gesture label text, change video border color, and update instructions if initializing"""
        self.gesture_label.config(text=text)
        if gesture_active:
            if extra_gesture:
                self.video_container.config(highlightbackground=self.GESTURE_ACTIVE_COLOR_EXTRA)
            elif going_down:
                self.video_container.config(highlightbackground=self.GESTURE_ACTIVE_COLOR_DOWN)
            else:
                self.video_container.config(highlightbackground=self.GESTURE_ACTIVE_COLOR_UP)
        else:
            self.video_container.config(highlightbackground=self.ACCENT_COLOR)

        # Hide instructions during initialization
        if initializing:
            self.hide_instructions()

    def start(self, update_callback):
        self.root.after(10, update_callback)
        self.root.mainloop()

    def show_instructions(self):
        self.INSTRUCTIONS_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(self.PADDING, 0))

    def hide_instructions(self):
        self.INSTRUCTIONS_frame.pack_forget()
