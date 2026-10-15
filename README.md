# 肴とお野菜 ひより — 店舗サイト

福岡・天神南の「肴とお野菜 ひより」の静的サイトです。店内写真と実店舗の盛付け動画を使用しています。

## 公開・管理画面の状態

- 公開リポジトリ：[atmos-dining/hiyori-site](https://github.com/atmos-dining/hiyori-site)（作成済み・public）
- 公開準備用URL：[ひよりのサイト](https://atmos-dining.github.io/hiyori-site/)
- 記事管理画面：[Sveltia CMS](https://atmos-dining.github.io/hiyori-site/admin/)
- 公開履歴・エラー確認：[GitHub Actions](https://github.com/atmos-dining/hiyori-site/actions)

GitHub Pagesの公開元はGitHub Actionsに設定済みです。`admin/config.yml` は上記リポジトリへ接続し、既存の共通OAuthプロキシを使用します。`main` へのpushでページ生成とPagesへの公開を行う構成です。**現在は初回デプロイ準備中です。公開の成功、CMSへのログイン、CMSからの記事保存の成功はまだ確認していません。**

GitHubのURLは `noindex` を付けた公開準備用です。これは検索掲載を抑える指定であり、アクセス制限ではありません。ひより用の独自ドメインは未設定・未定です。この作業ではドメインの取得・契約は行っていません。

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

## 未確定の店舗情報

提供されたGoogleの店舗情報URLは設定済みです。次の項目は推測せず空欄にしています。

| キー | 内容 |
| --- | --- |
| `telephone` / `hours` / `closed` | 電話番号・営業時間・定休日 |
| `reservationUrl` | 正式な予約ページURL |
| `origin` | ローカル設定の公開URL。現在は空欄を維持 |
| `ga4Id` | Google Analytics 4の測定ID |
| `heroVideo` / `fireVideo` / `riceVideo` | 追加撮影する動画の指定 |

電話番号・営業時間・定休日・予約URLは、確定値を入力して再生成すると表示に反映されます。GA4は有効な測定IDを設定するまで読み込みません。メニュー価格は提供資料の数値です。**税込・税別は未確認**のため、正式公開前に店舗側で価格と税表記を確定してください。

## 正式公開へ切り替える

ActionsではGitHub Pagesから取得した公開URLを環境変数 `SITE_URL` としてbuildへ渡します。`site-config.json` の `origin` は空欄のままです。現在のworkflowは `SITE_INDEXABLE: 'false'` で、canonical・共有用URLには公開準備用URLを使い、検索掲載は抑えます。ローカルも `origin` 空欄のため `noindex` です。

正式公開時は、店舗情報・メニュー価格と税表記・掲載内容を確認したうえで、次を行います。

1. 使用する独自ドメインを決め、GitHub Pages・DNS・HTTPSを設定する。
2. `admin/config.yml` の `site_url` を正式なURLへ変更する。
3. `.github/workflows/pages.yml` の `SITE_INDEXABLE` を `'true'` にして公開する。
4. 公開サイト、管理画面、記事、画像、canonical・共有用URL・`robots.txt`・サイトマップを確認する。

サイトマップはbuild時に記事データから自動生成します。URLだけを変更しても公開・検索掲載の確認まで完了したことにはなりません。

## 動画の差し替え

現在の `videos/plating.mp4` は、提供された実店舗映像から切り出した約3.17秒の無音動画です。盛付けの手元を映しており、藁焼き・土鍋ご飯の映像ではありません。ポスターは `videos/plating-poster.jpg` です。

追加撮影する3本の内容、保存名、形式は [VIDEO-SHOT-LIST.md](VIDEO-SHOT-LIST.md) を参照してください。動画が揃うまでは、ヒーローに実店舗の静止画を使用します。
