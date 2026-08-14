# MochiFitter JSON補助ツール

MochiFitter-BlenderAddon-kai（GPL v3）を利用して、`pose_basis` JSON と `posediff` JSON の生成を補助する Blender アドオンです。3Dビューポートのサイドバーから、対象アーマチュアの指定とJSON出力をワンクリックで行えます。

本アドオンは MochiFitter-BlenderAddon-kai に依存しており、単体では動作しません。

## 動作要件

- Blender 3.0 以降
- [MochiFitter-BlenderAddon-kai](https://github.com/Mega-Gorilla/MochiFitter-BlenderAddon-kai)（GPL v3）がインストール・有効化されていること

## インストール

1. 本アドオンのファイル（`mochi_json_helper.py`）を Blender の「編集 > プリファレンス > アドオン > インストール」から読み込みます。
2. アドオン一覧で「MochiFitter JSON補助ツール」を有効化します。
3. MochiFitter-BlenderAddon-kai が別途インストール・有効化されていることを確認します（未検出の場合、本アドオンの機能は使用できません）。

インストール後、3Dビューポートのサイドバー（`N`キーで表示）に「MochiJSON補助」タブが追加されます。

## 事前に必要なファイル

このアドオンは、以下のファイルが出力フォルダ内に存在することを前提に動作します。

- `avatar_data_{アバター名}.json`：MochiFitter側で生成される、各アバターの素体情報ファイル。ターゲット用・ソース用それぞれの名前分が必要です（大文字・小文字どちらのファイル名でも自動検索されます）。
- `pose_basis_template.json`：`posediff` 生成時の基準ポーズとなるファイル。あらかじめ用意しておくか、本アドオンで生成した `pose_basis_{アバター名}.json` を手動でリネームして配置してください。

## パネルの構成

サイドバーのパネルは、誤操作や誤認識を避けるため以下のように区分されています。

### MochiFitter検出状態

MochiFitter-BlenderAddon-kai が検出されているかどうかを表示します。未検出の場合、以降の全機能が無効化されます。

### 共通設定

出力フォルダ、ソース名、ターゲット名を入力します。出力フォルダは JSON の保存先であり、`avatar_data_{名前}.json` や `pose_basis_template.json` の検索先にもなります（未指定の場合は `.blend` ファイルの保存先フォルダが使われます）。ソース名・ターゲット名はそれぞれ `avatar_data_{名前}.json` の自動検索、および出力ファイル名の生成に使われます。

このセクションで表示される `pose_basis_template.json` の有無は、内部的な準備状態の確認用です（表示自体は「ファイル確認」セクションにまとめてあります）。

### ターゲット設定（pose_basis 生成に使用）

ターゲットArmature を指定します。ここで選択したアーマチュアの現在のポーズが、`pose_basis` 生成時の対象になります。生成予定のファイル名（`pose_basis_{ターゲット名}.json`）がボタンの上に表示されます。

### ソース設定（posediff 生成に使用）

ソースArmature（ポーズ編集済み）を指定します。ここで選択したアーマチュアの現在のポーズと `pose_basis_template.json` との差分が、`posediff` 生成時に使われます。生成予定のファイル名（`posediff_template_to_{ターゲット名}.json`）がボタンの上に表示されます。

### ファイル確認

`pose_basis_template.json` および、ターゲット名・ソース名にそれぞれ対応する `avatar_data_{名前}.json` の有無を、出力ファイルと混同しないよう最下層にまとめて表示します。

### ライセンス表記

本アドオンおよび MochiFitter-BlenderAddon-kai のライセンス（GPL v3）を表示します。

## 使い方

### 1. pose_basis の生成

1. 「共通設定」で出力フォルダとターゲット名を入力します。
2. 出力フォルダに `avatar_data_{ターゲット名}.json` が存在することを確認します（「ファイル確認」セクションで確認できます）。
3. 「ターゲット設定」でターゲットArmature を指定します。
4. 「pose_basis を生成」ボタンを押すと、`pose_basis_{ターゲット名}.json` が出力フォルダに生成されます。

生成した `pose_basis_{ターゲット名}.json` を基準ポーズとして使う場合は、`pose_basis_template.json` にリネームして出力フォルダに配置してください。

### 2. posediff の生成

1. 出力フォルダに `pose_basis_template.json` が存在することを確認します。
2. 「共通設定」でソース名とターゲット名を入力します。
3. 出力フォルダに `avatar_data_{ソース名}.json` が存在することを確認します。
4. 「ソース設定」でソースArmature（ポーズを編集した状態のアーマチュア）を指定します。
5. 「posediff を生成」ボタンを押すと、`pose_basis_template.json` とソースの現在ポーズとの差分が計算され、`posediff_template_to_{ターゲット名}.json` が出力フォルダに生成されます。

出力ファイル名にはターゲット名が使われますが、実際のポーズ差分の計算にはソースArmature の現在ポーズが使われる点に注意してください。

## 生成されるファイル一覧

| 操作 | 生成ファイル名 | 使用データ |
| --- | --- | --- |
| pose_basis 生成 | `pose_basis_{ターゲット名}.json` | ターゲットArmature の現在ポーズ + `avatar_data_{ターゲット名}.json` |
| posediff 生成 | `posediff_template_to_{ターゲット名}.json` | `pose_basis_template.json` とソースArmature の現在ポーズ（`avatar_data_{ソース名}.json` 経由）との差分 |

ファイル名の `{名前}` 部分は自動的に小文字化されます。

## ライセンス

本アドオンは GNU General Public License v3.0 の下で配布されます。MochiFitter-BlenderAddon-kai（Copyright (C) Mega-Gorilla, GPL v3）を利用しています。

- MochiFitter-BlenderAddon-kai: https://github.com/Mega-Gorilla/MochiFitter-BlenderAddon-kai
