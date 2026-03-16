"""
Whistle Report Generator API v1
Generates branded football report PNGs.
Outputs files locally with predictable names for manual upload workflow.
"""

from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.image_generator import generate_reports, BASE_DIR

app = FastAPI(title="Whistle Report Generator", version="1.0.0")


class ReportRequest(BaseModel):
    team_logo: str
    primary_color: str
    secondary_color: str
    client_name: Optional[str] = None
    row_id: Optional[str] = None


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/generate-reports")
def create_reports(req: ReportRequest):
    """
    Generate branded report PNGs.
    Saves files locally with predictable names.
    """
    # Build folder name from client_name, row_id, or fallback
    if req.client_name:
        folder_name = req.client_name
    elif req.row_id:
        folder_name = f"row_{req.row_id}"
    else:
        folder_name = "output"

    result = generate_reports(
        team_name=folder_name,
        logo_filename=req.team_logo,
        primary_color=req.primary_color,
        secondary_color=req.secondary_color,
    )

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])

    # Build predictable filename for manual upload
    safe_name = folder_name.lower().replace(" ", "_")
    output_folder = result["output_folder"]

    # Console output for clarity
    print("\n" + "=" * 50)
    print("RENDER COMPLETE")
    print("=" * 50)
    print(f"Client/Row:      {folder_name}")
    print(f"Output folder:   {output_folder}")
    print(f"Files generated: {len(result['generated_files'])}")
    print("-" * 50)
    for f in result["generated_files"]:
        print(f"  - {f}")
    print("-" * 50)
    print(f"Primary file:    {safe_name}_slide13.png")
    print(f"Full path:       {BASE_DIR / output_folder}")
    print("=" * 50 + "\n")

    return {
        "success": True,
        "client_name": folder_name,
        "output_folder": output_folder,
        "output_path": str(BASE_DIR / output_folder),
        "primary_filename": f"{safe_name}_slide13.png",
        "generated_files": result["generated_files"],
    }
