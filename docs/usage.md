# Usage Guide

## Initial Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Google Cloud

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google Drive API
4. Create credentials (OAuth 2.0 Client ID)
5. Download credentials as `credentials.json`
6. Place in project root directory

### 3. Configure Gemini API

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create an API key
3. Save for later use

### 4. Setup Notion

Follow the instructions in [notion-setup.md](notion-setup.md)

### 5. Run Setup Script

```bash
python setup.py
```

This will create your `.env` file with all necessary configurations.

### 6. Authenticate with Google

```bash
python src/drive/auth.py
```

This will open a browser for Google authentication.

### 7. Verify Notion Setup

```bash
python main.py --setup-notion
```

## Running the Application

### Continuous Monitoring (Default)

```bash
python main.py
```

The application will:
- Check for new PDFs every 5 minutes (configurable)
- Download and analyze new papers
- Create entries in your Notion database
- Continue running until stopped (Ctrl+C)

### Single Run

```bash
python main.py --once
```

This will:
- Check for new papers once
- Process any found
- Exit

## Monitoring

### Logs

Logs are stored in `logs/paperpile-to-notion.log` and rotated daily.

### Processed Files

The application tracks processed files in `processed_files.txt` to avoid duplicates.

## Troubleshooting

### Common Issues

1. **"credentials.json not found"**
   - Download from Google Cloud Console
   - Place in project root

2. **"Invalid Notion database ID"**
   - Check the ID in your Notion database URL
   - Ensure the integration has access

3. **"PDF text extraction failed"**
   - Some PDFs may be scanned images
   - Check if PDF is corrupted

4. **Rate Limiting**
   - Increase CHECK_INTERVAL in .env
   - The app includes delays between papers

### Debug Mode

Set `LOG_LEVEL=DEBUG` in `.env` for detailed logging.

## Advanced Configuration

### Custom Paperpile Folder

If Paperpile saves to a specific subfolder:
1. Navigate to the folder in Google Drive
2. Copy the folder ID from the URL
3. Update GOOGLE_DRIVE_FOLDER_ID in .env

### Deployment Options

See [deployment guide](deployment.md) for options to run continuously:
- Systemd service (Linux)
- LaunchAgent (macOS)
- Docker container
- Cloud Functions