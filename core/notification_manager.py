
from PySide6.QtCore import (
    Qt,
    QTimer,
    QPropertyAnimation,
    QEasingCurve,
)
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
)


class Notification(QWidget):

    def __init__(
        self,
        title,
        message,
        parent=None,
        duration=3500,
    ):

        super().__init__(
            parent
        )

        self.duration = duration

        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.Tool
        )

        self.setAttribute(
            Qt.WA_TranslucentBackground
        )

        self.setup_ui(
            title,
            message
        )


    def setup_ui(
        self,
        title,
        message
    ):

        outer = QVBoxLayout(
            self
        )

        outer.setContentsMargins(
            0,
            0,
            0,
            0
        )


        card = QFrame()

        card.setObjectName(
            "notificationCard"
        )


        card.setStyleSheet(
            """
            QFrame#notificationCard {
                background-color:
                    rgba(25, 25, 30, 245);

                border:
                    2px solid
                    rgba(255, 255, 255, 45);

                border-radius: 18px;
            }

            QLabel#title {
                color: white;
                font-size: 21px;
                font-weight: bold;
            }

            QLabel#message {
                color:
                    rgba(255, 255, 255, 180);

                font-size: 16px;
            }
            """
        )


        layout = QHBoxLayout(
            card
        )

        layout.setContentsMargins(
            22,
            18,
            22,
            18
        )

        layout.setSpacing(
            16
        )


        check = QLabel(
            "✓"
        )

        check.setStyleSheet(
            """
            QLabel {
                color: white;
                font-size: 28px;
                font-weight: bold;
            }
            """
        )


        text_layout = QVBoxLayout()

        text_layout.setSpacing(
            3
        )


        title_label = QLabel(
            title
        )

        title_label.setObjectName(
            "title"
        )


        message_label = QLabel(
            message
        )

        message_label.setObjectName(
            "message"
        )

        message_label.setWordWrap(
            True
        )


        text_layout.addWidget(
            title_label
        )

        text_layout.addWidget(
            message_label
        )


        layout.addWidget(
            check
        )

        layout.addLayout(
            text_layout
        )


        outer.addWidget(
            card
        )


        self.setMinimumWidth(
            360
        )

        self.setMaximumWidth(
            520
        )


    def show_notification(self):

        self.adjustSize()

        self.fade_in()

        self.show()

        QTimer.singleShot(
            self.duration,
            self.fade_out
        )


    def fade_in(self):

        self.setWindowOpacity(
            0.0
        )


        animation = QPropertyAnimation(
            self,
            b"windowOpacity"
        )

        animation.setDuration(
            250
        )

        animation.setStartValue(
            0.0
        )

        animation.setEndValue(
            1.0
        )

        animation.setEasingCurve(
            QEasingCurve.OutCubic
        )

        animation.start(
            QPropertyAnimation.DeleteWhenStopped
        )


    def fade_out(self):

        animation = QPropertyAnimation(
            self,
            b"windowOpacity"
        )

        animation.setDuration(
            350
        )

        animation.setStartValue(
            self.windowOpacity()
        )

        animation.setEndValue(
            0.0
        )

        animation.setEasingCurve(
            QEasingCurve.InCubic
        )

        animation.finished.connect(
            self.close
        )

        animation.start(
            QPropertyAnimation.DeleteWhenStopped
        )


class NotificationManager:

    def __init__(
        self,
        parent
    ):

        self.parent = parent

        self.notifications = []


    def show(
        self,
        title,
        message,
        duration=3500
    ):

        notification = Notification(
            title,
            message,
            self.parent,
            duration
        )


        self.notifications.append(
            notification
        )


        notification.destroyed.connect(
            lambda: self.remove(
                notification
            )
        )


        self.position_notifications()

        notification.show_notification()


    def remove(
        self,
        notification
    ):

        if notification in self.notifications:

            self.notifications.remove(
                notification
            )

        self.position_notifications()


    def position_notifications(self):

        margin = 30
        spacing = 12

        y = margin


        for notification in self.notifications:

            if not notification.isVisible():

                continue


            notification.adjustSize()


            x = (
                self.parent.width()
                - notification.width()
                - margin
            )


            notification.move(
                x,
                y
            )


            y += (
                notification.height()
                + spacing
            )


    def wallpaper_changed(self):

        self.show(
            "Wallpaper updated",
            "Your new wallpaper is now active."
        )


    def profile_saved(self):

        self.show(
            "Profile picture saved",
            "Your profile picture has been updated."
        )


    def settings_saved(self):

        self.show(
            "Settings saved",
            "Your changes have been applied."
        )


    def error(
        self,
        message
    ):

        self.show(
            "Something went wrong",
            message,
            5000
        )
