# Whistle Report Generator v1

API service that generates 9 branded football report PNGs from grayscale templates, uploads them to Google Drive, and returns Drive file metadata for Apps Script consumption.

## Folder Structure

```
whistle-report-generator/
├── app/
│   ├── main.py               # FastAPI app
│   ├── image_generator.py    # Image processing logic
│   ├── drive_upload.py       # Google Drive upload helpers
│   └── utils.py              # Input normalization helpers
├── templates/
│   └── Football_v1/          # 9 template PNGs
├── logos/                     # Team logo PNGs
├── outputs/                   # Generated reports (gitignored)
├── credentials.json           # Google service account credentials (gitignored)
├── requirements.txt
├── example_request.json
├── .gitignore
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

## Google Drive Setup

### 1. Create a Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable the **Google Drive API**:
   - Go to APIs & Services > Library
   - Search for "Google Drive API"
   - Click Enable
4. Create a service account:
   - Go to APIs & Services > Credentials
   - Click "Create Credentials" > "Service Account"
   - Give it a name (e.g., `whistle-drive-uploader`)
   - Click Create and Continue
   - Skip the optional steps, click Done
5. Create a key for the service account:
   - Click on the service account you just created
   - Go to the "Keys" tab
   - Click "Add Key" > "Create new key"
   - Select JSON format
   - Download the file

### 2. Place Credentials File

Save the downloaded JSON file as `credentials.json` in the project root.

Or set a custom path via environment variable:

```bash
export GOOGLE_CREDENTIALS_FILE=/path/to/your/credentials.json
```

### 3. Create a Google Drive Parent Folder

1. Create a folder in Google Drive where all generated reports will be stored
2. Copy the folder ID from the URL:
   - URL looks like: `https://drive.google.com/drive/folders/ABC123XYZ`
   - The folder ID is: `ABC123XYZ`

### 4. Share the Folder with the Service Account

1. Right-click the folder in Google Drive > Share
2. Add the service account email (found in credentials.json as `client_email`)
   - Looks like: `whistle-drive-uploader@your-project.iam.gserviceaccount.com`
3. Give it **Editor** access

### 5. Set the Parent Folder ID

```bash
export DRIVE_PARENT_FOLDER_ID=your_folder_id_here
```

## Start the API

```bash
export DRIVE_PARENT_FOLDER_ID=your_folder_id_here
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
  "drive_folder_id": "abc123xyz",
  "generated_files": [
    {
      "filename": "01_gps_session_report.png",
      "local_path": "outputs/Indiana Football_pitch_deck/01_gps_session_report.png",
      "drive_file_id": "fileid1",
      "drive_link": "https://drive.google.com/file/d/fileid1/view"
    },
    {
      "filename": "02_drills.png",
      "local_path": "outputs/Indiana Football_pitch_deck/02_drills.png",
      "drive_file_id": "fileid2",
      "drive_link": "https://drive.google.com/file/d/fileid2/view"
    }
  ]
}
```

Files are returned in order (01-09) so Apps Script can map them to slide positions.

## Output

- **Local**: PNGs saved to `outputs/{team_name}_pitch_deck/`
- **Drive**: Uploaded to `{parent_folder}/{team_name}_pitch_deck/`

If the Drive subfolder already exists, it's reused. If files with the same names exist, they're replaced.

## How It Works

1. Replaces template primary `#4A4A4A` with your `primary_color`
2. Replaces template secondary `#BDBDBD` with your `secondary_color`
3. Places team logo in the top-left corner (0.5% offset, 8% of image size)
4. Preserves logo transparency
5. Uploads all 9 PNGs to Google Drive subfolder
6. Returns Drive file IDs and links for Apps Script consumption

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GOOGLE_CREDENTIALS_FILE` | `credentials.json` | Path to service account JSON file |
| `DRIVE_PARENT_FOLDER_ID` | (required) | Google Drive folder ID for uploads |
