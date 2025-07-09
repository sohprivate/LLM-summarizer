# Deployment Guide

## Local Machine Deployment

### macOS (LaunchAgent)

1. Create LaunchAgent plist file:

```bash
mkdir -p ~/Library/LaunchAgents
cp deploy/com.paperpile-notion.plist ~/Library/LaunchAgents/
```

2. Edit the plist file to update paths:
   - Update `WorkingDirectory` to your project path
   - Update `ProgramArguments` with your Python path

3. Load the agent:

```bash
launchctl load ~/Library/LaunchAgents/com.paperpile-notion.plist
```

4. Start/Stop/Status:

```bash
# Start
launchctl start com.paperpile-notion

# Stop
launchctl stop com.paperpile-notion

# Check status
launchctl list | grep paperpile
```

### Linux (systemd)

1. Copy service file:

```bash
sudo cp deploy/paperpile-notion.service /etc/systemd/system/
```

2. Edit the service file:
   - Update `WorkingDirectory`
   - Update `ExecStart` with correct paths
   - Update `User` to your username

3. Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable paperpile-notion
sudo systemctl start paperpile-notion
```

4. Check status:

```bash
sudo systemctl status paperpile-notion
journalctl -u paperpile-notion -f
```

## Docker Deployment

1. Build image:

```bash
docker build -t paperpile-notion .
```

2. Run container:

```bash
docker run -d \
  --name paperpile-notion \
  -v $(pwd)/.env:/app/.env \
  -v $(pwd)/credentials.json:/app/credentials.json \
  -v $(pwd)/token.pickle:/app/token.pickle \
  -v $(pwd)/processed_files.txt:/app/processed_files.txt \
  -v $(pwd)/logs:/app/logs \
  paperpile-notion
```

## Cloud Deployment

### Google Cloud Functions

For serverless deployment with scheduled triggers:

1. Install gcloud CLI
2. Deploy function:

```bash
cd deploy/cloud-function
gcloud functions deploy paperpile-notion-sync \
  --runtime python39 \
  --trigger-topic paperpile-sync \
  --env-vars-file .env.yaml
```

3. Create Cloud Scheduler job:

```bash
gcloud scheduler jobs create pubsub paperpile-sync-schedule \
  --schedule="*/5 * * * *" \
  --topic=paperpile-sync \
  --message-body="{}"
```

### AWS Lambda

Similar setup available for AWS Lambda with CloudWatch Events.

## Production Considerations

### Monitoring

1. **Health Checks**: Add endpoint or file-based health check
2. **Alerts**: Configure alerts for failures
3. **Metrics**: Track papers processed, API calls, errors

### Security

1. **Secrets Management**: 
   - Use environment-specific secret managers
   - Rotate API keys regularly
   - Never commit credentials

2. **Access Control**:
   - Limit Google Drive scope to read-only
   - Restrict Notion integration permissions

### Scaling

1. **Rate Limits**: 
   - Gemini API: 60 requests/minute
   - Notion API: 3 requests/second
   - Adjust CHECK_INTERVAL accordingly

2. **Parallel Processing**:
   - Process multiple papers concurrently
   - Use queue system for large volumes

### Backup

1. Keep local copy of `processed_files.txt`
2. Regular backups of Notion database
3. Store paper PDFs in separate backup location