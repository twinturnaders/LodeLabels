import json
from datetime import date
from pathlib import Path
from threading import Lock

import keyboard
import pyperclip
import win32ui

from PIL import (
    Image,
    ImageDraw,
    ImageFont,
    ImageWin,
)

import history_db

from sale_listener import (
    start_sale_listener,
)


# ============================================================
# CONFIGURATION
# ============================================================

PRINTER_NAME = "PPG A40 SD"

PRINTER_DPI = 203
LABEL_SIZE = int(2 * PRINTER_DPI)

SAFE_MARGIN = 28
VERTICAL_OFFSET = -12

ITEM_FONT_SIZE = 62
BUYER_FONT_SIZE = 34
USERNAME_FONT_SIZE = 30


# ============================================================
# DIRECTORIES
# ============================================================

LABELS_DIR = Path("labels")
LABELS_DIR.mkdir(exist_ok=True)

SESSIONS_DIR = Path("sessions")
SESSIONS_DIR.mkdir(exist_ok=True)

current_date = date.today().isoformat()

SESSION_FILE = (
    SESSIONS_DIR
    / f"session_{current_date}.json"
)


# ============================================================
# DATABASE
# ============================================================

history_db.init_db()


# ============================================================
# SESSION
# ============================================================

session_lock = Lock()


def load_session():

    if not SESSION_FILE.exists():

        return {
            "item_number": 0,
            "givvy_number": 0,
            "buyers": {},
            "next_buyer_number": None,
        }

    try:

        with SESSION_FILE.open(
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(file)

    except (
        json.JSONDecodeError,
        OSError,
    ):

        print(
            "Warning: Could not read session file."
        )

        return {
            "item_number": 0,
            "givvy_number": 0,
            "buyers": {},
            "next_buyer_number": None,
        }

    return {
        "item_number": data.get(
            "item_number",
            0,
        ),

        "givvy_number": data.get(
            "givvy_number",
            0,
        ),

        "buyers": data.get(
            "buyers",
            {},
        ),

        "next_buyer_number": data.get(
            "next_buyer_number"
        ),
    }


session = load_session()


buyers = session.get(
    "buyers",
    {},
)

item_number = session.get(
    "item_number",
    0,
)

givvy_number = session.get(
    "givvy_number",
    0,
)


stored_next_buyer_number = (
    session.get(
        "next_buyer_number"
    )
)


# Backward compatibility for older session JSON files.
if stored_next_buyer_number is None:

    next_buyer_number = (
        max(
            buyers.values(),
            default=0,
        )
        + 1
    )

else:

    next_buyer_number = max(
        1,
        int(
            stored_next_buyer_number
        ),
    )


auto_print_enabled = False


def save_session():

    data = {
        "item_number": item_number,
        "givvy_number": givvy_number,
        "buyers": buyers,
        "next_buyer_number": next_buyer_number,
    }

    with SESSION_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
        )


# Automatically upgrade older session files.
save_session()


# ============================================================
# BUYERS
# ============================================================

def get_next_buyer_number():

    return next_buyer_number


def get_buyer_number(
    username
):

    global next_buyer_number

    if username not in buyers:

        buyers[username] = (
            next_buyer_number
        )

        next_buyer_number += 1

    return buyers[username]


# ============================================================
# USERNAME HELPERS
# ============================================================

def clean_username(
    username
):

    if username is None:
        return ""

    username = username.strip()

    if username.startswith("@"):
        username = username[1:]

    return username.strip()


def get_clipboard_text():

    try:

        return clean_username(
            pyperclip.paste()
        )

    except Exception as error:

        print(
            f"Clipboard error: "
            f"{error!r}"
        )

        return ""


# ============================================================
# FONTS
# ============================================================

def load_font(
    size,
    bold=False,
):

    font_names = [
        (
            "arialbd.ttf"
            if bold
            else "arial.ttf"
        ),
        (
            "segoeuib.ttf"
            if bold
            else "segoeui.ttf"
        ),
        (
            "calibrib.ttf"
            if bold
            else "calibri.ttf"
        ),
    ]

    for font_name in font_names:

        try:

            return ImageFont.truetype(
                font_name,
                size,
            )

        except OSError:

            continue

    print(
        "Warning: Could not load "
        "TrueType font."
    )

    return ImageFont.load_default()


def fit_font(
    draw,
    text,
    starting_size,
    max_width,
    bold=False,
):

    size = starting_size

    while size >= 10:

        font = load_font(
            size,
            bold=bold,
        )

        bbox = draw.textbbox(
            (0, 0),
            text,
            font=font,
        )

        width = (
            bbox[2]
            - bbox[0]
        )

        if width <= max_width:
            return font

        size -= 2

    return load_font(
        10,
        bold=bold,
    )


# ============================================================
# LABEL CREATION
# ============================================================

def create_text_label(
    top_text,
    buyer_number,
    username,
    output_path,
):

    image = Image.new(
        "RGB",
        (
            LABEL_SIZE,
            LABEL_SIZE,
        ),
        "white",
    )

    draw = ImageDraw.Draw(
        image
    )

    buyer_text = (
        f"B#{buyer_number:02d}"
    )

    username_text = (
        f"@{username}"
    )

    max_width = (
        LABEL_SIZE
        - (
            SAFE_MARGIN * 2
        )
    )

    top_font = fit_font(
        draw,
        top_text,
        ITEM_FONT_SIZE,
        max_width,
        bold=True,
    )

    buyer_font = fit_font(
        draw,
        buyer_text,
        BUYER_FONT_SIZE,
        max_width,
        bold=True,
    )

    username_font = fit_font(
        draw,
        username_text,
        USERNAME_FONT_SIZE,
        max_width,
    )

    lines = [
        (
            top_text,
            top_font,
        ),
        (
            buyer_text,
            buyer_font,
        ),
        (
            username_text,
            username_font,
        ),
    ]

    spacing = 14

    measurements = []

    total_height = 0

    for text, font in lines:

        bbox = draw.textbbox(
            (0, 0),
            text,
            font=font,
        )

        width = (
            bbox[2]
            - bbox[0]
        )

        height = (
            bbox[3]
            - bbox[1]
        )

        measurements.append(
            (
                text,
                font,
                width,
                height,
            )
        )

        total_height += height

    total_height += (
        spacing
        * (
            len(lines) - 1
        )
    )

    y = (
        (
            LABEL_SIZE
            - total_height
        )
        / 2
        + VERTICAL_OFFSET
    )

    for (
        text,
        font,
        width,
        height,
    ) in measurements:

        x = (
            LABEL_SIZE
            - width
        ) / 2

        draw.text(
            (
                x,
                y,
            ),
            text,
            fill="black",
            font=font,
        )

        y += (
            height
            + spacing
        )

    image.save(
        output_path
    )

    return output_path


def create_label(
    item_number,
    buyer_number,
    username,
):

    safe_username = (
        username
        .replace("/", "_")
        .replace("\\", "_")
    )

    file_name = (
        f"item_{item_number:03d}"
        f"_buyer_{buyer_number:02d}"
        f"_{safe_username}.png"
    )

    output_path = (
        LABELS_DIR
        / file_name
    )

    return create_text_label(
        f"ITEM {item_number:03d}",
        buyer_number,
        username,
        output_path,
    )


def create_givvy_label(
    givvy_number,
    buyer_number,
    username,
):

    safe_username = (
        username
        .replace("/", "_")
        .replace("\\", "_")
    )

    file_name = (
        f"givvy_{givvy_number:02d}"
        f"_buyer_{buyer_number:02d}"
        f"_{safe_username}.png"
    )

    output_path = (
        LABELS_DIR
        / file_name
    )

    return create_text_label(
        f"GIVVY {givvy_number:02d}",
        buyer_number,
        username,
        output_path,
    )


# ============================================================
# PRINTING
# ============================================================

def print_label(
    file_path
):

    printer_dc = None

    try:

        image = Image.open(
            file_path
        ).convert(
            "RGB"
        )

        printer_dc = (
            win32ui.CreateDC()
        )

        printer_dc.CreatePrinterDC(
            PRINTER_NAME
        )

        printable_width = (
            printer_dc.GetDeviceCaps(
                8
            )
        )

        printable_height = (
            printer_dc.GetDeviceCaps(
                10
            )
        )

        dib = ImageWin.Dib(
            image
        )

        printer_dc.StartDoc(
            "LodeLabels"
        )

        printer_dc.StartPage()

        dib.draw(
            printer_dc.GetHandleOutput(),
            (
                0,
                0,
                printable_width,
                printable_height,
            ),
        )

        printer_dc.EndPage()
        printer_dc.EndDoc()

        print(
            f"Printed: {file_path}"
        )

    except Exception as error:

        print(
            f"Print error: "
            f"{error!r}"
        )

        raise

    finally:

        if printer_dc is not None:

            try:

                printer_dc.DeleteDC()

            except Exception:

                pass


# ============================================================
# HISTORY HELPERS
# ============================================================

def record_history(
    label_type,
    sequence_number,
    buyer_number,
    username,
    label_path,
):

    try:

        return history_db.add_label(
            label_type=label_type,
            sequence_number=sequence_number,
            buyer_number=buyer_number,
            username=username,
            file_path=label_path,
        )

    except Exception as error:

        print(
            "History database error: "
            f"{error!r}"
        )

        return None


def get_recent_history(
    limit=50
):

    return history_db.get_recent_labels(
        limit
    )


def reprint_history_label(
    label_id
):

    row = history_db.get_label(
        label_id
    )

    if row is None:

        raise ValueError(
            "History record not found."
        )

    label_path = Path(
        row["file_path"]
    )

    if not label_path.exists():

        raise FileNotFoundError(
            f"Label file no longer exists: "
            f"{label_path}"
        )

    try:

        print_label(
            label_path
        )

        history_db.mark_print_success(
            label_id
        )

    except Exception as error:

        history_db.mark_print_failure(
            label_id,
            error,
        )

        raise

    return history_db.get_label(
        label_id
    )


# ============================================================
# SALE PROCESSING
# ============================================================

def process_sale(
    username
):

    global item_number

    username = clean_username(
        username
    )

    if not username:

        print(
            "No username provided."
        )

        return None

    with session_lock:

        buyer_number = (
            get_buyer_number(
                username
            )
        )

        item_number += 1

        sequence_number = (
            item_number
        )

        save_session()

        label_path = create_label(
            sequence_number,
            buyer_number,
            username,
        )

    history_id = record_history(
        label_type="sale",
        sequence_number=sequence_number,
        buyer_number=buyer_number,
        username=username,
        label_path=label_path,
    )

    try:

        print_label(
            label_path
        )

        if history_id is not None:

            history_db.mark_print_success(
                history_id
            )

    except Exception as error:

        if history_id is not None:

            history_db.mark_print_failure(
                history_id,
                error,
            )

        raise

    print(
        f"Item #{sequence_number:03d} | "
        f"Buyer #{buyer_number:02d}: "
        f"{username}"
    )

    return {
        "history_id": history_id,
        "type": "sale",
        "sequence_number": sequence_number,
        "buyer_number": buyer_number,
        "username": username,
        "file_path": label_path,
    }


def handle_sale():

    process_sale(
        get_clipboard_text()
    )


# ============================================================
# GIVVY PROCESSING
# ============================================================

def process_givvy(
    username
):

    global givvy_number

    username = clean_username(
        username
    )

    if not username:

        print(
            "No username provided."
        )

        return None

    with session_lock:

        buyer_number = (
            get_buyer_number(
                username
            )
        )

        givvy_number += 1

        sequence_number = (
            givvy_number
        )

        save_session()

        label_path = (
            create_givvy_label(
                sequence_number,
                buyer_number,
                username,
            )
        )

    history_id = record_history(
        label_type="givvy",
        sequence_number=sequence_number,
        buyer_number=buyer_number,
        username=username,
        label_path=label_path,
    )

    try:

        print_label(
            label_path
        )

        if history_id is not None:

            history_db.mark_print_success(
                history_id
            )

    except Exception as error:

        if history_id is not None:

            history_db.mark_print_failure(
                history_id,
                error,
            )

        raise

    print(
        f"Givvy #{sequence_number:02d} | "
        f"Buyer #{buyer_number:02d}: "
        f"{username}"
    )

    return {
        "history_id": history_id,
        "type": "givvy",
        "sequence_number": sequence_number,
        "buyer_number": buyer_number,
        "username": username,
        "file_path": label_path,
    }


def handle_givvy():

    process_givvy(
        get_clipboard_text()
    )


# ============================================================
# AUTO PRINT
# ============================================================

def set_auto_print(
    enabled
):

    global auto_print_enabled

    auto_print_enabled = bool(
        enabled
    )

    status = (
        "ON"
        if auto_print_enabled
        else "OFF"
    )

    print()
    print(
        "=============================="
    )
    print(
        f"AUTO PRINT: {status}"
    )
    print(
        "=============================="
    )
    print()


def toggle_auto_print():

    set_auto_print(
        not auto_print_enabled
    )


def process_auto_sale(
    username
):

    username = clean_username(
        username
    )

    if not auto_print_enabled:

        print(
            f"Auto sale ignored: "
            f"{username} "
            f"(Auto Print OFF)"
        )

        return False

    print(
        f"Auto sale accepted: "
        f"{username}"
    )

    process_sale(
        username
    )

    return True


# ============================================================
# NUMBER / SESSION CONTROLS
# ============================================================

def reset_item_number():

    global item_number

    with session_lock:

        item_number = 0

        save_session()

    print(
        "Item number reset to 0. "
        "Next sale will be Item #001."
    )


def set_next_item_number(
    next_number
):

    global item_number

    next_number = int(
        next_number
    )

    if next_number < 1:

        raise ValueError(
            "Next item number must be at least 1."
        )

    with session_lock:

        # Sale processing increments the stored value before
        # creating the label.
        item_number = (
            next_number - 1
        )

        save_session()

    print(
        f"Next sale will be "
        f"Item #{next_number:03d}."
    )


def reset_givvy_number():

    global givvy_number

    with session_lock:

        givvy_number = 0

        save_session()

    print(
        "Givvy number reset to 0. "
        "Next givvy will be Givvy #01."
    )


def reset_buyer_numbers():

    global next_buyer_number

    with session_lock:

        buyers.clear()

        next_buyer_number = 1

        save_session()

    print(
        "Buyer numbers reset. "
        "Next buyer will be B#01."
    )


def set_next_buyer_number(
    next_number
):

    global next_buyer_number

    next_number = int(
        next_number
    )

    if next_number < 1:

        raise ValueError(
            "Next buyer number must be at least 1."
        )

    with session_lock:

        next_buyer_number = (
            next_number
        )

        save_session()

    print(
        f"Next new buyer will be "
        f"B#{next_number:02d}."
    )


def reset_session():

    global item_number
    global givvy_number
    global next_buyer_number

    with session_lock:

        item_number = 0
        givvy_number = 0
        next_buyer_number = 1

        buyers.clear()

        save_session()

    print()
    print(
        "=============================="
    )
    print(
        "SESSION RESET"
    )
    print(
        "Item #: 0"
    )
    print(
        "Givvy #: 0"
    )
    print(
        "Buyers: 0"
    )
    print(
        "Next Buyer #: 1"
    )
    print(
        "History preserved."
    )
    print(
        "=============================="
    )
    print()


# ============================================================
# REPRINT LATEST
# ============================================================

def test_print_latest_label():

    rows = (
        history_db.get_recent_labels(
            1
        )
    )

    if rows:

        reprint_history_label(
            rows[0]["id"]
        )

        return

    # Fallback for labels created before SQLite history existed.
    label_files = list(
        LABELS_DIR.glob(
            "*.png"
        )
    )

    if not label_files:

        print(
            "No labels found."
        )

        return

    latest_label = max(
        label_files,
        key=lambda path: (
            path.stat().st_mtime
        ),
    )

    print_label(
        latest_label
    )


# ============================================================
# CLI MODE
# ============================================================

def run_cli():

    keyboard.add_hotkey(
        "f8",
        handle_sale,
    )

    keyboard.add_hotkey(
        "ctrl+g",
        handle_givvy,
    )

    keyboard.add_hotkey(
        "ctrl+r",
        reset_item_number,
    )

    keyboard.add_hotkey(
        "ctrl+shift+g",
        reset_givvy_number,
    )

    keyboard.add_hotkey(
        "ctrl+p",
        test_print_latest_label,
    )

    keyboard.add_hotkey(
        "ctrl+alt+a",
        toggle_auto_print,
    )

    sale_server = (
        start_sale_listener(
            process_auto_sale
        )
    )

    print(
        "LodeLabels running."
    )

    print(
        f"Item #: {item_number}"
    )

    print(
        f"Givvy #: {givvy_number}"
    )

    print(
        f"Buyers: {len(buyers)}"
    )

    print(
        f"Next Buyer #: "
        f"{next_buyer_number}"
    )

    print(
        "Auto Print starts OFF."
    )

    _ = sale_server

    keyboard.wait(
        "esc"
    )


# ============================================================
# ENTRY
# ============================================================

if __name__ == "__main__":

    run_cli()