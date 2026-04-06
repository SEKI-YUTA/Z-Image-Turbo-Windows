# Task Completion Guidelines

When a task is completed in this project:
- Ensure that the primary Python script (`run_gradio_ui.py`) or the installer scripts (`setup_and_run.ps1`, `start_zimage.bat`) are fully working.
- No automated testing framework (like `pytest`) is currently configured in this project. Manual testing is required to verify the Web UI or installer script behaves as expected.
- Since it operates on Windows CMD/PowerShell, ensure any file paths used in Python or Scripts handle Windows backslashes properly or utilize relative paths using `os.path` and `Pathlib`.
- If a pull request or git commits are to be run, ensure `git status` verifies the changed files correctly before pushing.