# Z-Image Turbo API Usage Guide

Z-Image Turbo 起動中（デフォルト: `http://127.0.0.1:9000`）であれば、外部プログラムや他のコマンドラインから `/api/generate` エンドポイントを呼び出して画像を生成することができます。

## 概要
- **エンドポイント**: `POST http://127.0.0.1:9000/api/generate`
- **Content-Type**: `application/json`
- **レスポンス形式**: JSON

## リクエストパラメータ
JSONのボディに以下のパラメータを含めることができます。`prompt`以外は省略可能で、省略した場合はデフォルト値が使用されます。

| パラメータ名  | 型    | デフォルト値    | 説明                                                                                |
|---------------|-------|-----------------|-------------------------------------------------------------------------------------|
| `prompt`      | 文字列| *(必須)*        | 生成する画像の内容・指示。                                                          |
| `width`       | 数値  | `512`           | 生成する画像の幅（ピクセル単位）。                                                  |
| `height`      | 数値  | `512`           | 生成する画像の高さ（ピクセル単位）。                                                |
| `steps`       | 数値  | `8`             | 生成のステップ数。増やすと詳細になりますが時間がかかります。                        |
| `seed`        | 数値  | `0`             | シード値。`0` を指定した場合はランダムなシードが使用されます。再現させたい場合は同じ値を入力します。|
| `cfg_scale`   | 数値  | `1.0`           | CFGスケール。値が高いほどプロンプトの指示に忠実になりますが、破綻しやすくなる場合があります。 |
| `output_path` | 文字列| *(なし)*        | 画像を保存するローカルのフルパス（例: `C:\images\out.png`）。指定がない場合は `outputs/out_〇〇.png` となります。|
| `vae_path`    | 文字列| *(自動設定)*    | カスタムのVAEモデルを使用する場合のファイルパス。                                   |
| `llm_path`    | 文字列| *(自動設定)*    | カスタムのLLM(テキストエンコーダ)モデルを使用する場合のファイルパス。               |

## 利用例 (curlを使用した場合)

以下は、WindowsのコマンドプロンプトやPowerShell、または別プログラムから `curl` を使って呼び出す例です。

### 1. 最小構成のコマンド（プロンプトのみ）
サイズやファイルパスをお任せにしてとにかく生成したい場合。
```bash
curl -X POST http://127.0.0.1:9000/api/generate ^
  -H "Content-Type: application/json" ^
  -d "{\"prompt\": \"A highly detailed portrait of a cyberpunk hacker\"}"
```

### 2. 詳細設定を行うコマンド
保存先(`output_path`)の指定や、画像サイズ(`width`/`height`)、ランダムシード(`seed`)の指定を行う場合。

```bash
curl -X POST http://127.0.0.1:9000/api/generate ^
  -H "Content-Type: application/json" ^
  -d "{\"prompt\": \"A cute black cat sleeping on a sofa\", \"width\": 256, \"height\": 256, \"steps\": 10, \"output_path\": \"C:\\Users\\zards\\Desktop\\custom_cat.png\"}"
```

## レスポンスについて
生成が完了するか、エラーが発生すると以下のようなJSONレスポンスが返されます。

**成功時のレスポンス例:**
```json
{
  "status": "success",
  "image_path": "C:\\Users\\zards\\Desktop\\custom_cat.png",
  "log": "Wall-clock time: 4.20s\nsd.exe generate_image: 2.15s\n...\n[INFO ] 1/1 images saved"
}
```

**失敗時・エラー発生時のレスポンス例:**
```json
{
  "status": "error",
  "message": "生成中にエラーが発生しました等のバックエンドエラー詳細"
}
```
