"""
Google Drive upload module.
Handles authentication and file uploads using a service account.
"""

import os
from pathlib import Path
from typing import Optional

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Configuration
CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
DRIVE_PARENT_FOLDER_ID = os.getenv("DRIVE_PARENT_FOLDER_ID", "")

SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def load_credentials():
    """Load service account credentials from JSON file."""
    creds_path = Path(CREDENTIALS_FILE)
    if not creds_path.exists():
        raise FileNotFoundError(f"Service account credentials not found: {CREDENTIALS_FILE}")

    return service_account.Credentials.from_service_account_file(
        str(creds_path), scopes=SCOPES
    )


def get_drive_service():
    """Create and return a Google Drive API service instance."""
    creds = load_credentials()
    return build("drive", "v3", credentials=creds)


def find_folder(service, folder_name: str, parent_id: str) -> Optional[str]:
    """Find a folder by name within a parent folder. Returns folder ID or None."""
    query = (
        f"name = '{folder_name}' and "
        f"'{parent_id}' in parents and "
        f"mimeType = 'application/vnd.google-apps.folder' and "
        f"trashed = false"
    )
    results = service.files().list(
        q=query,
        spaces="drive",
        fields="files(id, name)",
        pageSize=1,
    ).execute()

    files = results.get("files", [])
    return files[0]["id"] if files else None


def create_folder(service, folder_name: str, parent_id: str) -> str:
    """Create a folder in Drive. Returns the new folder ID."""
    metadata = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id],
    }
    folder = service.files().create(body=metadata, fields="id").execute()
    return folder["id"]


def get_or_create_folder(service, folder_name: str, parent_id: str) -> str:
    """Find existing folder or create new one. Returns folder ID."""
    folder_id = find_folder(service, folder_name, parent_id)
    if folder_id:
        return folder_id
    return create_folder(service, folder_name, parent_id)


def find_file_in_folder(service, filename: str, folder_id: str) -> Optional[str]:
    """Find a file by name in a folder. Returns file ID or None."""
    query = (
        f"name = '{filename}' and "
        f"'{folder_id}' in parents and "
        f"trashed = false"
    )
    results = service.files().list(
        q=query,
        spaces="drive",
        fields="files(id, name)",
        pageSize=1,
    ).execute()

    files = results.get("files", [])
    return files[0]["id"] if files else None


def delete_file(service, file_id: str):
    """Delete a file by ID."""
    service.files().delete(fileId=file_id).execute()


def upload_file(service, local_path: Path, folder_id: str, replace_existing: bool = True) -> dict:
    """
    Upload a file to a Drive folder.
    If replace_existing is True, deletes any existing file with the same name first.
    Returns dict with file_id and web view link.
    """
    filename = local_path.name

    # Delete existing file if it exists
    if replace_existing:
        existing_id = find_file_in_folder(service, filename, folder_id)
        if existing_id:
            delete_file(service, existing_id)

    # Upload new file
    metadata = {
        "name": filename,
        "parents": [folder_id],
    }
    media = MediaFileUpload(str(local_path), mimetype="image/png", resumable=True)

    uploaded = service.files().create(
        body=metadata,
        media_body=media,
        fields="id, webViewLink",
    ).execute()

    return {
        "file_id": uploaded["id"],
        "web_view_link": uploaded.get("webViewLink", f"https://drive.google.com/file/d/{uploaded['id']}/view"),
    }


def upload_reports_to_drive(local_folder: Path, team_folder_name: str) -> dict:
    """
    Upload all PNG files from a local folder to Google Drive.

    Args:
        local_folder: Path to local folder containing PNGs
        team_folder_name: Name of subfolder to create/use in Drive

    Returns:
        dict with drive_folder_id and list of uploaded file metadata
    """
    if not DRIVE_PARENT_FOLDER_ID:
        raise ValueError("DRIVE_PARENT_FOLDER_ID environment variable not set")

    service = get_drive_service()

    # Create or find team subfolder
    drive_folder_id = get_or_create_folder(service, team_folder_name, DRIVE_PARENT_FOLDER_ID)

    # Get all PNG files sorted by name to preserve order
    png_files = sorted(local_folder.glob("*.png"))

    uploaded_files = []
    for png_path in png_files:
        result = upload_file(service, png_path, drive_folder_id)
        uploaded_files.append({
            "filename": png_path.name,
            "local_path": str(png_path),
            "drive_file_id": result["file_id"],
            "drive_link": result["web_view_link"],
        })

    return {
        "drive_folder_id": drive_folder_id,
        "uploaded_files": uploaded_files,
    }
