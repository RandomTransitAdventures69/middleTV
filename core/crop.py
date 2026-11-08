
from pathlib import Path

from PySide6.QtCore import Qt, QRect, QPoint, Signal
from PySide6.QtGui import QPixmap, QPainter
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QSlider,
    QMessageBox,
)


class CropWidget(QWidget):
    """
    MiddleTV profile-picture crop screen.

    Usage:

        crop = CropWidget(
            image_path="path/to/image.jpg",
            output_path="profiles/user-cropped.jpg"
        )

        crop.show()
    """

    cropSaved = Signal(str)
    cancelled = Signal()

    def __init__(
        self,
        image_path=None,
        output_path=None,
        parent=None
    ):

        super().__init__(parent)

        self.image_path = (
            Path(image_path)
            if image_path
            else None
        )

        self.output_path = (
            Path(output_path)
            if output_path
            else None
        )

        self.original_pixmap = QPixmap()

        self.zoom = 1.0

        self.setWindowTitle(
            "MiddleTV - Crop Picture"
        )

        self.setMinimumSize(
            900,
            650
        )

        self.setup_ui()

        if self.image_path:

            self.load_image(
                self.image_path
            )


    # -----------------------------------------------------
    # UI
    # -----------------------------------------------------

    def setup_ui(self):

        layout = QVBoxLayout()

        layout.setContentsMargins(
            40,
            30,
            40,
            30
        )

        layout.setSpacing(
            20
        )


        # Title

        title = QLabel(
            "Crop Profile Picture"
        )

        title.setAlignment(
            Qt.AlignCenter
        )

        title.setStyleSheet(
            """
            QLabel {
                color: white;
                font-size: 34px;
                font-weight: bold;
            }
            """
        )

        layout.addWidget(
            title
        )


        # Image preview

        self.preview = CropPreview(
            self
        )

        self.preview.setMinimumSize(
            500,
            400
        )

        layout.addWidget(
            self.preview,
            1
        )


        # Zoom label

        self.zoom_label = QLabel(
            "Zoom: 100%"
        )

        self.zoom_label.setAlignment(
            Qt.AlignCenter
        )

        self.zoom_label.setStyleSheet(
            """
            QLabel {
                color: white;
                font-size: 20px;
            }
            """
        )

        layout.addWidget(
            self.zoom_label
        )


        # Zoom slider

        self.zoom_slider = QSlider(
            Qt.Horizontal
        )

        self.zoom_slider.setMinimum(
            100
        )

        self.zoom_slider.setMaximum(
            300
        )

        self.zoom_slider.setValue(
            100
        )

        self.zoom_slider.setFocusPolicy(
            Qt.StrongFocus
        )

        self.zoom_slider.valueChanged.connect(
            self.change_zoom
        )

        layout.addWidget(
            self.zoom_slider
        )


        # Buttons

        buttons = QHBoxLayout()

        buttons.setSpacing(
            20
        )


        self.choose_button = QPushButton(
            "Choose Picture"
        )

        self.cancel_button = QPushButton(
            "Cancel"
        )

        self.save_button = QPushButton(
            "Save"
        )


        for button in (
            self.choose_button,
            self.cancel_button,
            self.save_button
        ):

            button.setMinimumHeight(
                60
            )

            button.setMinimumWidth(
                180
            )

            button.setFocusPolicy(
                Qt.StrongFocus
            )

            button.setStyleSheet(
                """
                QPushButton {
                    color: white;

                    background-color:
                        rgba(30, 30, 30, 220);

                    border:
                        2px solid
                        rgba(255, 255, 255, 60);

                    border-radius: 14px;

                    font-size: 20px;
                }

                QPushButton:hover {
                    background-color:
                        rgba(55, 55, 55, 230);

                    border:
                        2px solid
                        rgba(80, 170, 255, 220);
                }

                QPushButton:focus {
                    background-color:
                        rgba(50, 90, 140, 235);

                    border:
                        3px solid
                        rgba(80, 170, 255, 255);
                }
                """
            )


        self.choose_button.clicked.connect(
            self.choose_picture
        )

        self.cancel_button.clicked.connect(
            self.cancel
        )

        self.save_button.clicked.connect(
            self.save
        )


        buttons.addWidget(
            self.choose_button
        )

        buttons.addStretch()

        buttons.addWidget(
            self.cancel_button
        )

        buttons.addWidget(
            self.save_button
        )


        layout.addLayout(
            buttons
        )


        self.setLayout(
            layout
        )


        # Initial focus

        self.choose_button.setFocus()


    # -----------------------------------------------------
    # LOAD IMAGE
    # -----------------------------------------------------

    def load_image(
        self,
        path
    ):

        path = Path(
            path
        )


        if not path.exists():

            return False


        pixmap = QPixmap(
            str(path)
        )


        if pixmap.isNull():

            return False


        self.image_path = path

        self.original_pixmap = pixmap

        self.zoom = 1.0

        self.zoom_slider.blockSignals(
            True
        )

        self.zoom_slider.setValue(
            100
        )

        self.zoom_slider.blockSignals(
            False
        )

        self.zoom_label.setText(
            "Zoom: 100%"
        )


        self.preview.set_pixmap(
            pixmap
        )

        self.preview.set_zoom(
            self.zoom
        )

        self.preview.update()


        return True


    # -----------------------------------------------------
    # CHOOSE IMAGE
    # -----------------------------------------------------

    def choose_picture(self):

        path, _ = QFileDialog.getOpenFileName(
            self,
            "Choose Profile Picture",
            "",
            (
                "Images (*.png *.jpg *.jpeg "
                "*.webp *.bmp);;"
                "All Files (*)"
            )
        )


        if not path:

            return


        self.load_image(
            path
        )


    # -----------------------------------------------------
    # ZOOM
    # -----------------------------------------------------

    def change_zoom(
        self,
        value
    ):

        self.zoom = (
            value / 100.0
        )


        self.zoom_label.setText(
            f"Zoom: {value}%"
        )


        self.preview.set_zoom(
            self.zoom
        )


        self.preview.update()


    # -----------------------------------------------------
    # SAVE
    # -----------------------------------------------------

    def save(self):

        if self.original_pixmap.isNull():

            QMessageBox.warning(
                self,
                "No Picture",
                "Choose a picture first."
            )

            return


        if not self.output_path:

            path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Profile Picture",
                "",
                "PNG Image (*.png)"
            )


            if not path:

                return


            self.output_path = Path(
                path
            )


        cropped = (
            self.preview.get_crop(
                self.original_pixmap
            )
        )


        if cropped.isNull():

            QMessageBox.warning(
                self,
                "Crop Error",
                "The picture could not be cropped."
            )

            return


        self.output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )


        if not cropped.save(
            str(self.output_path),
            "PNG"
        ):

            QMessageBox.warning(
                self,
                "Save Error",
                "The cropped picture could not be saved."
            )

            return


        self.cropSaved.emit(
            str(self.output_path)
        )


        self.close()


    # -----------------------------------------------------
    # CANCEL
    # -----------------------------------------------------

    def cancel(self):

        self.cancelled.emit()

        self.close()


    # -----------------------------------------------------
    # KEYBOARD / REMOTE
    # -----------------------------------------------------

    def keyPressEvent(
        self,
        event
    ):

        key = event.key()


        if key == Qt.Key_Escape:

            self.cancel()

            return


        if key in (
            Qt.Key_Return,
            Qt.Key_Enter
        ):

            focused = self.focusWidget()


            if isinstance(
                focused,
                QPushButton
            ):

                focused.click()

                return


        super().keyPressEvent(
            event
        )


# =========================================================
# CROP PREVIEW
# =========================================================

class CropPreview(QWidget):

    def __init__(
        self,
        parent=None
    ):

        super().__init__(
            parent
        )

        self.pixmap = QPixmap()

        self.zoom = 1.0


    def set_pixmap(
        self,
        pixmap
    ):

        self.pixmap = pixmap


    def set_zoom(
        self,
        zoom
    ):

        self.zoom = zoom


    def paintEvent(
        self,
        event
    ):

        painter = QPainter(
            self
        )

        painter.setRenderHint(
            QPainter.SmoothPixmapTransform
        )


        # Background

        painter.fillRect(
            self.rect(),
            Qt.black
        )


        if self.pixmap.isNull():

            painter.setPen(
                Qt.white
            )

            painter.drawText(
                self.rect(),
                Qt.AlignCenter,
                "Choose a picture"
            )

            painter.end()

            return


        # Make a square crop area.

        size = min(
            self.width(),
            self.height()
        ) - 40


        crop_rect = QRect(
            (
                self.width()
                - size
            ) // 2,

            (
                self.height()
                - size
            ) // 2,

            size,
            size
        )


        # Scale image so the crop area is filled.

        image_size = self.pixmap.size()


        scale = max(
            size / image_size.width(),
            size / image_size.height()
        )


        scale *= self.zoom


        scaled_width = int(
            image_size.width()
            * scale
        )

        scaled_height = int(
            image_size.height()
            * scale
        )


        scaled = self.pixmap.scaled(
            scaled_width,
            scaled_height,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )


        image_x = (
            self.width()
            - scaled.width()
        ) // 2


        image_y = (
            self.height()
            - scaled.height()
        ) // 2


        painter.drawPixmap(
            image_x,
            image_y,
            scaled
        )


        # Darken outside crop area.

        overlay = self.rect()

        painter.setBrush(
            Qt.black
        )

        painter.setOpacity(
            0.55
        )


        painter.drawRect(
            overlay
        )


        painter.setOpacity(
            1.0
        )


        # Redraw crop area.

        painter.setClipRect(
            crop_rect
        )


        painter.drawPixmap(
            image_x,
            image_y,
            scaled
        )


        painter.setClipping(
            False
        )


        # Crop border.

        painter.setPen(
            Qt.white
        )

        painter.setBrush(
            Qt.NoBrush
        )

        painter.drawRect(
            crop_rect
        )


        painter.end()


    def get_crop(
        self,
        original
    ):

        if original.isNull():

            return QPixmap()


        size = min(
            self.width(),
            self.height()
        ) - 40


        if size <= 0:

            return QPixmap()


        image_width = (
            original.width()
        )

        image_height = (
            original.height()
        )


        base_scale = max(
            size / image_width,
            size / image_height
        )


        scale = (
            base_scale
            * self.zoom
        )


        scaled_width = int(
            image_width
            * scale
        )

        scaled_height = int(
            image_height
            * scale
        )


        # Position of scaled image.

        image_x = (
            self.width()
            - scaled_width
        ) // 2


        image_y = (
            self.height()
            - scaled_height
        ) // 2


        crop_x = (
            (self.width() - size) // 2
            - image_x
        )

        crop_y = (
            (self.height() - size) // 2
            - image_y
        )


        source_x = int(
            crop_x / scale
        )

        source_y = int(
            crop_y / scale
        )

        source_size = int(
            size / scale
        )


        source_x = max(
            0,
            min(
                source_x,
                image_width - source_size
            )
        )

        source_y = max(
            0,
            min(
                source_y,
                image_height - source_size
            )
        )


        source_size = min(
            source_size,
            image_width - source_x,
            image_height - source_y
        )


        if source_size <= 0:

            return QPixmap()


        return original.copy(
            QRect(
                source_x,
                source_y,
                source_size,
                source_size
            )
        )
