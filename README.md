# 肴とお野菜 ひより — 店舗サイト

福岡・天神南の「肴とお野菜 ひより」の静的サイトです。店内写真と実店舗の盛付け動画を使用しています。

## 公開・管理画面の状態

- 公開リポジトリ：[atmos-dining/hiyori-site](https://github.com/atmos-dining/hiyori-site)（作成済み・public）
- 本番URL：[ひよりのサイト](https://sakanatooyasai-hiyori.com/)
- お客様向け予約ページ：[ひよりのネット予約](https://pos-reserve.vercel.app/s/hiyori/book)
- 記事管理画面：[Sveltia CMS](https://sakanatooyasai-hiyori.com/admin/)
- 公開履歴・エラー確認：[GitHub Actions](https://github.com/atmos-dining/hiyori-site/actions)

GitHub Pagesの公開元はGitHub Actionsに設定済みです。`admin/config.yml` は上記リポジトリへ接続し、既存の共通OAuthプロキシを使用します。`main` へのpushでページ生成とPagesへの公開を行う構成です。**2026年10月15日、公開URLでの表示、CMSへのGitHubログイン、既存記事の保存、保存後の自動公開まで確認済みです。**

本番ドメインは `sakanatooyasai-hiyori.com` です（Xserverでユーザー取得）。GitHub Pagesの独自ドメインとして公開し、検索掲載を許可します。

## ローカルで見る

Macでは `プレビュー.command` をダブルクリックするとブラウザが開きます。終了は開いたターミナルで `Ctrl+C` です。Python 3 があれば追加のライブラリは不要です。このREADMEのあるフォルダで次を実行しても確認できます。

```sh
python3 -m http.server 4180 --bind 127.0.0.1
```

ブラウザで <http://127.0.0.1:4180/> を開きます。HTMLファイルを直接開く方法では、画像やメニュー・記事の読み込みが正しく動作しない場合があります。

## ブログを投稿する

投稿手順は [BLOG-GUIDE.md](BLOG-GUIDE.md) を参照してください。GitHubへのログインと、このリポジトリの編集権限が必要です。新しい記事と写真はCMSで追加し、引き続き同じ `blog/posts.json` に記事を保存します。

CMS保存後はActionsの生成・公開処理が終わるまで数分待ち、実際の記事を確認します。記事URL名の形式違反・重複などで生成に失敗した場合、直前の公開内容を維持します。Actionsのエラーを確認し、CMSで修正して再保存してください。予約投稿はありません。

記事本文の表示には同梱の marked 17.0.5 を使用します（`vendor/marked/`、ライセンス同梱）。

## 情報を更新する

設定やデータを変更したら、このフォルダでHTMLを再生成します。

```sh
python3 scripts/build.py
```

生成HTMLは再生成時に上書きされます。ページの文章や構成を直す場合は `scripts/build.py` を編集してください。

| ファイル | 内容 |
| --- | --- |
| `site-config.json` | 店名、所在地、営業情報、予約・Googleリンク、計測ID、動画の指定 |
| `menu-data.json` | 全86品のお品書き。料理38品、飲み物48品 |
| `blog/posts.json` | CMSと共有する「ひより便り」の記事データ |
| `scripts/build.py` | ページ・サイトマップなどの生成元 |
| `style.css` / `common.js` | 見た目と画面操作 |
| `site-paths.js` | 公開先のサブパスに合わせたURL処理 |
| `images/` | 実店舗写真とCMSへ追加した画像 |
| `videos/` | 実店舗の動画とポスター画像 |
| `admin/config.yml` | CMSの接続先と投稿項目 |
| `.github/workflows/pages.yml` | `main` 更新時の生成・公開処理 |

画像は `images/` に保存し、CMSの `public_folder` は `/images` を維持します。記事データにGitHub Pagesのリポジトリ名を埋め込まず、表示時に `HiyoriSite.url` で `/hiyori-site` を補います。独自ドメインへ移る際も同じ記事データを使います。

## 店舗情報と計測

電話番号 `092-401-5788`、営業時間 `17:00〜24:00`、定休日 `なし`、店舗を直接表示するGoogleマップのURL、お客様向け予約URLは設定済みです。営業時間・定休日は2026年10月29日にGoogleマップの曜日別営業時間（月〜日）で確認しました。予約ボタンはメニュー内・ご来店案内に表示し、スマートフォンのトップでは暖簾の右下に縦書きで配置しています。追従ボタンはHEROを通り過ぎてからPCの右上・スマートフォンの下部に表示します（下層ページは従来のスクロール位置で表示）。予約リンクは `site-config.json` の `reservationUrl` に集約しています。次の項目は推測せず空欄にしています。

| キー | 内容 |
| --- | --- |
| `origin` | ローカル設定の公開URL。現在は空欄を維持 |

| `heroVideo` / `fireVideo` / `riceVideo` | 追加撮影する動画の指定 |

営業時間などの変更時は、設定を更新して再生成してください。GA4測定IDは `G-3QDBXSNRTM`、プロパティIDは `561442335`、ウェブストリームIDは `16226986150` です。予約ボタンは既存の `reservation_click` 計測に対応しています。メニュー価格は提供資料の数値です。**税込・税別は未確認**のため、正式公開前に店舗側で価格と税表記を確定してください。

## 独自ドメインでの公開

ActionsはGitHub Pagesの公開URLを環境変数 `SITE_URL` としてbuildへ渡します。`site-config.json` の `origin` は空欄を維持し、workflowは `SITE_INDEXABLE: 'true'` です。ローカルだけで通常のbuildを実行すると `noindex` になります。本番と同じ生成結果を確認するときは次を使用します。

```sh
SITE_URL=https://sakanatooyasai-hiyori.com SITE_INDEXABLE=true python3 scripts/build.py
```

canonical・OG URL・robots・サイトマップは本番URLへ統一し、実在するページと記事URLだけを掲載します。営業時間をRestaurant構造化データへ設定し、来店案内に表示したFAQとFAQPage構造化データを揃えています。GA4は全ページで読み込み、電話・予約・地図リンクを計測します。アクセス解析の案内は `/privacy.html` にあります。

Search Consoleはドメインプロパティを使用し、サイトマップには `https://sakanatooyasai-hiyori.com/sitemap.xml` のフルURLを送信します。CMSの許可ドメインは共通OAuth Workerの `ALLOWED_DOMAINS` で管理します。

## 動画の差し替え

現在の `videos/plating.mp4` は、提供された実店舗映像から切り出した約3.17秒の無音動画です。盛付けの手元を映しており、藁焼き・土鍋ご飯の映像ではありません。ポスターは `videos/plating-poster.jpg` です。

追加撮影する3本の内容、保存名、形式は [VIDEO-SHOT-LIST.md](VIDEO-SHOT-LIST.md) を参照してください。動画が揃うまでは、ヒーローに実店舗の静止画を使用します。

### 2026-10-29 公開確認

- HTTPS証明書発行・HTTPS強制を確認。HTTP、www、旧GitHub Pages URLから正規のHTTPS URLへ転送されます。
- Search Consoleのドメイン所有権確認とサイトマップ送信が成功（8ページ検出）。
- GA4は既存のアトモスダイニング株式会社アカウント（378307648）、GSCも他店舗と同じGoogleアカウントに統一。両サービスの連携とアクセス・予約クリックの受信を確認済み。
- 新ドメインを共通CMS OAuthの許可ドメインへ追加・公開済み。
- 個別インデックス登録リクエストはGoogleのreCAPTCHA接続エラーにより未送信。サイトマップは受理済みで、検索結果への掲載自体はGoogleのクロール・判定待ちです。
