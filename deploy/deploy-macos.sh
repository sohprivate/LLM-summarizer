#!/bin/bash
# Deploy script for macOS using LaunchAgent

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLIST_NAME="com.paperpile-notion.plist"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"

echo "Deploying Paperpile to Notion sync service..."

# Check if already installed
if launchctl list | grep -q "com.paperpile-notion"; then
    echo "Service already running. Stopping..."
    launchctl stop com.paperpile-notion
    launchctl unload "$LAUNCH_AGENTS_DIR/$PLIST_NAME" 2>/dev/null
fi

# Create LaunchAgents directory if it doesn't exist
mkdir -p "$LAUNCH_AGENTS_DIR"

# Copy and update plist file
cp "$PROJECT_DIR/deploy/$PLIST_NAME" "$LAUNCH_AGENTS_DIR/"

# Update paths in plist
sed -i '' "s|/Users/YOUR_USERNAME/paperpile-to-notion|$PROJECT_DIR|g" "$LAUNCH_AGENTS_DIR/$PLIST_NAME"
sed -i '' "s|YOUR_USERNAME|$USER|g" "$LAUNCH_AGENTS_DIR/$PLIST_NAME"

# Update Python path if needed
PYTHON_PATH=$(which python3)
sed -i '' "s|/usr/bin/python3|$PYTHON_PATH|g" "$LAUNCH_AGENTS_DIR/$PLIST_NAME"

# Load the service
echo "Loading service..."
launchctl load "$LAUNCH_AGENTS_DIR/$PLIST_NAME"

# Start the service
echo "Starting service..."
launchctl start com.paperpile-notion

# Check status
sleep 2
if launchctl list | grep -q "com.paperpile-notion"; then
    echo "✅ Service deployed successfully!"
    echo ""
    echo "Commands:"
    echo "  Start:   launchctl start com.paperpile-notion"
    echo "  Stop:    launchctl stop com.paperpile-notion"
    echo "  Status:  launchctl list | grep paperpile"
    echo "  Logs:    tail -f $PROJECT_DIR/logs/stderr.log"
else
    echo "❌ Failed to deploy service"
    echo "Check logs at: $PROJECT_DIR/logs/stderr.log"
fi