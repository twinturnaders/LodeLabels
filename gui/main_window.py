from pathlib import Path

import win32print

from PySide6.QtCore import (
    Qt,
    QSettings,
)

from PySide6.QtGui import (
    QCloseEvent,
    QPixmap,
)

from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QDoubleSpinBox,
    QSpinBox,
    QSplitter,
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

        self.settings = QSettings(
            "MontanaMotherlodes",
            "LodeLabels"
        )

        self.load_label_settings()

        self.setWindowTitle(
            "LodeLabels"
        )

        # Allow the user to resize freely, while keeping a
        # reasonable minimum so controls do not become unusable.
        self.setMinimumSize(
            720,
            560
        )

        self.resize(
            1050,
            850
        )

        self.build_ui()

        self.refresh_printer_list()

        self.restore_window_layout()

        self.refresh_session()
        self.refresh_history()
        self.sync_auto_print_state()
        self.update_preview()

        self.username_input.setFocus()


    # ========================================================
    # SETTINGS
    # ========================================================

    def load_label_settings(self):

        self.backend.set_label_dimensions(
            float(
                self.settings.value(
                    "label/width_inches",
                    self.backend.LABEL_WIDTH_INCHES
                )
            ),
            float(
                self.settings.value(
                    "label/height_inches",
                    self.backend.LABEL_HEIGHT_INCHES
                )
            ),
        )

        self.backend.SAFE_MARGIN = int(
            self.settings.value(
                "label/safe_margin",
                self.backend.SAFE_MARGIN
            )
        )

        self.backend.VERTICAL_OFFSET = int(
            self.settings.value(
                "label/vertical_offset",
                self.backend.VERTICAL_OFFSET
            )
        )

        self.backend.ITEM_FONT_SIZE = int(
            self.settings.value(
                "label/item_font_size",
                self.backend.ITEM_FONT_SIZE
            )
        )

        self.backend.BUYER_FONT_SIZE = int(
            self.settings.value(
                "label/buyer_font_size",
                self.backend.BUYER_FONT_SIZE
            )
        )

        self.backend.USERNAME_FONT_SIZE = int(
            self.settings.value(
                "label/username_font_size",
                self.backend.USERNAME_FONT_SIZE
            )
        )


    def save_label_settings(self):

        self.backend.set_label_dimensions(
            self.label_width_spin.value(),
            self.label_height_spin.value(),
        )

        self.backend.SAFE_MARGIN = (
            self.safe_margin_spin.value()
        )

        self.backend.VERTICAL_OFFSET = (
            self.vertical_offset_spin.value()
        )

        self.backend.ITEM_FONT_SIZE = (
            self.item_font_spin.value()
        )

        self.backend.BUYER_FONT_SIZE = (
            self.buyer_font_spin.value()
        )

        self.backend.USERNAME_FONT_SIZE = (
            self.username_font_spin.value()
        )

        self.settings.setValue(
            "label/width_inches",
            self.backend.LABEL_WIDTH_INCHES
        )

        self.settings.setValue(
            "label/height_inches",
            self.backend.LABEL_HEIGHT_INCHES
        )

        self.settings.setValue(
            "label/safe_margin",
            self.backend.SAFE_MARGIN
        )

        self.settings.setValue(
            "label/vertical_offset",
            self.backend.VERTICAL_OFFSET
        )

        self.settings.setValue(
            "label/item_font_size",
            self.backend.ITEM_FONT_SIZE
        )

        self.settings.setValue(
            "label/buyer_font_size",
            self.backend.BUYER_FONT_SIZE
        )

        self.settings.setValue(
            "label/username_font_size",
            self.backend.USERNAME_FONT_SIZE
        )

        self.settings.sync()

        self.update_preview()


    def reset_layout_defaults(self):

        self.label_width_spin.setValue(
            2.0
        )

        self.label_height_spin.setValue(
            2.0
        )

        self.safe_margin_spin.setValue(
            28
        )

        self.vertical_offset_spin.setValue(
            -12
        )

        self.item_font_spin.setValue(
            62
        )

        self.buyer_font_spin.setValue(
            34
        )

        self.username_font_spin.setValue(
            30
        )

        self.save_label_settings()

        self.status_label.setText(
            "Label layout restored to defaults."
        )


    # ========================================================
    # WINDOW / SPLITTER PERSISTENCE
    # ========================================================

    def restore_window_layout(self):

        geometry = self.settings.value(
            "window/geometry"
        )

        if geometry is not None:

            self.restoreGeometry(
                geometry
            )


        main_splitter_state = self.settings.value(
            "window/main_splitter"
        )

        if main_splitter_state is not None:

            self.main_splitter.restoreState(
                main_splitter_state
            )


        preview_splitter_state = self.settings.value(
            "window/preview_splitter"
        )

        if preview_splitter_state is not None:

            self.preview_splitter.restoreState(
                preview_splitter_state
            )


    def save_window_layout(self):

        self.settings.setValue(
            "window/geometry",
            self.saveGeometry()
        )

        self.settings.setValue(
            "window/main_splitter",
            self.main_splitter.saveState()
        )

        self.settings.setValue(
            "window/preview_splitter",
            self.preview_splitter.saveState()
        )

        self.settings.sync()


    def closeEvent(
        self,
        event: QCloseEvent
    ):

        self.save_window_layout()

        super().closeEvent(
            event
        )


    # ========================================================
    # UI
    # ========================================================

    def build_ui(self):

        # ----------------------------------------------------
        # SCROLLABLE OUTER SHELL
        # ----------------------------------------------------

        scroll_area = QScrollArea()

        scroll_area.setWidgetResizable(
            True
        )

        scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        self.setCentralWidget(
            scroll_area
        )


        content_widget = QWidget()

        scroll_area.setWidget(
            content_widget
        )


        main_layout = QVBoxLayout(
            content_widget
        )

        main_layout.setContentsMargins(
            12,
            12,
            12,
            12
        )

        main_layout.setSpacing(
            10
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
        # PRINTER
        # ----------------------------------------------------

        printer_group = QGroupBox(
            "Printer"
        )

        printer_layout = QHBoxLayout(
            printer_group
        )


        printer_layout.addWidget(
            QLabel("Windows Printer:")
        )


        self.printer_combo = QComboBox()


        self.refresh_printers_button = QPushButton(
            "Refresh Printers"
        )


        printer_layout.addWidget(
            self.printer_combo,
            stretch=1
        )

        printer_layout.addWidget(
            self.refresh_printers_button
        )


        main_layout.addWidget(
            printer_group
        )


        # ----------------------------------------------------
        # MANUAL LABEL
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

        session_outer_layout = QVBoxLayout(
            session_group
        )


        session_count_layout = QHBoxLayout()


        self.item_count_label = QLabel(
            "Item: 0"
        )

        self.givvy_count_label = QLabel(
            "Givvy: 0"
        )

        self.buyer_count_label = QLabel(
            "Buyers: 0"
        )

        self.next_buyer_label = QLabel(
            "Next Buyer: B#01"
        )


        for label in (
            self.item_count_label,
            self.givvy_count_label,
            self.buyer_count_label,
            self.next_buyer_label,
        ):

            label.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            label.setStyleSheet(
                """
                font-size: 17px;
                font-weight: bold;
                padding: 8px;
                """
            )


        session_count_layout.addWidget(
            self.item_count_label
        )

        session_count_layout.addWidget(
            self.givvy_count_label
        )

        session_count_layout.addWidget(
            self.buyer_count_label
        )

        session_count_layout.addWidget(
            self.next_buyer_label
        )


        session_outer_layout.addLayout(
            session_count_layout
        )


        number_control_layout = QHBoxLayout()


        self.set_item_button = QPushButton(
            "Set Next Item #"
        )

        self.reset_givvy_button = QPushButton(
            "Reset Givvy #"
        )

        self.set_buyer_button = QPushButton(
            "Set Next Buyer #"
        )

        self.reset_buyers_button = QPushButton(
            "Reset Buyer #s"
        )

        self.reset_session_button = QPushButton(
            "Reset Session"
        )


        number_control_layout.addWidget(
            self.set_item_button
        )

        number_control_layout.addWidget(
            self.reset_givvy_button
        )

        number_control_layout.addWidget(
            self.set_buyer_button
        )

        number_control_layout.addWidget(
            self.reset_buyers_button
        )

        number_control_layout.addWidget(
            self.reset_session_button
        )


        session_outer_layout.addLayout(
            number_control_layout
        )


        main_layout.addWidget(
            session_group
        )


        # ----------------------------------------------------
        # ADJUSTABLE MAIN WORK AREA
        # ----------------------------------------------------
        #
        # This vertical splitter lets you drag the boundary
        # between the preview/settings area and label history.
        #

        self.main_splitter = QSplitter(
            Qt.Orientation.Vertical
        )

        self.main_splitter.setChildrenCollapsible(
            False
        )

        self.main_splitter.setHandleWidth(
            7
        )


        # ----------------------------------------------------
        # PREVIEW + SETTINGS
        # ----------------------------------------------------

        preview_group = QGroupBox(
            "Label Preview & Layout"
        )

        preview_group_layout = QVBoxLayout(
            preview_group
        )


        # A second splitter lets you resize the preview
        # and settings columns horizontally.
        self.preview_splitter = QSplitter(
            Qt.Orientation.Horizontal
        )

        self.preview_splitter.setChildrenCollapsible(
            False
        )

        self.preview_splitter.setHandleWidth(
            7
        )


        # LEFT: PREVIEW
        preview_widget = QWidget()

        preview_left_layout = QVBoxLayout(
            preview_widget
        )


        self.preview_type_combo = QComboBox()

        self.preview_type_combo.addItems(
            [
                "Sale",
                "Givvy",
            ]
        )


        preview_left_layout.addWidget(
            self.preview_type_combo
        )


        self.preview_label = QLabel()

        self.preview_label.setMinimumSize(
            220,
            220
        )

        self.preview_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.preview_label.setStyleSheet(
            """
            background: white;
            border: 1px solid #999999;
            """
        )


        preview_left_layout.addWidget(
            self.preview_label,
            stretch=1
        )


        # RIGHT: SETTINGS
        settings_widget = QWidget()

        settings_outer_layout = QVBoxLayout(
            settings_widget
        )

        settings_layout = QFormLayout()


        self.label_width_spin = QDoubleSpinBox()

        self.label_width_spin.setRange(
            0.50,
            4.25
        )

        self.label_width_spin.setDecimals(
            2
        )

        self.label_width_spin.setSingleStep(
            0.25
        )

        self.label_width_spin.setSuffix(
            " in"
        )

        self.label_width_spin.setValue(
            self.backend.LABEL_WIDTH_INCHES
        )


        self.label_height_spin = QDoubleSpinBox()

        self.label_height_spin.setRange(
            0.50,
            6.00
        )

        self.label_height_spin.setDecimals(
            2
        )

        self.label_height_spin.setSingleStep(
            0.25
        )

        self.label_height_spin.setSuffix(
            " in"
        )

        self.label_height_spin.setValue(
            self.backend.LABEL_HEIGHT_INCHES
        )


        self.safe_margin_spin = QSpinBox()

        self.safe_margin_spin.setRange(
            0,
            100
        )

        self.safe_margin_spin.setValue(
            self.backend.SAFE_MARGIN
        )


        self.vertical_offset_spin = QSpinBox()

        self.vertical_offset_spin.setRange(
            -150,
            150
        )

        self.vertical_offset_spin.setSuffix(
            " px"
        )

        self.vertical_offset_spin.setValue(
            self.backend.VERTICAL_OFFSET
        )


        self.item_font_spin = QSpinBox()

        self.item_font_spin.setRange(
            10,
            120
        )

        self.item_font_spin.setValue(
            self.backend.ITEM_FONT_SIZE
        )


        self.buyer_font_spin = QSpinBox()

        self.buyer_font_spin.setRange(
            10,
            100
        )

        self.buyer_font_spin.setValue(
            self.backend.BUYER_FONT_SIZE
        )


        self.username_font_spin = QSpinBox()

        self.username_font_spin.setRange(
            10,
            100
        )

        self.username_font_spin.setValue(
            self.backend.USERNAME_FONT_SIZE
        )


        settings_layout.addRow(
            "Label Width:",
            self.label_width_spin
        )

        settings_layout.addRow(
            "Label Height:",
            self.label_height_spin
        )

        settings_layout.addRow(
            "Safe Margin:",
            self.safe_margin_spin
        )

        settings_layout.addRow(
            "Vertical Offset:",
            self.vertical_offset_spin
        )

        settings_layout.addRow(
            "Item/Givvy Font:",
            self.item_font_spin
        )

        settings_layout.addRow(
            "Buyer Font:",
            self.buyer_font_spin
        )

        settings_layout.addRow(
            "Username Font:",
            self.username_font_spin
        )


        settings_outer_layout.addLayout(
            settings_layout
        )


        reset_defaults_button = QPushButton(
            "Reset Layout Defaults"
        )

        reset_defaults_button.clicked.connect(
            self.reset_layout_defaults
        )


        settings_outer_layout.addWidget(
            reset_defaults_button
        )

        settings_outer_layout.addStretch()


        self.preview_splitter.addWidget(
            preview_widget
        )

        self.preview_splitter.addWidget(
            settings_widget
        )


        self.preview_splitter.setStretchFactor(
            0,
            2
        )

        self.preview_splitter.setStretchFactor(
            1,
            1
        )


        preview_group_layout.addWidget(
            self.preview_splitter
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


        self.history_table.setMinimumHeight(
            180
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


        # Add both areas to the adjustable vertical splitter.
        self.main_splitter.addWidget(
            preview_group
        )

        self.main_splitter.addWidget(
            history_group
        )


        self.main_splitter.setStretchFactor(
            0,
            1
        )

        self.main_splitter.setStretchFactor(
            1,
            1
        )


        main_layout.addWidget(
            self.main_splitter,
            stretch=1
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

        self.status_label.setWordWrap(
            True
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

        self.printer_combo.currentTextChanged.connect(
            self.handle_printer_changed
        )

        self.refresh_printers_button.clicked.connect(
            self.refresh_printer_list
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


        self.set_item_button.clicked.connect(
            self.choose_next_item_number
        )

        self.reset_givvy_button.clicked.connect(
            self.confirm_reset_givvies
        )

        self.set_buyer_button.clicked.connect(
            self.choose_next_buyer_number
        )

        self.reset_buyers_button.clicked.connect(
            self.confirm_reset_buyers
        )

        self.reset_session_button.clicked.connect(
            self.confirm_reset_session
        )


        self.preview_type_combo.currentTextChanged.connect(
            self.update_preview
        )

        self.username_input.textChanged.connect(
            self.update_preview
        )


        for spin_box in (
            self.label_width_spin,
            self.label_height_spin,
            self.safe_margin_spin,
            self.vertical_offset_spin,
            self.item_font_spin,
            self.buyer_font_spin,
            self.username_font_spin,
        ):

            spin_box.valueChanged.connect(
                self.save_label_settings
            )


    # ========================================================
    # GENERAL HELPERS
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

        self.next_buyer_label.setText(
            f"Next Buyer: "
            f"B#{self.backend.get_next_buyer_number():02d}"
        )


    # ========================================================
    # LIVE PREVIEW
    # ========================================================

    def update_preview(
        self,
        *args
    ):

        username = (
            self.get_username()
            or "sample_buyer"
        )


        if username in self.backend.buyers:

            buyer_number = (
                self.backend
                .buyers[username]
            )

        else:

            buyer_number = (
                self.backend
                .get_next_buyer_number()
            )


        preview_type = (
            self.preview_type_combo
            .currentText()
        )


        if preview_type == "Givvy":

            sequence_number = (
                self.backend.givvy_number
                + 1
            )

            top_text = (
                f"GIVVY "
                f"{sequence_number:02d}"
            )

        else:

            sequence_number = (
                self.backend.item_number
                + 1
            )

            top_text = (
                f"ITEM "
                f"{sequence_number:03d}"
            )


        preview_dir = Path(
            "data"
        )

        preview_dir.mkdir(
            exist_ok=True
        )


        preview_path = (
            preview_dir
            / "preview.png"
        )


        try:

            self.backend.create_text_label(
                top_text,
                buyer_number,
                username,
                preview_path,
            )


            pixmap = QPixmap(
                str(preview_path)
            )


            available_size = (
                self.preview_label.size()
            )


            pixmap = pixmap.scaled(
                available_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )


            self.preview_label.setPixmap(
                pixmap
            )


        except Exception as error:

            self.preview_label.setText(
                f"Preview error:\n{error}"
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
    # PRINTERS
    # ========================================================

    def get_windows_printers(
        self
    ):

        flags = (
            win32print.PRINTER_ENUM_LOCAL
            | win32print.PRINTER_ENUM_CONNECTIONS
        )


        try:

            printer_info = (
                win32print.EnumPrinters(
                    flags,
                    None,
                    1,
                )
            )

        except Exception as error:

            print(
                f"Could not enumerate printers: "
                f"{error!r}"
            )

            return []


        printer_names = {
            printer[2]
            for printer in printer_info
            if len(printer) > 2
            and printer[2]
        }


        return sorted(
            printer_names,
            key=str.lower,
        )


    def get_default_printer_name(
        self
    ):

        try:

            return (
                win32print.GetDefaultPrinter()
            )

        except Exception:

            return None


    def refresh_printer_list(
        self
    ):

        printers = (
            self.get_windows_printers()
        )


        saved_printer = (
            self.settings.value(
                "printer/name",
                ""
            )
            or ""
        )


        preferred_printer = (
            saved_printer
            or self.backend.PRINTER_NAME
        )


        default_printer = (
            self.get_default_printer_name()
        )


        self.printer_combo.blockSignals(
            True
        )

        self.printer_combo.clear()


        if not printers:

            self.printer_combo.addItem(
                "No Windows printers found"
            )

            self.printer_combo.setEnabled(
                False
            )

            self.printer_combo.blockSignals(
                False
            )

            self.status_label.setText(
                "No Windows printers found."
            )

            return


        self.printer_combo.setEnabled(
            True
        )


        self.printer_combo.addItems(
            printers
        )


        if preferred_printer in printers:

            selected_printer = (
                preferred_printer
            )

        elif default_printer in printers:

            selected_printer = (
                default_printer
            )

        else:

            selected_printer = (
                printers[0]
            )


        index = (
            self.printer_combo
            .findText(
                selected_printer
            )
        )


        self.printer_combo.setCurrentIndex(
            index
        )


        self.printer_combo.blockSignals(
            False
        )


        self.backend.PRINTER_NAME = (
            selected_printer
        )


        self.settings.setValue(
            "printer/name",
            selected_printer
        )

        self.settings.sync()


        self.status_label.setText(
            f"Printer selected: "
            f"{selected_printer}"
        )


    def handle_printer_changed(
        self,
        printer_name
    ):

        printer_name = (
            printer_name.strip()
        )


        if (
            not printer_name
            or printer_name
            == "No Windows printers found"
        ):

            return


        self.backend.PRINTER_NAME = (
            printer_name
        )


        self.settings.setValue(
            "printer/name",
            printer_name
        )

        self.settings.sync()


        self.status_label.setText(
            f"Printer selected: "
            f"{printer_name}"
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
            self.update_preview()

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

        self.update_preview()


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
            self.update_preview()

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

        self.update_preview()


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
            self.update_preview()

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
        self.update_preview()


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
            self.update_preview()

            self.status_label.setText(
                f"F8 sale error: {error}"
            )

            return


        self.refresh_session()
        self.refresh_history()
        self.update_preview()


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
            self.update_preview()

            self.status_label.setText(
                f"Givvy error: {error}"
            )

            return


        self.refresh_session()
        self.refresh_history()
        self.update_preview()


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
    # SET / RESET NUMBER DIALOGS
    # ========================================================

    def choose_next_item_number(
        self
    ):

        suggested_number = (
            self.backend.item_number
            + 1
        )


        number, accepted = (
            QInputDialog.getInt(
                self,
                "Set Next Item Number",
                (
                    "What number should the "
                    "NEXT sale use?"
                ),
                suggested_number,
                1,
                999999,
                1,
            )
        )


        if not accepted:
            return


        self.backend.set_next_item_number(
            number
        )

        self.refresh_session()
        self.update_preview()


        self.status_label.setText(
            f"Next sale will be "
            f"Item {number:03d}."
        )


    def choose_next_buyer_number(
        self
    ):

        suggested_number = (
            self.backend
            .get_next_buyer_number()
        )


        number, accepted = (
            QInputDialog.getInt(
                self,
                "Set Next Buyer Number",
                (
                    "What number should the "
                    "NEXT NEW buyer receive?"
                ),
                suggested_number,
                1,
                99999,
                1,
            )
        )


        if not accepted:
            return


        existing_username = None


        for username, buyer_number in (
            self.backend.buyers.items()
        ):

            if buyer_number == number:

                existing_username = username
                break


        if existing_username is not None:

            answer = QMessageBox.warning(
                self,
                "Buyer Number Already Assigned",
                (
                    f"B#{number:02d} is currently assigned "
                    f"to @{existing_username}.\n\n"
                    "Using it again would create two active "
                    "buyers with the same buyer number.\n\n"
                    "Set it anyway?"
                ),
                (
                    QMessageBox.StandardButton.Yes
                    | QMessageBox.StandardButton.No
                ),
                QMessageBox.StandardButton.No,
            )


            if (
                answer
                != QMessageBox.StandardButton.Yes
            ):

                return


        self.backend.set_next_buyer_number(
            number
        )

        self.refresh_session()
        self.update_preview()


        self.status_label.setText(
            f"Next new buyer will be "
            f"B#{number:02d}."
        )


    def confirm_reset_givvies(
        self
    ):

        answer = QMessageBox.question(
            self,
            "Reset Givvy Number?",
            (
                "Reset the givvy number to 0?\n\n"
                "The next givvy will be Givvy 01.\n"
                "Label history will NOT be deleted."
            ),
            (
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No
            ),
            QMessageBox.StandardButton.No,
        )


        if answer == QMessageBox.StandardButton.Yes:

            self.handle_reset_givvies()


    def confirm_reset_buyers(
        self
    ):

        answer = QMessageBox.question(
            self,
            "Reset Buyer Numbers?",
            (
                "Clear ALL current buyer-number assignments?\n\n"
                "The next buyer will become B#01.\n"
                "Existing label history will NOT be deleted."
            ),
            (
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No
            ),
            QMessageBox.StandardButton.No,
        )


        if answer == QMessageBox.StandardButton.Yes:

            self.handle_reset_buyers()


    def confirm_reset_session(
        self
    ):

        answer = QMessageBox.question(
            self,
            "Reset Entire Session?",
            (
                "Reset ALL current session counters?\n\n"
                "• Item number → 0\n"
                "• Givvy number → 0\n"
                "• Buyer assignments → cleared\n"
                "• Next buyer → B#01\n\n"
                "SQLite label history will NOT be deleted."
            ),
            (
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No
            ),
            QMessageBox.StandardButton.No,
        )


        if answer == QMessageBox.StandardButton.Yes:

            self.handle_reset_session()


    # ========================================================
    # RESET ACTIONS
    # ========================================================

    def handle_reset_items(
        self
    ):

        self.backend.reset_item_number()

        self.refresh_session()
        self.update_preview()

        self.status_label.setText(
            "Item number reset. "
            "Next sale will be Item 001."
        )


    def handle_reset_givvies(
        self
    ):

        self.backend.reset_givvy_number()

        self.refresh_session()
        self.update_preview()

        self.status_label.setText(
            "Givvy number reset. "
            "Next givvy will be Givvy 01."
        )


    def handle_reset_buyers(
        self
    ):

        self.backend.reset_buyer_numbers()

        self.refresh_session()
        self.update_preview()

        self.status_label.setText(
            "Buyer assignments reset. "
            "Next buyer will be B#01."
        )


    def handle_reset_session(
        self
    ):

        self.backend.reset_session()

        self.refresh_session()
        self.update_preview()

        self.status_label.setText(
            "Session reset. History preserved."
        )

        self.last_event_label.setText(
            "New session started."
        )
