"""
Whistle Report Generator API v1
FastAPI service that generates branded football report PNGs.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.image_generator import generate_reports

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
    result = generate_reports(
        team_name=req.team_name,
        logo_filename=req.team_logo,
        primary_color=req.primary_color,
        secondary_color=req.secondary_color,
    )

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])

    return result
