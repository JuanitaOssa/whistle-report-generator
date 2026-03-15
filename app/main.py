"""
Whistle Report Generator API v1
FastAPI service that generates branded football report PNGs and uploads to Google Drive.
"""

from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.image_generator import generate_reports, BASE_DIR
from app.drive_upload import upload_reports_to_drive, DRIVE_PARENT_FOLDER_ID

app = FastAPI(title="Whistle Report Generator", version="1.0.0")


class ReportRequest(BaseModel):
    team_name: str
    team_logo: str
    primary_color: str
    secondary_color: str


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/generate-reports")
def create_reports(req: ReportRequest):
    # Generate images locally
    result = generate_reports(
        team_name=req.team_name,
        logo_filename=req.team_logo,
        primary_color=req.primary_color,
        secondary_color=req.secondary_color,
    )

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])

    # Skip Drive upload if not configured
    if not DRIVE_PARENT_FOLDER_ID:
        generated_files = []
        for filename in result["generated_files"]:
            generated_files.append({
                "filename": filename,
                "local_path": str(Path(result["output_folder"]) / filename),
                "drive_file_id": None,
                "drive_link": None,
            })
        return {
            "success": True,
            "output_folder": result["output_folder"],
            "drive_folder_id": None,
            "generated_files": generated_files,
        }

    # Upload to Google Drive
    local_folder = BASE_DIR / result["output_folder"]
    team_folder_name = f"{req.team_name}_pitch_deck"

    try:
        drive_result = upload_reports_to_drive(local_folder, team_folder_name)
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=f"Drive credentials error: {e}")
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Drive upload failed: {e}")

    # Build response with Drive metadata
    generated_files = []
    for uploaded in drive_result["uploaded_files"]:
        generated_files.append({
            "filename": uploaded["filename"],
            "local_path": str(Path(result["output_folder"]) / uploaded["filename"]),
            "drive_file_id": uploaded["drive_file_id"],
            "drive_link": uploaded["drive_link"],
        })

    return {
        "success": True,
        "output_folder": result["output_folder"],
        "drive_folder_id": drive_result["drive_folder_id"],
        "generated_files": generated_files,
    }
