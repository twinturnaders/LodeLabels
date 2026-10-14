import json
from datetime import date
from pathlib import Path

import keyboard
import pyperclip
import win32ui
from PIL import Image, ImageDraw, ImageFont, ImageWin
from sale_listener import start_sale_listener

PRINTER_NAME = "PPG A40 SD"


# -------------------------
# Folder / file setup
# -------------------------

LABELS_DIR = Path("labels")
LABELS_DIR.mkdir(exist_ok=True)

SESSIONS_DIR = Path("sessions")
SESSIONS_DIR.mkdir(exist_ok=True)

current_date = date.today().isoformat()
SESSION_FILE = SESSIONS_DIR / f"session_{current_date}.json"


# -------------------------
# Label settings
# -------------------------

PRINTER_DPI = 203
LABEL_SIZE = int(2 * PRINTER_DPI)  # 2" x 2" = 406 px at 203 DPI

SAFE_MARGIN = 28
VERTICAL_OFFSET = -12

ITEM_FONT_SIZE = 62
BUYER_FONT_SIZE = 34
USERNAME_FONT_SIZE = 30

buyers = ...
item_number = ...
givvy_number = ...

auto_print_enabled = False
# -------------------------
# Printing
# -------------------------

def print_label(file_path):
    try:
        printer_dc = win32ui.CreateDC()
        printer_dc.CreatePrinterDC(PRINTER_NAME)

        printable_width = printer_dc.GetDeviceCaps(8)    # HORZRES
        printable_height = printer_dc.GetDeviceCaps(10)  # VERTRES

        image = Image.open(file_path).convert("RGB")
        image_width, image_height = image.size

        scale = min(
            printable_width / image_width,
            printable_height / image_height
        )

        print_width = int(image_width * scale)
        print_height = int(image_height * scale)

        x = (printable_width - print_width) // 2
        y = ((printable_height - print_height) // 2) + VERTICAL_OFFSET

        dib = ImageWin.Dib(image)

        printer_dc.StartDoc("LodeLabels")
        printer_dc.StartPage()

        dib.draw(
            printer_dc.GetHandleOutput(),
            (
                x,
                y,
                x + print_width,
                y + print_height
            )
        )

        printer_dc.EndPage()
        printer_dc.EndDoc()
        printer_dc.DeleteDC()

        print(f"Printed successfully to {PRINTER_NAME}")
        return True

    except Exception as error:
        print(f"Printing failed: {error}")
        return False


def test_print_latest_label():
    label_files = sorted(LABELS_DIR.glob("*.png"))

    if not label_files:
        print("No label files found to print.")
        return

    latest_label = label_files[-1]

    print(f"Printing latest label: {latest_label}")
    print_label(latest_label)


# -------------------------
# Session persistence
# -------------------------

def load_session():
    if not SESSION_FILE.exists():
        return {
            "item_number": 0,
            "givvy_number": 0,
            "buyers": {}
        }

    with open(SESSION_FILE, "r") as file:
        return json.load(file)


session = load_session()

buyers = session.get("buyers", {})
item_number = session.get("item_number", 0)
givvy_number = session.get("givvy_number", 0)


def save_session():
    session_data = {
        "item_number": item_number,
        "givvy_number": givvy_number,
        "buyers": buyers
    }

    with open(SESSION_FILE, "w") as file:
        json.dump(session_data, file, indent=4)


save_session()


# -------------------------
# Clipboard input
# -------------------------

def get_clipboard_text():
    return pyperclip.paste().strip()


# -------------------------
# Buyer logic
# -------------------------

def get_next_buyer_number():
    if not buyers:
        return 1

    return max(buyers.values()) + 1


def get_buyer_number(username):
    if username in buyers:
        return buyers[username]

    buyer_number = get_next_buyer_number()
    buyers[username] = buyer_number

    save_session()

    return buyer_number


# -------------------------
# Counter controls
# -------------------------

def reset_item_number(number=0):
    global item_number

    item_number = number
    save_session()

    print(f"Item number set to {item_number}.")


def reset_givvy_number(number=0):
    global givvy_number

    givvy_number = number
    save_session()

    print(f"Givvy number set to {givvy_number}.")


# -------------------------
# Font / text helpers
# -------------------------

def load_font(size, bold=False):
    font_names = [
        "arialbd.ttf" if bold else "arial.ttf",
        "segoeuib.ttf" if bold else "segoeui.ttf",
        "calibrib.ttf" if bold else "calibri.ttf"
    ]

    for font_name in font_names:
        try:
            return ImageFont.truetype(font_name, size)
        except OSError:
            continue

    print("Warning: Could not load TrueType font. Using default font.")
    return ImageFont.load_default()


def get_text_size(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)

    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]

    return width, height


def centered_x(draw, text, font):
    text_width, _ = get_text_size(draw, text, font)
    return (LABEL_SIZE - text_width) // 2


def fit_font(draw, text, start_size, min_size, max_width, bold=False):
    font_size = start_size

    while font_size >= min_size:
        font = load_font(font_size, bold=bold)
        text_width, _ = get_text_size(draw, text, font)

        if text_width <= max_width:
            return font

        font_size -= 2

    return load_font(min_size, bold=bold)


# -------------------------
# Filename helper
# -------------------------

def sanitize_filename(text):
    safe_text = "".join(
        char if char.isalnum() or char in ("-", "_") else "_"
        for char in text
    )

    return safe_text[:50]


# -------------------------
# Regular sale label
# -------------------------

def create_label(item_number, buyer_number, username):
    image = Image.new(
        "RGB",
        (LABEL_SIZE, LABEL_SIZE),
        "white"
    )

    draw = ImageDraw.Draw(image)

    item_text = f"ITEM {item_number:03d}"
    buyer_text = f"B#{buyer_number:02d}"
    username_text = f"@{username}"

    safe_width = LABEL_SIZE - (SAFE_MARGIN * 2)

    item_font = fit_font(
        draw,
        item_text,
        start_size=ITEM_FONT_SIZE,
        min_size=28,
        max_width=safe_width - 20,
        bold=True
    )

    buyer_font = fit_font(
        draw,
        buyer_text,
        start_size=BUYER_FONT_SIZE,
        min_size=20,
        max_width=safe_width - 40,
        bold=True
    )

    username_font = fit_font(
        draw,
        username_text,
        start_size=USERNAME_FONT_SIZE,
        min_size=18,
        max_width=safe_width - 30,
        bold=False
    )

    _, item_height = get_text_size(
        draw,
        item_text,
        item_font
    )

    _, buyer_height = get_text_size(
        draw,
        buyer_text,
        buyer_font
    )

    _, username_height = get_text_size(
        draw,
        username_text,
        username_font
    )

    gap_1 = 18
    gap_2 = 12

    total_height = (
        item_height
        + gap_1
        + buyer_height
        + gap_2
        + username_height
    )

    start_y = (
        (LABEL_SIZE - total_height) // 2
    ) + VERTICAL_OFFSET

    item_x = centered_x(
        draw,
        item_text,
        item_font
    )
    item_y = start_y

    buyer_x = centered_x(
        draw,
        buyer_text,
        buyer_font
    )
    buyer_y = item_y + item_height + gap_1

    username_x = centered_x(
        draw,
        username_text,
        username_font
    )
    username_y = buyer_y + buyer_height + gap_2

    draw.text(
        (item_x, item_y),
        item_text,
        font=item_font,
        fill="black"
    )

    draw.text(
        (buyer_x, buyer_y),
        buyer_text,
        font=buyer_font,
        fill="black"
    )

    draw.text(
        (username_x, username_y),
        username_text,
        font=username_font,
        fill="black"
    )

    safe_username = sanitize_filename(username)

    file_path = LABELS_DIR / (
        f"item_{item_number:03d}_"
        f"buyer_{buyer_number:02d}_"
        f"{safe_username}.png"
    )

    image.save(file_path)

    return file_path


# -------------------------
# Giveaway label
# -------------------------

def create_givvy_label(givvy_number, buyer_number, username):
    image = Image.new(
        "RGB",
        (LABEL_SIZE, LABEL_SIZE),
        "white"
    )

    draw = ImageDraw.Draw(image)

    givvy_text = f"GIVVY {givvy_number:02d}"
    buyer_text = f"B#{buyer_number:02d}"
    username_text = f"@{username}"

    safe_width = LABEL_SIZE - (SAFE_MARGIN * 2)

    givvy_font = fit_font(
        draw,
        givvy_text,
        start_size=ITEM_FONT_SIZE,
        min_size=28,
        max_width=safe_width - 20,
        bold=True
    )

    buyer_font = fit_font(
        draw,
        buyer_text,
        start_size=BUYER_FONT_SIZE,
        min_size=20,
        max_width=safe_width - 40,
        bold=True
    )

    username_font = fit_font(
        draw,
        username_text,
        start_size=USERNAME_FONT_SIZE,
        min_size=18,
        max_width=safe_width - 30,
        bold=False
    )

    _, givvy_height = get_text_size(
        draw,
        givvy_text,
        givvy_font
    )

    _, buyer_height = get_text_size(
        draw,
        buyer_text,
        buyer_font
    )

    _, username_height = get_text_size(
        draw,
        username_text,
        username_font
    )

    gap_1 = 18
    gap_2 = 12

    total_height = (
        givvy_height
        + gap_1
        + buyer_height
        + gap_2
        + username_height
    )

    start_y = (
        (LABEL_SIZE - total_height) // 2
    ) + VERTICAL_OFFSET

    givvy_x = centered_x(
        draw,
        givvy_text,
        givvy_font
    )
    givvy_y = start_y

    buyer_x = centered_x(
        draw,
        buyer_text,
        buyer_font
    )
    buyer_y = givvy_y + givvy_height + gap_1

    username_x = centered_x(
        draw,
        username_text,
        username_font
    )
    username_y = buyer_y + buyer_height + gap_2

    draw.text(
        (givvy_x, givvy_y),
        givvy_text,
        font=givvy_font,
        fill="black"
    )

    draw.text(
        (buyer_x, buyer_y),
        buyer_text,
        font=buyer_font,
        fill="black"
    )

    draw.text(
        (username_x, username_y),
        username_text,
        font=username_font,
        fill="black"
    )

    safe_username = sanitize_filename(username)

    file_path = LABELS_DIR / (
        f"givvy_{givvy_number:02d}_"
        f"buyer_{buyer_number:02d}_"
        f"{safe_username}.png"
    )

    image.save(file_path)

    return file_path


# -------------------------
# Regular sale event
# -------------------------

def process_sale(username):
    global item_number

    username = username.strip()

    if username.startswith("@"):
        username = username[1:]

    if username == "":
        print("No username provided.")
        return

    buyer_number = get_buyer_number(username)

    item_number += 1

    save_session()

    label_path = create_label(
        item_number,
        buyer_number,
        username
    )

    print_label(label_path)

    print(
        f"Item #{item_number:03d} | "
        f"Buyer #{buyer_number:02d}: "
        f"{username}"
    )

    print(f"Label created: {label_path}")

def process_auto_sale(username):
    if not auto_print_enabled:
        print(
            f"Auto sale ignored: {username} "
            f"(Auto Print OFF)"
        )
        return

    print(
        f"Auto sale accepted: {username}"
    )

    process_sale(username)
def handle_sale():
    username = get_clipboard_text()

    process_sale(username)


# -------------------------
# Giveaway event
# -------------------------

def handle_givvy():
    global givvy_number

    username = get_clipboard_text()

    if username == "":
        print("No username found in clipboard.")
        return

    buyer_number = get_buyer_number(username)

    givvy_number += 1
    save_session()

    label_path = create_givvy_label(
        givvy_number,
        buyer_number,
        username
    )

    print_label(label_path)

    print(
        f"Givvy #{givvy_number:02d} | "
        f"Buyer #{buyer_number:02d}: {username}"
    )

    print(f"Givvy label created: {label_path}")
def toggle_auto_print():
    global auto_print_enabled

    auto_print_enabled = not auto_print_enabled

    status = (
        "ON"
        if auto_print_enabled
        else "OFF"
    )

    print()
    print("==============================")
    print(f"AUTO PRINT: {status}")
    print("==============================")
    print()
sale_server = start_sale_listener(
    process_auto_sale
)
# -------------------------
# Program startup
# -------------------------

print("LodeLabels is running.")
print(f"Printer: {PRINTER_NAME}")
print(f"Session file: {SESSION_FILE}")
print(f"Loaded {len(buyers)} existing buyers.")
print(f"Current item number: {item_number}")
print(f"Current givvy number: {givvy_number}")
print()

print("F8                Capture sale")
print("Ctrl + G          Capture givvy")
print("Ctrl + R          Reset item number")
print("Ctrl + Shift + G  Reset givvy number")
print("Ctrl + P          Print latest label")
print("ESC               Quit")
print("Ctrl+Alt+A = Toggle Auto Print")
print("Auto Print starts OFF")

# -------------------------
# Hotkeys
# -------------------------
keyboard.add_hotkey(
    "ctrl+alt+a",
    toggle_auto_print
)
keyboard.add_hotkey(
    "f8",
    handle_sale
)

keyboard.add_hotkey(
    "ctrl+g",
    handle_givvy
)

keyboard.add_hotkey(
    "ctrl+r",
    reset_item_number
)

keyboard.add_hotkey(
    "ctrl+shift+g",
    reset_givvy_number
)

keyboard.add_hotkey(
    "ctrl+p",
    test_print_latest_label
)


keyboard.wait("esc")
