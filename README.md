# Whistle Report Generator v1

API service that generates 9 branded football report PNGs from grayscale templates. Replaces template colors with team colors and places the team logo.

## Folder Structure

```
report-image-generator/
├── app/
│   ├── main.py               # FastAPI app
│   ├── image_generator.py    # Image processing logic
│   └── utils.py              # Input normalization helpers
├── templates/
│   └── Football_v1/          # 9 template PNGs
├── logos/                     # Team logo PNGs
├── outputs/                   # Generated reports (gitignored)
├── requirements.txt
├── example_request.json
├── .gitignore
└── README.md
```

## Setup

```bash
git clone <repo-url>
cd report-image-generator
pip install -r requirements.txt
```

## Add Your Assets

1. Place 9 template PNGs in `templates/Football_v1/`
2. Place your team logo PNG in `logos/`

## Start the API

```bash
uvicorn app.main:app --reload
```

Server runs at `http://127.0.0.1:8000`.

## API Endpoints

### Health Check

```bash
curl http://127.0.0.1:8000/health
```

Returns: `{"ok": true}`

### Generate Reports

```bash
curl -X POST http://127.0.0.1:8000/generate-reports \
  -H "Content-Type: application/json" \
  -d @example_request.json
```

Or inline:

```bash
curl -X POST http://127.0.0.1:8000/generate-reports \
  -H "Content-Type: application/json" \
  -d '{
    "team_name": "Indiana Football",
    "team_logo": "indiana_logo.png",
    "primary_color": "990000",
    "secondary_color": "A9A9A9"
  }'
```

Colors work with or without `#`. Logo filename works with or without `.png`.

### Response

```json
{
  "success": true,
  "output_folder": "outputs/Indiana Football_pitch_deck",
  "generated_files": [
    "01_gps_session_report.png",
    "02_drills.png",
    "03_qb_gps_report.png",
    "04_rb_gps_report.png",
    "05_wr_gps_report.png",
    "06_te_gps_report.png",
    "07_ol_gps_report.png",
    "08_dl_gps_report.png",
    "09_lb_gps_report.png"
  ]
}
```

## Output

Generated PNGs are saved to `outputs/{team_name}_pitch_deck/`.

## How It Works

- Replaces template primary `#4A4A4A` with your `primary_color`
- Replaces template secondary `#BDBDBD` with your `secondary_color`
- Places team logo in the top-left corner (0.5% offset, 8% of image size)
- Preserves logo transparency
