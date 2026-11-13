
import hashlib
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent
TARGET_DIR = BASE_DIR / "test_files"
BASELINE_FILE = BASE_DIR / "baseline.json"


def calculate_hash(file_path):
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


def scan_files():
    file_data = {}

    for file_path in TARGET_DIR.rglob("*"):
        if file_path.is_file():
            relative_path = str(file_path.relative_to(TARGET_DIR))
            file_data[relative_path] = calculate_hash(file_path)

    return file_data


def main():
    TARGET_DIR.mkdir(exist_ok=True)

    current_data = scan_files()

    if not BASELINE_FILE.exists():
        with open(BASELINE_FILE, "w") as file:
            json.dump(current_data, file, indent=4)

        print("Baseline created successfully!")
        print("Files are now being monitored.")
        return

    with open(BASELINE_FILE, "r") as file:
        old_data = json.load(file)

    print("\n--- FILE INTEGRITY REPORT ---")

    added = set(current_data) - set(old_data)
    deleted = set(old_data) - set(current_data)

    changed = {
        name for name in set(current_data) & set(old_data)
        if current_data[name] != old_data[name]
    }

    for name in sorted(added):
        print("[ADDED]   ", name)

    for name in sorted(changed):
        print("[MODIFIED]", name)

    for name in sorted(deleted):
        print("[DELETED] ", name)

    if not added and not changed and not deleted:
        print("[SAFE] No changes detected.")

    print("\nScan completed.")


if __name__ == "__main__":
    main()

