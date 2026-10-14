import sys

import keyboard

from PySide6.QtCore import (
    QObject,
    Signal,
)

from PySide6.QtWidgets import (
    QApplication,
)

import main as backend

from gui.main_window import (
    MainWindow,
)

from sale_listener import (
    start_sale_listener,
)


# ============================================================
# THREAD-SAFE BRIDGE
# ============================================================

class AppBridge(QObject):

    auto_sale_received = Signal(str)

    clipboard_sale_requested = Signal()
    clipboard_givvy_requested = Signal()

    reprint_requested = Signal()

    toggle_auto_requested = Signal()

    reset_items_requested = Signal()
    reset_givvies_requested = Signal()


# ============================================================
# APPLICATION
# ============================================================

def main():

    app = QApplication(
        sys.argv
    )

    app.setApplicationName(
        "LodeLabels"
    )


    # --------------------------------------------------------
    # WINDOW
    # --------------------------------------------------------

    window = MainWindow(
        backend
    )


    # --------------------------------------------------------
    # QT BRIDGE
    # --------------------------------------------------------

    bridge = AppBridge()


    bridge.auto_sale_received.connect(
        window.handle_auto_sale
    )

    bridge.clipboard_sale_requested.connect(
        window.handle_clipboard_sale
    )

    bridge.clipboard_givvy_requested.connect(
        window.handle_clipboard_givvy
    )

    bridge.reprint_requested.connect(
        window.handle_reprint
    )

    bridge.toggle_auto_requested.connect(
        window.toggle_auto_print_from_hotkey
    )

    bridge.reset_items_requested.connect(
        window.handle_reset_items
    )

    bridge.reset_givvies_requested.connect(
        window.handle_reset_givvies
    )


    # --------------------------------------------------------
    # GLOBAL HOTKEYS
    # --------------------------------------------------------

    keyboard.add_hotkey(
        "f8",
        bridge.clipboard_sale_requested.emit
    )

    keyboard.add_hotkey(
        "ctrl+g",
        bridge.clipboard_givvy_requested.emit
    )

    keyboard.add_hotkey(
        "ctrl+p",
        bridge.reprint_requested.emit
    )

    keyboard.add_hotkey(
        "ctrl+alt+a",
        bridge.toggle_auto_requested.emit
    )

    keyboard.add_hotkey(
        "ctrl+r",
        bridge.reset_items_requested.emit
    )

    keyboard.add_hotkey(
        "ctrl+shift+g",
        bridge.reset_givvies_requested.emit
    )


    # --------------------------------------------------------
    # WHATNOT LISTENER
    # --------------------------------------------------------

    sale_server = None

    try:

        sale_server = start_sale_listener(
            bridge.auto_sale_received.emit
        )

        window.set_listener_status(
            True,
            "Listening on 127.0.0.1:8765"
        )

    except OSError as error:

        window.set_listener_status(
            False,
            "Port 8765 unavailable"
        )

        window.status_label.setText(
            "Could not start Whatnot listener. "
            "Another process may already be using port 8765."
        )

        print(
            f"Listener startup error: {error!r}"
        )


    # --------------------------------------------------------
    # CLEANUP
    # --------------------------------------------------------

    def cleanup():

        print(
            "Closing LodeLabels..."
        )

        try:

            keyboard.unhook_all()

        except Exception:
            pass


        if sale_server is not None:

            try:

                sale_server.shutdown()

            except Exception:
                pass

            try:

                sale_server.server_close()

            except Exception:
                pass


    app.aboutToQuit.connect(
        cleanup
    )


    # Keep objects alive.
    window.app_bridge = bridge
    window.sale_server = sale_server


    window.show()


    sys.exit(
        app.exec()
    )


if __name__ == "__main__":
    main()