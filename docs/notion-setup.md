# Notion Database Setup Guide

## 1. Create Notion Integration

1. Go to https://www.notion.so/my-integrations
2. Click "New integration"
3. Give it a name (e.g., "Paperpile Paper Manager")
4. Select the workspace
5. Copy the "Internal Integration Token" - this is your `NOTION_API_KEY`

## 2. Create Database

1. In Notion, create a new page
2. Add a Database - Full page
3. Name it "Papers" or similar

## 3. Add Database Properties

Add the following properties to your database:

| Property Name | Type | Notes |
|--------------|------|-------|
| Title | Title | Default (paper title) |
| Authors | Text | Paper authors |
| Journal | Text | Journal/conference name |
| Year | Number | Publication year |
| Added Date | Date | When added to database |
| Research Field | Select | Research area |
| Keywords | Multi-select | Paper keywords |
| Summary | Text | Brief summary |
| Google Drive ID | Text | File ID for linking |

## 4. Share Database with Integration

1. Open your database page
2. Click "..." menu → "Add connections"
3. Search for your integration name
4. Click to add it

## 5. Get Database ID

1. Open your database in Notion
2. Look at the URL: `https://www.notion.so/workspace/xxxxxxxxxxxxxxxxxxxxxxxxxxxxx?v=...`
3. The `xxxxxxxxxxxxxxxxxxxxxxxxxxxxx` part is your database ID
4. Set this as `NOTION_DATABASE_ID` in your .env file

## Example .env Configuration

```
NOTION_API_KEY=secret_AbCdEfGhIjKlMnOpQrStUvWxYz1234567890
NOTION_DATABASE_ID=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```