import threading
from pyboy import PyBoy
from pyboy.utils import WindowEvent


class Emulator:

    def __init__(self, rom_path):
        self.rom_path = rom_path
        self.running = False
        self.pyboy = None

        # Map abstract actions to PyBoy events
        self.input_map = {
            "UP": WindowEvent.PRESS_ARROW_UP,
            "DOWN": WindowEvent.PRESS_ARROW_DOWN,
            "LEFT": WindowEvent.PRESS_ARROW_LEFT,
            "RIGHT": WindowEvent.PRESS_ARROW_RIGHT,
            "A": WindowEvent.PRESS_BUTTON_A,
            "B": WindowEvent.PRESS_BUTTON_B,
            "START": WindowEvent.PRESS_BUTTON_START,
            "SELECT": WindowEvent.PRESS_BUTTON_SELECT,
        }

    def start(self):
        self.pyboy = PyBoy(self.rom_path, window="null")

        t = threading.Thread(target=self.run)
        t.daemon = True
        self.running = True
        t.start()

    def run(self):
        print(f"Loaded GameBoy ROM: {self.rom_path}")

        while self.running:
            self.pyboy.tick()

    def handle_input(self, action):

        if action not in self.input_map:
            return

        event = self.input_map[action]
        self.pyboy.send_input(event)
    
    def get_frame(self):
        if not self.pyboy:
            return None
        frame = self.pyboy.screen.ndarray
        return frame