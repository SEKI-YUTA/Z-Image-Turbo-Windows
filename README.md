# Z-Image Turbo - One-Click Windows Installer (Low VRAM)

A beginner-friendly Windows package to run **Z-Image Turbo (GGUF)** locally with a simple **Gradio Web UI**.

Target users:

- Low-VRAM NVIDIA GPUs (including 4GB)
- Anyone who wants free local image generation without complex tools

## Features

- One-click installer: `start_zimage.bat`
- Creates an isolated Python `venv` automatically
- Downloads required model weights (GGUF) automatically
- Minimal, safe UI (Prompt -> Image)
- Safety-first: does **not** auto-download executables (`.exe`)

## Quickstart

1. Download / clone this repo.
2. Put `sd.exe` in `sd_bin\` (see instructions below).
3. Double-click `start_zimage.bat`.
4. Open the UI:
   - http://127.0.0.1:9000

## Requirements

- Windows 10/11 (64-bit)
- Python 3.10+
- Microsoft Visual C++ Redistributable 2015-2022 (x64)
- NVIDIA GPU users (optional)
  - Latest NVIDIA driver recommended

## Running the setup

Double-click:

- `start_zimage.bat`

The installer will:

- Create a Python virtual environment (`venv\`)
- Ask you to choose a VRAM tier (4GB / 6-8GB / 10GB+)
- Download the required weights
- Launch the Gradio UI at http://127.0.0.1:9000

Keep the terminal window open while it downloads models.

## Why `sd.exe` is manual

This project **will never download executable (.exe) files automatically**.

`sd.exe` (or `sd-cli.exe`) is the Windows binary for **stable-diffusion.cpp** (the inference backend). You download it yourself so you can choose which release/build you trust.

**Note:** Recent releases use `sd-cli.exe` instead of `sd.exe`. The installer and UI will automatically detect which one you have.

## Where to get the executable (Windows)

Download a Windows build from the **stable-diffusion.cpp Releases** page.

Recommended assets (names include a commit/hash):

- NVIDIA (recommended): `sd-...-bin-win-cuda12-x64.zip`
- CPU only: `sd-...-bin-win-x64.zip`

Inside the ZIP, you'll find the executable. Recent releases use `sd-cli.exe` (recommended), while older releases use `sd.exe`. Either will work with this project.

Install steps:

1. Extract the ZIP.
2. Copy the executable to one of:
   - `sd_bin\sd-cli.exe` (recommended)
   - `sd_bin\sd.exe` (legacy)
3. Copy any `*.dll` files from the ZIP into the same folder:
   - `sd_bin\`

Important:

- Some releases provide DLLs as a separate asset. If your ZIP contains only `sd.exe`, download the matching DLL package for the same release and copy all DLLs next to `sd.exe`.
- **If upgrading from an older release**: Make sure to also update the DLL files. Use the DLLs that came with your downloaded executable (e.g., `stable-diffusion.dll`). Mixing old DLLs with a new executable (or vice versa) will cause errors.

## What the installer downloads (and what is manual)

Automatic (safe, non-executable downloads):

- Z-Image Turbo GGUF (diffusion model)
- Qwen GGUF (LLM/text encoder)

Manual:

- `sd.exe` (+ DLLs)
- VAE: `models\vae\ae.safetensors`
  - This file may require a Hugging Face login, so the installer asks you to download it manually.

Manual download sources:

- Z-Image Turbo GGUF:
  - https://huggingface.co/leejet/Z-Image-Turbo-GGUF/tree/main
- VAE (`ae.safetensors`):
  - https://huggingface.co/black-forest-labs/FLUX.1-schnell/tree/main
- Qwen GGUF:
  - https://huggingface.co/unsloth/Qwen3-4B-Instruct-2507-GGUF/tree/main

## Troubleshooting

If generation fails or the executable crashes:

- Make sure you copied **all DLLs** that came with your executable. Use the DLLs from the same ZIP/release as your executable.
- **Important**: If you upgraded from an older release, make sure to also update the DLL files. Mixing old DLLs with a new executable will cause errors.
- Install Microsoft Visual C++ Redistributable 2015-2022 (x64).
- If the CUDA build fails, try the CPU build to confirm everything else works.
- Common crash code:
  - `3221225781` (`0xC0000135`) typically means a missing DLL/runtime dependency.

If model downloads fail in the installer but the same URL works in your browser:

- Your network (proxy/firewall/antivirus) may block programmatic downloads from Hugging Face/CDN.
- The installer prefers `curl.exe` (resume + retries + progress bar). If that is unavailable, it falls back to `Invoke-WebRequest`.
- If it still fails, use the manual download links above and place the files into the indicated `models\...` folders.

## Credits / Upstream

This project is a Windows-friendly wrapper around the excellent **stable-diffusion.cpp** backend:

- https://github.com/leejet/stable-diffusion.cpp

Z-Image weights and related resources are hosted on Hugging Face by their respective authors.

