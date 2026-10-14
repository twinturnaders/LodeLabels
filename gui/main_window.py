from PySide6.QtCore import Qt

from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class MainWindow(QMainWindow):

    def __init__(
        self,
        backend
    ):

        super().__init__()

        self.backend = backend

        self.setWindowTitle(
            "LodeLabels"
        )

        self.resize(
            950,
            700
        )

        self.build_ui()

        self.refresh_session()

        self.refresh_history()

        self.sync_auto_print_state()

        self.username_input.setFocus()


    # ========================================================
    # UI
    # ========================================================

    def build_ui(self):

        central_widget = QWidget()

        self.setCentralWidget(
            central_widget
        )


        main_layout = QVBoxLayout(
            central_widget
        )


        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        title_label = QLabel(
            "LodeLabels"
        )

        title_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        title_label.setStyleSheet(
            """
            font-size: 28px;
            font-weight: bold;
            padding: 8px;
            """
        )

        main_layout.addWidget(
            title_label
        )


        # ----------------------------------------------------
        # AUTO PRINT
        # ----------------------------------------------------

        auto_group = QGroupBox(
            "Automatic Whatnot Sales"
        )

        auto_layout = QHBoxLayout(
            auto_group
        )


        self.auto_print_checkbox = (
            QCheckBox(
                "Auto Print"
            )
        )


        self.auto_status_label = QLabel(
            "OFF"
        )


        self.listener_status_label = QLabel(
            "Starting..."
        )


        auto_layout.addWidget(
            self.auto_print_checkbox
        )

        auto_layout.addWidget(
            self.auto_status_label
        )

        auto_layout.addStretch()

        auto_layout.addWidget(
            QLabel("Listener:")
        )

        auto_layout.addWidget(
            self.listener_status_label
        )


        main_layout.addWidget(
            auto_group
        )


        # ----------------------------------------------------
        # MANUAL
        # ----------------------------------------------------

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

        self.reprint_button = QPushButton(
            "Reprint Latest"
        )


        button_layout.addWidget(
            self.sale_button
        )

        button_layout.addWidget(
            self.givvy_button
        )

        button_layout.addWidget(
            self.reprint_button
        )


        manual_layout.addLayout(
            button_layout
        )


        main_layout.addWidget(
            manual_group
        )


        # ----------------------------------------------------
        # SESSION
        # ----------------------------------------------------

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


        for label in (
            self.item_count_label,
            self.givvy_count_label,
            self.buyer_count_label,
        ):

            label.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            label.setStyleSheet(
                """
                font-size: 18px;
                font-weight: bold;
                padding: 8px;
                """
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


        # ----------------------------------------------------
        # HISTORY
        # ----------------------------------------------------

        history_group = QGroupBox(
            "Recent Labels"
        )

        history_layout = QVBoxLayout(
            history_group
        )


        self.history_table = QTableWidget()

        self.history_table.setColumnCount(
            8
        )

        self.history_table.setHorizontalHeaderLabels(
            [
                "Time",
                "Type",
                "#",
                "Buyer",
                "Username",
                "Prints",
                "Status",
                "",
            ]
        )


        self.history_table.setEditTriggers(
            QAbstractItemView
            .EditTrigger
            .NoEditTriggers
        )

        self.history_table.setSelectionBehavior(
            QAbstractItemView
            .SelectionBehavior
            .SelectRows
        )


        header = (
            self.history_table
            .horizontalHeader()
        )


        header.setSectionResizeMode(
            QHeaderView
            .ResizeMode
            .ResizeToContents
        )


        header.setSectionResizeMode(
            4,
            QHeaderView
            .ResizeMode
            .Stretch
        )


        history_layout.addWidget(
            self.history_table
        )


        refresh_button = QPushButton(
            "Refresh History"
        )

        refresh_button.clicked.connect(
            self.refresh_history
        )

        history_layout.addWidget(
            refresh_button
        )


        main_layout.addWidget(
            history_group
        )


        # ----------------------------------------------------
        # ACTIVITY / STATUS
        # ----------------------------------------------------

        self.last_event_label = QLabel(
            "No activity yet."
        )

        self.last_event_label.setWordWrap(
            True
        )

        main_layout.addWidget(
            self.last_event_label
        )


        self.status_label = QLabel(
            "Ready."
        )

        self.status_label.setStyleSheet(
            """
            padding: 8px;
            background-color: #eeeeee;
            border-radius: 4px;
            """
        )

        main_layout.addWidget(
            self.status_label
        )


        # ----------------------------------------------------
        # SIGNALS
        # ----------------------------------------------------

        self.auto_print_checkbox.toggled.connect(
            self.handle_auto_toggle
        )

        self.sale_button.clicked.connect(
            self.handle_manual_sale
        )

        self.givvy_button.clicked.connect(
            self.handle_manual_givvy
        )

        self.reprint_button.clicked.connect(
            self.handle_reprint
        )

        self.username_input.returnPressed.connect(
            self.handle_manual_sale
        )


    # ========================================================
    # HELPERS
    # ========================================================

    def get_username(self):

        username = (
            self.username_input
            .text()
            .strip()
        )

        if username.startswith("@"):
            username = username[1:]

        return username.strip()


    def refresh_session(self):

        self.item_count_label.setText(
            f"Item: "
            f"{self.backend.item_number}"
        )

        self.givvy_count_label.setText(
            f"Givvy: "
            f"{self.backend.givvy_number}"
        )

        self.buyer_count_label.setText(
            f"Buyers: "
            f"{len(self.backend.buyers)}"
        )


    # ========================================================
    # HISTORY
    # ========================================================

    def refresh_history(self):

        try:

            rows = (
                self.backend
                .get_recent_history(
                    50
                )
            )

        except Exception as error:

            self.status_label.setText(
                f"Could not load history: "
                f"{error}"
            )

            return


        self.history_table.setRowCount(
            len(rows)
        )


        for table_row, record in enumerate(
            rows
        ):

            created_at = (
                record["created_at"]
            )


            if "T" in created_at:

                time_text = (
                    created_at
                    .split("T", 1)[1]
                )

            else:

                time_text = created_at


            label_type = (
                record["label_type"]
            )


            if label_type == "sale":

                type_text = "Sale"

                sequence_text = (
                    f"{record['sequence_number']:03d}"
                )

            else:

                type_text = "Givvy"

                sequence_text = (
                    f"G{record['sequence_number']:02d}"
                )


            buyer_text = (
                f"B#{record['buyer_number']:02d}"
            )


            values = [
                time_text,
                type_text,
                sequence_text,
                buyer_text,
                f"@{record['username']}",
                str(
                    record["print_count"]
                ),
                record["print_status"],
            ]


            for column, value in enumerate(
                values
            ):

                item = QTableWidgetItem(
                    value
                )

                self.history_table.setItem(
                    table_row,
                    column,
                    item,
                )


            reprint_button = QPushButton(
                "Reprint"
            )


            label_id = record["id"]


            reprint_button.clicked.connect(
                lambda checked=False,
                current_id=label_id:
                self.handle_history_reprint(
                    current_id
                )
            )


            self.history_table.setCellWidget(
                table_row,
                7,
                reprint_button,
            )


    def handle_history_reprint(
        self,
        label_id
    ):

        try:

            record = (
                self.backend
                .reprint_history_label(
                    label_id
                )
            )


        except Exception as error:

            self.status_label.setText(
                f"Reprint failed: {error}"
            )

            self.refresh_history()

            return


        self.status_label.setText(
            "Label reprinted."
        )


        self.last_event_label.setText(
            f"Reprinted "
            f"@{record['username']}"
        )


        self.refresh_history()


    # ========================================================
    # AUTO PRINT
    # ========================================================

    def sync_auto_print_state(self):

        enabled = (
            self.backend.auto_print_enabled
        )


        self.auto_print_checkbox.blockSignals(
            True
        )

        self.auto_print_checkbox.setChecked(
            enabled
        )

        self.auto_print_checkbox.blockSignals(
            False
        )


        self.update_auto_display(
            enabled
        )


    def update_auto_display(
        self,
        enabled
    ):

        self.auto_status_label.setText(
            "ON"
            if enabled
            else "OFF"
        )


    def handle_auto_toggle(
        self,
        checked
    ):

        self.backend.set_auto_print(
            checked
        )

        self.update_auto_display(
            checked
        )


        if checked:

            self.status_label.setText(
                "Automatic Whatnot printing enabled."
            )

        else:

            self.status_label.setText(
                "Automatic Whatnot printing disabled."
            )


    def toggle_auto_print_from_hotkey(
        self
    ):

        self.auto_print_checkbox.setChecked(
            not self.backend.auto_print_enabled
        )


    # ========================================================
    # LISTENER
    # ========================================================

    def set_listener_status(
        self,
        running,
        message=None
    ):

        if running:

            self.listener_status_label.setText(
                message or "Connected"
            )

        else:

            self.listener_status_label.setText(
                message or "Not running"
            )


    # ========================================================
    # MANUAL SALE
    # ========================================================

    def handle_manual_sale(self):

        username = self.get_username()


        if not username:

            self.status_label.setText(
                "Enter a username first."
            )

            self.username_input.setFocus()

            return


        try:

            self.backend.process_sale(
                username
            )


        except Exception as error:

            self.refresh_session()
            self.refresh_history()

            self.status_label.setText(
                f"Sale error: {error}"
            )

            return


        self.refresh_session()

        self.refresh_history()


        self.last_event_label.setText(
            f"Manual sale: @{username}"
        )


        self.status_label.setText(
            f"Sale processed for "
            f"@{username}"
        )


        self.username_input.clear()

        self.username_input.setFocus()


    # ========================================================
    # GIVVY
    # ========================================================

    def handle_manual_givvy(self):

        username = self.get_username()


        if not username:

            self.status_label.setText(
                "Enter a username first."
            )

            return


        try:

            self.backend.process_givvy(
                username
            )


        except Exception as error:

            self.refresh_session()
            self.refresh_history()

            self.status_label.setText(
                f"Givvy error: {error}"
            )

            return


        self.refresh_session()

        self.refresh_history()


        self.last_event_label.setText(
            f"Manual givvy: @{username}"
        )


        self.status_label.setText(
            f"Givvy processed for "
            f"@{username}"
        )


        self.username_input.clear()

        self.username_input.setFocus()


    # ========================================================
    # AUTOMATIC SALE
    # ========================================================

    def handle_auto_sale(
        self,
        username
    ):

        username = (
            self.backend
            .clean_username(
                username
            )
        )


        try:

            accepted = (
                self.backend
                .process_auto_sale(
                    username
                )
            )


        except Exception as error:

            self.refresh_session()
            self.refresh_history()

            self.status_label.setText(
                f"Auto sale error: {error}"
            )

            return


        if not accepted:

            self.status_label.setText(
                f"Detected @{username} — "
                f"Auto Print OFF"
            )

            return


        self.refresh_session()

        self.refresh_history()


        self.last_event_label.setText(
            f"Automatic sale: "
            f"@{username}"
        )


        self.status_label.setText(
            f"Auto sale processed "
            f"for @{username}"
        )


    # ========================================================
    # CLIPBOARD HOTKEYS
    # ========================================================

    def handle_clipboard_sale(self):

        username = (
            self.backend
            .get_clipboard_text()
        )

        if not username:
            return


        try:

            self.backend.process_sale(
                username
            )

        except Exception as error:

            self.refresh_session()
            self.refresh_history()

            self.status_label.setText(
                f"F8 sale error: {error}"
            )

            return


        self.refresh_session()
        self.refresh_history()


        self.last_event_label.setText(
            f"F8 sale: @{username}"
        )


    def handle_clipboard_givvy(self):

        username = (
            self.backend
            .get_clipboard_text()
        )

        if not username:
            return


        try:

            self.backend.process_givvy(
                username
            )

        except Exception as error:

            self.refresh_session()
            self.refresh_history()

            self.status_label.setText(
                f"Givvy error: {error}"
            )

            return


        self.refresh_session()
        self.refresh_history()


        self.last_event_label.setText(
            f"Givvy: @{username}"
        )


    # ========================================================
    # REPRINT
    # ========================================================

    def handle_reprint(self):

        try:

            self.backend.test_print_latest_label()


        except Exception as error:

            self.status_label.setText(
                f"Reprint failed: {error}"
            )

            self.refresh_history()

            return


        self.refresh_history()

        self.status_label.setText(
            "Latest label reprinted."
        )


    # ========================================================
    # RESET
    # ========================================================

    def handle_reset_items(self):

        self.backend.reset_item_number()

        self.refresh_session()

        self.status_label.setText(
            "Item number reset to 0."
        )


    def handle_reset_givvies(self):

        self.backend.reset_givvy_number()

        self.refresh_session()

        self.status_label.setText(
            "Givvy number reset to 0."
        )