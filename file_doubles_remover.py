import os
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

def move_corrupted_files(source_folder: Path, corrupted_folder: Path):
    print("--- ETAP 1: Sprawdzanie uszkodzonych plików ---")
    corrupted_folder.mkdir(parents = True, exist_ok = True)
    
    all_files = [p for p in source_folder.rglob('*') if p.suffix.lower() in SUPPORTED_EXTENSIONS and p.is_file()]
    moved_count = 0
    
    for i, file_path in enumerate(all_files):
        print(f"Sprawdzanie [{i + 1} / {len(all_files)}]: {file_path.name}", end = '\r')
        if not is_file_valid(file_path):
            target_path = handle_filename_conflict(corrupted_folder / file_path.name)
            try:
                shutil.move(str(file_path), str(target_path))
                print(f"\nPRZENIESIONO USZKODZONY: {file_path.name}")
                moved_count += 1
            except Exception as e:
                print(f"\nBŁĄD przenoszenia {file_path.name}: {e}")

    print(f"\nZakończono Etap 1. Przeniesiono {moved_count} uszkodzonych plików.")


def move_duplicate_files(source_folder: Path, duplicates_folder: Path):
    print("\n--- ETAP 2: Wyszukiwanie duplikatów ---")
    duplicates_folder.mkdir(parents = True, exist_ok = True)

    hashes = defaultdict(list)
    remaining_files = [p for p in source_folder.rglob('*') if p.suffix.lower() in SUPPORTED_EXTENSIONS and p.is_file()]

    if not remaining_files:
        print("Brak plików do sprawdzenia.")
        return

    print(f"Skanowanie {len(remaining_files)} pozostałych plików...")

    for i, file_path in enumerate(remaining_files, 1):
        print(f"Skanowanie [{i}/{len(remaining_files)}]: {file_path.name}", end='\r')
        file_hash = get_file_hash(file_path)
        if file_hash:
            hashes[file_hash].append(file_path)

    print(" " * 100, end='\r')

    moved_count = 0
    duplicate_groups = {h: p for h, p in hashes.items() if len(p) > 1}

    if not duplicate_groups:
        print("Nie znaleziono żadnych duplikatów.")
        return

    for group in duplicate_groups.values():
        group.sort()
        original = group[0]
        files_to_move = group[1:]
        print(f"Znaleziono grupę duplikatów. Oryginał: {original.name}")

        for file_path in files_to_move:
            target_path = handle_filename_conflict(duplicates_folder / file_path.name)
            try:
                shutil.move(str(file_path), str(target_path))
                print(f"  -> Przeniesiono duplikat: {file_path.name}")
                moved_count += 1
            except Exception as e:
                print(f"  -> BŁĄD przenoszenia {file_path.name}: {e}")

    print(f"\nZakończono Etap 2. Przeniesiono {moved_count} duplikatów.")

if __name__ == "__main__":
    source_folder_str = input("Podaj ścieżkę do folderu, który chcesz posprzątać: ")
    source_path = Path(source_folder_str)
    
    if not source_path.is_dir():
        print("Błąd: Podana ścieżka nie jest prawidłowym folderem.")
    else:
        corrupted_path = Path("D:/corrupted_files")
        duplicates_path = Path("D:/duplicate_files")

        move_corrupted_files(source_path, corrupted_path)
        move_duplicate_files(source_path, duplicates_path)
        
        print("Sprzątanie zakończone!")