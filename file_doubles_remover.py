import tkinter
from tkinter import filedialog
import hashlib
from pathlib import Path
from collections import defaultdict
import shutil
from PIL import Image
import mutagen

SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.mp3'}
CHUNK_SIZE = 65536

def get_file_hash(path: Path) -> str:
    hasher = hashlib.sha256()
    try:
        with open(path, 'rb') as f:
            while chunk := f.read(CHUNK_SIZE):
                hasher.update(chunk)
        return hasher.hexdigest()
    except (IOError, PermissionError):
        return ""

def is_file_valid(path: Path) -> bool:
    ext = path.suffix.lower()
    try:
        if ext in {'.jpg', '.jpeg', '.png'}:
            with Image.open(path) as img:
                img.verify()
            return True
        elif ext == '.mp3':
            audio = mutagen.File(path)
            if audio is None: return False
            return True
    except Exception:
        return False
    return False

def handle_filename_conflict(target_path: Path) -> Path:
    if not target_path.exists():
        return target_path
    counter = 1
    while True:
        new_name = f"{target_path.stem}_{counter}{target_path.suffix}"
        new_path = target_path.with_name(new_name)
        if not new_path.exists():
            return new_path
        counter += 1

def line_scanning(file_path, i, remaining_files):
    prefix = f"Checking [{i}/{len(remaining_files)}]: "
    max_filename_len = 79 - len(prefix)
    filename = file_path.name
    if len(filename) > max_filename_len:
        filename = filename[:max_filename_len - 20] + "..."
    output_line = f"{prefix}{filename}"
    print(output_line.ljust(79), end='\r', flush=True)


def move_corrupted_files(source_folder: Path, corrupted_folder: Path):
    print("--- STAGE 1: Checking for corrupted files ---")
    corrupted_folder.mkdir(parents=True, exist_ok=True)
    
    all_files = [p for p in source_folder.rglob('*') if p.suffix.lower() in SUPPORTED_EXTENSIONS and p.is_file()]
    valid_files_to_keep = []
    moved_count = 0

    print(f"Scanning {len(all_files)} files for corruption...")
    
    for i, file_path in enumerate(all_files):
        line_scanning(file_path, i, all_files)

        if not is_file_valid(file_path):
            print(" ".ljust(79), end='\r', flush=True)
            target_path = handle_filename_conflict(corrupted_folder / file_path.name)
            try:
                shutil.move(str(file_path), str(target_path))
                print(f"Moved corrupted: {file_path.name}")
                moved_count += 1
            except Exception as e:
                print(f"Transmission error - {file_path.name}: {e}")
        else:
            valid_files_to_keep.append(file_path)

    print(" ".ljust(79), end='\r', flush=True)
    print(f"\nStage 1 finished. Moved {moved_count} corrupted files.")
    return valid_files_to_keep


def move_duplicate_files(files_to_scan: list[Path], duplicates_folder: Path):
    print("\n--- STAGE 2: Searching for duplicates ---")
    duplicates_folder.mkdir(parents=True, exist_ok=True)

    hashes = defaultdict(list)
    remaining_files = files_to_scan

    if not remaining_files:
        print("No files to check.")
        return

    print(f"Scanning {len(remaining_files)} files for duplicates...")

    for i, file_path in enumerate(remaining_files, 1):
        line_scanning(file_path, i, remaining_files)

        file_hash = get_file_hash(file_path)
        if file_hash:
            hashes[file_hash].append(file_path)

    print(" " * 120, end='\r', flush=True)

    moved_count = 0
    duplicate_groups = {h: p for h, p in hashes.items() if len(p) > 1}

    if not duplicate_groups:
        print("No duplicates found.")
        return

    print(f"Found {len(duplicate_groups)} duplicate groups. Moving files ...")

    for group in duplicate_groups.values():
        group.sort()
        original = group[0]
        files_to_move = group[1:]

        print(f"\nOriginal: {original.name}")

        for file_path in files_to_move:
            target_path = handle_filename_conflict(duplicates_folder / file_path.name)
            try:
                shutil.move(str(file_path), str(target_path))
                print(f"  -> Moved duplicate: {file_path.name}")
                moved_count += 1
            except Exception as e:
                print(f"  -> Transmission error - {file_path.name}: {e}")

    print(f"\nStage 2 finished. Moved {moved_count} duplicate files.")


if __name__ == "__main__":
    root = tkinter.Tk()
    root.withdraw()

    print("Please select a folder to clean up in the dialog window...")
    source_folder_str = filedialog.askdirectory(title="Select a folder to clean up")

    if not source_folder_str:
        print("No folder selected. Exiting script.")
    else:
        source_path = Path(source_folder_str)
        print(f"Selected folder: {source_path}")

        if not source_path.is_dir():
            print("Error: The provided path is not a valid folder.")
        else:
            corrupted_path = source_path / "corrupted"
            duplicates_path = source_path / "duplicates"

            valid_files = move_corrupted_files(source_path, corrupted_path)
            move_duplicate_files(valid_files, duplicates_path)

            print("\nCleanup finished!")