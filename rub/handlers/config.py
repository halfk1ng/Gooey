import json

def load_config(path):
    with open(path) as f:
        data = json.load(f)

    return data
