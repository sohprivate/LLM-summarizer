# LLM-Summarizer: Paperpile to Notion 自動連携ツール

学術論文管理ツールPaperpileとNotionを自動連携し、Google Driveに保存されたPDFからGemini APIを使用して論文の要約を生成し、Notionデータベースに自動的に整理するツールです。

## 📚 Paperpileとは

Paperpileは研究者向けの論文管理ツールで、以下の特徴があります：

- **論文の自動取り込み**: ブラウザ拡張機能でワンクリックで論文を保存
- **Google Drive統合**: すべての論文PDFをGoogle Driveに自動保存
- **引用管理**: Google DocsやMicrosoft Wordでの引用挿入
- **タグ・フォルダ管理**: 論文を効率的に整理

### Paperpileのワークフロー

1. **論文の追加**: 
   - 学術データベース（PubMed、Google Scholar等）から直接インポート
   - PDFをドラッグ&ドロップ
   - DOIやPubMed IDから自動取得

2. **Google Drive同期**:
   - Paperpileは論文PDFを指定したGoogle Driveフォルダに自動保存
   - フォルダ構造: `/Paperpile/[著者名] [年] - [タイトル].pdf`

3. **本ツールの役割**:
   - PaperpileがGoogle Driveに保存したPDFを監視
   - 新しい論文を検出して自動的に処理
   - Notionで研究ノートや要約を管理

## 🌟 主な機能

### 自動論文処理
- **Google Drive監視**: 指定フォルダ内の新しいPDFを自動検出
- **AI要約生成**: Gemini APIによる日本語での詳細な論文要約
- **Notion自動登録**: 構造化されたデータベースへの自動追加
- **重複チェック**: 既存論文の重複登録を防止

### 抽出される情報
- **タイトル**: 論文の完全なタイトル
- **筆者**: 著者リスト
- **雑誌**: ジャーナル/会議名
- **出版年**: 発表年
- **IF(impact factor)**: インパクトファクター
- **背景**: 研究の背景と動機（なぜこの研究が必要か）
- **対象集団**: サンプルサイズ、選択基準、人口統計学的特徴
- **研究デザイン**: 前向き/後ろ向き、RCTなど
- **方法**: データ収集方法、測定手法、実験手順
- **統計手法**: 検定方法、有意水準、多重比較補正
- **結果**: 具体的な数値、統計的有意性、効果量
- **考察**: 結果の解釈、既存研究との比較、臨床的意義
- **限界**: サンプルサイズ、バイアス、一般化可能性
- **結論**: 主要な発見と今後の展望
- **強み**: 新規性、方法論的優位性、実用性

## 📋 必要な準備

### 1. Google Cloud Platform設定

#### 1.1 プロジェクトの作成
1. [Google Cloud Console](https://console.cloud.google.com/)にアクセス
2. 新しいプロジェクトを作成（または既存のものを使用）
3. プロジェクトIDをメモしておく

#### 1.2 Google Drive APIの有効化
1. 左メニューから「APIとサービス」→「ライブラリ」を選択
2. 「Google Drive API」を検索
3. 「有効にする」をクリック

#### 1.3 認証情報の作成
1. 「APIとサービス」→「認証情報」を選択
2. 「認証情報を作成」→「OAuthクライアントID」を選択
3. アプリケーションの種類: 「デスクトップアプリ」を選択
4. 名前を入力（例: "Paperpile to Notion"）
5. 作成後、JSONファイルをダウンロード
6. ダウンロードしたファイルを`credentials.json`にリネームし、プロジェクトルートに配置

### 2. Gemini API キーの取得

1. [Google AI Studio](https://makersuite.google.com/app/apikey)にアクセス
2. Googleアカウントでログイン
3. 「Get API Key」をクリック
4. 新しいAPIキーを作成
5. 生成されたAPIキーをコピー（後で`.env`ファイルに設定）

### 3. Notion設定

#### 3.1 Notion Integration作成
1. [Notion Integrations](https://www.notion.so/my-integrations)にアクセス
2. 「New integration」をクリック
3. 基本情報を入力:
   - Name: "Paperpile Sync"（任意）
   - Associated workspace: 使用するワークスペースを選択
4. Capabilitiesで以下を有効化:
   - Read content
   - Update content
   - Insert content
5. 「Submit」をクリック
6. 表示される「Internal Integration Token」をコピー

#### 3.2 Notionデータベースの準備
1. Notionで新しいページを作成
2. データベース（フルページ）を追加
3. 以下のプロパティを設定:

| プロパティ名 | タイプ | 説明 |
|------------|--------|------|
| タイトル | タイトル | 論文タイトル |
| 筆者 | テキスト | 著者リスト |
| 雑誌 | テキスト | ジャーナル名 |
| 出版年 | 数値 | 発表年 |
| IF(impact factor) | 数値 | インパクトファクター |
| 背景 | テキスト | 研究の背景と動機 |
| 対象集団 | テキスト | 研究対象の詳細 |
| 研究デザイン | テキスト | 研究設計の種類 |
| 方法 | テキスト | 研究方法の詳細 |
| 統計手法 | テキスト | 使用した統計解析 |
| 結果 | テキスト | 主要な研究結果 |
| 考察 | テキスト | 結果の解釈と意義 |
| 限界 | テキスト | 研究の制限事項 |
| 結論 | テキスト | 最終的な結論 |
| 強み | テキスト | 研究の優れた点 |

4. データベースの共有:
   - データベース右上の「…」→「Connections」
   - 作成したIntegrationを検索して追加
5. データベースIDの取得:
   - データベースのURLから取得
   - 例: `https://www.notion.so/xxxxx?v=yyyyy`の`xxxxx`部分

### 4. Paperpile設定

#### 4.1 Paperpileアカウントの作成
1. [Paperpile](https://paperpile.com/)にアクセス
2. Googleアカウントでサインアップ
3. 30日間の無料トライアル開始（その後は月額$2.99）

#### 4.2 Google Drive同期の設定
1. Paperpileの設定画面を開く
2. 「Google Drive Sync」を有効化
3. Googleアカウントと連携
4. 同期フォルダが自動作成される（通常は`/Paperpile`）

#### 4.3 ブラウザ拡張機能のインストール
1. [Chrome拡張機能](https://chrome.google.com/webstore/detail/paperpile/bomfdkbfpdhijjbeoicnfhjbdhncfhig)または[Firefox拡張機能](https://addons.mozilla.org/en-US/firefox/addon/paperpile/)をインストール
2. 拡張機能にログイン

### 5. Google Driveフォルダの確認

1. Google DriveでPaperpileフォルダを確認
   - 通常は`/Paperpile`に作成される
2. フォルダIDを取得:
   - フォルダを開いてURLを確認
   - `https://drive.google.com/drive/folders/FOLDER_ID`の`FOLDER_ID`部分
3. このIDを`.env`ファイルの`GOOGLE_DRIVE_FOLDER_ID`に設定

## 🚀 セットアップ

### 1. リポジトリのクローン
```bash
git clone https://github.com/sohprivate/LLM-summarizer.git
cd LLM-summarizer
```

### 2. Python環境の準備
```bash
# Python 3.9以上が必要
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. 環境変数の設定
`.env.example`をコピーして`.env`を作成:
```bash
cp .env.example .env
```

`.env`ファイルを編集:
```env
# Google Drive API
GOOGLE_DRIVE_FOLDER_ID=YOUR_FOLDER_ID_HERE
GOOGLE_CREDENTIALS_PATH=credentials.json

# Gemini API
GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE

# Notion API
NOTION_API_KEY=YOUR_NOTION_INTEGRATION_TOKEN_HERE
NOTION_DATABASE_ID=YOUR_DATABASE_ID_HERE

# Application Settings
CHECK_INTERVAL=300  # チェック間隔（秒）
LOG_LEVEL=INFO      # ログレベル
```

### 4. Google認証の実行
初回のみ、ブラウザでの認証が必要:
```bash
python src/drive/auth.py
```
ブラウザが開き、Googleアカウントでのログインを求められます。

### 5. Notionデータベースの確認
```bash
python main.py --setup-notion
```
正常に接続できれば「Notion database is properly configured!」と表示されます。

## 📖 使い方

### 基本的な使用フロー

1. **Paperpileで論文を追加**:
   - ブラウザ拡張機能で論文ページから直接追加
   - PDFをPaperpileにドラッグ&ドロップ
   - DOI/PubMed IDで検索して追加

2. **自動同期を待つ**:
   - PaperpileがGoogle Driveに自動でPDFを保存
   - 通常は数秒〜1分程度

3. **本ツールが自動処理**:
   - 新しいPDFを検出
   - Gemini APIで論文を分析
   - Notionに日本語要約付きで登録

### 継続的な監視モード（推奨）
```bash
python main.py
```
- 5分ごと（デフォルト）に新しいPDFをチェック
- Ctrl+Cで停止
- バックグラウンド実行推奨

### 1回だけ実行
```bash
python main.py --once
```
- 現在の新しいファイルのみ処理
- cronやタスクスケジューラーでの定期実行に適用

### ログの確認
```bash
tail -f logs/paperpile-to-notion.log
```

### 処理状況の確認
- `processed_files.txt`: 処理済みファイルのリスト
- Notionデータベース: 追加された論文を確認

## 🔧 トラブルシューティング

### Google Drive APIエラー
- `credentials.json`が正しい場所にあるか確認
- `token.pickle`を削除して再認証

### Gemini APIエラー
- APIキーが正しいか確認
- [Google AI Studio](https://makersuite.google.com/app/apikey)でAPIキーの状態を確認

### Notion APIエラー
- Integration TokenとDatabase IDが正しいか確認
- データベースにIntegrationがアクセス権を持っているか確認
- 必要なプロパティがすべて存在するか確認

### PDFが処理されない
- PDFがGoogle Driveの指定フォルダにあるか確認
- `processed_files.txt`に既に記録されていないか確認
- ログファイルでエラーを確認

## 📁 プロジェクト構成

```
LLM-summarizer/
├── src/
│   ├── drive/          # Google Drive API関連
│   ├── gemini/         # Gemini API関連
│   ├── notion/         # Notion API関連
│   └── utils/          # ユーティリティ
├── config/             # 設定ファイル
├── docs/               # ドキュメント
├── logs/               # ログファイル
├── downloads/          # 一時的なPDFダウンロード
├── main.py             # メインプログラム
├── requirements.txt    # 依存パッケージ
└── .env.example        # 環境変数テンプレート
```

## 💡 活用例

### 研究者の使用例
- **文献レビュー**: 大量の論文を効率的に整理・要約
- **研究ノート**: Notionで論文ごとにメモや考察を追加
- **共同研究**: チームでNotionデータベースを共有
- **進捗管理**: 読んだ論文の管理と引用準備

### カスタマイズ例
- 要約の詳細度を調整（プロンプト編集）
- 特定の研究分野に特化した分析
- 追加のメタデータ抽出（実験手法、データセット等）

## 🤝 貢献

Issue報告やPull Requestを歓迎します。

## 📄 ライセンス

MIT License

## 🙏 謝辞

このプロジェクトは以下のサービスを使用しています:
- [Paperpile](https://paperpile.com/) - 優れた論文管理ツール
- Google Drive API
- Google Gemini API
- Notion API