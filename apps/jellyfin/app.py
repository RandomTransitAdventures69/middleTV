
import json
from core.fact_manager import FactManager
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QListWidget,
    QListWidgetItem,
)

from PySide6.QtCore import (
    Qt,
    QUrl,
    QTimer,
)

from PySide6.QtWebEngineWidgets import (
    QWebEngineView,
)


class App(QWidget):

    def __init__(self):

        super().__init__()

        self.setWindowTitle(
            "Jellyfin"
        )

        self.setMinimumSize(
            1100,
            700
        )

        self.config_file = (
            Path(__file__)
            .resolve()
            .parent.parent.parent
            / "config"
            / "jellyfin.json"
        )

        self.config_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self.browser = None

        self.server = ""

        self.server_id = ""

        self.loading_label = None

        self.setup()


    # =================================================
    # SETUP
    # =================================================

    def setup(self):

        config = self.load_config()

        servers = config.get(
            "servers",
            {}
        )

        active_server = config.get(
            "active_server",
            ""
        )


        if (
            active_server
            and active_server in servers
        ):

            self.server_id = active_server

            self.server = servers[
                active_server
            ].get(
                "url",
                ""
            ).strip()


            if self.server:

                self.show_loading()

                QTimer.singleShot(
                    250,
                    lambda:
                    self.open_jellyfin(
                        self.server
                    )
                )

                return


        self.show_server_picker()


    # =================================================
    # CONFIG
    # =================================================

    def default_config(self):

        return {
            "active_server": "",
            "servers": {}
        }


    def load_config(self):

        if not self.config_file.exists():

            return self.default_config()


        try:

            with open(
                self.config_file,
                "r"
            ) as f:

                data = json.load(f)

        except (
            json.JSONDecodeError,
            OSError
        ):

            return self.default_config()


        # -------------------------------------------------
        # Migrate old MiddleTV Jellyfin config.
        #
        # Old:
        #
        # {
        #     "server": "http://..."
        # }
        #
        # New:
        #
        # {
        #     "active_server": "home",
        #     "servers": {
        #         "home": {
        #             "name": "Home",
        #             "url": "http://..."
        #         }
        #     }
        # }
        # -------------------------------------------------

        if (
            "server" in data
            and "servers" not in data
        ):

            old_server = str(
                data.get(
                    "server",
                    ""
                )
            ).strip()


            if old_server:

                old_server = (
                    old_server.rstrip("/")
                )


                if not old_server.startswith(
                    (
                        "http://",
                        "https://"
                    )
                ):

                    old_server = (
                        "http://"
                        + old_server
                    )


                data = {
                    "active_server": "home",

                    "servers": {
                        "home": {
                            "name": "Home",
                            "url": old_server
                        }
                    }
                }


                self.save_config(
                    data
                )

                return data


        if not isinstance(
            data,
            dict
        ):

            return self.default_config()


        if not isinstance(
            data.get(
                "servers",
                {}
            ),
            dict
        ):

            data[
                "servers"
            ] = {}


        return data


    def save_config(
        self,
        data
    ):

        try:

            with open(
                self.config_file,
                "w"
            ) as f:

                json.dump(
                    data,
                    f,
                    indent=4
                )

            return True

        except OSError:

            return False


    # =================================================
    # BASE STYLE
    # =================================================

    def apply_base_style(self):

        self.setStyleSheet(
            """
            QWidget {
                background: #101014;
            }

            QLabel {
                color: white;
            }

            QPushButton {

                color: white;

                background:
                    rgba(
                        35,
                        35,
                        40,
                        230
                    );

                border:
                    2px solid
                    rgba(
                        255,
                        255,
                        255,
                        55
                    );

                border-radius:
                    16px;

                font-size: 20px;

                font-weight: bold;

                padding:
                    10px 20px;
            }

            QPushButton:hover {

                background:
                    rgba(
                        50,
                        75,
                        105,
                        235
                    );

                border:
                    3px solid
                    rgba(
                        90,
                        180,
                        255,
                        230
                    );
            }

            QPushButton:focus {

                background:
                    rgba(
                        45,
                        85,
                        130,
                        240
                    );

                border:
                    4px solid
                    rgba(
                        90,
                        190,
                        255,
                        255
                    );
            }

            QLineEdit {

                color: white;

                background:
                    rgba(
                        30,
                        30,
                        35,
                        230
                    );

                border:
                    2px solid
                    rgba(
                        255,
                        255,
                        255,
                        60
                    );

                border-radius:
                    16px;

                padding:
                    0px 20px;

                font-size: 21px;
            }

            QLineEdit:focus {

                border:
                    3px solid
                    rgba(
                        90,
                        190,
                        255,
                        255
                    );

                background:
                    rgba(
                        40,
                        50,
                        65,
                        240
                    );
            }

            QListWidget {

                color: white;

                background:
                    rgba(
                        25,
                        25,
                        30,
                        235
                    );

                border:
                    2px solid
                    rgba(
                        255,
                        255,
                        255,
                        45
                    );

                border-radius:
                    18px;

                padding:
                    10px;

                font-size: 21px;
            }

            QListWidget::item {

                padding:
                    18px;

                margin:
                    5px;

                border-radius:
                    12px;
            }

            QListWidget::item:selected {

                background:
                    rgba(
                        45,
                        85,
                        130,
                        240
                    );

                border:
                    2px solid
                    rgba(
                        90,
                        190,
                        255,
                        255
                    );
            }
            """
        )


    # =================================================
    # SERVER PICKER
    # =================================================

    def show_server_picker(self):

        self.browser = None

        self.apply_base_style()


        layout = QVBoxLayout()

        layout.setContentsMargins(
            80,
            60,
            80,
            60
        )

        layout.setSpacing(
            20
        )


        title = QLabel(
            "Jellyfin"
        )

        title.setAlignment(
            Qt.AlignCenter
        )

        title.setStyleSheet(
            """
            QLabel {
                font-size: 48px;
                font-weight: bold;
            }
            """
        )


        layout.addWidget(
            title
        )


        subtitle = QLabel(
            "Choose a server"
        )

        subtitle.setAlignment(
            Qt.AlignCenter
        )

        subtitle.setStyleSheet(
            """
            QLabel {
                color:
                    rgba(
                        255,
                        255,
                        255,
                        160
                    );

                font-size: 20px;
            }
            """
        )


        layout.addWidget(
            subtitle
        )


        self.server_list = QListWidget()

        self.server_list.setFocusPolicy(
            Qt.StrongFocus
        )


        config = self.load_config()

        servers = config.get(
            "servers",
            {}
        )


        for server_id, server in (
            servers.items()
        ):

            name = server.get(
                "name",
                server_id
            )

            url = server.get(
                "url",
                ""
            )


            item = QListWidgetItem(
                f"{name}\n{url}"
            )


            item.setData(
                Qt.UserRole,
                server_id
            )


            self.server_list.addItem(
                item
            )


        layout.addWidget(
            self.server_list
        )


        buttons = QHBoxLayout()

        buttons.setSpacing(
            15
        )


        connect = QPushButton(
            "Connect"
        )

        add = QPushButton(
            "Add Server"
        )

        delete = QPushButton(
            "Delete"
        )

        back = QPushButton(
            "Back"
        )


        for button in (
            connect,
            add,
            delete,
            back
        ):

            button.setMinimumHeight(
                60
            )


        connect.clicked.connect(
            self.connect_selected_server
        )

        add.clicked.connect(
            self.show_add_server
        )

        delete.clicked.connect(
            self.delete_selected_server
        )

        back.clicked.connect(
            self.close
        )


        self.server_list.itemDoubleClicked.connect(
            lambda item:
            self.connect_selected_server()
        )


        buttons.addWidget(
            connect
        )

        buttons.addWidget(
            add
        )

        buttons.addWidget(
            delete
        )

        buttons.addWidget(
            back
        )


        layout.addLayout(
            buttons
        )


        self.setLayout(
            layout
        )


        if self.server_list.count():

            self.server_list.setCurrentRow(
                0
            )

            self.server_list.setFocus()

        else:

            add.setFocus()


    # =================================================
    # SELECT SERVER
    # =================================================

    def connect_selected_server(
        self
    ):

        item = (
            self.server_list
            .currentItem()
        )


        if not item:

            return


        server_id = item.data(
            Qt.UserRole
        )


        config = self.load_config()

        servers = config.get(
            "servers",
            {}
        )


        server = servers.get(
            server_id
        )


        if not server:

            return


        url = server.get(
            "url",
            ""
        ).strip()


        if not url:

            return


        config[
            "active_server"
        ] = server_id


        self.save_config(
            config
        )


        self.server_id = server_id

        self.server = url


        self.show_loading()


        QTimer.singleShot(
            250,
            lambda:
            self.open_jellyfin(
                url
            )
        )


    # =================================================
    # ADD SERVER
    # =================================================

    def show_add_server(self):

        self.show_setup(
            adding=True
        )


    def show_setup(
        self,
        adding=False
    ):

        self.apply_base_style()


        layout = QVBoxLayout()

        layout.setContentsMargins(
            80,
            60,
            80,
            60
        )

        layout.setSpacing(
            20
        )


        layout.addStretch()


        title = QLabel(
            "Add Jellyfin Server"
            if adding
            else
            "Connect to Jellyfin"
        )

        title.setAlignment(
            Qt.AlignCenter
        )

        title.setStyleSheet(
            """
            QLabel {
                font-size: 42px;
                font-weight: bold;
            }
            """
        )


        layout.addWidget(
            title
        )


        name_label = QLabel(
            "Server name"
        )

        name_label.setStyleSheet(
            "font-size: 18px;"
        )


        layout.addWidget(
            name_label
        )


        self.name_input = QLineEdit()

        self.name_input.setPlaceholderText(
            "Home"
        )

        self.name_input.setMinimumHeight(
            60
        )


        layout.addWidget(
            self.name_input
        )


        url_label = QLabel(
            "Server address"
        )

        url_label.setStyleSheet(
            "font-size: 18px;"
        )


        layout.addWidget(
            url_label
        )


        self.server_input = QLineEdit()

        self.server_input.setPlaceholderText(
            "http://192.168.1.100:8096"
        )

        self.server_input.setMinimumHeight(
            60
        )


        layout.addWidget(
            self.server_input
        )


        layout.addSpacing(
            15
        )


        buttons = QHBoxLayout()

        cancel = QPushButton(
            "Cancel"
        )

        save = QPushButton(
            "Save Server"
        )


        cancel.setMinimumHeight(
            60
        )

        save.setMinimumHeight(
            60
        )


        cancel.clicked.connect(
            self.show_server_picker
        )

        save.clicked.connect(
            self.add_server
        )


        self.server_input.returnPressed.connect(
            self.add_server
        )


        buttons.addWidget(
            cancel
        )

        buttons.addWidget(
            save
        )


        layout.addLayout(
            buttons
        )


        layout.addStretch()


        self.setLayout(
            layout
        )


        self.name_input.setFocus()


    # =================================================
    # ADD SERVER
    # =================================================

    def add_server(self):

        name = (
            self.name_input
            .text()
            .strip()
        )

        url = (
            self.server_input
            .text()
            .strip()
        )


        if not name:

            name = "Jellyfin Server"


        if not url:

            QMessageBox.warning(
                self,
                "Jellyfin",
                "Please enter a server address."
            )

            self.server_input.setFocus()

            return


        url = url.rstrip(
            "/"
        )


        if not url.startswith(
            (
                "http://",
                "https://"
            )
        ):

            url = (
                "http://"
                + url
            )


        config = self.load_config()

        servers = config.setdefault(
            "servers",
            {}
        )


        # -------------------------------------------------
        # Generate an ID.
        # -------------------------------------------------

        base_id = (
            name
            .lower()
            .replace(
                " ",
                "_"
            )
        )


        server_id = base_id

        counter = 2


        while server_id in servers:

            server_id = (
                f"{base_id}_{counter}"
            )

            counter += 1


        servers[
            server_id
        ] = {

            "name": name,

            "url": url
        }


        # First server automatically
        # becomes active.

        if not config.get(
            "active_server"
        ):

            config[
                "active_server"
            ] = server_id


        if not self.save_config(
            config
        ):

            QMessageBox.critical(
                self,
                "Jellyfin",
                "Could not save the server."
            )

            return


        self.show_server_picker()


    # =================================================
    # DELETE SERVER
    # =================================================

    def delete_selected_server(
        self
    ):

        item = (
            self.server_list
            .currentItem()
        )


        if not item:

            return


        server_id = item.data(
            Qt.UserRole
        )


        config = self.load_config()

        servers = config.get(
            "servers",
            {}
        )


        if server_id not in servers:

            return


        name = servers[
            server_id
        ].get(
            "name",
            server_id
        )


        result = QMessageBox.question(
            self,
            "Delete Server",
            f"Delete '{name}'?",
            QMessageBox.Yes
            | QMessageBox.No
        )


        if result != QMessageBox.Yes:

            return


        del servers[
            server_id
        ]


        if (
            config.get(
                "active_server"
            )
            == server_id
        ):

            if servers:

                config[
                    "active_server"
                ] = next(
                    iter(
                        servers
                    )
                )

            else:

                config[
                    "active_server"
                ] = ""


        self.save_config(
            config
        )


        self.show_server_picker()


    # =================================================
    # LOADING SCREEN
    # =================================================

    def show_loading(self):

        self.apply_base_style()


        layout = QVBoxLayout()

        layout.setContentsMargins(
            80,
            60,
            80,
            60
        )


        layout.addStretch()


        title = QLabel(
            "jellyfin™"
        )

        title.setAlignment(
            Qt.AlignCenter
        )

        title.setStyleSheet(
            """
            QLabel {
                font-size: 52px;
                font-weight: bold;
            }
            """
        )


        layout.addWidget(
            title
        )


        label = QLabel(
            "Connecting to your server..."
        )

        label.setAlignment(
            Qt.AlignCenter
        )

        label.setStyleSheet(
            """
            QLabel {
                color:
                    rgba(
                        255,
                        255,
                        255,
                        165
                    );

                font-size: 21px;
            }
            """
        )


        layout.addWidget(
            label
        )


        server_label = QLabel(
            self.server
        )

        server_label.setAlignment(
            Qt.AlignCenter
        )

        server_label.setStyleSheet(
            """
            QLabel {
                color:
                    rgba(
                        255,
                        255,
                        255,
                        100
                    );

                font-size: 16px;
            }
            """
        )


        layout.addWidget(
            server_label
        )


        layout.addStretch()


        self.setLayout(
            layout
        )


    # =================================================
    # OPEN JELLYFIN
    # =================================================

    def open_jellyfin(
        self,
        server
    ):

        self.browser = QWebEngineView()

        self.browser.setFocusPolicy(
            Qt.StrongFocus
        )


        self.browser.loadStarted.connect(
            lambda:
            print(
                "Jellyfin: loading..."
            )
        )


        self.browser.loadFinished.connect(
            self.jellyfin_loaded
        )


        self.browser.setUrl(
            QUrl(server)
        )


        layout = QVBoxLayout()

        layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        layout.setSpacing(
            0
        )

        layout.addWidget(
            self.browser
        )


        self.setLayout(
            layout
        )


        self.setStyleSheet(
            """
            QWidget {
                background: black;
            }
            """
        )


        self.browser.setFocus()


    # =================================================
    # LOAD RESULT
    # =================================================

    def jellyfin_loaded(
        self,
        success
    ):

        print(
            "Jellyfin load finished:",
            success
        )


        if not success:

            self.show_error(
                "Unable to connect to Jellyfin."
            )


    # =================================================
    # ERROR
    # =================================================

    def show_error(
        self,
        message
    ):

        self.apply_base_style()


        layout = QVBoxLayout()

        layout.setContentsMargins(
            80,
            60,
            80,
            60
        )


        layout.addStretch()


        title = QLabel(
            "Jellyfin isn't available"
        )

        title.setAlignment(
            Qt.AlignCenter
        )

        title.setStyleSheet(
            """
            QLabel {
                font-size: 38px;
                font-weight: bold;
            }
            """
        )


        layout.addWidget(
            title
        )


        text = QLabel(
            message
            + "\n\n"
            + self.server
        )

        text.setAlignment(
            Qt.AlignCenter
        )

        text.setWordWrap(
            True
        )

        text.setStyleSheet(
            """
            QLabel {
                color:
                    rgba(
                        255,
                        255,
                        255,
                        165
                    );

                font-size: 19px;
            }
            """
        )


        layout.addWidget(
            text
        )


        layout.addSpacing(
            30
        )


        buttons = QHBoxLayout()


        retry = QPushButton(
            "Retry"
        )

        servers = QPushButton(
            "Servers"
        )

        back = QPushButton(
            "Back"
        )


        for button in (
            retry,
            servers,
            back
        ):

            button.setMinimumHeight(
                60
            )

            button.setMinimumWidth(
                200
            )


        retry.clicked.connect(
            self.retry
        )

        servers.clicked.connect(
            self.show_server_picker
        )

        back.clicked.connect(
            self.close
        )


        buttons.addWidget(
            retry
        )

        buttons.addWidget(
            servers
        )

        buttons.addWidget(
            back
        )


        layout.addLayout(
            buttons
        )


        layout.addStretch()


        self.setLayout(
            layout
        )


        retry.setFocus()


    # =================================================
    # RETRY
    # =================================================

    def retry(self):

        self.show_loading()


        QTimer.singleShot(
            250,
            lambda:
            self.open_jellyfin(
                self.server
            )
        )


    # =================================================
    # KEYBOARD / REMOTE
    # =================================================

    def keyPressEvent(
        self,
        event
    ):

        key = event.key()


        if key in (
            Qt.Key_Escape,
            Qt.Key_Backspace
        ):

            if self.browser:

                if (
                    self.browser
                    .history()
                    .canGoBack()
                ):

                    self.browser.back()

                    return


            self.close()

            return


        if key == Qt.Key_F5:

            if self.browser:

                self.browser.reload()

            return


        super().keyPressEvent(
            event
        )
