import os

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
KEY_DIR = os.path.join(os.path.dirname(__file__), "keys")
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(KEY_DIR, exist_ok=True)
