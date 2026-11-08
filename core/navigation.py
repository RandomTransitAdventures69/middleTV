from PySide6.QtCore import QObject, QEvent, Qt
from PySide6.QtWidgets import QApplication, QDialog, QLineEdit, QTextEdit, QPlainTextEdit, QComboBox


class NavigationController(QObject):
    """Shared Escape/Back handling for MiddleTV apps.

    Order:
    1. Active popup/modal dialog closes.
    2. Focused text/combo may consume Escape/Backspace when editing.
    3. Widget/app handle_back() can consume and navigate internally.
    4. Root MiddleTV app windows close to return to launcher.
    5. Launcher handles Back by returning True and not quitting.
    """

    def eventFilter(self, obj, event):
        if event.type() != QEvent.KeyPress:
            return False
        key = event.key()
        if key not in (Qt.Key_Escape, Qt.Key_Back, Qt.Key_Backspace):
            return False
        focus = QApplication.focusWidget()
        if key == Qt.Key_Backspace and isinstance(focus, (QLineEdit, QTextEdit, QPlainTextEdit)):
            return False
        # Let editable combo text keep Escape semantics unless popup is closed.
        if key == Qt.Key_Escape and isinstance(focus, QComboBox) and focus.isEditable():
            pass
        popup = QApplication.activePopupWidget()
        if popup is not None:
            popup.close()
            return True
        modal = QApplication.activeModalWidget()
        if modal is not None and isinstance(modal, QDialog):
            modal.reject()
            return True
        # Walk up from focus/window.
        widget = QApplication.activeWindow() or obj
        if hasattr(widget, "focusWidget") and widget.focusWidget():
            widget = widget.focusWidget()
        seen = set()
        while widget is not None and id(widget) not in seen:
            seen.add(id(widget))
            if isinstance(widget, QDialog):
                try:
                    widget.reject()
                except Exception:
                    widget.close()
                return True
            handler = getattr(widget, "handle_back", None)
            if callable(handler):
                try:
                    if handler():
                        return True
                except Exception:
                    pass
            if getattr(widget, "is_middletv_root", False):
                # Launcher should override handle_back and return True.
                try:
                    widget.close()
                except Exception:
                    pass
                return True
            widget = widget.parentWidget() if hasattr(widget, "parentWidget") else None
        return False
