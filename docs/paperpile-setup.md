# Paperpileの設定と使い方

## Paperpileとは

Paperpileは学術論文管理ツールで、以下の方法で論文をGoogle Driveに自動保存します：

### 論文の追加方法

1. **ブラウザ拡張機能から追加（最も一般的）**
   - Chrome/Edge拡張機能をインストール
   - Google Scholar、PubMed、arXivなどで論文を見つける
   - Paperpileボタンをクリックして追加
   - **自動的にPDFがダウンロードされGoogle Driveに保存**

2. **PDFを直接アップロード**
   - Paperpileアプリにドラッグ&ドロップ
   - 自動的にメタデータを抽出
   - Google Driveに同期

3. **DOIやPubMed IDから追加**
   - Paperpileの検索ボックスにDOIを入力
   - 論文情報とPDFを自動取得
   - Google Driveに保存

## Google Drive同期の仕組み

### 初回設定（既に設定済みの場合はスキップ）
1. Paperpile設定 → 「Sync & Storage」
2. 「Connect Google Drive」をクリック
3. Googleアカウントで認証
4. Paperpileフォルダが自動作成される

### フォルダ構造
```
Google Drive/
└── Paperpile/
    ├── Author1 et al. - 2024 - Title.pdf
    ├── Author2 et al. - 2023 - Title.pdf
    └── ...
```

### 同期のタイミング
- **即座に同期**: 論文を追加すると数秒でGoogle Driveに反映
- **自動命名**: `著者名 - 年 - タイトル.pdf`形式
- **メタデータ保存**: 別途JSONファイルでメタデータも保存

## このアプリとの連携

1. **Paperpileで論文を追加**（手動操作）
   ↓
2. **自動的にGoogle Driveに保存**（Paperpileが実行）
   ↓
3. **本アプリが新規PDFを検知**（5分ごとにチェック）
   ↓
4. **Geminiで解析**（自動）
   ↓
5. **Notionに追加**（自動）

## Paperpileを使わない代替案

もしPaperpileを使用していない場合、以下の代替案があります：

### 1. 手動でGoogle Driveにアップロード
- 特定のフォルダにPDFを手動でアップロード
- 本アプリがそのフォルダを監視

### 2. Zotero + Google Drive
- Zotero（無料）でGoogle Drive同期設定
- 同様の自動化が可能

### 3. Mendeley + Google Drive
- Mendeleyの同期フォルダをGoogle Driveに設定

## Paperpileのメリット

1. **自動メタデータ取得**: 著者、タイトル、雑誌名を自動取得
2. **ブラウザ統合**: ワンクリックで論文追加
3. **Google Docs連携**: 引用管理が簡単
4. **整理された命名規則**: ファイル名が統一される

## 料金

- 月額: $2.99
- 年額: $35.88
- 学生割引あり
- 30日間無料トライアル

## 必要なフォルダIDの確認方法

1. Google Driveを開く
2. 「Paperpile」フォルダを探す
3. フォルダを開く
4. URLから最後の部分をコピー
   ```
   https://drive.google.com/drive/folders/1ABC123... ← この部分
   ```