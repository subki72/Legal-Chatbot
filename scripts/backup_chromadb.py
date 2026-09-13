#!/usr/bin/env python3
"""Automated Backup and Disaster Recovery Utility for ChromaDB Vector Database.

Creates compressed tar.gz archives of ChromaDB persistent state and enforces
retention policies to preserve disk space.
"""

import glob
import logging
import os
import sys
import tarfile
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("BackupChromaDB")

PROJECT_ROOT: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE_DIR: str = os.path.join(PROJECT_ROOT, "Data", "chroma")
BACKUP_DIR: str = os.path.join(PROJECT_ROOT, "backups")
MAX_BACKUPS_RETAINED: int = 7


def ensure_dirs() -> None:
    """Ensure the target backup directory exists."""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR, exist_ok=True)
        logger.info(f"Created backup directory at: {BACKUP_DIR}")


def verify_source_integrity() -> bool:
    """Verify that the source directory exists and contains valid data files.

    Returns:
        bool: True if source directory contains files, False otherwise.
    """
    if not os.path.exists(SOURCE_DIR):
        logger.warning(
            f"Source directory '{SOURCE_DIR}' does not exist. No data available to backup."
        )
        return False

    files = os.listdir(SOURCE_DIR)
    if not files:
        logger.warning(f"Source directory '{SOURCE_DIR}' is empty.")
        return False

    logger.info(f"Source directory verified with {len(files)} items present.")
    return True


def create_backup() -> str:
    """Compress the persistent ChromaDB data directory into a timestamped tar.gz archive.

    Returns:
        str: Absolute path to the created backup archive, or empty string on failure.

    Raises:
        Exception: If archive creation fails.
    """
    ensure_dirs()
    if not verify_source_integrity():
        return ""

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"chromadb_backup_{timestamp}.tar.gz"
    backup_path = os.path.join(BACKUP_DIR, backup_filename)

    logger.info(f"Creating compressed backup archive: {backup_filename}...")
    try:
        with tarfile.open(backup_path, "w:gz") as tar:
            tar.add(SOURCE_DIR, arcname="chroma")

        size_mb = os.path.getsize(backup_path) / (1024 * 1024)
        logger.info(f"Backup created successfully: {size_mb:.2f} MB at {backup_path}")
        return backup_path
    except Exception as e:
        logger.error(f"Failed to create backup archive: {e}")
        if os.path.exists(backup_path):
            os.remove(backup_path)
        raise


def enforce_retention_policy() -> None:
    """Prune historical backup archives exceeding MAX_BACKUPS_RETAINED."""
    pattern = os.path.join(BACKUP_DIR, "chromadb_backup_*.tar.gz")
    backups = sorted(glob.glob(pattern), key=os.path.getmtime)

    if len(backups) > MAX_BACKUPS_RETAINED:
        excess = len(backups) - MAX_BACKUPS_RETAINED
        logger.info(
            f"Purging {excess} older backup archives to satisfy retention limit ({MAX_BACKUPS_RETAINED})..."
        )
        for old_backup in backups[:excess]:
            try:
                os.remove(old_backup)
                logger.info(f"Removed archive: {os.path.basename(old_backup)}")
            except Exception as e:
                logger.warning(f"Failed to remove old backup archive {old_backup}: {e}")


def main() -> None:
    """Orchestrate the backup execution workflow."""
    logger.info("Initiating ChromaDB automated backup procedure...")
    try:
        created = create_backup()
        if created:
            enforce_retention_policy()
            logger.info("Backup and retention procedure completed successfully.")
        else:
            logger.info("No backup archive was created.")
    except Exception as e:
        logger.error(f"Backup procedure terminated with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
