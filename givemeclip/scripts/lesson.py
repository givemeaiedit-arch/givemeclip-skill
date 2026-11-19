# -*- coding: utf-8 -*-
"""GivemeClip pipeline C: full-length LESSON / screen-recording / any-orientation edit at the source's own size
(16:9 lessons บทที่ 2-3, 2026-11-19). Stdlib only; run with the system python:  PYTHONUTF8=1 python lesson.py <cmd> ...

    lesson.py prep  <source> <P>          ASCII project P: copy source, audio, silero VAD, batched Thai transcript (GPU),
                                          timestamped contact sheets build/s*.jpg, transcript with gaps -> build/words.txt
    lesson.py words <P>                   print the transcript (time | text, gaps) again
    lesson.py frames <P> t1,t2,...        full-res frames build/k/t<sec>.png (find zoom targets / layout in pixels)
    lesson.py cut   <P>                   P/lesson.json -> plate.mp4 (source size, GOP 15) + voice.wav + build/edl.json
                                          (--dry: print the pieces only)
    lesson.py reel  <P>                   P/reel: plate, voice (enhanced), fonts, SFX, reel.py from templates/lesson_reel.py
    lesson.py voice <P>                   re-run the voice chain (EQ + denoise + compressor, fast-forward parts at 0.25)
    lesson.py bed   <P> [--track digital-clouds] [--mute a-b,a-b] [--speed 1.1]
                                          looped music bed -> build/bed.wav; --mute = RAW source seconds (a clip that has its
                                          own music playing) mapped through the EDL and the speed-up
Then:  gmc.py snap <P>/reel t1,t2,...   and   gmc.py render <P>/reel "<next to source> (final).mp4" --speed 1.1
       --bed <P>/build/bed.wav --bed-db -32

lesson.json (all RAW source seconds):
  {"segments": [{"a": 0, "b": 16.75, "mode": "head"},        talking head: speech kept, pauses cut (jump cuts)
                {"a": 38.6, "b": 539.6, "mode": "screen"}],  screen: continuous, silent gaps fast-forwarded
   "drop": [[74.9, 81.45]],          retakes / mutters / black frames: removed
   "keep_1x": [[476.4, 510.8]],      never fast-forward (a finished clip playing, a demo)
   "wait": [[267.45, 469.0, 4.0]],   one fast-forward block squeezed to N seconds (Claude working, rendering ...)
   "ff_min_gap": 1.0, "ff_cap": 1.5, "ff_long": 3.0}
"""
import json, os, re, shutil, subprocess, sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
SKILLS = os.path.dirname(SKILL)                                   # the folder that holds givemeclip/ and depth-parallax/
# every path can be set by an environment variable (INSTALL.md), the same ones gmc.py reads
GE = os.environ.get("GMC_GHOST_EDITOR", os.path.join(SKILLS, "ghost-editor")).replace("\\", "/")
WHISPER_PY = os.environ.get("GMC_WHISPER_PY", sys.executable)     # torch + silero-vad (VAD)
FW_PY = os.environ.get("GMC_FW_PY", WHISPER_PY)                   # faster-whisper (batched Thai transcript)
FONTS = os.environ.get("GMC_FONTS", os.path.join(SKILL, "assets", "fonts"))   # Kanit-*.ttf (Google Fonts, OFL)
SFX_LIB = f"{GE}/library/sfx"
MUSIC_LIB = f"{GE}/library/music"
SFX_KIT = ["whoosh-1", "whoosh-2", "pop-2", "pop-3", "ding-1", "tech-ui-confirm", "impact-1", "send-swoosh", "kaching-1",
           "tech-digital-whoosh", "click-1", "riser-1", "cc0-tada", "tick-1"]
ENV = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}
FPS = 30
VOICE_CHAIN = ("highpass=f=80,afftdn=nf=-38:nr=8,equalizer=f=300:t=q:w=1.2:g=-2,equalizer=f=3200:t=q:w=1.0:g=3,"
               "equalizer=f=9000:t=h:w=0.7:g=1.5,acompressor=threshold=-24dB:ratio=3.5:attack=8:release=120:makeup=4dB,"
               "loudnorm=I=-15:LRA=6:TP=-2")


def sh(cmd, **kw):
    print("$", " ".join(str(c) for c in cmd)[:220], flush=True)
    return subprocess.run(cmd, check=True, env=ENV, **kw)


def ff(*a):
    sh(["ffmpeg", "-v", "error", "-y", *a])


def probe(path):
    o = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height:format=duration",
                        "-of", "json", path], capture_output=True, text=True).stdout
    j = json.loads(o)
    return j["streams"][0]["width"], j["streams"][0]["height"], float(j["format"]["duration"])


def need_ascii(P):
    if not P.isascii():
        sys.exit(f"project folder must be ASCII (OpenCV / some tools cannot open Thai paths): {P}")


# ---------------------------------------------------------------- prep
def prep(src, P):
    need_ascii(P)
    for d in ("src", "build/k", "build/f"):
        os.makedirs(f"{P}/{d}", exist_ok=True)
    raw = f"{P}/src/raw.mp4"
    if not os.path.exists(raw):
        try:
            os.link(src, raw)
        except OSError:
            shutil.copy(src, raw)
    json.dump({"source": os.path.abspath(src)}, open(f"{P}/build/source.json", "w", encoding="utf-8"), ensure_ascii=False)
    w, h, d = probe(raw)
    shape = "16:9 landscape" if w > h * 1.3 else "9:16 vertical" if h > w * 1.3 else "square-ish"
    print(f"source {w}x{h}, {d:.1f} s -> {shape}")
    if not os.path.exists(f"{P}/build/a16.wav"):
        ff("-i", raw, "-vn", "-ac", "1", "-ar", "16000", f"{P}/build/a16.wav")
        ff("-i", raw, "-vn", "-ac", "2", "-ar", "48000", f"{P}/build/full.wav")
    # contact sheets while the GPU transcribes
    sheets = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-i", raw, "-vf",
                               "fps=1/5,scale=480:-1,drawtext=text='%{pts\\:hms}':x=6:y=6:fontsize=22:fontcolor=yellow:box=1:boxcolor=black",
                               f"{P}/build/f/%03d.jpg"])
    if not os.path.exists(f"{P}/build/vad.json"):
        sh([WHISPER_PY, f"{GE}/scripts/vad_pauses.py", f"{P}/build/full.wav", "--min-pause", "0.3", "--out", f"{P}/build/vad.json"])
    if not os.path.exists(f"{P}/build/fw.json"):
        sh([FW_PY, f"{HERE}/fw_batch.py", f"{P}/build/a16.wav", f"{P}/build/fw.json"])
    sheets.wait()
    n = len(os.listdir(f"{P}/build/f"))
    for i in range(0, n, 20):
        ff("-start_number", str(i + 1), "-i", f"{P}/build/f/%03d.jpg", "-frames:v", "1", "-vf", "tile=4x5", f"{P}/build/s{i // 20}.jpg")
    print(f"contact sheets: {P}/build/s0.jpg ... (every 5 s, 20 per sheet)")
    words(P)


def words(P):
    d = json.load(open(f"{P}/build/fw.json", encoding="utf-8"))
    ws = [w for s in d for w in s["words"]]
    out, line, t0, prev = [], "", ws[0]["start"], ws[0]["start"]
    for w in ws:
        if w["start"] - prev > 0.6 or len(line) > 80:
            out.append(f"{t0:7.1f}-{prev:7.1f} {line}")
            if w["start"] - prev > 0.6:
                out.append(f"          gap {w['start'] - prev:.1f}")
            line, t0 = "", w["start"]
        line += w["word"]; prev = w["end"]
    out.append(f"{t0:7.1f}-{prev:7.1f} {line}")
    txt = "\n".join(out)
    open(f"{P}/build/words.txt", "w", encoding="utf-8").write(txt)
    print(txt)
    print("\nWhisper Thai garbles names (Claude -> คอร์ดโค้ด/cross code, GivemeClip -> กิ๊บมีคลิป): use it for TIMES, write the captions yourself.")


def frames(P, ts):
    for t in ts.split(","):
        ff("-ss", t, "-i", f"{P}/src/raw.mp4", "-frames:v", "1", f"{P}/build/k/t{t}.png")
    print(f"{P}/build/k/t<sec>.png")


# ---------------------------------------------------------------- cut
def plan(P):
    cfg = json.load(open(f"{P}/lesson.json", encoding="utf-8"))
    takes = [(t["a"], t["b"]) for t in json.load(open(f"{P}/build/vad.json"))["takes"]]
    drop = [tuple(x) for x in cfg.get("drop", [])]
    keep = [tuple(x) for x in cfg.get("keep_1x", [])]
    waits = [tuple(x) for x in cfg.get("wait", [])]
    gmin, cap, long_ = cfg.get("ff_min_gap", 1.0), cfg.get("ff_cap", 1.5), cfg.get("ff_long", 3.0)
    pieces = []
    for seg in cfg["segments"]:
        A, B, mode = seg["a"], seg["b"], seg.get("mode", "screen")
        tk = [(max(a, A), min(b, B)) for a, b in takes if b > A and a < B]
        if mode == "head":
            m = []
            for a, b in tk:
                a, b = max(A, a - 0.04), min(B, b + 0.08)
                if m and a - m[-1][1] < 0.22:
                    m[-1] = (m[-1][0], b)
                else:
                    m.append((a, b))
            pieces += [(a, b, 1.0, True) for a, b in m]
        else:
            t = A
            for a, b in tk:
                a, b = max(a - 0.06, t), min(b + 0.10, B)
                if a > t:
                    g = a - t
                    if g < gmin or any(t >= k0 and a <= k1 for k0, k1 in keep):
                        pieces.append((t, a, 1.0, False))
                    else:
                        out = long_ if g > 60 else min(cap, 0.35 + g * 0.11)
                        pieces.append((t, a, round(g / out, 3), False))
                if b > a:
                    pieces.append((a, b, 1.0, False))
                t = max(t, b)
            if B - t > 0.05:
                g = B - t
                pieces.append((t, B, 1.0 if g < gmin else round(g / min(cap, 0.35 + g * 0.11), 3), False))
    # drop ranges
    out = []
    for a, b, s, h in pieces:
        parts = [(a, b)]
        for d0, d1 in drop:
            nxt = []
            for x, y in parts:
                if x < d1 and y > d0:
                    if x < d0: nxt.append((x, d0))
                    if y > d1: nxt.append((d1, y))
                else:
                    nxt.append((x, y))
            parts = nxt
        out += [(x, y, s, h) for x, y in parts]
    # wait blocks: everything inside becomes one fast-forward piece
    for w0, w1, secs in waits:
        glued = []
        for a, b, s, h in out:
            if a < w0 < b:
                b = w0                      # the piece before the wait ends where it starts
            elif w0 <= a < w1 < b:
                a = w1                      # the piece after it starts where it ends
            if b <= w0 or a >= w1:
                glued.append((a, b, s, h))
        out = glued
        out.append((w0, w1, round((w1 - w0) / secs, 3), False))
    out = sorted((round(a, 3), round(b, 3), s, h) for a, b, s, h in out if b - a > 0.05)
    m = []
    for a, b, s, h in out:
        if m and s == 1.0 and m[-1][2] == 1.0 and m[-1][3] == h and abs(a - m[-1][1]) < 0.02:
            m[-1] = (m[-1][0], b, 1.0, h)
        else:
            m.append((a, b, s, h))
    edl, e = [], 0.0
    for i, (a, b, s, h) in enumerate(m):
        n = max(1, round((b - a) / s * FPS))
        edl.append({"i": i, "a": a, "b": b, "speed": s, "edit": round(e, 4), "dur": n / FPS, "head": h})
        e += n / FPS
    return edl, round(e, 4)


def cut(P, dry=False):
    edl, total = plan(P)
    w, h, _ = probe(f"{P}/src/raw.mp4")
    json.dump({"pieces": edl, "total": total, "width": w, "height": h}, open(f"{P}/build/edl.json", "w"), indent=1)
    nff = sum(1 for x in edl if x["speed"] > 1)
    print(f"{len(edl)} pieces, edit {total:.2f} s, fast-forward pieces {nff}")
    prev = None
    for x in edl:
        if dry:
            print(f"  {x['a']:8.2f}-{x['b']:8.2f}  x{x['speed']:<7} edit {x['edit']:7.2f} +{x['dur']:.2f} {'head' if x['head'] else ''}")
        if prev and not x["head"] and abs(x["a"] - prev["b"]) > 0.3:
            print(f"  jump {prev['b']:.2f} -> {x['a']:.2f} (dropped)")
        prev = x
    if dry:
        return
    fc = []
    for x in edl:
        i, a, b, s, n = x["i"], x["a"], x["b"], x["speed"], round(x["dur"] * FPS)
        fc.append(f"[0:v]trim={a}:{b},setpts=(PTS-STARTPTS)/{s},fps={FPS},trim=end_frame={n},tpad=stop_mode=clone:stop={n},"
                  f"trim=end_frame={n},setpts=PTS-STARTPTS[v{i}]")
        if s == 1.0:
            fc.append(f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,aresample=48000,afade=t=in:d=0.012,areverse,afade=t=in:d=0.025,"
                      f"areverse,apad,atrim=end={n / FPS:.6f}[a{i}]")
        else:
            fc.append(f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,aresample=48000,volume=0.35,atempo=2,apad,atrim=end={n / FPS:.6f},"
                      f"afade=t=in:d=0.03,areverse,afade=t=in:d=0.03,areverse[a{i}]")
    fc.append("".join(f"[v{x['i']}][a{x['i']}]" for x in edl) + f"concat=n={len(edl)}:v=1:a=1[v][a]")
    open(f"{P}/build/cut_fc.txt", "w").write(";\n".join(fc))
    print("assembling (about 0.4x real time of the source) ...", flush=True)
    ff("-i", f"{P}/src/raw.mp4", "-filter_complex_script", f"{P}/build/cut_fc.txt", "-map", "[v]", "-map", "[a]",
       "-c:v", "libx264", "-preset", "fast", "-crf", "15", "-g", "15", "-pix_fmt", "yuv420p", "-c:a", "pcm_s16le", f"{P}/build/plate_full.mkv")
    ff("-i", f"{P}/build/plate_full.mkv", "-map", "0:v", "-c", "copy", f"{P}/build/plate.mp4")
    ff("-i", f"{P}/build/plate_full.mkv", "-map", "0:a", "-c:a", "pcm_s16le", f"{P}/build/voice.wav")
    print(f"{P}/build/plate.mp4 + voice.wav ({total:.1f} s)")


# ---------------------------------------------------------------- reel folder, voice, bed
def voice(P):
    R = f"{P}/reel/assets"
    edl = json.load(open(f"{P}/build/edl.json"))["pieces"]
    fast = "+".join(f"between(t,{p['edit']:.3f},{p['edit'] + p['dur']:.3f})" for p in edl if p["speed"] > 1) or "0"
    shutil.copy(f"{P}/build/voice.wav", f"{R}/voice_orig.wav")
    ff("-i", f"{R}/voice_orig.wav", "-af", f"{VOICE_CHAIN},volume='if(gt({fast},0),0.25,1)':eval=frame,aresample=48000",
       "-c:a", "pcm_s16le", f"{R}/voice.wav")
    e = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", f"{R}/voice.wav", "-af", "ebur128", "-f", "null", "-"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    print("voice:", " | ".join(re.findall(r"(I:\s+-?[\d.]+ LUFS|LRA:\s+[\d.]+ LU)", e)[-2:]))


def reel(P):
    R = f"{P}/reel"
    for d in ("assets/fonts", "assets/sfx", "build"):
        os.makedirs(f"{R}/{d}", exist_ok=True)
    shutil.copy(f"{P}/build/plate.mp4", f"{R}/assets/plate.mp4")
    if os.path.isdir(FONTS) and any(f.lower().startswith("kanit") for f in os.listdir(FONTS)):
        for f in os.listdir(FONTS):
            if f.lower().endswith(".ttf"):
                shutil.copy(f"{FONTS}/{f}", f"{R}/assets/fonts/{f}")
    else:
        print("Kanit not found: put Kanit-Medium/SemiBold/Bold/ExtraBold/Black.ttf (fonts.google.com/specimen/Kanit) in a folder"
              " and set GMC_FONTS to it; until then Chrome falls back to Leelawadee UI")
    for s in SFX_KIT:
        if os.path.exists(f"{SFX_LIB}/{s}.wav"):
            shutil.copy(f"{SFX_LIB}/{s}.wav", f"{R}/assets/sfx/{s}.wav")
    voice(P)
    if not os.path.exists(f"{R}/reel.py"):
        shutil.copy(f"{SKILL}/templates/lesson_reel.py", f"{R}/reel.py")
    print(f"{R}: plate, voice (enhanced), Kanit, SFX kit, reel.py (the บทที่ 3 generator: rewrite CAP / CAM / STEPS / scenes)")


def edit_time(edl, t):
    for p in edl:
        if t < p["a"]:
            return p["edit"]
        if p["a"] <= t < p["b"]:
            return p["edit"] + (t - p["a"]) / p["speed"]
    return edl[-1]["edit"] + edl[-1]["dur"]


def bed(P, track="digital-clouds", mute="", speed=1.1):
    E = json.load(open(f"{P}/build/edl.json"))
    need = E["total"] / speed + 2
    src = f"{MUSIC_LIB}/{track}.mp3"
    d = probe_audio(src)
    n = max(1, int(need // (d - 4)) + 1)
    ins = sum([["-i", src] for _ in range(n)], [])
    # chain the copies with 4 s crossfades
    parts, last = [], "[0]"
    for i in range(1, n):
        parts.append(f"{last}[{i}]acrossfade=d=4[x{i}]"); last = f"[x{i}]"
    vol = []
    for rng in [m for m in mute.split(",") if m]:
        a, b = (float(x) for x in rng.split("-"))
        a, b = edit_time(E["pieces"], a) / speed, edit_time(E["pieces"], b) / speed
        vol.append((round(a, 2), round(b, 2)))
    expr = "1"
    for a, b in vol:
        expr = f"if(between(t,{a},{b}),0,if(between(t,{a - 0.8},{a}),({a}-t)/0.8,if(between(t,{b},{b + 1.2}),(t-{b})/1.2,{expr})))"
    fc = ";".join(parts + [f"{last}volume='{expr}':eval=frame,aresample=48000,atrim=end={need:.2f}[out]"])
    ff(*ins, "-filter_complex", fc, "-map", "[out]", f"{P}/build/bed.wav")
    print(f"{P}/build/bed.wav  ({track}, {n}x looped, muted at final {vol})  -> gmc.py render ... --bed {P}/build/bed.wav --bed-db -32")


def probe_audio(path):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                                capture_output=True, text=True).stdout.strip())


def main():
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help"):
        print(__doc__); return
    cmd, rest = a[0], a[1:]
    opt = lambda k, d=None: rest[rest.index(k) + 1] if k in rest else d
    if cmd == "prep":
        prep(rest[0], rest[1])
    elif cmd == "words":
        words(rest[0])
    elif cmd == "frames":
        frames(rest[0], rest[1])
    elif cmd == "cut":
        cut(rest[0], "--dry" in rest)
    elif cmd == "reel":
        reel(rest[0])
    elif cmd == "voice":
        voice(rest[0])
    elif cmd == "bed":
        bed(rest[0], opt("--track", "digital-clouds"), opt("--mute", ""), float(opt("--speed", 1.1)))
    else:
        sys.exit(f"unknown command {cmd}\n{__doc__}")


if __name__ == "__main__":
    main()
