from flask import Flask, render_template, request
from flask_socketio import SocketIO
from emulator import Emulator
from keymap import KeyMapper
import base64
import cv2
import numpy as np
import time
import os

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

ROM_PATH = os.path.join(os.path.dirname(__file__), "..", "roms", "pokemon_red.gb")
emulator = Emulator(ROM_PATH)

def stream_frames():

    while True:

        frame = emulator.get_frame()

        if frame is not None:

            _, buffer = cv2.imencode(".png", frame)

            socketio.emit(
                "frame",
                base64.b64encode(buffer).decode("utf-8")
            )

        time.sleep(1/60)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/set_keymap", methods=["POST"])
def set_keymap():
    data = request.json
    keymapper.set_custom_mapping(data)
    return {"status": "ok"}

@socketio.on("key_event")
def key_event(data):
    key = data["key"]
    action = keymapper.translate(key)
    emulator.handle_input(action)

@app.route("/save", methods=["POST"])
def save():
    emulator.save_state()
    return {"status": "saved"}


@app.route("/load", methods=["POST"])
def load():
    emulator.load_state()
    return {"status": "loaded"}

@socketio.on("connect")
def on_connect():
    print("Client connected")

@socketio.on("disconnect")
def on_disconnect():
    print("Client disconnected")

if __name__ == "__main__":
    emulator.start()
    socketio.start_background_task(stream_frames)
    socketio.run(app, host="0.0.0.0", port=8080, allow_unsafe_werkzueg=True)
