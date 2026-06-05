# MochiFitter JSON補助ツール (mochi_json_helper)

MochiFitter-BlenderAddon-kai を使用して、VRChatアバター向けの
pose_basis / posediff JSON ファイルを生成する Blender アドオンです。

---

## 概要

このアドオンは [MochiFitter-BlenderAddon-kai](https://github.com/Mega-Gorilla/MochiFitter-BlenderAddon-kai) の
`save_armature_pose()` 関数を呼び出し、以下の JSON ファイルを生成します。

| ファイル | 内容 |
|---|---|
| `pose_basis_{アバター名}.json` | ターゲットアーマチュアの現在ポーズ情報 |
| `posediff_template_to_{アバター名}.json` | `pose_basis_template.json` とソースの現在ポーズの差分 |

---

## 必要環境

- Blender 3.0 以上
- [MochiFitter-BlenderAddon-kai](https://github.com/Mega-Gorilla/MochiFitter-BlenderAddon-kai) がインストール・有効化されていること

---

## インストール

1. このリポジトリから `mochi_json_helper.py` をダウンロード
2. Blender を起動
3. `編集` → `プリファレンス` → `アドオン` → `インストール`
4. ダウンロードした `mochi_json_helper.py` を選択
5. アドオン一覧で **MochiFitter JSON補助ツール** を有効化

> ⚠️ MochiFitter-BlenderAddon-kai が有効化されていないと、JSON生成機能は使用できません。

---

## 使い方

### 共通設定

| 項目 | 説明 |
|---|---|
| **ターゲット名** | 出力ファイル名に使われるアバター名（自動的に小文字化されます） |
| **出力フォルダ** | JSON の保存先。`avatar_data_{名前}.json` と `pose_basis_template.json` もここから検索します |

### pose_basis の生成

1. Nパネル → `MochiJSON` タブを開く
2. **出力フォルダ** を指定
3. **ターゲット名** を入力（例: `Beryl`）
4. **ターゲットArmature** を指定
5. **pose_basis を生成** ボタンを押す

→ `pose_basis_beryl.json` が出力フォルダに生成されます。

### posediff の生成

1. 出力フォルダに `pose_basis_template.json` が存在することを確認
2. **ソース名** を入力（テンプレートアバターの名前）
3. **ソースArmature** にポーズ編集済みのアーマチュアを指定
4. **posediff を生成** ボタンを押す

→ `posediff_template_to_beryl.json` が出力フォルダに生成されます。

---

## フォルダ構成例

---

## 頂点ふぃった～との関係

このアドオンは [頂点ふぃった～](../surface_relax_snap.py) の JSON 出力機能を
ライセンス上の理由から切り出したものです。

| アドオン | 役割 | ライセンス |
|---|---|---|
| `surface_relax_snap.py`（頂点ふぃった～） | メッシュ吸着・シェイプキー生成 | 独自 |
| `mochi_json_helper.py`（本アドオン） | JSON生成（MochiFitter依存） | GPL v3 |

---

## ライセンス

本アドオンは **GNU General Public License v3.0** の下で配布されます。

Copyrihgt(c) 2025 amanoissui


### 使用しているソフトウェア

**MochiFitter-BlenderAddon-kai**
- Copyright (C) Mega-Gorilla
- License: GNU General Public License v3.0
- Repository: https://github.com/Mega-Gorilla/MochiFitter-BlenderAddon-kai
- 用途: `save_armature_pose()` を `sys.modules` 経由で呼び出し

**Blender Python API**
- Copyright (C) Blender Foundation
- License: GNU General Public License v2.0 or later
- Website: https://www.blender.org

詳細は [LICENSE](./LICENSE) を参照してください。

---

## 免責事項

本アドオンは非公式のツールです。
MochiFitter の仕様変更により動作しなくなる場合があります。

