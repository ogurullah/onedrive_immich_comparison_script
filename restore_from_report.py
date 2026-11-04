
import csv
import shutil
from pathlib import Path

# Existing report
reportPath = Path.home() / "Desktop" / "onedrive_recovery_report.csv"

# SMB share mounted on macOS
sharedDir = Path("/Volumes/Storage/Shared")

# New recovery folder on SMB storage
recoveryDir = sharedDir / "Recovered_Film_Rulosu"

ALLOWED_STATUS = "METADATA_DATE"


def main():
    if not reportPath.is_file():
        raise FileNotFoundError(f"Report not found: {reportPath}")

    # Prevent accidentally writing to a local directory if SMB isn't mounted
    if not sharedDir.is_dir():
        raise FileNotFoundError(
            f"SMB Shared directory not found: {sharedDir}\n"
            "Mount the SMB share in Finder before running this script."
        )

    recoveryDir.mkdir(parents=True, exist_ok=True)

    logPath = recoveryDir / "recovery_copy_log.csv"

    copied = 0
    skipped = 0
    errors = 0
    logRows = []

    with reportPath.open("r", newline="", encoding="utf-8-sig") as csvFile:
        reader = csv.DictReader(csvFile)

        for row in reader:
            source = Path(row["source_path"])

            if row["status"] != ALLOWED_STATUS:
                skipped += 1
                continue

            if not source.is_file():
                errors += 1
                print(f"MISSING SOURCE: {source}")
                continue

            # Build folder structure using the selected metadata date
            date = row["selected_date"]

            if not date:
                skipped += 1
                continue

            year = date[:4]
            month = date[:4] + date[5:7] + "__"

            destination = recoveryDir / year / month / source.name

            if destination.exists():
                skipped += 1
                print(f"SKIPPED EXISTING: {destination}")
                continue

            try:
                destination.parent.mkdir(parents=True, exist_ok=True)

                # Copy only — original quarantine files remain untouched
                shutil.copy2(source, destination)

                copied += 1
                print(f"COPIED: {source.name}")

                logRows.append({
                    "source": str(source),
                    "destination": str(destination),
                    "result": "COPIED",
                })

            except Exception as error:
                errors += 1
                print(f"ERROR: {source.name}: {error}")

                logRows.append({
                    "source": str(source),
                    "destination": str(destination),
                    "result": f"ERROR: {error}",
                })

    with logPath.open("w", newline="", encoding="utf-8-sig") as logFile:
        writer = csv.DictWriter(
            logFile,
            fieldnames=["source", "destination", "result"],
        )
        writer.writeheader()
        writer.writerows(logRows)

    print("\nRecovery copy finished.")
    print(f"Copied:  {copied}")
    print(f"Skipped: {skipped}")
    print(f"Errors:  {errors}")
    print(f"Destination: {recoveryDir}")


if __name__ == "__main__":
    main()
