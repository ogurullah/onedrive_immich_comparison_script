
import csv
import json
import re
import subprocess
from pathlib import Path
from datetime import datetime

# Directories
recoverOnedrive = Path("/Volumes/Storage/OneDrive/VDF-Quarantine")
onedriveDir = Path("/Volumes/Storage/OneDrive/Resimler/Film Rulosu")

# Report location — outside the quarantine folder
reportPath = Path.home() / "Desktop" / "onedrive_recovery_report.csv"

# Metadata fields to inspect.
# FileCreateDate / FileModifyDate are intentionally excluded.
DATE_TAGS = [
    "DateTimeOriginal",
    "CreateDate",
    "MediaCreateDate",
    "TrackCreateDate",
    "CreationDate",
]

# Date fields we consider reliable enough to suggest a destination.
PRIORITY_TAGS = [
    "DateTimeOriginal",
    "MediaCreateDate",
    "CreateDate",
    "TrackCreateDate",
    "CreationDate",
]


def parse_date(value):
    """Parse common ExifTool date formats."""
    if not value:
        return None

    value = str(value).strip()

    # Remove timezone suffix for folder placement.
    # We only need the date's year and month.
    value = re.sub(r"([+-]\d{2}:\d{2}|Z)$", "", value)

    formats = [
        "%Y:%m:%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y:%m:%d",
        "%Y-%m-%d",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(value[:19], fmt)
        except ValueError:
            continue

    return None


def get_tag_name(tag):
    """Remove ExifTool group prefix, e.g. EXIF:DateTimeOriginal."""
    return tag.split(":")[-1]


def get_metadata(file_path):
    """Read metadata for one file using ExifTool JSON output."""
    command = [
        "exiftool",
        "-json",
        "-G1",
        *[f"-{tag}" for tag in DATE_TAGS],
        str(file_path),
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True,
    )

    data = json.loads(result.stdout)

    return data[0] if data else {}


def get_filename_date(file_path):
    """
    Fallback for iPhone-style filenames such as:
    20220408_175203339_iOS.heic

    Only used when embedded date metadata is unavailable.
    """
    match = re.match(
        r"^(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})",
        file_path.stem,
    )

    if not match:
        return None

    try:
        year, month, day, hour, minute, second = map(
            int, match.groups()
        )

        return datetime(year, month, day, hour, minute, second)

    except ValueError:
        return None


def determine_date(metadata, file_path):
    """
    Return selected date, selected field, status,
    and all usable metadata date candidates.
    """
    candidates = []

    for tag, value in metadata.items():
        tag_name = get_tag_name(tag)

        if tag_name not in DATE_TAGS:
            continue

        parsed = parse_date(value)

        if parsed:
            candidates.append({
                "tag": tag,
                "value": value,
                "date": parsed,
            })

    # Look for disagreement between metadata fields.
    # Different year/month means we should not blindly trust
    # the selected destination.
    date_groups = {
        (item["date"].year, item["date"].month)
        for item in candidates
    }

    if len(date_groups) > 1:
        return None, None, "REVIEW_DATE_CONFLICT", candidates

    # Select the highest-priority available metadata field.
    for preferred_tag in PRIORITY_TAGS:
        for candidate in candidates:
            if get_tag_name(candidate["tag"]) == preferred_tag:
                return (
                    candidate["date"],
                    candidate["tag"],
                    "METADATA_DATE",
                    candidates,
                )

    # Filename fallback — lower confidence than embedded metadata.
    filename_date = get_filename_date(file_path)

    if filename_date:
        return (
            filename_date,
            "Filename",
            "REVIEW_FILENAME_FALLBACK",
            candidates,
        )

    return None, None, "REVIEW_NO_DATE", candidates


def main():
    if not recoverOnedrive.exists():
        raise FileNotFoundError(
            f"Quarantine directory does not exist: {recoverOnedrive}"
        )

    if not onedriveDir.exists():
        raise FileNotFoundError(
            f"Original archive directory does not exist: {onedriveDir}"
        )

    files = sorted(
        path for path in recoverOnedrive.rglob("*")
        if path.is_file()
    )

    print(f"Found {len(files)} files.")
    print("Generating report only. No files will be moved.")

    rows = []

    for index, file_path in enumerate(files, start=1):
        print(f"[{index}/{len(files)}] {file_path.name}")

        try:
            metadata = get_metadata(file_path)

            date, date_source, status, candidates = determine_date(
                metadata, file_path
            )

            candidate_summary = " | ".join(
                f'{item["tag"]}={item["value"]}'
                for item in candidates
            )

            destination = ""
            destination_exists = False

            if date:
                year = date.strftime("%Y")
                month = date.strftime("%Y%m") + "__"

                destination = (
                    onedriveDir / year / month / file_path.name
                )

                destination_exists = destination.exists()

                if destination_exists:
                    status = "REVIEW_DESTINATION_EXISTS"

            rows.append({
                "source_path": str(file_path),
                "filename": file_path.name,
                "selected_date": date.isoformat() if date else "",
                "date_source": date_source or "",
                "status": status,
                "suggested_destination": str(destination),
                "destination_exists": destination_exists,
                "metadata_candidates": candidate_summary,
            })

        except Exception as error:
            rows.append({
                "source_path": str(file_path),
                "filename": file_path.name,
                "selected_date": "",
                "date_source": "",
                "status": f"ERROR: {error}",
                "suggested_destination": "",
                "destination_exists": "",
                "metadata_candidates": "",
            })

    fieldnames = [
        "source_path",
        "filename",
        "selected_date",
        "date_source",
        "status",
        "suggested_destination",
        "destination_exists",
        "metadata_candidates",
    ]

    with reportPath.open("w", newline="", encoding="utf-8-sig") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print("\nReport completed.")
    print(f"Report saved to: {reportPath}")
    print(f"Total files: {len(rows)}")


if __name__ == "__main__":
    main()
    