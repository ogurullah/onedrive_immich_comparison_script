
import subprocess
import directories
from pathlib import Path

quarantine = Path(directories.recoverOnedrive)

for file in sorted(quarantine.iterdir()):
    if not file.is_file():
        continue

    result = subprocess.run(
        [
            "exiftool",
            "-s",
            "-s",
            "-s",
            "-DateTimeOriginal",
            "-CreateDate",
            "-MediaCreateDate",
            "-TrackCreateDate",
            "-FileCreateDate",
            str(file),
        ],
        capture_output=True,
        text=True,
    )

    print(f"\n{file.name}")
    print(result.stdout.strip() or "No recognized date metadata")
    if result.stderr:
        print("Error:", result.stderr.strip())
