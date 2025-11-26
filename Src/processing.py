


import os
import json
import time
import logging
from datetime import datetime
from PIL import Image, ImageFilter
from typing import Optional, Tuple


os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/forge.log",
    level=logging.INFO,
    format="%(asctime)s | %(message)s",
    encoding="utf-8"
)

def measure_time(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} выполнена за {(end-start)*1000:.2f}ms")
        return result
    return wrapper

class ImageProcessor:

    def __init__(self):
        self.history_file = "forge_history.json"
        self.history = self._load_history()

    @measure_time
    def load(self, path: str) -> Image.Image:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Файл не найден: {path}")
        img = Image.open(path).convert("RGB")
        img.format = Image.open(path).format
        logging.info(f"Загружено: {path}")
        return img

    @measure_time 
    def get_info(self, img: Image.Image) -> dict:
        return {
            "w": img.width,
            "h": img.height,
            "format": img.format or "Unknown",
            "mode": img.mode
        }

    @measure_time
    def transform(self, img: Image.Image, size: Optional[Tuple[int, int]],
                  sharpen: bool, contour: bool) -> Image.Image:
        result = img.copy()

        if size and size != img.size:
            result = result.resize(size, Image.LANCZOS)
            logging.info(f"Resize - {size}")

        if sharpen:
            result = result.filter(ImageFilter.SHARPEN)
        if contour:
            result = result.filter(ImageFilter.CONTOUR)

        return result

    @measure_time
    def save(self, img: Image.Image, path: str):
        img.save(path)
        logging.info(f"Сохранено: {path}")

    @measure_time
    def log_action(self, action: str, details=None):
        entry = {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "action": action,
            "data": details or {}
        }
        self.history.append(entry)
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(self.history, f, indent=2, ensure_ascii=False)

    @measure_time
    def _load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return []
        return []