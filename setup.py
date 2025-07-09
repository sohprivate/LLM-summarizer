#!/usr/bin/env python3
"""Setup script for first-time configuration."""
import os
import sys
from pathlib import Path


def setup_environment():
    """Interactive setup for environment variables."""
    print("=== Paperpile to Notion Setup ===\n")
    
    env_file = Path(".env")
    
    if env_file.exists():
        response = input(".env file already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Setup cancelled.")
            return
    
    print("\nPlease provide the following information:")
    print("(See docs/notion-setup.md for detailed instructions)\n")
    
    # Collect information
    config = {}
    
    # Google Drive
    print("1. Google Drive Configuration")
    config['GOOGLE_DRIVE_FOLDER_ID'] = input("   Paperpile folder ID in Google Drive: ").strip()
    
    # Gemini
    print("\n2. Gemini API Configuration")
    config['GEMINI_API_KEY'] = input("   Gemini API Key: ").strip()
    
    # Notion
    print("\n3. Notion Configuration")
    config['NOTION_API_KEY'] = input("   Notion Integration Token: ").strip()
    config['NOTION_DATABASE_ID'] = input("   Notion Database ID: ").strip()
    
    # Optional settings
    print("\n4. Optional Settings (press Enter for defaults)")
    interval = input("   Check interval in seconds (default: 300): ").strip()
    config['CHECK_INTERVAL'] = interval if interval else "300"
    
    log_level = input("   Log level (DEBUG/INFO/WARNING/ERROR, default: INFO): ").strip()
    config['LOG_LEVEL'] = log_level if log_level else "INFO"
    
    # Write .env file
    with open('.env', 'w') as f:
        f.write("# Google Drive API\n")
        f.write(f"GOOGLE_DRIVE_FOLDER_ID={config['GOOGLE_DRIVE_FOLDER_ID']}\n")
        f.write("GOOGLE_CREDENTIALS_PATH=credentials.json\n\n")
        
        f.write("# Gemini API\n")
        f.write(f"GEMINI_API_KEY={config['GEMINI_API_KEY']}\n\n")
        
        f.write("# Notion API\n")
        f.write(f"NOTION_API_KEY={config['NOTION_API_KEY']}\n")
        f.write(f"NOTION_DATABASE_ID={config['NOTION_DATABASE_ID']}\n\n")
        
        f.write("# Application Settings\n")
        f.write(f"CHECK_INTERVAL={config['CHECK_INTERVAL']}\n")
        f.write(f"LOG_LEVEL={config['LOG_LEVEL']}\n")
    
    print("\n✓ .env file created successfully!")
    
    # Check for credentials.json
    if not Path("credentials.json").exists():
        print("\n⚠️  Warning: credentials.json not found!")
        print("   Please download it from Google Cloud Console and place it in the project root.")
        print("   See: https://console.cloud.google.com/apis/credentials")
    
    print("\n=== Setup Complete ===")
    print("\nNext steps:")
    print("1. Ensure credentials.json is in the project root")
    print("2. Run: python src/drive/auth.py (to authenticate with Google)")
    print("3. Run: python main.py --setup-notion (to verify Notion setup)")
    print("4. Run: python main.py (to start monitoring)")


if __name__ == "__main__":
    setup_environment()