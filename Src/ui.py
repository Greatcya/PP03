


import os
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QSettings, QSize
from PIL.ImageQt import ImageQt
from processing import ImageProcessor


class ImageForgeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.processor = ImageProcessor()

        self.original_img = None
        self.processed_img = None
        self.last_version = None

        self.settings = QSettings("Mallenom", "ImageTool_1337")
        os.makedirs("output", exist_ok=True)

        self.setup_interface()
        self.connect_events()

    def setup_interface(self):
        self.setWindowTitle("Утилита обработки изображений - Практика Малленом Системс")
        self.resize(1400, 800)
        self.setAcceptDrops(True)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        toolbar = QHBoxLayout()
        toolbar.addWidget(self.create_btn("Открыть изображение", self.open_image))
        self.undo_btn = self.create_btn("Отменить", self.undo_last)
        self.undo_btn.setEnabled(False)
        toolbar.addWidget(self.undo_btn)
        toolbar.addWidget(self.create_btn("Сохранить как...", self.save_result))
        toolbar.addStretch()
        main_layout.addLayout(toolbar)

        content = QHBoxLayout()

        settings_box = QGroupBox("Параметры трансформации")
        settings_box.setFixedWidth(230)
        form = QFormLayout(settings_box)

        self.width_input = QSpinBox();  self.width_input.setRange(1, 20000);  self.width_input.setValue(1280)
        self.height_input = QSpinBox(); self.height_input.setRange(1, 20000); self.height_input.setValue(720)
        form.addRow("Ширина:", self.width_input)
        form.addRow("Высота:", self.height_input)

        self.sharpen_cb = QCheckBox("Увеличить резкость")
        self.contour_cb = QCheckBox("Выделить контуры")
        form.addRow(self.sharpen_cb)
        form.addRow(self.contour_cb)

        content.addWidget(settings_box)

        preview = QHBoxLayout()

        self.orig_view = QLabel("Исходное")
        self.orig_view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.orig_view.setMinimumSize(600, 480)
        self.orig_view.setStyleSheet("background: #0a0a0a; border: 2px dashed #333;")
        self.orig_view.setScaledContents(False)       
        preview.addWidget(self.wrap_label(self.orig_view, "Исходное"))

        self.result_view = QLabel("Обработанное")
        self.result_view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_view.setMinimumSize(600, 480)
        self.result_view.setStyleSheet("background: #0a0a0a; border: 2px dashed #333;")
        self.result_view.setScaledContents(False)
        preview.addWidget(self.wrap_label(self.result_view, "Обработанное"))

        content.addLayout(preview)
        main_layout.addLayout(content, stretch=1)

        self.status_bar = QLabel("Готов к работе | Перетащите изображение сюда")
        self.status_bar.setStyleSheet("background: #1e1e1e; color: #00ff00; padding: 10px; font: 10pt Consolas;")
        main_layout.addWidget(self.status_bar)

    def wrap_label(self, label: QLabel, title: str) -> QGroupBox:
        box = QGroupBox(title)
        box.setStyleSheet("QGroupBox { font-weight: bold; color: #00aaff; }")
        lay = QVBoxLayout(box)
        lay.addWidget(label)
        return box

    def create_btn(self, text, callback):
        btn = QPushButton(text)
        btn.setFixedHeight(40)
        btn.clicked.connect(callback)
        return btn

    def connect_events(self):
        self.width_input.valueChanged.connect(self.apply_effects)
        self.height_input.valueChanged.connect(self.apply_effects)
        self.sharpen_cb.stateChanged.connect(self.apply_effects)
        self.contour_cb.stateChanged.connect(self.apply_effects)

    def display(self, pil_img, label: QLabel):
        if pil_img is None:
            label.clear()
            label.setText("Нет изображения")
            return

        qimg = ImageQt(pil_img)
        pixmap = QPixmap.fromImage(qimg)

        label_size = label.size()
        if label_size.width() <= 0 or label_size.height() <= 0:
            target = QSize(600, 480)
        else:
            target = label_size

        scaled_pixmap = pixmap.scaled(
            target,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        label.setPixmap(scaled_pixmap)

    def open_image(self):
        last_dir = self.settings.value("last_dir", "")
        path, _ = QFileDialog.getOpenFileName(
            self, "Выбрать изображение", last_dir,
            "Images (*.png *.jpg *.jpeg *.bmp *.webp *.tiff)"
        )
        if path:
            self.load_image(path)

    def load_image(self, path):
        try:
            self.original_img = self.processor.load(path)
            self.display(self.original_img, self.orig_view)
            self.update_status()
            self.apply_effects()               
            self.settings.setValue("last_dir", os.path.dirname(path))
            self.processor.log_action("load", path)
            self.undo_btn.setEnabled(False)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить:\n{e}")

    def update_status(self):
        if not self.original_img:
            self.status_bar.setText("Нет изображения")
            return
        info = self.processor.get_info(self.original_img)
        text = f"Размер: {info['w']}×{info['h']} | Формат: {info['format']} | Режим: {info['mode']}"
        self.status_bar.setText(text)

        self.width_input.blockSignals(True)
        self.height_input.blockSignals(True)
        self.width_input.setValue(info['w'])
        self.height_input.setValue(info['h'])
        self.width_input.blockSignals(False)
        self.height_input.blockSignals(False)

    def apply_effects(self):
        if not self.original_img:
            return

        self.last_version = self.processed_img
        self.undo_btn.setEnabled(True)

        target_size = (self.width_input.value(), self.height_input.value())
        if target_size == self.original_img.size:
            target_size = None

        self.processed_img = self.processor.transform(
            self.original_img,
            target_size,
            self.sharpen_cb.isChecked(),
            self.contour_cb.isChecked()
        )
        self.display(self.processed_img, self.result_view)  

    def undo_last(self):
        if self.last_version:
            self.processed_img = self.last_version
            self.display(self.processed_img, self.result_view)
            self.width_input.setValue(self.last_version.width)
            self.height_input.setValue(self.last_version.height)
            self.last_version = None
            self.undo_btn.setEnabled(False)
            self.processor.log_action("undo")

    def save_result(self):
        if not self.processed_img:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить результат", "output/forge_result.png",
            "PNG (*.png);;JPEG (*.jpg *.jpeg)"
        )
        if path:
            self.processor.save(self.processed_img, path)
            self.processor.log_action("save", path)
            QMessageBox.information(self, "Готово", f"Сохранено:\n{path}")

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        path = event.mimeData().urls()[0].toLocalFile()
        if path.lower().split(".")[-1] in ["png", "jpg", "jpeg", "bmp", "webp", "tiff", "tif"]:
            self.load_image(path)