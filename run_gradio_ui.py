import os, subprocess, shlex, uuid, time, json
import re
from datetime import datetime
from pathlib import Path
import gradio as gr
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

ROOT = Path(__file__).parent
SD_BIN_DIR = ROOT / "sd_bin"
SD_EXE = str(SD_BIN_DIR / "sd-cli.exe")
MODEL_PATH = str(ROOT / "models" / "zimage" / "z_image_turbo_Q8_0.gguf")
OUTDIR = str(ROOT / "outputs")
os.makedirs(OUTDIR, exist_ok=True)
GENERATION_LOG_PATH = os.path.join(OUTDIR, "generation_log.json")


def load_generation_log():
    """Load existing generation log or return empty list."""
    if os.path.isfile(GENERATION_LOG_PATH):
        try:
            with open(GENERATION_LOG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return []
    return []


def save_generation_metadata(image_path, prompt, width, height, steps, seed_requested,
                             seed_actual, cfg_scale, vae_path, llm_path,
                             model_path, elapsed_seconds, sd_exe_used):
    """Append generation metadata to the JSON log file."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "image_path": image_path,
        "image_filename": os.path.basename(image_path),
        "prompt": prompt,
        "width": int(width),
        "height": int(height),
        "steps": int(steps),
        "seed_requested": int(seed_requested),
        "seed_actual": seed_actual,
        "cfg_scale": float(cfg_scale),
        "vae_path": vae_path,
        "llm_path": llm_path,
        "model_path": model_path,
        "sd_executable": sd_exe_used,
        "elapsed_seconds": round(elapsed_seconds, 2),
    }
    log = load_generation_log()
    log.append(entry)
    try:
        with open(GENERATION_LOG_PATH, "w", encoding="utf-8") as f:
            json.dump(log, f, indent=2, ensure_ascii=False)
    except OSError as e:
        print(f"Warning: Failed to save generation log: {e}")


def find_sd_executable():
    """Auto-detect available stable-diffusion executable."""
    candidates = [
        ("sd-cli.exe", "sd-cli.exe (recommended)"),
        ("sd.exe", "sd.exe (legacy)"),
    ]
    for exe_name, label in candidates:
        exe_path = SD_BIN_DIR / exe_name
        if exe_path.exists():
            return str(exe_path), label
    return None, None


SD_EXE, SD_EXE_LABEL = find_sd_executable()

DEFAULT_VAE_PATH = str(ROOT / "models" / "vae" / "ae.safetensors")
DEFAULT_LLM_PATH = str(ROOT / "models" / "llm" / "Qwen3-4B-Instruct-2507-Q4_K_M.gguf")

FIRST_RUN = True

RES_PRESETS = [
    ("1:1 (256x256)", 256, 256),
    ("1:1 (512x512)", 512, 512),
    ("1:1 (768x768)", 768, 768),
    ("1:1 (1024x1024)", 1024, 1024),
    ("16:9 (640x384)", 640, 384),
    ("16:9 (896x512)", 896, 512),
    ("16:9 (1024x576)", 1024, 576),
    ("9:16 (384x640)", 384, 640),
    ("9:16 (512x896)", 512, 896),
    ("9:16 (576x1024)", 576, 1024),
    ("4:3 (640x480)", 640, 480),
    ("4:3 (768x576)", 768, 576),
    ("3:2 (768x512)", 768, 512),
    ("2:3 (512x768)", 512, 768),
]

SIZE_OPTIONS = sorted({s for _, w, h in RES_PRESETS for s in (w, h)})

def apply_preset(preset_label):
    for name, w, h in RES_PRESETS:
        if name == preset_label:
            return w, h
    return gr.update(), gr.update()

def gen_image(prompt, width, height, steps, seed, cfg_scale, vae_path, llm_path, output_path=None):
    if SD_EXE is None:
        available = list(SD_BIN_DIR.glob("*.exe")) if SD_BIN_DIR.exists() else []
        if available:
            exe_list = ", ".join([f.name for f in available])
            return None, f"No supported executable found in sd_bin/. Found: {exe_list}\n\nExpected: sd-cli.exe or sd.exe\n\nDownload from: https://github.com/leejet/stable-diffusion.cpp/releases"
        return None, f"sd_bin folder not found. Create folder: {SD_BIN_DIR}"

    uid = uuid.uuid4().hex[:8]
    if output_path and str(output_path).strip():
        out_file = str(output_path).strip()
    else:
        out_file = os.path.join(OUTDIR, f"out_{uid}.png")
    if not os.path.isfile(SD_EXE):
        return None, f"Executable not found: {SD_EXE}"
    if not os.path.isfile(MODEL_PATH):
        return None, f"Model not found: {MODEL_PATH}"
    vae_path = (vae_path or "").strip() or DEFAULT_VAE_PATH
    llm_path = (llm_path or "").strip() or DEFAULT_LLM_PATH
    if not os.path.isfile(vae_path):
        return None, f"VAE not found: {vae_path}"
    if not os.path.isfile(llm_path):
        return None, f"LLM (text encoder) not found: {llm_path}"

    # sd-cli.exe uses seed < 0 for random; UI sends 0 for random
    seed_requested = int(seed)
    actual_seed = seed_requested
    if actual_seed == 0:
        actual_seed = -1

    # Use a list of arguments to avoid Windows shell quoting issues.
    # shell=True + embedded quotes can cause sd-cli.exe to silently ignore
    # flags like -o (output path) and -H/-W (dimensions).
    cmd = [
        SD_EXE,
        "--diffusion-model", MODEL_PATH,
        "--vae", vae_path,
        "--llm", llm_path,
        "-p", str(prompt),
        "--cfg-scale", str(cfg_scale),
        "--steps", str(int(steps)),
        "-H", str(int(height)),
        "-W", str(int(width)),
        "-o", out_file,
        "--seed", str(actual_seed),
    ]
    print("Running:", " ".join(cmd))
    t0 = time.perf_counter()
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=str(ROOT))
    t1 = time.perf_counter()
    elapsed = t1 - t0
    print(proc.stdout)
    reported = []
    # Try to extract the actual seed used from sd-cli.exe output
    resolved_seed = actual_seed
    if proc.stdout:
        m = re.search(r"generate_image completed in\s+([0-9.]+)s", proc.stdout)
        if m:
            reported.append(f"sd.exe generate_image: {m.group(1)}s")
        m = re.search(r"sampling completed, taking\s+([0-9.]+)s", proc.stdout)
        if m:
            reported.append(f"sd.exe sampling: {m.group(1)}s")
        m = re.search(r"loading tensors completed, taking\s+([0-9.]+)s", proc.stdout)
        if m:
            reported.append(f"sd.exe model load: {m.group(1)}s")
        # Extract actual seed when random was requested
        seed_match = re.search(r"seed:\s*(\d+)", proc.stdout)
        if seed_match:
            resolved_seed = int(seed_match.group(1))

    timing_line = f"Wall-clock time: {elapsed:.2f}s"
    if reported:
        timing_line += "\n" + "\n".join(reported)

    combined_log = (timing_line + "\n\n" + (proc.stdout.strip() if proc.stdout else "")).strip()
    if proc.returncode != 0:
        return None, f"sd.exe exited with code {proc.returncode}\n\n{combined_log}".strip()

    # Find the generated image
    result_path = None
    if os.path.isfile(out_file):
        result_path = out_file
    else:
        imgs = sorted(Path(OUTDIR).glob("*.png"), key=lambda p: p.stat().st_mtime, reverse=True)
        if imgs:
            result_path = str(imgs[0])

    if result_path:
        # Save generation metadata to log
        save_generation_metadata(
            image_path=result_path,
            prompt=str(prompt),
            width=int(width),
            height=int(height),
            steps=int(steps),
            seed_requested=seed_requested,
            seed_actual=resolved_seed,
            cfg_scale=float(cfg_scale),
            vae_path=vae_path,
            llm_path=llm_path,
            model_path=MODEL_PATH,
            elapsed_seconds=elapsed,
            sd_exe_used=SD_EXE,
        )
        return result_path, combined_log if combined_log else "Done"
    else:
        return None, (combined_log if combined_log else "No image was produced. Check sd.exe output above.")

with gr.Blocks() as demo:
    gr.Markdown("# Z-Image Turbo - Minimal UI")
    with gr.Tabs():
        with gr.Tab("Basic"):
            with gr.Row():
                prompt = gr.Textbox(label="Prompt", value="A large orange octopus on an ocean floor, cinematic, 8k")
            with gr.Row():
                preset = gr.Dropdown([n for n, _, _ in RES_PRESETS], value="1:1 (512x512)", label="Resolution / Aspect ratio")
            with gr.Row():
                width = gr.Dropdown(SIZE_OPTIONS, value=512, label="Width")
                height = gr.Dropdown(SIZE_OPTIONS, value=512, label="Height")
                steps = gr.Slider(1, 50, value=8, step=1, label="Steps")
            with gr.Row():
                cfg_scale = gr.Slider(0.0, 10.0, value=1.0, step=0.1, label="CFG Scale")
                seed = gr.Number(value=0, label="Seed (0 = random)")
            gr.Markdown("High resolutions (like 1024x1024) use more VRAM and take longer.")

        with gr.Tab("Advanced"):
            unlock = gr.Checkbox(value=False, label="Allow editing advanced paths")
            with gr.Row():
                vae_path = gr.Textbox(label="VAE path", value=DEFAULT_VAE_PATH, interactive=False)
                llm_path = gr.Textbox(label="LLM (Qwen) path", value=DEFAULT_LLM_PATH, interactive=False)
            with gr.Row():
                output_path = gr.Textbox(label="Output Path (Optional)", value="", placeholder="e.g. C:\\my_folder\\image.png", interactive=False)

            def set_unlocked(enabled):
                return gr.update(interactive=bool(enabled)), gr.update(interactive=bool(enabled)), gr.update(interactive=bool(enabled))

            unlock.change(set_unlocked, inputs=[unlock], outputs=[vae_path, llm_path, output_path])

    preset.change(apply_preset, inputs=[preset], outputs=[width, height])

    with gr.Row():
        btn = gr.Button("Generate")
    img = gr.Image(label="Result")
    status = gr.Textbox(label="Status", interactive=False, lines=12)

    def run_and_return(p, w, h, st, sd, cfg, vae, llm, out_path):
        global FIRST_RUN
        if FIRST_RUN:
            FIRST_RUN = False
            yield None, "Generating... (first run can take longer due to model loading)", gr.update(interactive=False)
        else:
            yield None, "Generating...", gr.update(interactive=False)
        out, log = gen_image(p, int(w), int(h), int(st), int(sd), float(cfg), vae, llm, out_path)
        if out:
            yield out, log if log else "Done", gr.update(interactive=True)
            return
        yield None, log if log else "Failed", gr.update(interactive=True)

    btn.click(run_and_return, inputs=[prompt, width, height, steps, seed, cfg_scale, vae_path, llm_path, output_path], outputs=[img, status, btn])

app = FastAPI()

class GenerateRequest(BaseModel):
    prompt: str
    width: int = 512
    height: int = 512
    steps: int = 8
    seed: int = 0
    cfg_scale: float = 1.0
    vae_path: str = ""
    llm_path: str = ""
    output_path: str = None

@app.post("/api/generate")
def api_generate(req: GenerateRequest):
    out, log = gen_image(
        prompt=req.prompt,
        width=req.width,
        height=req.height,
        steps=req.steps,
        seed=req.seed,
        cfg_scale=req.cfg_scale,
        vae_path=req.vae_path,
        llm_path=req.llm_path,
        output_path=req.output_path
    )
    if out:
        return {"status": "success", "image_path": out, "log": log}
    else:
        return {"status": "error", "message": log}

app = gr.mount_gradio_app(app, demo, path="/")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9000)
