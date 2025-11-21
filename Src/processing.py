import os
import json
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


class ImageProcessor:
    def __init__(self):
        self.history_file = "forge_history.json"
        self.history = self._load_history()

    def load(self, path: str) -> Image.Image:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Файл не найден: {path}")
        img = Image.open(path).convert("RGB")
        img.format = Image.open(path).format
        logging.info(f"Загружено: {path}")
        return img

    def get_info(self, img: Image.Image) -> dict:
        return {
            "w": img.width,
            "h": img.height,
            "format": img.format or "Unknown",
            "mode": img.mode
        }

    def transform(self, img: Image.Image, size: Optional[Tuple[int, int]],
                  sharpen: bool, contour: bool) -> Image.Image:
        result = img.copy()

        if size and size != img.size:
            result = result.resize(size, Image.LANCZOS)
            logging.info(f"Resize → {size}")

        if sharpen:
            result = result.filter(ImageFilter.SHARPEN)
        if contour:
            result = result.filter(ImageFilter.CONTOUR)

        return result

    def save(self, img: Image.Image, path: str):
        img.save(path)
        logging.info(f"Сохранено: {path}")

    def log_action(self, action: str, details=None):
        entry = {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "action": action,
            "data": details or {}
        }
        self.history.append(entry)
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(self.history, f, indent=2, ensure_ascii=False)

    def _load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return []
        return []