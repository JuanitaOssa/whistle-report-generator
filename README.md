# Whistle Report Generator v1

API service that generates branded football report PNGs from grayscale templates. Replaces template colors with team colors and places the team logo.

## Workflow

1. API receives render request with logo, colors, and client info
2. Generates 9 branded PNGs locally
3. Returns predictable filenames and paths
4. User manually downloads and uploads to Google Drive
5. Apps Script uses the uploaded images to build final deck

## Folder Structure

```
whistle-report-generator/
├── app/
│   ├── main.py               # FastAPI app
│   ├── image_generator.py    # Image processing logic
│   └── utils.py              # Input normalization helpers
├── templates/
│   └── Football_v1/          # 9 template PNGs
├── logos/                     # Team logo PNGs
├── outputs/                   # Generated reports (gitignored)
├── requirements.txt
└── README.md
```

## Setup

```bash
git clone <repo-url>
cd whistle-report-generator
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

### Generate Reports

```bash
curl -X POST http://127.0.0.1:8000/generate-reports \
  -H "Content-Type: application/json" \
  -d '{
    "team_logo": "indiana_footbal.png",
    "primary_color": "990000",
    "secondary_color": "A9A9A9",
    "client_name": "Indiana Football",
    "row_id": "5"
  }'
```

**Required fields:**
- `team_logo` - filename of logo in `logos/` folder
- `primary_color` - hex color (with or without `#`)
- `secondary_color` - hex color (with or without `#`)

**Optional fields:**
- `client_name` - used for output folder/filename
- `row_id` - fallback identifier if no client_name

### Response

```json
{
  "success": true,
  "client_name": "Indiana Football",
  "output_folder": "outputs/Indiana Football_pitch_deck",
  "output_path": "/full/path/to/outputs/Indiana Football_pitch_deck",
  "primary_filename": "indiana_football_slide13.png",
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

## Console Output

When a render completes, the console shows:

```
==================================================
RENDER COMPLETE
==================================================
Client/Row:      Indiana Football
Output folder:   outputs/Indiana Football_pitch_deck
Files generated: 9
--------------------------------------------------
  - 01_gps_session_report.png
  - 02_drills.png
  ...
--------------------------------------------------
Primary file:    indiana_football_slide13.png
Full path:       /Users/.../outputs/Indiana Football_pitch_deck
==================================================
```

## Manual Upload Workflow

1. Run the API and trigger a render
2. Navigate to the `output_path` shown in the response
3. Upload the desired PNG(s) to your Google Drive folder
4. Copy the Google Drive file ID from the uploaded file URL
5. Paste the file ID into your spreadsheet
6. Apps Script will use this ID to build the final deck

## Filename Pattern

Output files follow predictable naming:
- Folder: `{client_name}_pitch_deck/`
- Primary file suggestion: `{client_name_lowercase}_slide13.png`

## How It Works

1. Replaces template primary `#4A4A4A` with your `primary_color`
2. Replaces template secondary `#BDBDBD` with your `secondary_color`
3. Places team logo in top-left corner (0.5% offset, 8% of image size)
4. Saves all 9 branded PNGs to output folder
