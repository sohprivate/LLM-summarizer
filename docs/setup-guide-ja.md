# Paperpile to Notion 詳細セットアップガイド

## 必要なアカウント・API キー一覧

### 1. Google Cloud Platform (Google Drive API用)
- **必要なもの**: Googleアカウント
- **料金**: 無料枠で十分
- **用途**: PaperpileがGoogle Driveに保存したPDFファイルを読み取る

### 2. Google AI Studio (Gemini API用)
- **必要なもの**: Googleアカウント（同じもので可）
- **料金**: 無料枠あり（60リクエスト/分）
- **用途**: 論文のAI解析（要約、メタデータ抽出）

### 3. Notion
- **必要なもの**: Notionアカウント
- **料金**: 無料プランで可
- **用途**: 論文データベースの保存先

### 4. Paperpile
- **必要なもの**: Paperpileアカウント（既にお持ちと想定）
- **設定**: Google Driveと連携済みであること

## ステップバイステップ設定手順

### Step 1: Google Drive API の設定

1. **Google Cloud Console にアクセス**
   - https://console.cloud.google.com/ を開く
   - Googleアカウントでログイン

2. **新規プロジェクト作成**
   - 上部の「プロジェクトを選択」→「新しいプロジェクト」
   - プロジェクト名: `paperpile-notion` (任意)
   - 「作成」をクリック

3. **Google Drive API を有効化**
   - 左メニュー「APIとサービス」→「ライブラリ」
   - 「Google Drive API」を検索
   - 「有効にする」をクリック

4. **認証情報の作成**
   - 左メニュー「APIとサービス」→「認証情報」
   - 「認証情報を作成」→「OAuth クライアント ID」
   - アプリケーションの種類: 「デスクトップアプリ」
   - 名前: `paperpile-sync` (任意)
   - 「作成」をクリック

5. **credentials.json をダウンロード**
   - 作成された認証情報の右側のダウンロードボタンをクリック
   - ダウンロードしたファイルを `credentials.json` にリネーム
   - プロジェクトのルートディレクトリに配置:
     ```
     /Users/sohan/Desktop/asobi/Ren/paperpile-to-notion/credentials.json
     ```

### Step 2: Gemini API キーの取得

1. **Google AI Studio にアクセス**
   - https://makersuite.google.com/app/apikey を開く
   - Googleアカウントでログイン

2. **API キーの作成**
   - 「Create API Key」をクリック
   - 既存のプロジェクトを選択 or 新規作成
   - APIキーが生成される（例: `AIzaSyAbc...xyz`）
   - このキーをコピーして安全な場所に保存

### Step 3: Notion の設定

1. **Notion Integration の作成**
   - https://www.notion.so/my-integrations を開く
   - 「新しいインテグレーション」をクリック
   - 基本情報を入力:
     - 名前: `Paperpile Sync`
     - ワークスペースを選択
   - 「送信」をクリック
   - **Internal Integration Token** をコピー（`secret_...` で始まる）

2. **Notion データベースの作成**
   - Notionで新しいページを作成
   - 「/database」と入力して「データベース - フルページ」を選択
   - データベース名: `論文` (任意)

3. **データベースのプロパティ設定**
   以下のプロパティを追加:
   
   | プロパティ名 | タイプ | 説明 |
   |------------|--------|------|
   | Title | タイトル | 論文タイトル（デフォルト） |
   | Authors | テキスト | 著者名 |
   | Journal | テキスト | 雑誌名 |
   | Year | 数値 | 出版年 |
   | Added Date | 日付 | 追加日 |
   | Research Field | セレクト | 研究分野 |
   | Keywords | マルチセレクト | キーワード |
   | Summary | テキスト | 要約 |
   | Google Drive ID | テキスト | ファイルID |

4. **データベースとIntegrationの接続**
   - データベースページの右上「...」→「接続を追加」
   - 作成した Integration を検索して選択

5. **データベース ID の取得**
   - データベースのURLを確認:
     ```
     https://www.notion.so/workspace/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx?v=...
     ```
   - `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` の部分がデータベースID

### Step 4: Paperpile フォルダ ID の取得

1. **Google Drive でPaperpileフォルダを開く**
   - https://drive.google.com を開く
   - Paperpileが論文を保存しているフォルダを探す
   - 通常は「Paperpile」というフォルダ

2. **フォルダ ID を取得**
   - フォルダを開いた状態でURLを確認:
     ```
     https://drive.google.com/drive/folders/1a2B3c4D5e6F7g8H9i0J
     ```
   - 最後の `1a2B3c4D5e6F7g8H9i0J` の部分がフォルダID

## アプリケーションの設定と起動

### Step 5: 環境設定

1. **プロジェクトディレクトリに移動**
   ```bash
   cd /Users/sohan/Desktop/asobi/Ren/paperpile-to-notion
   ```

2. **Python仮想環境の作成（推奨）**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # macOS/Linux
   ```

3. **依存関係のインストール**
   ```bash
   pip install -r requirements.txt
   ```

4. **セットアップスクリプトの実行**
   ```bash
   python setup.py
   ```
   
   以下の情報を入力:
   - Paperpile folder ID: `Step 4で取得したID`
   - Gemini API Key: `Step 2で取得したキー`
   - Notion Integration Token: `Step 3で取得したトークン`
   - Notion Database ID: `Step 3で取得したID`
   - Check interval: `300` (5分ごと、Enterでデフォルト)
   - Log level: `INFO` (Enterでデフォルト)

### Step 6: Google認証

```bash
python src/drive/auth.py
```

- ブラウザが開いて Google ログイン画面が表示される
- アカウントを選択してアクセスを許可
- 「Authentication successful!」と表示されれば成功

### Step 7: Notion接続確認

```bash
python main.py --setup-notion
```

- 「Notion database is properly configured!」と表示されれば成功

### Step 8: アプリケーション起動

**テスト実行（1回だけ）:**
```bash
python main.py --once
```

**継続監視モード:**
```bash
python main.py
```

## トラブルシューティング

### よくあるエラーと対処法

1. **"credentials.json not found"**
   - Google Cloud ConsoleからOAuth2認証情報をダウンロード
   - ファイル名を `credentials.json` に変更
   - プロジェクトルートに配置

2. **"GOOGLE_DRIVE_FOLDER_ID not set"**
   - `.env` ファイルを確認
   - PaperpileフォルダのIDが正しく設定されているか確認

3. **"Invalid Notion database ID"**
   - NotionデータベースのURLから正しいIDをコピー
   - Integrationがデータベースに接続されているか確認

4. **Gemini API エラー**
   - API キーが正しいか確認
   - レート制限（60リクエスト/分）に達していないか確認

### ログの確認

```bash
# リアルタイムログ監視
tail -f logs/paperpile-to-notion.log

# エラーのみ表示
grep ERROR logs/paperpile-to-notion.log
```

### 処理済みファイルのリセット

既に処理したファイルを再処理したい場合:
```bash
rm processed_files.txt
```

## 自動起動設定（macOS）

```bash
# デプロイスクリプトを実行
./deploy/deploy-macos.sh

# サービスの状態確認
launchctl list | grep paperpile

# ログ確認
tail -f logs/stderr.log
```

## セキュリティに関する注意

1. **`.env` ファイルは絶対にGitにコミットしない**
2. **APIキーは定期的に更新する**
3. **`credentials.json` と `token.pickle` も共有しない**
4. **Notionのアクセス権限は最小限に設定**

## 次のステップ

1. 数件の論文でテスト実行
2. 正常に動作することを確認
3. 自動起動設定で常時監視
4. 定期的にログを確認して正常動作を監視