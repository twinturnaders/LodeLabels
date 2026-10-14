LODELABELS
==========

A small Windows utility for printing 2-inch Whatnot sale and giveaway labels
to a PeriPage A40 printer.

PROJECT CONTENTS
----------------
main.py
requirements.txt
install.bat
run.bat
README.txt
sessions/
labels/

FIRST-TIME SETUP
----------------
1. Make sure Python is installed.
2. Make sure the PeriPage A40 Windows driver is installed.
3. Make sure Windows sees the printer as:

   PPG A40 SD

   If your printer has a different name, edit PRINTER_NAME near the top of main.py.

4. Double-click:

   install.bat

   This creates a local .venv and installs the dependencies.

5. After setup finishes, double-click:

   run.bat

HOTKEYS
-------
F8                Capture normal sale
Ctrl + G          Capture giveaway
Ctrl + R          Reset item number
Ctrl + Shift + G  Reset giveaway number
Ctrl + P          Reprint latest saved PNG label
ESC               Quit

WORKFLOW
--------
Copy the buyer username from Whatnot to the Windows clipboard.

For a normal sale:
    Copy username -> F8

For a giveaway:
    Copy username -> Ctrl + G

DATA
----
Daily session state is stored under:

    sessions/session_YYYY-MM-DD.json

Generated labels are stored under:

    labels/

A new dated JSON file is automatically created on a new day.
