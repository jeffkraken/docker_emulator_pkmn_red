from flask import Flask, render_template, request
from flask_socketio import SocketIO
from emulator import Emulator
from keymap import KeyMapper
import base64
import cv2
import time
import os

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

ROM_PATH = "/roms/pokemon_red.gb"

emulator = Emulator(ROM_PATH)
keymapper = KeyMapper()


def stream_frames():
    while True:
        frame = emulator.get_frame()
        if frame is not None:
            _, buffer = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
            socketio.emit(
                "frame",
                base64.b64encode(buffer).decode("utf-8")
            )
        time.sleep(1/30)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/set_keymap", methods=["POST"])
def set_keymap():
    data = request.json or {}
    keymapper.set_custom_mapping(data)
    return {"status": "ok"}


@socketio.on("key_event")
def key_event(data):
    key = data["key"]
    event_type = data["type"]
    action = keymapper.translate(key)
    if action:
        emulator.handle_input(action, event_type)

@socketio.on("release_all")
def release_all():
    emulator.release_all()


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
    socketio.start_background_task(emulator.start)
    socketio.start_background_task(stream_frames)
    socketio.run(app, host="0.0.0.0", port=8080)
