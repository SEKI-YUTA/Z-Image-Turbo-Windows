# Suggested Commands

## Running the Application
* **One-Click Start**: `start_zimage.bat` (Executes `setup_and_run.ps1` under the hood)
* **Direct UI Run** (if venv is activated): `python run_gradio_ui.py`

## Running Inference Backend Directly
You can bypass the UI and directly run the backend:
`sd_bin\sd-cli.exe --diffusion-model models\zimage\z_image_turbo_Q8_0.gguf -p "Your prompt" --steps 8 -H 512 -W 512 -o "outputs/image.png"`

## Util Commands for Windows System
* Read a file: `Get-Content <file>`
* List directory: `Get-ChildItem` (or `ls` / `dir`)
* Search content: `Select-String` (or `findstr`)
* Find files: `Get-ChildItem -Recurse -Filter <pattern>`