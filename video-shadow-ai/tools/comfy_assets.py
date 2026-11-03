"""ComfyUI: genera due materiali di carta (SD-Turbo, 1 passo, CPU) e li mette nel montaggio HyperFrames.
- paper.png: carta crema fatta a mano per i cartellini
- endcard_bg.png: carta blu notte con fibre per il fondo del cartello finale
Non tocca le scene Blender (niente nuovi render). Richiede huggingface.co abilitato per il checkpoint.
Uso: /opt/venv/chatterbox/bin/python tools/comfy_assets.py
"""
import json, os, shutil, subprocess, time, urllib.request
from huggingface_hub import hf_hub_download

COMFY = "/opt/repos/Comfy-Org_ComfyUI"; ROOT = "/home/user/APEX-AI-Terminal/video-shadow-ai"
ck = f"{COMFY}/models/checkpoints/sd_turbo.safetensors"
if not os.path.exists(ck):
    p = hf_hub_download("stabilityai/sd-turbo", "sd_turbo.safetensors"); shutil.copy(p, ck)

def up():
    try: urllib.request.urlopen("http://127.0.0.1:8188/system_stats", timeout=2); return True
    except Exception: return False
srv = None
if not up():
    srv = subprocess.Popen(["/opt/venv/chatterbox/bin/python", "main.py", "--cpu", "--listen", "127.0.0.1", "--port", "8188", "--disable-auto-launch"], cwd=COMFY,
                           stdout=open("/opt/logs/comfy_run.log", "w"), stderr=subprocess.STDOUT)
    while not up(): time.sleep(2)

def gen(prompt, name, w=768, h=768, seed=1):
    wf = {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "sd_turbo.safetensors"}},
        "2": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["1", 1], "text": prompt}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["1", 1], "text": "text, letters, watermark, logo"}},
        "4": {"class_type": "EmptyLatentImage", "inputs": {"width": w, "height": h, "batch_size": 1}},
        "5": {"class_type": "SDTurboScheduler", "inputs": {"model": ["1", 0], "steps": 1, "denoise": 1.0}},
        "6": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "euler_ancestral"}},
        "7": {"class_type": "SamplerCustom", "inputs": {"model": ["1", 0], "add_noise": True, "noise_seed": seed, "cfg": 1.0,
              "positive": ["2", 0], "negative": ["3", 0], "sampler": ["6", 0], "sigmas": ["5", 0], "latent_image": ["4", 0]}},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["7", 0], "vae": ["1", 2]}},
        "9": {"class_type": "SaveImage", "inputs": {"images": ["8", 0], "filename_prefix": name}},
    }
    req = urllib.request.Request("http://127.0.0.1:8188/prompt", data=json.dumps({"prompt": wf}).encode(), headers={"Content-Type": "application/json"})
    pid = json.load(urllib.request.urlopen(req))["prompt_id"]
    while True:
        h = json.load(urllib.request.urlopen(f"http://127.0.0.1:8188/history/{pid}"))
        if pid in h: break
        time.sleep(2)
    img = h[pid]["outputs"]["9"]["images"][0]["filename"]
    return f"{COMFY}/output/{img}"

a = gen("close-up of cream handmade paper texture, visible natural fibers, soft even light, top view, high detail", "paper", seed=11)
b = gen("deep navy blue handmade paper texture, subtle fibers and flecks, soft even light, top view", "endcard", 1024, 576, seed=5)
subprocess.run(["/opt/ffmpeg-src/bin/ffmpeg", "-v", "error", "-y", "-i", a, "-vf", "scale=512:512", f"{ROOT}/hyperframes/assets/paper.png"], check=True)
subprocess.run(["/opt/ffmpeg-src/bin/ffmpeg", "-v", "error", "-y", "-i", b, "-vf", "scale=1920:1080:flags=lanczos", f"{ROOT}/hyperframes/assets/endcard_bg.png"], check=True)
print("asset ComfyUI pronti:", a, b)
if srv: srv.terminate()
