import os
import re

def safe_filename(name: str) -> str:
    if not name:
        return "file"
    name = name.replace(":", "-").replace("|", "").replace("/", "-")
    name = re.sub(r'[<>\"\\?*]', '', name)
    return name.strip()

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)
