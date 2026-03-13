import threading
from pyboy import PyBoy
from pyboy.utils import WindowEvent

class Emulator:

    def __init__(self, rom_path):
        self.rom_path = rom_path
        self.running = False
        self.pyboy = None
        self.lock = threading.Lock()

        self.latest_frame = None

        self.pressed_buttons = set()

        self.input_press_map = {
            "UP": WindowEvent.PRESS_ARROW_UP,
            "DOWN": WindowEvent.PRESS_ARROW_DOWN,
            "LEFT": WindowEvent.PRESS_ARROW_LEFT,
            "RIGHT": WindowEvent.PRESS_ARROW_RIGHT,
            "A": WindowEvent.PRESS_BUTTON_A,
            "B": WindowEvent.PRESS_BUTTON_B,
            "START": WindowEvent.PRESS_BUTTON_START,
            "SELECT": WindowEvent.PRESS_BUTTON_SELECT,
        }

        self.input_release_map = {
            "UP": WindowEvent.RELEASE_ARROW_UP,
            "DOWN": WindowEvent.RELEASE_ARROW_DOWN,
            "LEFT": WindowEvent.RELEASE_ARROW_LEFT,
            "RIGHT": WindowEvent.RELEASE_ARROW_RIGHT,
            "A": WindowEvent.RELEASE_BUTTON_A,
            "B": WindowEvent.RELEASE_BUTTON_B,
            "START": WindowEvent.RELEASE_BUTTON_START,
            "SELECT": WindowEvent.RELEASE_BUTTON_SELECT,
        }

    def start(self):
        """Initialize PyBoy and start the emulator thread."""
        self.pyboy = PyBoy(self.rom_path, window="null")
        t = threading.Thread(target=self.run, daemon=True)
        self.running = True
        t.start()

    def run(self):
        """Main loop: tick the emulator and update latest_frame."""
        print(f"Loaded GameBoy ROM: {self.rom_path}")

        while self.running:
            self.pyboy.tick()
            with self.lock:
                self.latest_frame = self.pyboy.screen.ndarray.copy()

    def handle_input(self, action, event_type="down"):
        """Handle a key press or release event."""
        if not action:
            return

        if event_type == "down":
            event = self.input_press_map.get(action)
            if event:
                self.pyboy.send_input(event)
                self.pressed_buttons.add(action)
        elif event_type == "up":
            if action in self.pressed_buttons:
                event = self.input_release_map.get(action)
                if event:
                    self.pyboy.send_input(event)
                self.pressed_buttons.discard(action)

    def get_frame(self):
        """Return the latest frame as a NumPy array."""
        with self.lock:
            if self.latest_frame is not None:
                return self.latest_frame.copy()
            return None

    def release_all(self):
        """Release all currently pressed buttons."""
        for action in list(self.pressed_buttons):
            event = self.input_release_map.get(action)
            if event:
                self.pyboy.send_input(event)
            self.pressed_buttons.discard(action)