const socket = io();

const canvas = document.getElementById("screen");
const ctx = canvas.getContext("2d");

canvas.focus();

canvas.addEventListener("click", () => {canvas.focus();});

ctx.imageSmoothingEnabled = false;

socket.on("frame", (data) => {
    const img = new Image();
    img.onload = () => ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
    img.src = "data:image/png;base64," + data;
});

function normalizeKey(key) {
    return key.toLowerCase();
}

canvas.addEventListener("keydown", (e) => {
    if (["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight", " "].includes(e.key)) {
        e.preventDefault();
    }

    socket.emit("key_event", {
        key: normalizeKey(e.key),
        type: "down"
    });
});

canvas.addEventListener("keyup", (e) => {
    socket.emit("key_event", {
        key: normalizeKey(e.key),
        type: "up"
    });
});

window.addEventListener("blur", () => {
    socket.emit("release_all");
});

document.getElementById("save").onclick = async () => {
    await fetch("/save", { method: "POST" });
    console.log("Game saved");
};

document.getElementById("load").onclick = async () => {
    await fetch("/load", { method: "POST" });
    console.log("Game loaded");
};

const keymapPanel = document.getElementById("keymap-panel");
const keymapRows = document.getElementById("keymap-rows");
const saveKeymapBtn = document.getElementById("save-keymap");
const resetKeymapBtn = document.getElementById("reset-keymap");
const closeKeymapBtn = document.getElementById("close-keymap");
const keymapStatus = document.getElementById("keymap-status");
const remapButton = document.getElementById("remap");

let currentMapping = {
    "arrowup": "UP",
    "arrowdown": "DOWN",
    "arrowleft": "LEFT",
    "arrowright": "RIGHT",
    "z": "A",
    "x": "B",
    "enter": "START",
    "shift": "SELECT"
};

let waitingForKey = null;

function formatKey(key) {
    const specialKeys = {
        "arrowup": "ArrowUp",
        "arrowdown": "ArrowDown",
        "arrowleft": "ArrowLeft",
        "arrowright": "ArrowRight",
        "enter": "Enter",
        "shift": "Shift"
    };
    return specialKeys[key] || key;
}

remapButton.onclick = () => {
    keymapPanel.style.display = "block";
    populateKeymapRows();
    keymapStatus.textContent = "";
};

closeKeymapBtn.onclick = () => {
    keymapPanel.style.display = "none";
    waitingForKey = null;
};

function populateKeymapRows() {
    keymapRows.innerHTML = "";
    Object.entries(currentMapping).forEach(([key, action]) => {
        const row = document.createElement("div");
        row.classList.add("keymap-row");

        const label = document.createElement("span");
        label.textContent = `${action}: `;

        const button = document.createElement("button");
        button.textContent = formatKey(key);
        button.tabIndex = 0;

        button.onclick = () => {
            waitingForKey = key;
            button.textContent = "Press new key...";
            keymapStatus.textContent = "Press any key to remap...";
        };

        row.appendChild(label);
        row.appendChild(button);
        keymapRows.appendChild(row);
    });
}

document.addEventListener("keydown", (e) => {
    if (!waitingForKey) return;

    e.stopPropagation();
    e.preventDefault();

    const oldKey = normalizeKey(waitingForKey);
    const newKey = normalizeKey(e.key);
    const action = currentMapping[oldKey];

    if (!action) {
        waitingForKey = null;
        return;
    }

    delete currentMapping[oldKey];

    if (currentMapping[newKey]) {
        keymapStatus.textContent = `"${formatKey(newKey)}" was already assigned to ${currentMapping[newKey]}, overriding.`;
        delete currentMapping[newKey];
    }

    currentMapping[newKey] = action;
    waitingForKey = null;
    populateKeymapRows();
    keymapStatus.textContent = `Mapped "${formatKey(newKey)}" to ${action}`;
});

saveKeymapBtn.onclick = async () => {
    const normalizedMapping = {};
    for (const [key, action] of Object.entries(currentMapping)) {
        normalizedMapping[key.toLowerCase()] = action;
    }
    const resp = await fetch("/set_keymap", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(normalizedMapping),
    });
    keymapStatus.textContent = resp.ok ? "Keymap saved!" : "Error saving keymap.";
};

resetKeymapBtn.onclick = async () => {
    currentMapping = {
        "arrowup": "UP",
        "arrowdown": "DOWN",
        "arrowleft": "LEFT",
        "arrowright": "RIGHT",
        "z": "A",
        "x": "B",
        "enter": "START",
        "shift": "SELECT"
    };
    populateKeymapRows();
    keymapStatus.textContent = "Reset to default mapping.";

    await fetch("/set_keymap", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
    });
};

socket.on("connect", () => console.log("Connected to emulator server"));
socket.on("disconnect", () => console.log("Disconnected from emulator server"));
