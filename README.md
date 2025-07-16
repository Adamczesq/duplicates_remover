Advanced File Cleaner
A Python script to automatically scan a folder, identify and move corrupted media files and duplicates, helping you clean up your digital clutter.

Features
Corruption Check: Scans for corrupted images (.jpg, .png) and audio files (.mp3) by attempting to verify their integrity.
Duplicate Check: Identifies duplicate files of any type by comparing their SHA-256 hashes.
Safe Operation: Instead of deleting, it safely moves corrupted and duplicate files to separate subfolders (./corrupted and ./duplicates).
User-Friendly: Features a graphical user interface (GUI) to select the target folder, so no command-line path typing is needed.
Robust Progress Bar: Provides real-time feedback in the console, showing the progress of scanning operations, even with very long filenames.

Requirements
Python 3.7+
Pillow
mutagen

Installation
Clone or download the script to your local machine.
Open a terminal or command prompt and install the required libraries using pip:

Bash
pip install Pillow mutagen

How to Use
Ensure you have completed the installation steps above.

Run the script from your terminal:

Bash
python file_doubles_remover.py

A dialog window will appear. Navigate to and select the folder you wish to clean up.
The script will begin processing in two stages. You can monitor the progress directly in your terminal window.
Once finished, you will find two new subfolders inside your target directory:
corrupted/: Contains all files that failed the integrity check.
duplicates/: Contains all duplicate files, keeping one original copy in place.

How It Works
The script operates in a two-stage pipeline to ensure efficiency and accuracy:

Stage 1: Corruption Check
The script first iterates through all supported files (.jpg, .png, .mp3). It uses the Pillow library to verify images and the mutagen library to check audio files. Any file that raises an exception during this process is considered corrupted and moved to the corrupted folder.

Stage 2: Duplicate Check
All files that passed the corruption check are then processed for duplicates. The script calculates a unique SHA-256 hash for each file's content. Files that share the same hash are duplicates. The script keeps the first file it encountered as the original and moves all subsequent copies to the duplicates folder.

License
This project is licensed under the MIT License. See the LICENSE file for details.
