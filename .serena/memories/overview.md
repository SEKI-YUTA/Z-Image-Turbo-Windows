# Project Overview

Z-Image Turbo - One-Click Windows Installer (Low VRAM)

**Purpose**: 
A beginner-friendly Windows package to run Z-Image Turbo (GGUF) locally with a simple Gradio Web UI. Targets low-VRAM NVIDIA GPUs and anyone wanting free local image generation without complex tools.

**Tech Stack**:
- **Python 3.10+**
- **Gradio** for the Web UI.
- **stable-diffusion.cpp** C++ executable backend (`sd-cli.exe` or `sd.exe`) to run inference.
- **Batch / PowerShell scripts** for one-click installation and execution (`start_zimage.bat`, `setup_and_run.ps1`).

**Codebase Structure**:
- `start_zimage.bat` / `setup_and_run.ps1` : Installer and runner scripts. Handles Python `venv` creation, model downloading, and launching the UI.
- `run_gradio_ui.py`: The Main UI and API server. It mounts a Gradio app for the UI and a FastAPI endpoint (`/api/generate`) for remote image generation requests from external programs. It acts as a wrapper that calls `sd_bin/sd-cli.exe` as a subprocess.
- `API_USAGE.md`: Documentation on how to use the `/api/generate` API endpoint.
- `models/`: Stores downloaded models (VAE, LLM Qwen text encoder, Z-Image GGUF).
- `sd_bin/`: Contains the `stable-diffusion.cpp` executed binary and its DLLs. Manual download by the user.
- `outputs/`: Where generated images are saved.