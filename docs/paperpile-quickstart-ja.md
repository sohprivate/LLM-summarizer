# Paperpile クイックスタートガイド

## 初期設定（初回のみ）

### 1. Google Drive同期を有効化

1. **Paperpileにログイン**
   - https://app.paperpile.com/

2. **設定を開く**
   - 右上の歯車アイコン → Settings

3. **Sync & Storageタブ**
   - 「Google Drive」セクションを探す
   - 「Connect Google Drive」ボタンをクリック
   - Googleアカウントでログインして権限を許可

4. **同期開始**
   - 自動的に「Paperpile」フォルダがGoogle Driveに作成される
   - 既存の論文も同期される（少し時間がかかる）

## 論文を追加する方法

### 方法1: ブラウザ拡張機能（推奨）

1. **拡張機能をインストール**
   - Chrome: https://chrome.google.com/webstore/detail/paperpile/bomfdkbfpdhijjbeoicnfhjbdhncfhig
   - Edge/Firefox版もあり

2. **論文を追加**
   - Google Scholar、PubMed、arXiv、大学図書館などで論文を探す
   - ページ上部に緑色の「View PDF」や「Paperpile」ボタンが表示される
   - クリックすると自動的に：
     - PDFをダウンロード
     - メタデータ（著者、タイトル、雑誌名等）を取得
     - Google Driveに保存

### 方法2: Paperpileアプリから直接追加

1. **検索して追加**
   ```
   Paperpileアプリの検索ボックスに：
   - 論文タイトル
   - DOI（例: 10.1038/nature12373）
   - PubMed ID
   - arXiv ID
   を入力
   ```

2. **「Add to Paperpile」をクリック**
   - 自動的にPDFとメタデータを取得
   - Google Driveに即座に同期

### 方法3: PDFファイルをドラッグ&ドロップ

1. **既にPDFを持っている場合**
   - Paperpileアプリを開く
   - PDFファイルをドラッグ&ドロップ
   - 自動的にメタデータを検索（見つからない場合は手動入力）

## Google Driveでの確認

1. **Google Driveを開く**
   - https://drive.google.com/

2. **Paperpileフォルダを確認**
   ```
   マイドライブ/
   └── Paperpile/
       ├── Smith et al. - 2024 - Machine Learning.pdf
       ├── Tanaka et al. - 2023 - Quantum Computing.pdf
       └── ...
   ```

3. **フォルダIDの取得**（自動化に必要）
   - Paperpileフォルダを開く
   - URLをコピー：
     ```
     https://drive.google.com/drive/folders/1a2B3c4D5e6F7g8H9i0J
                                            ^^^^^^^^^^^^^^^^^^^^^^^^
                                            この部分がフォルダID
     ```

## 実際の使用例

### 例1: Google Scholarから追加

1. Google Scholarで「machine learning healthcare」を検索
2. 興味のある論文を見つける
3. Paperpile拡張機能のボタンをクリック（ページ上部）
4. 数秒後、Google DriveのPaperpileフォルダに表示

### 例2: DOIから追加

1. Paperpileアプリで「10.1038/s41586-021-03819-2」を検索
2. 論文が表示されたら「Add to Paperpile」
3. PDFが自動ダウンロードされGoogle Driveに保存

## トラブルシューティング

### PDFが見つからない場合
- 有料論文の場合、大学のVPN経由でアクセス
- Sci-Hubプロキシを設定（Settings → Proxies）

### 同期されない場合
1. Settings → Sync & Storage
2. 「Sync Now」ボタンをクリック
3. エラーメッセージを確認

### フォルダが作成されない場合
1. Google Driveの容量を確認
2. Paperpileの権限を再設定

## このアプリとの連携準備

Paperpileフォルダが作成され、論文が保存されるようになったら：

1. Google DriveでPaperpileフォルダのIDをコピー
2. このIDを使って自動化アプリを設定
3. 新しい論文が自動的にNotionに追加される！