# -*- coding: utf-8 -*-
"""GivemeClip driver (Windows / macOS / Linux): one command per stage of the ghost-editor raw-cut pipeline, with every Windows fix
found on the "Claude AI ตัดคลิป" job (2026-11-12) built in. Stdlib only; run with the system python3.

    python3 gmc.py doctor [--fix]                 tools, venvs, SFX names; --fix restores the stuck *.wav.tmp.wav SFX
    python3 gmc.py prep  <source.mp4> <P> [--script สคิป.txt]
                                                  ASCII project P (e.g. D:/reels/<name>): hardlink + rawcut_prep + VAD + Thai
                                                  island transcripts (GPU) and facescan running side by side
    python3 gmc.py islands <P>                    the island table (raw seconds + text) to pick takes from
    python3 gmc.py cut   <P>                      cut.json -> plan_cut + assemble --alt + voice_smooth + qa_cut
    python3 gmc.py reel  <P>                      P/reel: plate + voice + face.json, ready for a generator (reel.py)
    python3 gmc.py snap  <P/reel> <t1,t2,...>     HyperFrames snapshots -> build/snaps + build/sheet.jpg
    python3 gmc.py render <P/reel> <out.mp4> [--speed 1.15] [--bed music.wav --bed-at 7.7 --bed-from 3.2 --bed-db -16]
                                                  [--no-render]   HyperFrames render -> speed -> music bed ducked
                                                  under the voice -> -14 LUFS H.264 delivery -> QA numbers
Every python child gets PYTHONUTF8=1 (Thai json / cp874), every .sh goes through Git Bash, and HyperFrames gets the real
ffmpeg.exe (its hf_ffmpeg.sh wrapper cannot be spawned by Node on Windows: "spawn EFTYPE")."""
import json, os, re, shutil, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
SKILLS = os.path.abspath(os.path.join(HERE, "..", ".."))           # the folder that holds givemeclip/ and depth-parallax/
# every path can be set by an environment variable (INSTALL.md); the defaults follow the install guide
GE = os.environ.get("GMC_GHOST_EDITOR", os.path.join(SKILLS, "ghost-editor")).replace("\\", "/")  # ASCII path!
WHISPER_PY = os.environ.get("GMC_WHISPER_PY", sys.executable)      # python with torch (+CUDA) + openai-whisper + silero-vad
MP_PY = os.environ.get("GMC_MEDIAPIPE_PY", sys.executable)         # python with mediapipe + opencv (facescan, face_track)
PARALLAX = os.environ.get("GMC_PARALLAX", os.path.join(SKILLS, "depth-parallax", "scripts", "parallax.py"))
BASH = next((b for b in ("C:/Program Files/Git/bin/bash.exe", shutil.which("bash")) if b and os.path.exists(b)), "bash")
FFMPEG = shutil.which("ffmpeg") or "ffmpeg"
ENV = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8", "HYPERFRAMES_FFMPEG_PATH": FFMPEG}


def sh(cmd, cwd=None, check=True, **kw):
    print("$", " ".join(str(c) for c in cmd), flush=True)
    t = time.time()
    r = subprocess.run([str(c) for c in cmd], cwd=cwd, env=ENV, check=check, **kw)
    print(f"  ({time.time() - t:.0f} s)", flush=True)
    return r


def need_ascii(p):
    if not str(p).isascii():
        sys.exit(f"{p}: use an ASCII path (OpenCV cannot open non-ASCII paths on Windows), e.g. D:/reels/<name>")


# ---------------------------------------------------------------- doctor
def doctor(fix=False):
    ok = lambda b, m: print(("  ok    " if b else "  MISS  ") + m)
    ok(os.path.exists(GE + "/SKILL.md"), f"ghost-editor at {GE}")
    ok(os.path.exists(WHISPER_PY), f"whisper venv {WHISPER_PY}")
    r = subprocess.run([WHISPER_PY, "-c", "import silero_vad, whisper, torch; print(torch.cuda.is_available())"],
                       capture_output=True, text=True) if os.path.exists(WHISPER_PY) else None
    ok(bool(r and r.returncode == 0), "silero-vad + whisper in that venv" + (f" (CUDA {r.stdout.strip()})" if r and r.returncode == 0 else
       "  -> <GMC_WHISPER_PY> -m pip install silero-vad==6.2.3  (INSTALL.md step 3)"))
    r = subprocess.run([MP_PY, "-c", "import mediapipe, cv2"], capture_output=True) if os.path.exists(MP_PY) else None
    ok(bool(r and r.returncode == 0), f"mediapipe python {MP_PY}")
    ok(os.path.exists(PARALLAX), "depth-parallax")
    ok(bool(shutil.which("ffmpeg")), f"ffmpeg {FFMPEG}")
    ok(os.path.exists(BASH), f"Git Bash {BASH}")
    sfx = os.path.join(GE, "library", "sfx")
    man = json.load(open(os.path.join(sfx, "manifest.json"), encoding="utf-8"))
    miss = [v["file"] for v in man.values() if not os.path.exists(os.path.join(sfx, v["file"]))]
    stuck = [f for f in miss if os.path.exists(os.path.join(sfx, f + ".tmp.wav"))]
    if stuck and fix:
        for f in stuck:
            shutil.copy(os.path.join(sfx, f + ".tmp.wav"), os.path.join(sfx, f))
        print(f"  fixed {len(stuck)} SFX copied from *.wav.tmp.wav")
        miss = [f for f in miss if f not in stuck]
    ok(not miss, f"SFX kit {len(man) - len(miss)}/{len(man)}" + (f"  -> gmc.py doctor --fix ({len(stuck)} stuck as .tmp.wav)" if miss else ""))
    du = shutil.disk_usage(os.path.abspath(os.sep))
    ok(du.free > 15e9, f"disk free {du.free / 1e9:.1f} GB (a 2 GB source needs ~10 GB of proxies and plates)")


# ---------------------------------------------------------------- prep
def prep(src, P, script=None):
    need_ascii(P)
    os.makedirs(f"{P}/src", exist_ok=True)
    raw = f"{P}/src/raw.mp4"
    if not os.path.exists(raw):
        try:
            os.link(src, raw)                                  # same drive: no copy of a 2 GB file
        except OSError:
            shutil.copy(src, raw)
    if script:
        shutil.copy(script, f"{P}/src/script.txt")
    if not os.path.exists(f"{P}/build/proxy.mp4"):
        sh([BASH, f"{GE}/scripts/rawcut_prep.sh", raw, P])     # ~7.5 min for a 5 min 1728x3072 HEVC on CPU
    # facescan (CPU, ~25 min for 18k frames) runs while the GPU transcribes
    fs = None
    if not os.path.exists(f"{P}/build/facescan.json"):
        print("$ facescan (background)")
        fs = subprocess.Popen([MP_PY, f"{GE}/scripts/facescan.py", f"{P}/build/proxy.mp4", f"{P}/build/facescan.json", "--pts", raw],
                              env=ENV, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if not os.path.exists(f"{P}/build/vad.json"):
        sh([WHISPER_PY, f"{GE}/scripts/vad_pauses.py", f"{P}/build/full.wav", "--min-pause", "0.3", "--out", f"{P}/build/vad.json"])
    if not os.path.exists(f"{P}/build/islands.json"):
        sh([WHISPER_PY, f"{GE}/scripts/islands_tx.py", f"{P}/build/a16.wav", "--vad", f"{P}/build/vad.json", "--lang", "th",
            "--out", f"{P}/build/islands.json"], cwd=P)         # ~17 min for 97 s of Thai speech (fp32 + word timing)
    islands(P)
    if fs:
        print("waiting for facescan ...", flush=True)
        fs.wait()
        print("facescan", "done" if fs.returncode == 0 else f"FAILED ({fs.returncode})")


def load_islands(P):
    p = f"{P}/build/islands.json"
    try:
        return json.load(open(p, encoding="utf-8"))
    except UnicodeDecodeError:                                 # written by a child without PYTHONUTF8: cp874 -> utf-8
        d = json.load(open(p, encoding="cp874"))
        json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False)
        return d


def islands(P):
    sys.stdout.reconfigure(encoding="utf-8")
    for i, x in enumerate(load_islands(P)):
        txt = re.sub(r"(.{1,4}?)\1{5,}", r"\1\1…", x["text"].replace(" ", ""))   # whisper's Thai repeat loops, squeezed
        print(f"{i:3d} {x['a']:8.2f} {x['b']:8.2f} ({x['b'] - x['a']:4.1f}) {txt[:110]}")


# ---------------------------------------------------------------- cut
def cut(P):
    if not os.path.exists(f"{P}/cut.json"):
        sys.exit(f"write {P}/cut.json first (pieces in raw seconds; references in SKILL.md step 3)")
    fs = ["--facescan", f"{P}/build/facescan.json"] if os.path.exists(f"{P}/build/facescan.json") else []
    sh(["python3", f"{GE}/scripts/plan_cut.py", P])
    sh(["python3", f"{GE}/recipes/clean-os/assemble.py", P, "--plan", "build/plan.json", "--alt"])   # ~9.5 min
    sh(["python3", f"{GE}/scripts/voice_smooth.py", P, "--plan", "build/plan.json"])
    if fs:
        sh(["python3", f"{GE}/scripts/qa_cut.py", f"{P}/build/rawcut.mp4", "--plan", f"{P}/build/plan.json", *fs], check=False)
    print(f"raw cut: {P}/build/rawcut.mp4  cut sheet: {P}/build/cutsheet.jpg (look at it: facescan 'turn' flags on every"
          " piece are a baseline artefact when the speaker sits off-centre)")


# ---------------------------------------------------------------- reel project
def reel(P):
    R = f"{P}/reel"
    for d in ("assets", "build"):
        os.makedirs(f"{R}/{d}", exist_ok=True)
    shutil.copy(f"{P}/assets/alt.mp4", f"{R}/assets/plate.mp4")
    shutil.copy(f"{P}/assets/voice.wav", f"{R}/assets/voice.wav")
    sh([MP_PY, f"{GE}/scripts/face_track.py", f"{R}/assets/plate.mp4", "--out", f"{R}/build/face.json"])
    for f in ("LeelaUIb.ttf", "LeelawUI.ttf"):
        os.makedirs(f"{R}/assets/fonts", exist_ok=True)
        if os.path.exists(f"C:/Windows/Fonts/{f}"):
            shutil.copy(f"C:/Windows/Fonts/{f}", f"{R}/assets/fonts/{f}")
    ex = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "templates", "reel_example.py")
    if not os.path.exists(f"{R}/reel.py"):
        src = open(ex, encoding="utf-8").read()
        src = re.sub(r"^SK = .*$", f'SK = "{GE}"', src, count=1, flags=re.M)   # this machine's ghost-editor
        open(f"{R}/reel.py", "w", encoding="utf-8").write(src)
    print(f"{R}: plate, voice, face.json, Thai fonts, reel.py (the Claude AI ตัดคลิป generator to adapt)")


# ---------------------------------------------------------------- snapshots
def snap(R, times):
    out = f"{R}/build/snaps"
    sh([BASH, f"{GE}/scripts/hf.sh", "snapshot", ".", "-o", out, "--keep", "--no-end", "--timeout", "20000", "--at", times], cwd=R)
    ts = [t.strip() for t in times.split(",") if t.strip()]
    ins = []
    for t in ts:
        f = f"{out}/at-{float(t):g}s.png"
        if os.path.exists(f):
            ins += ["-i", f]
    n = len(ins) // 2
    if n:
        sh([FFMPEG, "-v", "error", "-y", *ins, "-filter_complex", f"{''.join(f'[{i}]' for i in range(n))}hstack={n},scale={min(2400, 240 * n)}:-1"
            if n > 1 else "scale=240:-1", f"{R}/build/sheet.jpg"])
        print(f"sheet: {R}/build/sheet.jpg")


# ---------------------------------------------------------------- render + delivery
def ebur(path):
    e = subprocess.run([FFMPEG, "-hide_banner", "-nostats", "-i", path, "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    I = re.findall(r"I:\s+(-?[\d.]+) LUFS", e)
    tp = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", e)
    return float(I[-1]) if I else None, float(tp[-1]) if tp else None


def render(R, out, speed=1.0, bed=None, bed_at=0.0, bed_from=0.0, bed_db=-16.0, do_render=True):
    master = f"{R}/build/reel.mp4"
    if do_render:
        sh([BASH, f"{GE}/scripts/hf.sh", "render", ".", "-o", "build/reel.mp4"], cwd=R)     # ~1.5 min for 28 s
    ins = ["-i", master]
    vf = f"setpts=PTS/{speed},fps=30" if speed != 1.0 else "fps=30"
    af = [f"[0:a]atempo={speed},aresample=48000[v]" if speed != 1.0 else "[0:a]aresample=48000[v]"]
    if bed:
        ins += ["-ss", f"{bed_from}", "-i", bed]
        ms = int(bed_at / speed * 1000)                                   # the bed is placed on the FINAL (sped) timeline
        af += [f"[1:a]aresample=48000,volume={bed_db}dB,afade=t=in:d=0.6,adelay={ms}|{ms}[b0]",
               "[v]asplit=2[v1][sc]", "[b0][sc]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=350[b]",
               "[v1][b]amix=inputs=2:duration=first:normalize=0[m]"]
    else:
        af += ["[v]anull[m]"]
    af += ["[m]loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]"]
    tmp = f"{R}/build/delivery_tmp.mp4"
    sh([FFMPEG, "-v", "error", "-y", *ins, "-filter_complex", f"[0:v]{vf}[vv];" + ";".join(af), "-map", "[vv]", "-map", "[a]",
        "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-maxrate", "20M", "-bufsize", "40M", "-profile:v", "high", "-level", "4.2",
        "-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
        "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", "-shortest", tmp])
    shutil.move(tmp, out)
    # QA: length, loudness, true peak, black, freeze
    d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", out],
                             capture_output=True, text=True).stdout.strip() or 0)
    I, tp = ebur(out)
    e = subprocess.run([FFMPEG, "-hide_banner", "-nostats", "-i", out, "-an", "-vf", "blackdetect=d=0.1:pix_th=0.1,freezedetect=n=0.003:d=0.8",
                        "-f", "null", "-"], capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    black, freeze = len(re.findall("black_start", e)), len(re.findall("freeze_start", e))
    print(f"\n{out}\n  length {d:.2f} s | {I} LUFS | true peak {tp} dBFS | black {black} | freeze {freeze}")
    print("  PASS" if (I is not None and abs(I + 14) <= 1 and (tp or 0) <= -1.0 and not black and not freeze and d <= 60) else "  CHECK the numbers above")


def main():
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help"):
        print(__doc__); return
    cmd, rest = a[0], a[1:]
    opt = lambda k, d=None: rest[rest.index(k) + 1] if k in rest else d
    if cmd == "doctor":
        doctor("--fix" in rest)
    elif cmd == "prep":
        prep(rest[0], rest[1], opt("--script"))
    elif cmd == "islands":
        islands(rest[0])
    elif cmd == "cut":
        cut(rest[0])
    elif cmd == "reel":
        reel(rest[0])
    elif cmd == "snap":
        snap(rest[0], rest[1])
    elif cmd == "render":
        render(rest[0], rest[1], float(opt("--speed", 1.0)), opt("--bed"), float(opt("--bed-at", 0)), float(opt("--bed-from", 0)),
               float(opt("--bed-db", -16)), "--no-render" not in rest)
    else:
        sys.exit(f"unknown command {cmd}\n{__doc__}")


if __name__ == "__main__":
    main()
