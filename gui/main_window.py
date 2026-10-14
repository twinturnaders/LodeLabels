from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QCheckBox,
)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("LodeLabels")
        self.resize(700, 450)

        self.build_ui()


    def build_ui(self):

        # QMainWindow needs a "central widget."
        central_widget = QWidget()

        self.setCentralWidget(
            central_widget
        )

        # Main vertical layout for the entire window.
        main_layout = QVBoxLayout(
            central_widget
        )


        # ---------------------------------
        # TITLE
        # ---------------------------------

        title_label = QLabel("LodeLabels")

        title_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        title_label.setStyleSheet(
            """
            font-size: 26px;
            font-weight: bold;
            """
        )

        main_layout.addWidget(
            title_label
        )


        # ---------------------------------
        # AUTO PRINT SECTION
        # ---------------------------------

        auto_group = QGroupBox(
            "Automatic Whatnot Sales"
        )

        auto_layout = QHBoxLayout(
            auto_group
        )


        self.auto_print_checkbox = (
            QCheckBox("Auto Print")
        )

        # Safe default:
        self.auto_print_checkbox.setChecked(
            False
        )


        self.auto_status_label = QLabel(
            "OFF"
        )

        self.auto_status_label.setStyleSheet(
            """
            font-weight: bold;
            """
        )


        auto_layout.addWidget(
            self.auto_print_checkbox
        )

        auto_layout.addStretch()

        auto_layout.addWidget(
            QLabel("Status:")
        )

        auto_layout.addWidget(
            self.auto_status_label
        )


        main_layout.addWidget(
            auto_group
        )


        # ---------------------------------
        # MANUAL LABEL SECTION
        # ---------------------------------

        manual_group = QGroupBox(
            "Manual Label"
        )

        manual_layout = QVBoxLayout(
            manual_group
        )


        form_layout = QFormLayout()


        self.username_input = QLineEdit()

        self.username_input.setPlaceholderText(
            "Enter Whatnot username"
        )

        self.username_input.setClearButtonEnabled(
            True
        )


        form_layout.addRow(
            "Username:",
            self.username_input
        )

        manual_layout.addLayout(
            form_layout
        )


        button_layout = QHBoxLayout()


        self.sale_button = QPushButton(
            "Print Sale"
        )

        self.givvy_button = QPushButton(
            "Print Givvy"
        )


        button_layout.addWidget(
            self.sale_button
        )

        button_layout.addWidget(
            self.givvy_button
        )


        manual_layout.addLayout(
            button_layout
        )


        main_layout.addWidget(
            manual_group
        )


        # ---------------------------------
        # SESSION INFORMATION
        # ---------------------------------

        session_group = QGroupBox(
            "Current Session"
        )

        session_layout = QHBoxLayout(
            session_group
        )


        self.item_count_label = QLabel(
            "Item: 0"
        )

        self.givvy_count_label = QLabel(
            "Givvy: 0"
        )

        self.buyer_count_label = QLabel(
            "Buyers: 0"
        )


        session_layout.addWidget(
            self.item_count_label
        )

        session_layout.addWidget(
            self.givvy_count_label
        )

        session_layout.addWidget(
            self.buyer_count_label
        )


        main_layout.addWidget(
            session_group
        )


        # Push everything upward instead
        # of vertically stretching it.
        main_layout.addStretch()


        # ---------------------------------
        # STATUS BAR-LIKE LABEL
        # ---------------------------------

        self.status_label = QLabel(
            "Ready."
        )

        self.status_label.setStyleSheet(
            """
            padding: 6px;
            background-color: #eeeeee;
            """
        )

        main_layout.addWidget(
            self.status_label
        )


        # ---------------------------------
        # SIGNAL CONNECTIONS
        # ---------------------------------

        self.auto_print_checkbox.toggled.connect(
            self.handle_auto_toggle
        )

        self.sale_button.clicked.connect(
            self.handle_manual_sale
        )

        self.givvy_button.clicked.connect(
            self.handle_manual_givvy
        )

        # Pressing Enter in username field
        # acts like clicking Print Sale.
        self.username_input.returnPressed.connect(
            self.handle_manual_sale
        )


    def get_username(self):

        username = (
            self.username_input
            .text()
            .strip()
        )

        if username.startswith("@"):
            username = username[1:]

        return username


    def handle_auto_toggle(
        self,
        checked
    ):

        if checked:

            self.auto_status_label.setText(
                "ON"
            )

            self.status_label.setText(
                "Automatic Whatnot printing enabled."
            )

            print(
                "GUI: Auto Print ON"
            )

        else:

            self.auto_status_label.setText(
                "OFF"
            )

            self.status_label.setText(
                "Automatic Whatnot printing disabled."
            )

            print(
                "GUI: Auto Print OFF"
            )


    def handle_manual_sale(self):

        username = self.get_username()

        if not username:

            self.status_label.setText(
                "Enter a username first."
            )

            self.username_input.setFocus()

            return


        print(
            f"GUI SALE: {username}"
        )

        self.status_label.setText(
            f"Sale requested for @{username}"
        )

        self.username_input.clear()

        self.username_input.setFocus()


    def handle_manual_givvy(self):

        username = self.get_username()

        if not username:

            self.status_label.setText(
                "Enter a username first."
            )

            self.username_input.setFocus()

            return


        print(
            f"GUI GIVVY: {username}"
        )

        self.status_label.setText(
            f"Givvy requested for @{username}"
        )

        self.username_input.clear()

        self.username_input.setFocus()