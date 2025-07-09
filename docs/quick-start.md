# クイックスタートガイド

## 必要なもの（チェックリスト）

- [ ] Googleアカウント
- [ ] Notionアカウント  
- [ ] Paperpileアカウント（Google Drive連携済み）
- [ ] Python 3.9以上がインストール済み

## 最速セットアップ（15分）

### 1. プロジェクトをダウンロード
```bash
cd /Users/sohan/Desktop/asobi/Ren/paperpile-to-notion
```

### 2. 必要なAPIキーを取得

#### Google Drive API（5分）
1. https://console.cloud.google.com/ にアクセス
2. 新規プロジェクト作成 → Google Drive API有効化
3. 認証情報作成 → OAuth2.0 → デスクトップアプリ
4. `credentials.json` をダウンロードしてプロジェクトルートに配置

#### Gemini API（2分）
1. https://makersuite.google.com/app/apikey にアクセス
2. 「Create API Key」をクリック
3. 生成されたキーをコピー

#### Notion API（5分）
1. https://www.notion.so/my-integrations で新規Integration作成
2. トークンをコピー
3. Notionで論文用データベースを作成
4. データベースにIntegrationを接続
5. データベースURLからIDをコピー

#### Google DriveフォルダID（1分）
1. PaperpileのGoogle Driveフォルダを開く
2. URLから最後の部分（フォルダID）をコピー

### 3. セットアップ実行（2分）
```bash
# 依存関係インストール
pip install -r requirements.txt

# 対話式セットアップ
python setup.py
```

入力項目:
- Paperpile folder ID: `（GoogleDriveのフォルダID）`
- Gemini API Key: `AIzaSy...`
- Notion Integration Token: `secret_...`
- Notion Database ID: `32文字の英数字`
- その他はEnterでデフォルト値

### 4. 認証と起動
```bash
# Google認証（ブラウザが開く）
python src/drive/auth.py

# Notion接続テスト
python main.py --setup-notion

# 実行開始！
python main.py --once  # テスト実行
python main.py         # 継続監視
```

## 動作確認

1. Paperpileで新しい論文をGoogle Driveに保存
2. 5分以内にNotionデータベースに自動追加される
3. 論文のタイトル、著者、要約などが自動入力される

## うまくいかない時は

`docs/setup-guide-ja.md` の詳細ガイドを参照してください。