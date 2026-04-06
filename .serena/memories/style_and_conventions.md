# Style and Conventions

**Python (`run_gradio_ui.py`)**:
- Uses simple procedural approach with basic functions.
- Uses `gr.Blocks()` for UI layout.
- Very minimal usage of type hints, mostly standard Python.
- Subprocess is used to interact with the backend `.exe` (via `subprocess.run` passing exact arguments).
- No complex class hierarchies; focuses on functional simplicity.

**Windows Scripts**:
- Standard Batch (`.bat`) and PowerShell (`.ps1`) for handling OS-level work.
- Output commands correctly handle UI prompts to users.

**Data & Outputs**:
- Images are generated to the `outputs/` folder with UUIDs by default.
- Uses a `generation_log.json` to locally log generation metadata.
- Avoids automatic executable (.exe) downloading for user safety.