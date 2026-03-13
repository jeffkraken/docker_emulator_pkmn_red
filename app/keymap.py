VALID_ACTIONS = {
    "UP","DOWN","LEFT","RIGHT",
    "A","B","START","SELECT"
}

class KeyMapper:

    def __init__(self, custom_map=None):

        self.default_map = {
            "arrowup": "UP",
            "arrowdown": "DOWN",
            "arrowleft": "LEFT",
            "arrowright": "RIGHT",
            "z": "A",
            "x": "B",
            "enter": "START",
            "shift": "SELECT"
        }

        self.custom_map = custom_map or {}

    def set_custom_mapping(self, mapping):

        self.custom_map = {
            k.lower(): v
            for k, v in mapping.items()
            if v in VALID_ACTIONS
        }

    def translate(self, key):

        key = key.lower()

        if key in self.custom_map:
            return self.custom_map[key]

        return self.default_map.get(key)

    def reset_custom_mapping(self):
        self.custom_map = {}

    def get_mapping(self):
        return {**self.default_map, **self.custom_map}