# -*- coding: utf-8 -*-
"""EXAMPLE generator from the first GivemeClip job (Claude AI ตัดคลิป). gmc.py reel copies it into <P>/reel/reel.py;
change LINES (your script) and the scene blocks. Needs the assets it names (house.png, house_orbit.mp4, files/clip*.jpg,
pip_raw.mp4, fast_raw.mp4, emoji/*.webm): make your own or delete those blocks.

Claude AI ตัดคลิป: a custom talking-head reel on ghost-editor's facereel base, keyed to the cut plan.
Run: PYTHONUTF8=1 python3 reel.py   (then hf.sh lint / snapshots / finals.py preview)"""
import json, os, re, sys, wave, array, math
SK = os.environ.get("GMC_GHOST_EDITOR", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "ghost-editor"))
sys.path.insert(0, SK + "/scripts/lib")
from facereel import Reel, W, H, r3, esc  # noqa

P = os.path.dirname(os.path.abspath(__file__))
CUT = os.path.join(P, "..")
plan = json.load(open(os.path.join(CUT, "build/plan.json"), encoding="utf-8"))
isl = json.load(open(os.path.join(CUT, "build/islands.json"), encoding="utf-8"))
TOK = [w for i in isl for w in i["words"]]

# ---------------------------------------------------------------- script phrases -> edit times
LINES = {
    "L1": ["Claude AI", "ตัดคลิปจากไฟล์ดิบ", "ได้ดีขนาดไหน?", "มาดูกันค่ะ"],
    "L4": ["ก่อนอื่น", "ตัดเดดแอร์", "ตัดช่วงที่ไม่ใช้ออกก่อน"],
    "L5": ["เพิ่มเพลง", "ฟังสบายๆ หน่อย"],
    "L6": ["เพิ่มซับไตเติ้ล", "ให้หน่อย"],
    "L7": ["และเพิ่มวีดีโอต้นฉบับ", "เป็นจอเล็กๆ"],
    "L8": ["เพิ่มรูปแบบ", "แบ่งครึ่งจอบน"],
    "L9": ["ทำเป็นโมเดล 3D"],
    "L10": ["และทั้งคลิปนี้", "ส้มใช้ AI ตัด", "ไม่ถึง 10 นาทีค่ะ"],
    "L11": ["พิมพ์ \"ตัดคลิป\" มาค่ะ", "เดี๋ยวส้มส่ง", "Skill ที่ใช้ให้"],
}
PIECE = {}
for p in plan["pieces"]:
    key = p["note"].split()[0]
    PIECE[key] = p
PH = {}          # key -> [(text, s, e)]
words_out = []
for key, phrases in LINES.items():
    p = PIECE[key]
    toks = [w for w in TOK if p["a"] - 0.05 <= w["a"] < p["b"] and w["b"] > p["a"]]
    toks = [w for w in toks if w["w"].strip()]
    cum, c = [], 0
    for w in toks:
        n = len(w["w"].replace(" ", ""))
        cum.append((c, c + n, max(w["a"], p["a"]), min(w["b"], p["b"])))
        c += n
    total = c or 1

    def at(frac):
        x = frac * total
        for c0, c1, a, b in cum:
            if x <= c1:
                return a + (b - a) * ((x - c0) / max(1, c1 - c0))
        return cum[-1][3]
    lens = [len(t.replace(" ", "")) for t in phrases]
    L = sum(lens)
    out, acc = [], 0
    for t, n in zip(phrases, lens):
        s, e = at(acc / L), at((acc + n) / L)
        acc += n
        out.append((t, r3(p["edit"] + s - p["a"]), r3(p["edit"] + e - p["a"])))
        words_out.append({"word": t, "start": out[-1][1], "end": out[-1][2]})
    PH[key] = out
json.dump(words_out, open(os.path.join(P, "build/words.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)

E = lambda k: r3(PIECE[k]["edit"])                                  # piece start (edit s)
END = lambda k: r3(PIECE[k]["edit"] + PIECE[k]["b"] - PIECE[k]["a"])  # piece end (edit s)
S = lambda k, i=0: PH[k][i][1]                                       # phrase start
SE = lambda k, i=-1: PH[k][i][2]                                     # phrase end


class Cut(Reel):
    music_at = 0.0

    def _music(self, **kw):
        """the bed starts on "เพิ่มเพลง" (L5), not at 0: shift the ducked lane"""
        tag = super()._music(**kw)
        m = re.search(r"data-automation='([^']+)'", tag)
        lane = json.loads(m.group(1)); a = self.music_at
        pts = [p for p in lane["lanes"][0]["points"] if p["t"] >= a + 0.8]
        full = max(p["v"] for p in lane["lanes"][0]["points"])
        lane["lanes"][0]["points"] = [{"t": 0, "v": 0}, {"t": 0.5, "v": round(full * 0.35, 3)}, {"t": 0.9, "v": full}] +             [{"t": round(p["t"] - a, 3), "v": p["v"]} for p in pts]
        tag = tag.replace(m.group(1), json.dumps(lane))
        tag = tag.replace('data-start="0"', f'data-start="{a:.3f}"').replace(f'data-duration="{self.T:.3f}"', f'data-duration="{self.T - a:.3f}"')
        return tag


R = Cut(P, plate="assets/plate.mp4", voice="assets/voice.wav", words="build/words.json", tail=0.5, music=None)

def emoji(eid, name, a, dur, x, y, size=200, snd="pop-3"):
    """a Fluent animated emoji (WebM alpha) that pops in at a"""
    add(f'<div id="{eid}" class="emo" style="left:{x}px;top:{y}px;width:{size}px;height:{size}px">'
        f'<video src="assets/emoji/{name}.webm" data-start="{a:.3f}" data-duration="{dur:.3f}" data-track-index="{60 + len(EMO)}" muted playsinline></video></div>')
    EMO.append(eid)
    R.ft(f"#{eid}", {"scale": 0, "rotation": -25, "opacity": 0}, {"scale": 1, "rotation": 0, "opacity": 1, "duration": 0.32, "ease": "back.out(3)"}, a)
    R.tween(f"#{eid}", {"scale": 1, "opacity": 1}, {"scale": 0, "opacity": 0, "duration": 0.18, "ease": "power2.in"}, a + dur - 0.18)
    if snd:
        R.sound(snd, a, f"emoji {name}", db=-3)
EMO = []
T = R.T
print("total", T, {k: (E(k), END(k)) for k in PIECE})
FB = R.face_box()           # [l, t, r, b] of the face core over the reel
print("face box", FB)

body, css = [], []
add = body.append

# ---------------------------------------------------------------- base: the plate
plate = R.held_plate()
add(f'<div id="cam"><video id="vplate" src="{plate}" data-start="0" data-duration="{T}" data-track-index="0" muted playsinline></video></div>')
add('<div id="shade"></div>')
css.append("""
@font-face { font-family: "TH"; font-weight: 700; src: url(assets/fonts/LeelaUIb.ttf); }
@font-face { font-family: "TH"; font-weight: 400; src: url(assets/fonts/LeelawUI.ttf); }
* { box-sizing: border-box; }
#root { font-family: "TH", sans-serif; color: #fff; }
#cam { position: absolute; inset: 0; transform-origin: 50% 40%; }
#cam video { position: absolute; inset: 0; width: 1080px; height: 1920px; object-fit: cover; }
#shade { position: absolute; inset: 0; background: radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0) 40%, rgba(0,0,0,.55) 100%); opacity: 0; }
.abs { position: absolute; }
.emo { position: absolute; z-index: 60; } .emo video { width: 100%; height: 100%; }
""")

# ================================================================ 1. "Claude AI" title (motion, grand entrance)
t0 = 0.0
tA = SE("L1", 0) + 0.15          # title holds while "Claude AI" is said
add('<div id="ttl" class="abs"><div id="ttlglow"></div>'
    '<div id="ttlrow">' + "".join(f'<span class="ch">{c if c != " " else "&nbsp;"}</span>' for c in "Claude AI") + '</div>'
    '<div id="ttlline"></div><div id="ttlsub">AI VIDEO EDITOR</div></div>'
    '<div id="flash" class="abs"></div>')
css.append("""
#ttl { left: 0; top: 0; width: 1080px; height: 1920px; display: flex; flex-direction: column; align-items: center; justify-content: center;
       background: radial-gradient(circle at 50% 46%, rgba(217,119,87,.35), rgba(10,8,8,.82) 60%); opacity: 0; }
#ttlglow { position: absolute; left: 140px; top: 760px; width: 800px; height: 300px; border-radius: 50%;
           background: radial-gradient(closest-side, rgba(255,170,120,.55), rgba(255,170,120,0)); filter: blur(30px); }
#ttlrow { position: relative; font-family: "Inter Tight", "TH", sans-serif; font-weight: 800; font-size: 190px; letter-spacing: -6px;
          line-height: 1; white-space: nowrap; text-shadow: 0 0 40px rgba(255,160,110,.55), 0 8px 30px rgba(0,0,0,.5); }
#ttlrow .ch { display: inline-block; }
#ttlline { width: 620px; height: 6px; margin-top: 34px; border-radius: 3px; background: linear-gradient(90deg, #D97757, #FFD3B5, #D97757); }
#ttlsub { margin-top: 26px; font-family: "Inter Tight", sans-serif; font-weight: 600; font-size: 40px; letter-spacing: 18px; color: #FFD9C4; opacity: 0; }
#flash { inset: 0; background: #fff; opacity: 0; }
""")
R.st("#ttl", {"opacity": 1}, 0)
R.ft("#ttlrow .ch", {"y": 220, "opacity": 0, "rotationX": -90, "filter": "blur(18px)"},
     {"y": 0, "opacity": 1, "rotationX": 0, "filter": "blur(0px)", "duration": 0.5, "stagger": 0.035, "ease": "back.out(2)"}, 0.02)
R.ft("#ttlrow", {"scale": 1.25}, {"scale": 1.0, "duration": 1.1, "ease": "power3.out"}, 0.0)
R.ft("#ttlline", {"scaleX": 0}, {"scaleX": 1, "duration": 0.45, "ease": "power3.inOut"}, 0.4)
R.ft("#ttlsub", {"opacity": 0, "y": 24}, {"opacity": 1, "y": 0, "duration": 0.4, "ease": "power2.out"}, 0.5)
R.ft("#ttlglow", {"scale": 0.3, "opacity": 0}, {"scale": 1.2, "opacity": 1, "duration": 0.8, "ease": "power2.out"}, 0.05)
R.tween("#ttl", {"opacity": 1, "scale": 1}, {"opacity": 0, "scale": 1.12, "filter": "blur(10px)", "duration": 0.25, "ease": "power2.in"}, tA)
R.ft("#flash", {"opacity": 0}, {"opacity": 0.85, "duration": 0.05}, tA + 0.18)
R.tween("#flash", {"opacity": 0.85}, {"opacity": 0, "duration": 0.3}, tA + 0.23)
R.full_screen("title", 0.0, tA + 0.25, "Claude AI title", cap=2.5)
R.sound("whoosh-cine", 0.0, "title in")
R.sound("glitch-hit", 0.42, "title lands")
R.ft("#ttlrow", {"x": 0}, {"x": 14, "duration": 0.035, "yoyo": True, "repeat": 5, "ease": "none"}, 0.45)
R.beat("title", "title", 0.0, tA + 0.25, "Claude AI")

# ================================================================ 2. "ตัดคลิปจากไฟล์ดิบ": raw files fly in (made from ต้นฉบับ.MP4)
fA, fB = S("L1", 1) - 0.05, S("L1", 2) + 0.1
names = ["IMG_0412.MP4", "IMG_0413.MP4", "IMG_0415.MP4", "IMG_0418.MP4", "IMG_0421.MP4", "IMG_0422.MP4",
         "IMG_0426.MP4", "IMG_0430.MP4", "IMG_0431.MP4", "IMG_0437.MP4", "IMG_0440.MP4", "IMG_0444.MP4"]
cards = []
for i in range(12):
    col, row = i % 4, i // 4
    x, y = 48 + col * 252, 560 + row * 330
    cards.append(f'<div class="fc" id="fc{i}" style="left:{x}px;top:{y}px"><img src="assets/files/clip{i + 1}.jpg">'
                 f'<div class="fdur">0{(i * 7) % 5}:{(17 + i * 13) % 60:02d}</div><div class="fn">{names[i]}</div></div>')
add('<div id="files" class="abs"><div id="fhead"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span>'
    '<span id="fpath">D:\\ AI ตัดคลิป \\ ไฟล์ดิบ</span><span id="fcount">12 คลิป · 27 GB</span></div>' + "".join(cards) +
    '<div id="fword">ไฟล์ดิบ</div></div>')
css.append("""
#files { inset: 0; background: rgba(12,12,16,.9); opacity: 0; }
#fhead { position: absolute; left: 40px; right: 40px; top: 400px; height: 110px; border-radius: 26px; background: rgba(255,255,255,.08);
         display: flex; align-items: center; padding: 0 30px; gap: 14px; font-size: 34px; font-weight: 700; }
#fhead .dot { width: 22px; height: 22px; border-radius: 50%; display: inline-block; }
.dot.r { background: #FF5F57 } .dot.y { background: #FEBC2E } .dot.g { background: #28C840 }
#fpath { margin-left: 18px; color: #fff; } #fcount { margin-left: auto; color: #9aa0a6; font-weight: 400; font-size: 30px; }
.fc { position: absolute; width: 232px; height: 312px; border-radius: 18px; overflow: hidden; background: #222;
      box-shadow: 0 14px 30px rgba(0,0,0,.5); border: 2px solid rgba(255,255,255,.12); }
.fc img { width: 100%; height: 250px; object-fit: cover; display: block; }
.fc .fn { height: 62px; line-height: 62px; text-align: center; font-family: "Inter Tight", sans-serif; font-weight: 600; font-size: 24px; color: #ddd; background: #1c1c22; }
.fc .fdur { position: absolute; right: 8px; top: 206px; padding: 2px 10px; border-radius: 8px; background: rgba(0,0,0,.65); font-family: "Inter Tight", sans-serif; font-size: 22px; }
#fword { position: absolute; left: 0; right: 0; top: 1600px; text-align: center; font-size: 110px; font-weight: 700; color: #FFD3B5;
         text-shadow: 0 6px 30px rgba(0,0,0,.6); opacity: 0; }
""")
R.ft("#files", {"opacity": 0}, {"opacity": 1, "duration": 0.18}, fA)
R.ft("#fhead", {"y": -80, "opacity": 0}, {"y": 0, "opacity": 1, "duration": 0.3, "ease": "power3.out"}, fA)
order = [5, 2, 9, 0, 7, 11, 4, 1, 10, 6, 3, 8]
for k, i in enumerate(order):
    R.ft(f"#fc{i}", {"y": 260, "x": (i % 4 - 1.5) * 60, "scale": 0.4, "rotation": (k % 3 - 1) * 14, "opacity": 0},
         {"y": 0, "x": 0, "scale": 1, "rotation": 0, "opacity": 1, "duration": 0.38, "ease": "back.out(1.6)"}, fA + 0.04 + k * 0.045)
R.ft("#fword", {"scale": 1.6, "opacity": 0}, {"scale": 1, "opacity": 1, "duration": 0.3, "ease": "back.out(2)"}, fA + 0.35)
R.tween("#files", {"opacity": 1, "scale": 1}, {"opacity": 0, "scale": 0.92, "duration": 0.2, "ease": "power2.in"}, fB - 0.2)
R.full_screen("files", fA, fB, "raw files grid", cap=2.5)
R.sound("tech-digital-whoosh", fA, "files fly in")
R.beat("files", "scene", fA, fB, "ไฟล์ดิบ grid")

# ================================================================ 3. "ได้ดีขนาดไหน? มาดูกัน": zoom into the speaker as she starts
zA = fB
fy = (FB[1] + FB[3]) / 2
R.ft("#cam", {"scale": 1.0, "transformOrigin": f"50% {fy / H * 100:.1f}%"}, {"scale": 1.22, "duration": 0.55, "ease": "power3.out"}, zA)
R.ft("#shade", {"opacity": 0}, {"opacity": 1, "duration": 0.4}, zA)
R.tween("#cam", {"scale": 1.22}, {"scale": 1.0, "duration": 0.35, "ease": "power2.inOut"}, END("L1") - 0.3)
R.tween("#shade", {"opacity": 1}, {"opacity": 0, "duration": 0.3}, END("L1") - 0.3)
add('<div id="q" class="abs"><span id="q1">ได้ดีขนาดไหน?</span><span id="q2">มาดูกัน</span></div>')
css.append("""
#q { left: 0; right: 0; top: 1360px; text-align: center; }
#q span { display: inline-block; padding: 10px 34px; border-radius: 22px; font-size: 76px; font-weight: 700; margin: 0 8px; }
#q1 { background: #fff; color: #111; } #q2 { background: #D97757; color: #fff; }
""")
R.ft("#q1", {"y": 40, "opacity": 0, "filter": "blur(8px)"}, {"y": 0, "opacity": 1, "filter": "blur(0px)", "duration": 0.22}, S("L1", 2))
R.ft("#q2", {"scale": 0.3, "opacity": 0}, {"scale": 1, "opacity": 1, "duration": 0.3, "ease": "back.out(2.4)"}, S("L1", 3))
R.tween("#q", {"opacity": 1}, {"opacity": 0, "duration": 0.15}, END("L1") - 0.12)
R.sound("whoosh-1", zA, "zoom in", db=-4)
R.beat("zoom", "zoom", zA, END("L1"), "zoom on face")
R.guard("q", [60, 1360, 960, 110], S("L1", 2), END("L1"))

# ================================================================ 4. "ตัดเดดแอร์": editor scene, fast cut + timeline (~3 s)
eA = S("L4", 2) - 0.05
eB = E("L5") + 0.05
# the real audio of the first 60 s of the raw file + its real speech islands (what was kept)
wv = wave.open(os.path.join(CUT, "build/a16.wav"))
sr = wv.getframerate(); n60 = sr * 60
data = array.array("h", wv.readframes(n60)); wv.close()
NB = 240; step = len(data) // NB
env = []
for i in range(NB):
    seg = data[i * step:(i + 1) * step:8]
    env.append(math.sqrt(sum(v * v for v in seg) / max(1, len(seg))))
mx = max(env) or 1
TLW = 960
pts = " ".join(f"{i * TLW / NB:.1f},{60 - 56 * min(1, (e / mx) ** 0.6):.1f}" for i, e in enumerate(env))
pts2 = " ".join(f"{i * TLW / NB:.1f},{60 + 56 * min(1, (e / mx) ** 0.6):.1f}" for i, e in reversed(list(enumerate(env))))
vad = json.load(open(os.path.join(CUT, "build/vad.json")))["islands"]
keep = [(x["a"], x["b"]) for x in vad if x["a"] < 60]
gaps, prev = [], 0.0
for a, b in keep:
    if a - prev > 0.5:
        gaps.append((prev, a))
    prev = b
if 60 - prev > 0.5:
    gaps.append((prev, 60.0))
gap_html = "".join(f'<div class="dead" id="dg{i}" style="left:{a / 60 * TLW:.1f}px;width:{(b - a) / 60 * TLW:.1f}px"></div>' for i, (a, b) in enumerate(gaps))
clip_html = "".join(f'<div class="vclip" style="left:{a / 60 * TLW:.1f}px;width:{max(4, (b - a) / 60 * TLW):.1f}px"></div>' for a, b in keep)
add(f'''<div id="ed" class="abs">
 <div id="edtop"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><b>ตัดเดดแอร์</b><span id="edst">กำลังตัด…</span></div>
 <div id="edprev"><video id="vfast" src="assets/fast_raw.mp4" data-start="{eA:.3f}" data-duration="{eB - eA:.3f}" data-track-index="2" muted playsinline></video>
   <div id="edspeed">×20</div></div>
 <div id="tl"><div class="tlab">V1</div><div class="tlab a">A1</div>
   <div id="tlv">{clip_html}</div>
   <div id="tla"><svg width="{TLW}" height="120" viewBox="0 0 {TLW} 120"><polygon points="{pts} {pts2}" fill="#5AC8FA" opacity=".85"/></svg>{gap_html}</div>
   <div id="ph"></div>
   <div id="ruler">{"".join(f'<span style="left:{k * TLW / 6:.0f}px">0:{k * 10:02d}</span>' for k in range(6))}</div>
 </div>
 <div id="edcount"><b id="edn">0</b> ช่วงเงียบ ถูกตัดออก</div>
</div>''')
css.append(f"""
#ed {{ inset: 0; background: #121216; opacity: 0; }}
#edtop {{ position: absolute; left: 40px; right: 40px; top: 250px; height: 96px; display: flex; align-items: center; gap: 14px; padding: 0 28px;
          border-radius: 22px; background: #1e1e24; font-size: 38px; }}
#edtop b {{ margin-left: 16px; }} #edst {{ margin-left: auto; color: #FF6B6B; font-size: 30px; }}
#edprev {{ position: absolute; left: 324px; top: 380px; width: 432px; height: 768px; border-radius: 24px; overflow: hidden; border: 3px solid #2c2c34; }}
#edprev video {{ width: 100%; height: 100%; object-fit: cover; }}
#edspeed {{ position: absolute; right: 14px; top: 14px; padding: 4px 16px; border-radius: 12px; background: #D97757; font-family: "Inter Tight"; font-weight: 800; font-size: 34px; }}
#tl {{ position: absolute; left: 20px; right: 20px; top: 1190px; height: 330px; border-radius: 22px; background: #1b1b21; }}
.tlab {{ position: absolute; left: 14px; top: 64px; width: 56px; font-family: "Inter Tight"; font-size: 26px; color: #888; }}
.tlab.a {{ top: 190px; }}
#tlv, #tla {{ position: absolute; left: 70px; width: {TLW}px; }}
#tlv {{ top: 46px; height: 70px; }} #tla {{ top: 140px; height: 120px; }}
.vclip {{ position: absolute; top: 0; height: 70px; border-radius: 6px; background: linear-gradient(#7B61FF, #5B45E0); border: 1px solid #9d8bff; }}
.dead {{ position: absolute; top: -96px; height: 216px; background: rgba(255,59,48,.35); border-left: 2px solid #FF3B30; border-right: 2px solid #FF3B30; transform-origin: 50% 50%; }}
#ph {{ position: absolute; left: 70px; top: 30px; width: 4px; height: 250px; background: #fff; box-shadow: 0 0 12px #fff; }}
#ruler {{ position: absolute; left: 70px; top: 280px; width: {TLW}px; height: 40px; font-family: "Inter Tight"; font-size: 22px; color: #777; }}
#ruler span {{ position: absolute; top: 6px; }}
#edcount {{ position: absolute; left: 0; right: 0; top: 1560px; text-align: center; font-size: 54px; font-weight: 700; }}
#edcount b {{ color: #FF6B6B; font-family: "Inter Tight"; font-size: 70px; }}
""")
R.ft("#ed", {"opacity": 0, "scale": 1.06}, {"opacity": 1, "scale": 1, "duration": 0.22, "ease": "power2.out"}, eA)
R.ft("#tl", {"y": 200, "opacity": 0}, {"y": 0, "opacity": 1, "duration": 0.3, "ease": "power3.out"}, eA + 0.05)
R.ft("#ph", {"x": 0}, {"x": TLW, "duration": eB - eA - 0.35, "ease": "none"}, eA + 0.15)
span = eB - eA - 0.5
for i, (a, b) in enumerate(gaps):
    tt = eA + 0.15 + (a + b) / 2 / 60 * (eB - eA - 0.35)
    R.ft(f"#dg{i}", {"scaleX": 1, "opacity": 1}, {"scaleX": 0, "opacity": 0, "duration": 0.16, "ease": "power2.in"}, tt)
    R.tween("#ph", {"backgroundColor": "#FF3B30", "scaleX": 3}, {"backgroundColor": "#ffffff", "scaleX": 1, "duration": 0.14}, tt)
    R.tween("#tlv", {"x": 0}, {"x": -4, "duration": 0.04, "yoyo": True, "repeat": 1}, tt)
    R.sound("click-1" if i % 2 == 0 else "tick-1", tt, "blade cut", db=-2, gap=0.06)
R.js(f'(() => {{ const el = document.getElementById("edn"); const o = {{v: 0}}; tl.fromTo(o, {{v: 0}}, {{v: {len(gaps)}, duration: {eB - eA - 0.4:.2f}, ease: "none", immediateRender: false, onUpdate: () => {{ el.textContent = Math.round(o.v); }} }}, {eA + 0.15:.3f}); }})();')
R.st("#edst", {"textContent": "เสร็จแล้ว ✓", "color": "#34C759"}, eB - 0.35)
R.tween("#ed", {"opacity": 1}, {"opacity": 0, "duration": 0.16}, eB - 0.16)
R.full_screen("editor", eA, eB, "dead-air cut + timeline", cap=3.2)
R.sound("tech-digital-whoosh", eA, "editor in", db=-3)
R.sound("tech-keyboard-burst", eA + 0.12, "editing keys", db=-6, gap=0.05)
R.sound("cartoon-zip", eB - 0.38, "cut finished", db=-4, gap=0.05)
R.beat("editor", "scene", eA, eB, "timeline dead-air cut")

for k, a, b, sc in (("L4", S("L4", 1), eA, 1.16), ("L6", S("L6", 0), END("L6"), 1.13)):
    R.tween("#cam", {"scale": 1.0}, {"scale": sc, "duration": 0.07, "ease": "power4.out"}, a)
    R.tween("#cam", {"scale": sc}, {"scale": 1.0, "duration": 0.06, "ease": "none"}, b - 0.06)
    R.sound("whoosh-cine", a - 0.04, f"punch-in {k}", db=-6)

# ================================================================ 5. "เพิ่มเพลงฟังสบายๆหน่อย": volume slider pushed up; the bed fades in
vA, vB = S("L5", 0), END("L5") + 0.1
add('<div id="vol" class="abs"><div id="vtrack"><div id="vfill"></div><div id="vknob"></div></div>'
    '<div id="vico">♪</div><div id="vlab">MUSIC</div></div>')
css.append("""
#vol { left: 880px; top: 330px; width: 150px; height: 700px; border-radius: 40px; background: rgba(28,28,32,.72); backdrop-filter: blur(14px);
       box-shadow: 0 10px 40px rgba(0,0,0,.4); }
#vtrack { position: absolute; left: 45px; top: 40px; width: 60px; height: 520px; border-radius: 30px; background: rgba(255,255,255,.18); overflow: hidden; }
#vfill { position: absolute; left: 0; bottom: 0; width: 100%; height: 520px; background: linear-gradient(#FFD3B5, #D97757); transform-origin: 50% 100%; }
#vknob { position: absolute; left: 0; width: 60px; height: 8px; background: #fff; bottom: 0; }
#vico { position: absolute; left: 0; right: 0; top: 580px; text-align: center; font-size: 56px; }
#vlab { position: absolute; left: 0; right: 0; top: 646px; text-align: center; font-family: "Inter Tight"; font-size: 26px; color: #ddd; }
""")
R.ft("#vol", {"x": 220, "opacity": 0}, {"x": 0, "opacity": 1, "duration": 0.3, "ease": "back.out(1.4)"}, vA)
R.ft("#vfill", {"scaleY": 0.05}, {"scaleY": 0.85, "duration": 0.9, "ease": "power2.inOut"}, vA + 0.35)
R.ft("#vknob", {"y": -26}, {"y": -442, "duration": 0.9, "ease": "power2.inOut"}, vA + 0.35)
R.tween("#vol", {"x": 0, "opacity": 1}, {"x": 220, "opacity": 0, "duration": 0.25, "ease": "power2.in"}, vB)
R.guard("vol", [880, 330, 150, 700], vA, vB + 0.25)
R.beat("music", "chip", vA, vB, "volume up")
MUSIC_AT = vA + 0.35
emoji("e_party", "party", vA + 0.3, vB - vA, 690, 250, 190)

# ================================================================ captions: they switch on at "เพิ่มซับไตเติ้ล" (L6) and run to L10
add('<div id="caps" class="abs"></div>')
css.append("""
#caps { left: 0; right: 0; top: 0; height: 1920px; pointer-events: none; }
.cap { position: absolute; left: 50%; transform: translateX(-50%); white-space: nowrap; padding: 8px 30px 14px; border-radius: 20px;
       font-size: 66px; font-weight: 700; color: #111; background: #fff; box-shadow: 0 8px 26px rgba(0,0,0,.35); opacity: 0; }
.cap.hl { background: #D97757; color: #fff; }
#subon { position: absolute; left: 50%; top: 1250px; transform: translateX(-50%); padding: 6px 22px; border-radius: 14px; background: #FFD60A; color: #111;
         font-family: "Inter Tight", "TH"; font-weight: 800; font-size: 34px; letter-spacing: 3px; opacity: 0; }
""")
CAP_KEYS = ["L6", "L7", "L8", "L9", "L10"]
HL = {("L6", 0), ("L8", 1), ("L9", 0), ("L10", 2)}
split_from = r3(E("L8") + 201.70 - PIECE["L8"]["a"])   # her hand at the top of the pull-down (raw 201.70 s)
split_to = None
SEAM = 830
caps = []
for key in CAP_KEYS:
    ph = PH[key]
    for i, (txt, s, e) in enumerate(ph):
        nxt = ph[i + 1][1] if i + 1 < len(ph) else END(key) - 0.05
        top = (SEAM - 44) if s >= split_from - 0.05 else 1380
        cid = f"cap_{key}_{i}"
        cls = "cap hl" if (key, i) in HL else "cap"
        caps.append(f'<div class="{cls}" id="{cid}" style="top:{top}px">{esc(txt)}</div>')
        R.ft(f"#{cid}", {"opacity": 0, "y": 40, "scale": 0.45, "rotation": -5 if i % 2 else 5},
             {"opacity": 1, "y": 0, "scale": 1, "rotation": 0, "duration": 0.24, "ease": "back.out(3.2)"}, s - 0.05)
        R.tween(f"#{cid}", {"opacity": 1}, {"opacity": 0, "duration": 0.1}, max(s + 0.3, nxt - 0.08))
body.append('<div id="capwrap" style="position:absolute;inset:0;z-index:40">' + "".join(caps) + '</div><div id="subon">SUBTITLE ON</div>')
R.ft("#subon", {"opacity": 0, "scale": 0.5}, {"opacity": 1, "scale": 1, "duration": 0.25, "ease": "back.out(2.5)"}, S("L6") + 0.05)
R.tween("#subon", {"opacity": 1}, {"opacity": 0, "duration": 0.2}, END("L6") - 0.1)
R.sound("pop-3", S("L6"), "subtitles switch on")
R.beat("subs", "captions", S("L6"), END("L10"), "captions on")

# ================================================================ 7. "เพิ่มวีดีโอต้นฉบับเป็นจอเล็กๆ": PiP top-left
pA, pB = S("L7", 1) - 0.15, T
RAW0 = 127.3
add(f'<div id="pip" class="abs"><video id="vpip" src="assets/pip_raw.mp4" data-start="{pA:.3f}" data-duration="{pB - pA + 0.2:.3f}" data-track-index="3" muted playsinline></video>'
    '<div id="piplab">ต้นฉบับ</div><div id="piptc">02:07</div></div>')
css.append("""
#pip { left: 26px; top: 900px; width: 240px; height: 427px; z-index: 30; border-radius: 26px; overflow: hidden; border: 4px solid #fff;
       box-shadow: 0 14px 40px rgba(0,0,0,.5); transform-origin: 0 0; }
#pip video { width: 100%; height: 100%; object-fit: cover; }
#piptc { position: absolute; left: 0; right: 0; bottom: 0; padding: 4px 0; text-align: center; background: rgba(0,0,0,.6); font-family: "Inter Tight"; font-size: 24px; }
#piplab { position: absolute; left: 12px; top: 12px; padding: 2px 14px; border-radius: 10px; background: #FF3B30; font-size: 26px; font-weight: 700; }
""")
R.ft("#pip", {"scale": 0, "opacity": 0, "rotation": -8}, {"scale": 1, "opacity": 1, "rotation": 0, "duration": 0.35, "ease": "back.out(1.7)"}, pA)
R.js(f'(() => {{ const el = document.getElementById("piptc"); const o = {{v: 0}}; tl.fromTo(o, {{v: {RAW0}}}, {{v: {RAW0 + T - pA:.2f}, duration: {T - pA:.3f}, ease: "none", immediateRender: false, onUpdate: () => {{ const s = Math.floor(o.v); el.textContent = "RAW " + String(Math.floor(s / 60)).padStart(2, "0") + ":" + String(s % 60).padStart(2, "0"); }} }}, {pA:.3f}); }})();')
R.sound("shutter-1", pA, "pip in", db=-4)
R.guard("pip", [26, 900, 240, 427], pA, pB)
R.insert("pip", "assets/pip_raw.mp4", pA, pB, "วีดีโอต้นฉบับเป็นจอเล็กๆ", "pip", "own")
R.beat("pip", "insert", pA, pB, "PiP original")

# ================================================================ 8-10. split screen: house image -> 3D orbit -> workflow timeline
D3 = S("L9") + 0.15                      # the 3D model on "ทำเป็นโมเดล 3D"
WF = E("L10")                            # workflow replaces the picture on "ทั้งหมดนี้"
steps = ["ถอดเสียง", "เลือกเทค", "ตัดเดดแอร์", "ใส่เพลง", "ซับไตเติ้ล", "จอเล็ก", "แบ่งจอ", "โมเดล 3D", "เรนเดอร์"]
pieces_html = []
x = 0
tot = sum(p["b"] - p["a"] for p in plan["pieces"])
for p in plan["pieces"]:
    w = (p["b"] - p["a"]) / tot * 900
    pieces_html.append(f'<div class="wpc" style="left:{x:.1f}px;width:{w - 3:.1f}px"></div>')
    x += w
add(f'''<div id="split" class="abs">
 <div id="pimg"><img src="assets/house.png"></div>
 <div id="p3d"><video id="v3d" src="assets/house_orbit.mp4" data-start="{D3:.3f}" data-duration="{WF - D3 + 0.1:.3f}" data-track-index="4" muted playsinline></video>
   <div id="scan"></div><div id="hud"><span>3D MODEL</span><i>DEPTH · 2.5D ORBIT</i></div>
   <div class="corner c1"></div><div class="corner c2"></div><div class="corner c3"></div><div class="corner c4"></div></div>
 <div id="pwf"><div id="wfh">WORKFLOW<span>&lt; 10 นาที</span></div>
   <div id="wfs">{"".join(f'<div class="wst" id="ws{i}"><b>{i + 1}</b>{s}</div>' for i, s in enumerate(steps))}</div>
   <div id="wtl"><div class="wtr"><em>V1</em><div class="wtrk">{"".join(pieces_html)}</div></div>
     <div class="wtr"><em>T1</em><div class="wtrk"><div class="wsub" style="left:0;width:120px">Claude AI</div><div class="wsub" style="left:300px;width:150px">ไฟล์ดิบ</div><div class="wsub" style="left:560px;width:330px">ซับไตเติ้ล</div></div></div>
     <div class="wtr"><em>A2</em><div class="wtrk"><div class="wmus" style="left:300px;width:600px">♪ lo-fi</div></div></div>
     <div id="wph"></div></div>
 </div>
 <div id="seam"></div>
</div>''')
css.append(f"""
#split {{ left: 0; top: 0; width: 1080px; height: {SEAM}px; overflow: hidden; background: #0d0d10; transform-origin: 50% 0; }}
#pimg, #p3d, #pwf {{ position: absolute; inset: 0; }}
#pimg img {{ width: 100%; height: 100%; object-fit: cover; }}
#p3d video {{ width: 100%; height: 100%; object-fit: cover; }}
#p3d {{ opacity: 0; }} #pwf {{ opacity: 0; background: #131318; }}
#scan {{ position: absolute; left: 0; right: 0; height: 120px; top: -120px; background: linear-gradient(rgba(90,200,250,0), rgba(90,200,250,.55), rgba(90,200,250,0)); mix-blend-mode: screen; }}
#hud {{ position: absolute; left: 40px; top: 250px; padding: 10px 22px; border: 2px solid #5AC8FA; border-radius: 12px; background: rgba(0,20,30,.55);
        font-family: "Inter Tight"; color: #5AC8FA; }}
#hud span {{ display: block; font-weight: 800; font-size: 46px; letter-spacing: 4px; }} #hud i {{ font-style: normal; font-size: 22px; letter-spacing: 3px; color: #bfe9ff; }}
.corner {{ position: absolute; width: 70px; height: 70px; border: 0 solid #5AC8FA; }}
.c1 {{ left: 24px; top: 230px; border-left-width: 5px; border-top-width: 5px; }} .c2 {{ right: 24px; top: 230px; border-right-width: 5px; border-top-width: 5px; }}
.c3 {{ left: 24px; bottom: 24px; border-left-width: 5px; border-bottom-width: 5px; }} .c4 {{ right: 24px; bottom: 24px; border-right-width: 5px; border-bottom-width: 5px; }}
#wfh {{ position: absolute; left: 50px; right: 50px; top: 240px; font-family: "Inter Tight"; font-weight: 800; font-size: 44px; letter-spacing: 6px; color: #aaa; }}
#wfh span {{ float: right; letter-spacing: 0; font-family: "TH"; color: #34C759; font-size: 50px; }}
#wfs {{ position: absolute; left: 40px; right: 40px; top: 320px; display: flex; flex-wrap: wrap; gap: 12px; }}
.wst {{ padding: 8px 20px 10px; border-radius: 16px; background: #24242c; color: #777; font-size: 32px; font-weight: 700; }}
.wst b {{ display: inline-block; width: 40px; height: 40px; margin-right: 10px; border-radius: 50%; background: #333; color: #999; text-align: center;
          line-height: 40px; font-family: "Inter Tight"; font-size: 24px; }}
.wst.on {{ background: #1f3a2a; color: #fff; }} .wst.on b {{ background: #34C759; color: #fff; }}
#wtl {{ position: absolute; left: 40px; right: 40px; top: 560px; height: 220px; }}
.wtr {{ position: relative; height: 62px; margin-bottom: 10px; }}
.wtr em {{ position: absolute; left: 0; top: 16px; font-style: normal; font-family: "Inter Tight"; font-size: 24px; color: #777; }}
.wtrk {{ position: absolute; left: 60px; width: 900px; top: 0; height: 62px; border-radius: 10px; background: #1b1b21; }}
.wpc {{ position: absolute; top: 4px; height: 54px; border-radius: 6px; background: linear-gradient(#7B61FF, #5B45E0); }}
.wsub {{ position: absolute; top: 4px; height: 54px; border-radius: 6px; background: #FFD60A; color: #111; font-size: 24px; font-weight: 700; padding: 10px 10px; overflow: hidden; white-space: nowrap; }}
.wmus {{ position: absolute; top: 4px; height: 54px; border-radius: 6px; background: #2E7D5B; font-size: 26px; padding: 10px 14px; }}
#wph {{ position: absolute; left: 60px; top: -6px; width: 4px; height: 220px; background: #fff; box-shadow: 0 0 10px #fff; }}
#seam {{ position: absolute; left: 0; right: 0; bottom: 0; height: 6px; background: linear-gradient(90deg, #D97757, #FFD3B5, #D97757); }}
""")
# the panel drops in; the speaker moves down (scaled) into the bottom half
R.ft("#split", {"y": -SEAM - 20}, {"y": 0, "duration": 0.42, "ease": "back.out(1.3)"}, split_from + 0.05)
SC, TY = 1.0, 300
R.tween("#cam", {"scale": 1.0, "y": 0}, {"scale": SC, "y": TY, "duration": 0.42, "ease": "power3.out"}, split_from + 0.05)
R.ft("#pimg img", {"scale": 1.0}, {"scale": 1.12, "duration": D3 - split_from, "ease": "none"}, split_from)
R.sound("whoosh-2", split_from, "split opens", db=-3)
# 3D
R.ft("#p3d", {"opacity": 0}, {"opacity": 1, "duration": 0.12}, D3)
R.ft("#scan", {"y": 0}, {"y": SEAM + 240, "duration": 0.8, "ease": "power1.inOut"}, D3)
R.ft("#hud", {"x": -60, "opacity": 0}, {"x": 0, "opacity": 1, "duration": 0.3, "ease": "power3.out"}, D3 + 0.15)
R.ft(".corner", {"scale": 1.6, "opacity": 0}, {"scale": 1, "opacity": 1, "duration": 0.3, "ease": "power3.out"}, D3 + 0.05)
R.sound("tech-glitch-1", D3, "3D model", db=-3)
emoji("e_star", "star-struck", D3 + 0.35, WF - D3 - 0.35, 840, 560, 190, snd=None)
R.beat("model3d", "scene", D3, WF, "house 3D orbit")
# workflow
R.ft("#pwf", {"opacity": 0}, {"opacity": 1, "duration": 0.18}, WF)
nst = len(steps)
for i in range(nst):
    R.st(f"#ws{i}", {"backgroundColor": "#1f3a2a", "color": "#ffffff"}, WF + 0.25 + i * 0.22)
    R.st(f"#ws{i} b", {"backgroundColor": "#34C759", "color": "#ffffff"}, WF + 0.25 + i * 0.22)
R.ft("#wph", {"x": 0}, {"x": 900, "duration": END("L10") - WF - 0.2, "ease": "none"}, WF + 0.1)
R.sound("tech-digital-whoosh", WF, "workflow in", db=-4)
emoji("e_rocket", "rocket", S("L10", 2), END("L10") - S("L10", 2) + 0.1, 830, 900, 200)
R.beat("workflow", "scene", WF, END("L10"), "workflow timeline")
R.beat("split", "split", split_from, T, "split screen to the end")

# ================================================================ 11. CTA: พิมพ์ "ตัดคลิป" มาค่ะ เดี๋ยวส้มส่ง Skill ที่ใช้ให้
cA = S("L11")
add('<div id="cta" class="abs"><div id="cbig">พิมพ์ <span id="ckw">“ตัดคลิป”</span></div>'
    '<div id="cbox"><div id="cav">ส</div><div id="ctxt"><span id="ctyped"></span><span id="ccar">|</span></div><div id="csend">ส่ง</div></div>'
    '<div id="csub">เดี๋ยวส้มส่ง <b>Skill</b> ที่ใช้ให้</div></div>')
css.append("""
#cta { left: 0; right: 0; top: 0; height: 830px; background: radial-gradient(circle at 50% 55%, #3a2219, #0d0d10 75%); opacity: 0; }
#cbig { position: absolute; left: 0; right: 0; top: 270px; text-align: center; font-size: 92px; font-weight: 700; text-shadow: 0 6px 30px rgba(0,0,0,.6); }
#ckw { display: inline-block; padding: 0 22px 6px; border-radius: 22px; background: #D97757; }
#cbox { position: absolute; left: 90px; right: 90px; top: 440px; height: 100px; border-radius: 50px; background: rgba(255,255,255,.95); display: flex; align-items: center; padding: 0 16px; gap: 18px; color: #111; }
#cav { width: 70px; height: 70px; border-radius: 50%; background: #D97757; color: #fff; text-align: center; line-height: 70px; font-size: 36px; font-weight: 700; }
#ctxt { flex: 1; font-size: 44px; font-weight: 700; } #ccar { color: #D97757; }
#csend { padding: 6px 26px; border-radius: 30px; background: #0A84FF; color: #fff; font-size: 34px; font-weight: 700; }
#csub { position: absolute; left: 0; right: 0; top: 600px; text-align: center; font-size: 60px; font-weight: 700; text-shadow: 0 4px 20px rgba(0,0,0,.7); }
#csub b { color: #FFD3B5; font-family: "Inter Tight", "TH"; }
""")
R.ft("#cta", {"y": -40, "opacity": 0}, {"y": 0, "opacity": 1, "duration": 0.25, "ease": "power2.out"}, cA - 0.05)
R.ft("#cbig", {"scale": 0.4, "opacity": 0, "y": 40}, {"scale": 1, "opacity": 1, "y": 0, "duration": 0.35, "ease": "back.out(2.2)"}, cA)
R.ft("#ckw", {"backgroundColor": "rgba(217,119,87,0)"}, {"backgroundColor": "rgba(217,119,87,1)", "duration": 0.25}, cA + 0.3)
R.ft("#cbox", {"y": 60, "opacity": 0}, {"y": 0, "opacity": 1, "duration": 0.3, "ease": "power3.out"}, cA + 0.25)
word = "ตัดคลิป"
for i in range(1, len(word) + 1):
    R.st("#ctyped", {"textContent": word[:i]}, cA + 0.45 + i * 0.09)
tsend = cA + 0.45 + len(word) * 0.09 + 0.25
R.ft("#csend", {"scale": 1}, {"scale": 0.85, "duration": 0.08, "yoyo": True, "repeat": 1}, tsend)
R.st("#ccar", {"opacity": 0}, tsend)
R.ft("#csub", {"opacity": 0, "y": 30}, {"opacity": 1, "y": 0, "duration": 0.3, "ease": "power2.out"}, S("L11", 1))
R.sound("pop-1", cA, "CTA")
R.sound("tech-notification-2", tsend, "sent", db=-4)
R.beat("cta", "cta", cA, T, "comment ตัดคลิป")

# ---------------------------------------------------------------- page + numbers
R.write_page("\n".join(css), "\n".join(body) + "\n" + "\n".join(R._audio()), ["Inter Tight"], lang="th")
R.finish("claude-cut", extra={"music_at": MUSIC_AT})
json.dump({"music_at": MUSIC_AT, "total": T}, open(os.path.join(P, "build/post.json"), "w"))
