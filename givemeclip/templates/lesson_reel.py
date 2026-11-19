# -*- coding: utf-8 -*-
"""GivemeClip pipeline C template (= the บทที่ 3 generator, 2026-11-19): lesson / screen recording -> HyperFrames index.html.
All times below are RAW source seconds; M() maps them through build/edl.json to the edit. Run: PYTHONUTF8=1 python reel.py
REWRITE per job (keep the helpers, layers and the audio/page block):
  SCREEN_RAW   raw second the screen part starts (flash + PiP + mask switch on there)
  CAP          captions: your own Thai text (never whisper's), raw a/b; <b>keyword</b> = orange
  FACE / CAM   punch-in centre for the talking head; zoom keyframes (raw t, cx, cy, scale, PiP to top-right?)
  CAMBOX       where the webcam overlay sits inside the screen recording (masked, re-drawn as the orange PiP)
  STEPS        the 5-step bar; the numbered scene blocks (opening, recap, cards, freebie, end card) -> this lesson's content
Layout numbers are pixels on the 1920x1080 canvas; W/H follow the source (edl.json), move cards if the source is not 16:9."""
import json, os, sys
sys.stdout.reconfigure(encoding="utf-8")
R = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(R, "..")
edl = json.load(open(os.path.join(P, "build/edl.json")))
PCS, T = edl["pieces"], round(edl["total"], 3)
W, H, FPS = edl.get("width", 1920), edl.get("height", 1080), 30
GSAP = "https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"
SCREEN_RAW = 38.6
CAMBOX = (1500, 845, 420, 235)   # webcam overlay in the recording (x, y, w, h); None = no webcam to mask / re-draw
TASKBAR_Y = 1032                 # Windows taskbar top inside CAMBOX (masked dark); None if none


def M(t):
    """raw seconds -> edit seconds (a time inside a dropped part maps to the next kept piece)"""
    for p in PCS:
        if t < p["a"]:
            return round(p["edit"], 3)
        if p["a"] <= t < p["b"]:
            return round(p["edit"] + (t - p["a"]) / p["speed"], 3)
    return T


SCR = M(SCREEN_RAW)
base, tl, body, css, sounds = [], [], [], [], []
add = body.append
_set = set()


def j(o):
    return json.dumps(o, ensure_ascii=False)


def hide(sel, props=None):
    if sel not in _set:
        _set.add(sel)
        base.append(f'gsap.set("{sel}", {j(props or {"opacity": 0})});')


def ft(sel, frm, to, at):
    hide(sel, frm)
    tl.append(f'tl.fromTo("{sel}", {j(frm)}, {j({**to, "immediateRender": False})}, {at:.3f});')


def to(sel, props, at):
    tl.append(f'tl.to("{sel}", {j(props)}, {at:.3f});')


def tset(sel, props, at):
    tl.append(f'tl.set("{sel}", {j(props)}, {at:.3f});')


def pop_in(sel, at, dur=0.45, y=30, scale=0.9):
    ft(sel, {"opacity": 0, "y": y, "scale": scale}, {"opacity": 1, "y": 0, "scale": 1, "duration": dur, "ease": "back.out(1.8)"}, at)


def out(sel, at, dur=0.3):
    to(sel, {"opacity": 0, "y": -16, "duration": dur, "ease": "power2.in"}, at - dur)


QUIET = {"whoosh-1", "whoosh-2", "pop-2", "pop-3", "click-1", "riser-1", "cc0-tada"}   # user: SFX not too busy


def sfx(name, at, vol=0.35):
    if name in QUIET:
        return
    sounds.append((name, at, round(vol * 0.6, 3)))



# ================================================================ captions (raw a, raw b, text); keywords in <b>
CAP = [
    (0.0, 2.5, "โอเคค่ะทุกคน"),
    (2.5, 5.8, "มาต่อกันที่ EP นี้นะคะ"),
    (5.8, 9.0, "จากบทเรียนที่แล้ว ที่เราได้<b>สร้างโปรเจกต์</b>"),
    (9.0, 16.4, "แล้วก็<b>ตั้งกติกา</b>ในการตัดต่อคลิปไว้เรียบร้อย"),
    (39.6, 43.2, "โอเคค่ะ ก็จะมาต่อที่โฟลเดอร์เดิมเลย"),
    (43.2, 47.9, "ซึ่งตอนนี้ส้มได้เอา<b>คลิปวิดีโอที่ถ่ายไว้</b>"),
    (47.9, 50.7, "ใส่ไว้เรียบร้อยแล้ว"),
    (50.8, 56.3, "เป็นคลิปทำอาหาร <b>สามชั้นผัดกะปิชะอม</b>"),
    (56.3, 62.4, "ซึ่งถ่ายแบบดิบๆ เลย ไม่ได้เซ็ตอะไรเลย"),
    (62.4, 64.7, "ถ่ายทีละขั้นตอน"),
    (64.7, 70.0, "แล้วก็เอามาใส่ในโฟลเดอร์ที่เราสร้างไว้เมื่อกี้"),
    (71.0, 74.5, "แล้วก็จะมี<b>เสียงพากย์</b> ซึ่งส้มพากย์ไว้แล้ว"),
    (74.5, 78.1, "ใส่เข้าไปด้วย มี<b>สคริปต์</b>ขั้นตอนต่างๆ"),
    (78.8, 82.6, "แล้วก็มี <b>Sound Effect</b>"),
    (82.6, 85.8, "ก็เอามาจากใต้คลิปในบทที่ 2"),
    (85.8, 89.9, "โหลดมาแตกไฟล์ให้เรียบร้อย เอามาใส่ในโฟลเดอร์นี้"),
    (89.9, 96.2, "หรือจะเอาไปใส่ในโฟลเดอร์ที่ใช้ตัดคลิปอื่นๆ ก็ได้"),
    (98.5, 101.6, "มาต่อที่แชทเดิมเลยนะคะ"),
    (114.3, 117.1, "ก็จะใส่คำสั่งไปเลยค่ะ"),
    (120.6, 125.1, "ส้มจะใส่คำสั่งไปประมาณว่า"),
    (125.1, 131.3, "ให้ทำงานใน<b>โฟลเดอร์สามชั้นผัด</b> ที่เอาคลิปใส่ไว้"),
    (131.3, 135.3, "ใช้ <b>Skill GivemeClip</b> ตัดต่อให้กระชับ ตัด Dead Air"),
    (135.3, 140.3, "ใส่<b>ตัวหนังสืออธิบาย</b>และ<b>อินโฟกราฟิก</b>ที่ไม่น่าเบื่อ"),
    (140.3, 144.3, "มี<b>เพลงประกอบ</b>ที่ฟังสนุก"),
    (144.3, 146.2, "ใช้ <b>Sound Effect</b> จากในโฟลเดอร์"),
    (146.2, 150.1, "และยังคง<b>เสียงบรรยากาศเดิม</b>ในคลิปฟุตเทจไว้"),
    (150.1, 154.6, "เราใช้คำสั่ง<b>เหมือนสั่งพนักงานหนึ่งคน</b>ได้เลยค่ะ"),
    (157.6, 161.9, "เสร็จแล้วก็กด <b>Enter</b> สั่งงานได้เลย"),
    (177.9, 181.3, "ตอนนี้ค่อยๆ ทำไปทีละขั้นตอน"),
    (181.3, 188.8, "ส่วนคำสั่งที่ใช้ ถ้าใครคิดไม่ออกว่าจะสั่งแบบไหน"),
    (188.8, 193.4, "มีลิงก์ <b>PDF</b> ให้ใต้คลิปนี้"),
    (193.4, 201.3, "เป็น<b>รวมคำสั่ง</b>ที่ใช้สั่งตัดต่อคลิป ไว้หลายๆ คำสั่ง"),
    (201.3, 205.6, "สามารถโหลดออกไปใช้งานกันได้"),
    (228.8, 232.7, "นี่ใช้ไป 1 นาทีกว่าแล้ว"),
    (242.3, 247.1, "ตอนนี้ก็รอเขาตัดต่อคลิป"),
    (247.1, 251.7, "ทำทีละขั้นตอน ใช้เวลาประมาณ 15 นาที"),
    (265.8, 267.4, "แต่ก็น่าจะเร็วอยู่"),
    (469.1, 472.7, "โอเคค่ะ ตอนนี้คลิปของเรา<b>ตัดเสร็จแล้ว</b>"),
    (472.7, 475.6, "เรามากดดูได้เลย"),
    (512.0, 515.0, "คลิปของเราก็เสร็จแล้ว เห็นไหมคะ <b>ง่ายมากๆ</b>"),
    (515.0, 520.2, "ซึ่งถ้าใครอยากจะแก้ตรงจุดไหน"),
    (520.2, 524.2, "อย่างเช่น เสียงเอฟเฟกต์ดังไป"),
    (524.2, 526.3, "เสียงบรรยายเบาไป"),
    (526.3, 529.9, "หรืออยากแก้ช็อตไหน ก็<b>สั่งแก้ได้เลย</b>"),
    (531.9, 535.7, "ประมาณนี้นะคะ สำหรับบทเรียนนี้"),
    (535.7, 539.3, "แล้วไปติดตามกันต่อใน<b>บทเรียนถัดไป</b>ได้เลยค่ะ"),
]
for i, (a, b, txt) in enumerate(CAP):
    s, e = M(a), M(b)
    nxt = M(CAP[i + 1][0]) if i + 1 < len(CAP) else T
    e = min(max(e + 0.15, s + 0.7), nxt - 0.02, T)
    add(f'<div id="cap{i}" class="cap"><span>{txt}</span></div>')
    ft(f"#cap{i}", {"opacity": 0, "y": 14}, {"opacity": 1, "y": 0, "duration": 0.16, "ease": "power2.out"}, s)
    to(f"#cap{i}", {"opacity": 0, "duration": 0.1}, e - 0.1)

# ================================================================ camera (zoom) keyframes, raw time
FACE = (930, 470)
CAM = [  # (raw t, cx, cy, scale, pip_top)
    (SCREEN_RAW, 960, 540, 1.0, False),
    (42.3, 1000, 300, 1.3, False),       # the folder of raw files
    (50.8, 1000, 415, 1.3, False),       # the cooking clips
    (71.0, 520, 300, 1.5, True),         # voice-over, script, SFX folder
    (89.9, 960, 540, 1.0, False),
    (114.3, 945, 950, 1.9, True),        # typing the order
    (157.6, 960, 540, 1.0, False),       # sent
    (161.9, 945, 760, 1.7, True),        # Claude's plan / progress
    (267.45, 945, 760, 1.7, True),
    (469.1, 960, 540, 1.0, False),       # done
    (512.0, 960, 540, 1.0, True),        # wrap-up cards
]
def cam_xy(cx, cy, s):
    x = min(0, max(W - W * s, W / 2 - cx * s))
    y = min(0, max(H - H * s, H / 2 - cy * s))
    return round(x, 1), round(y, 1)


hide("#cam", {"x": 0, "y": 0, "scale": 1, "transformOrigin": "0 0"})
# talking head: punch-in alternates at every jump cut
head = [p for p in PCS if p["head"]]
for k, p in enumerate(head):
    s = 1.0 if k % 2 == 0 else 1.13
    x, y = cam_xy(*FACE, s)
    tset("#cam", {"x": x, "y": y, "scale": s}, p["edit"])
prev = None
for (t, cx, cy, s, top) in CAM:
    at = M(t)
    x, y = cam_xy(cx, cy, s)
    if t == SCREEN_RAW:
        tset("#cam", {"x": x, "y": y, "scale": s}, at)
    else:
        to("#cam", {"x": x, "y": y, "scale": s, "duration": 0.75, "ease": "power3.inOut"}, at - 0.15)
        if prev is not None and abs(s - prev) > 0.3:
            sfx("whoosh-1", at - 0.15, 0.18)
    if CAMBOX:
        to("#pip", {"left": W - CAMBOX[2] - 24 if top else CAMBOX[0], "top": 24 if top else CAMBOX[1], "duration": 0.6, "ease": "power3.inOut"}, at - 0.15)
    prev = s

# ================================================================ base layers
add(f'<div id="cam"><video id="vplate" src="assets/plate.mp4" data-start="0" data-duration="{T}" data-track-index="0" muted playsinline></video>'
    '<div id="maskw"></div><div id="maskt"></div><div id="hl"></div></div>')
add('<div id="shade"></div>')
add(f'<div id="pip"><video src="assets/plate.mp4" data-start="{SCR}" data-duration="{T - SCR:.3f}" data-media-start="{SCR}" '
    f'data-track-index="1" muted playsinline></video></div>')
add('<div id="flash"></div>')
hide("#maskw"); hide("#maskt")
tset("#maskw", {"opacity": 1}, SCR); tset("#maskt", {"opacity": 1}, SCR)
ft("#pip", {"opacity": 0, "scale": 0.8}, {"opacity": 1, "scale": 1, "duration": 0.4, "ease": "back.out(2)"}, SCR + 0.25)
# head -> screen: flash
ft("#flash", {"opacity": 0}, {"opacity": 0.9, "duration": 0.08}, SCR - 0.08)
to("#flash", {"opacity": 0, "duration": 0.35}, SCR)
sfx("tech-digital-whoosh", SCR - 0.3, 0.3)

css.append("""
@font-face { font-family: "K"; font-weight: 500; src: url(assets/fonts/Kanit-Medium.ttf); }
@font-face { font-family: "K"; font-weight: 600; src: url(assets/fonts/Kanit-SemiBold.ttf); }
@font-face { font-family: "K"; font-weight: 700; src: url(assets/fonts/Kanit-Bold.ttf); }
@font-face { font-family: "K"; font-weight: 800; src: url(assets/fonts/Kanit-ExtraBold.ttf); }
@font-face { font-family: "K"; font-weight: 900; src: url(assets/fonts/Kanit-Black.ttf); }
:root { --or: #FF7A1A; --or2: #FF9E3D; --ink: #0E0F14; --card: rgba(14,15,20,.92); --wh: #FFFFFF; --mint: #3EE6B0; }
* { box-sizing: border-box; }
#root { font-family: "K", "Leelawadee UI", "Segoe UI Emoji", sans-serif; color: var(--wh); }
#cam { position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; }
#cam video { position: absolute; inset: 0; width: 1920px; height: 1080px; }
#maskw { position: absolute; left: 1500px; top: 845px; width: 420px; height: 187px; background: #fff; }
#maskt { position: absolute; left: 1500px; top: 1032px; width: 420px; height: 48px; background: #2a2829; }
#hl { position: absolute; left: 566px; top: 551px; width: 520px; height: 40px; border: 4px solid var(--or); border-radius: 10px;
      box-shadow: 0 0 0 9999px rgba(0,0,0,0); opacity: 0; }
#shade { position: absolute; inset: 0; background: rgba(8,9,12,.72); opacity: 0; }
#pip { position: absolute; left: 1500px; top: 845px; width: 420px; height: 235px; overflow: hidden; border-radius: 22px;
       border: 4px solid var(--or); box-shadow: 0 12px 40px rgba(0,0,0,.35); z-index: 40; opacity: 0; }
#pip video { position: absolute; left: -1504px; top: -849px; width: 1920px; height: 1080px; }
#flash { position: absolute; inset: 0; background: #fff; opacity: 0; z-index: 90; }
.cap { position: absolute; left: 0; right: 0; bottom: 46px; text-align: center; z-index: 50; opacity: 0; }
.cap span { display: inline-block; max-width: 1080px; padding: 10px 30px 14px; border-radius: 18px; background: rgba(12,12,16,.84);
            font-weight: 600; font-size: 46px; line-height: 1.3; letter-spacing: .2px; box-shadow: 0 8px 30px rgba(0,0,0,.25); }
.cap b { color: var(--or2); font-weight: 700; }
.card { position: absolute; background: var(--card); border-radius: 28px; padding: 30px 36px; z-index: 30;
        box-shadow: 0 20px 60px rgba(0,0,0,.45); border: 1.5px solid rgba(255,255,255,.08); }
.kick { font-weight: 600; font-size: 28px; color: var(--or); letter-spacing: 2px; }
.ttl { font-weight: 800; font-size: 50px; line-height: 1.2; }
.row { display: flex; align-items: center; gap: 18px; font-weight: 600; font-size: 34px; margin-top: 18px; opacity: 0; }
.chk { flex: none; width: 46px; height: 46px; border-radius: 50%; background: var(--or); color: #111; display: flex; align-items: center;
       justify-content: center; font-weight: 900; font-size: 28px; }
.chip { display: inline-block; padding: 10px 26px 14px; border-radius: 999px; background: var(--or); color: #111; font-weight: 700; font-size: 36px; }
""")
if CAMBOX:
    cx_, cy_, cw_, ch_ = CAMBOX
    ty_ = TASKBAR_Y or (cy_ + ch_)
    css.append(f"""#maskw {{ left: {cx_}px; top: {cy_}px; width: {W - cx_}px; height: {ty_ - cy_}px; }}
#maskt {{ left: {cx_}px; top: {ty_}px; width: {W - cx_}px; height: {H - ty_}px; }}
#pip {{ left: {cx_}px; top: {cy_}px; width: {cw_}px; height: {ch_}px; }}
#pip video {{ left: -{cx_ + 4}px; top: -{cy_ + 4}px; width: {W}px; height: {H}px; }}
""")
else:
    css.append("#maskw, #maskt, #pip { display: none; }")


# ================================================================ 2. step tracker (screen part)
STEPS = [(40.5, "เตรียมไฟล์ในโฟลเดอร์"), (114.3, "พิมพ์คำสั่ง"), (157.6, "กด Enter"), (177.9, "รอ Claude ตัดต่อ"), (469.1, "ดูผลงาน")]
chips = "".join(f'<div id="st{k}" class="st"><i>{k + 1}</i><span>{n}</span></div>' for k, (_, n) in enumerate(STEPS))
add(f'<div id="bar">{chips}</div>')
css.append("""#bar { position: absolute; left: 22px; top: 20px; display: flex; gap: 8px; padding: 8px; border-radius: 18px; background: rgba(14,15,20,.9);
       z-index: 45; box-shadow: 0 10px 30px rgba(0,0,0,.25); opacity: 0; }
.st { display: flex; align-items: center; gap: 9px; padding: 4px 16px 6px 6px; border-radius: 12px; font-weight: 600; font-size: 23px; color: rgba(255,255,255,.45); }
.st i { font-style: normal; width: 32px; height: 32px; border-radius: 50%; background: rgba(255,255,255,.14); display: flex; align-items: center;
        justify-content: center; font-size: 19px; font-weight: 700; color: #fff; }
.st.on { background: var(--or); color: #111; } .st.on i { background: #111; color: var(--or); }
.st.done { color: #fff; } .st.done i { background: var(--mint); color: #111; }""")
ft("#bar", {"opacity": 0, "y": -30}, {"opacity": 1, "y": 0, "duration": 0.45, "ease": "power3.out"}, M(39.0))
to("#bar", {"opacity": 0, "y": -30, "duration": 0.35}, M(476.8))
for k, (t, n) in enumerate(STEPS):
    at = M(t)
    hide(f"#st{k}", {"backgroundColor": "rgba(255,122,26,0)", "color": "rgba(255,255,255,0.45)"})
    hide(f"#st{k} i", {"backgroundColor": "rgba(255,255,255,0.14)", "color": "#ffffff"})
    to(f"#st{k}", {"backgroundColor": "rgba(255,122,26,1)", "color": "#111111", "duration": 0.25}, at)
    to(f"#st{k} i", {"backgroundColor": "#111111", "color": "#FF7A1A", "duration": 0.25}, at)
    done_at = M(STEPS[k + 1][0]) if k + 1 < len(STEPS) else M(511.5)
    to(f"#st{k}", {"backgroundColor": "rgba(255,122,26,0)", "color": "#ffffff", "duration": 0.25}, done_at)
    to(f"#st{k} i", {"backgroundColor": "#3EE6B0", "color": "#111111", "duration": 0.25}, done_at)
    # big step announcement
    add(f'<div id="sa{k}" class="sa"><div class="san">STEP {k + 1}</div><div class="sat">{n}</div></div>')
    ft(f"#sa{k}", {"opacity": 0, "x": -60}, {"opacity": 1, "x": 0, "duration": 0.4, "ease": "back.out(1.7)"}, at + 0.1)
    out(f"#sa{k}", at + 2.3)
    sfx("ding-1", at + 0.1, 0.2)
css.append("""#root .sa { position: absolute; left: 22px; top: 92px; z-index: 46; padding: 14px 30px 20px; border-radius: 20px; background: var(--or);
       color: #111; box-shadow: 0 14px 40px rgba(255,122,26,.4); opacity: 0; }
.san { font-weight: 800; font-size: 24px; letter-spacing: 3px; } .sat { font-weight: 800; font-size: 46px; line-height: 1.15; }""")

# ================================================================ 3. fast-forward badge
css.append("""#root .ff { position: absolute; left: 1090px; top: 26px; width: 210px; z-index: 47; display: flex; gap: 10px; align-items: center;
      justify-content: center; padding: 6px 0 10px; border-radius: 999px; background: rgba(14,15,20,.88); font-weight: 800; font-size: 30px; opacity: 0; }
.ffi { color: var(--or); font-size: 26px; letter-spacing: -6px; margin-right: 6px; }""")
for p in PCS:
    if p["speed"] >= 2.5 and p["dur"] >= 0.5 and not p["head"]:
        a, b = p["edit"], p["edit"] + p["dur"]
        add(f'<div id="ff{p["i"]}" class="ff"><span class="ffi">▶▶</span><span>เร่ง x{round(p["speed"])}</span></div>')
        hide(f"#ff{p['i']}")
        to(f"#ff{p['i']}", {"opacity": 1, "duration": 0.1}, a)
        to(f"#ff{p['i']}", {"opacity": 0, "duration": 0.1}, b - 0.1)


# ================================================================ 1. opening + recap (talking head, right side)
add('<div id="ch" class="abs"><div class="chn">บทที่</div><div class="chb">3</div></div>')
css.append("""#ch { position: absolute; left: 1330px; top: 210px; width: 520px; text-align: center; z-index: 30; }
.chn { font-weight: 800; font-size: 90px; line-height: 1; } .chb { font-weight: 900; font-size: 380px; line-height: .9; color: var(--or);
       text-shadow: 0 10px 60px rgba(255,122,26,.45); }""")
ft("#ch", {"opacity": 0, "scale": 1.6}, {"opacity": 1, "scale": 1, "duration": 0.45, "ease": "expo.out"}, 0.05)
sfx("impact-1", 0.08, 0.45)
out("#ch", M(5.6))

add('<div id="recap" class="card" style="left:1290px;top:200px;width:590px">'
    '<div class="kick">ทบทวนบทที่แล้ว</div><div class="ttl">พร้อมแล้ว!</div>'
    '<div id="rc1" class="row"><div class="chk">✓</div><div>สร้างโปรเจกต์ (โฟลเดอร์ตัดต่อ)</div></div>'
    '<div id="rc2" class="row"><div class="chk">✓</div><div>ตั้งกติกาด้วย agent.md</div></div></div>')
pop_in("#recap", M(5.8))
for k, t in ((1, 7.0), (2, 11.6)):
    ft(f"#rc{k}", {"opacity": 0, "x": 40}, {"opacity": 1, "x": 0, "duration": 0.35, "ease": "power3.out"}, M(t))
add('<div id="today" class="card" style="left:1290px;top:560px;width:590px;padding:22px 32px">'
    '<div class="kick">บทนี้</div><div class="ttl" style="font-size:46px">สั่ง Claude <span style="color:var(--or)">ตัดคลิปจริง!</span> 🎬</div></div>')
pop_in("#today", M(13.9))
out("#recap", M(16.4)); out("#today", M(16.4))

# ================================================================ 2. what is in the folder
ITEMS = [(45.5, "🎬", "คลิปวิดีโอดิบ", "ถ่ายทีละขั้นตอน ไม่ได้เซ็ตอะไร"), (71.2, "🎙️", "เสียงพากย์", "พากย์ไว้แล้ว"),
         (74.5, "📝", "สคริปต์", "บอกขั้นตอนต่างๆ"), (79.5, "🔊", "Sound Effect", "จากใต้คลิปบทที่ 2")]
rows = "".join(f'<div id="fi{k}" class="frow"><div class="fe2">{e}</div><div><div class="fn">{n}</div><div class="fs">{d}</div></div></div>'
               for k, (_, e, n, d) in enumerate(ITEMS))
add(f'<div id="fold" class="card"><div class="kick">📁 ในโฟลเดอร์ “สามชั้นผัด”</div>{rows}</div>')
css.append("""#fold { left: 30px; top: 560px; width: 640px; padding: 22px 28px 24px; }
.frow { display: flex; gap: 16px; align-items: center; margin-top: 10px; opacity: 0; }
.fe2 { flex: none; width: 60px; height: 60px; border-radius: 16px; background: rgba(255,255,255,.1); font-size: 44px; display: flex; align-items: center; justify-content: center; }
.fn { font-weight: 700; font-size: 34px; line-height: 1.15; } .fs { font-weight: 500; font-size: 24px; opacity: .7; }""")
pop_in("#fold", M(45.4))
for k, (t, _, _, _) in enumerate(ITEMS):
    ft(f"#fi{k}", {"opacity": 0, "x": 30}, {"opacity": 1, "x": 0, "duration": 0.35, "ease": "power3.out"}, M(t))
    sfx("pop-2", M(t), 0.25)
out("#fold", M(97.5))
# the cooking-clip name tag
add('<div id="dish"><span>🍳 สามชั้นผัดกะปิชะอม</span></div>')
css.append("""#dish { position: absolute; left: 0; right: 0; top: 660px; text-align: center; z-index: 30; opacity: 0; }
#dish span { display: inline-block; font-weight: 800; font-size: 64px; color: #111; background: var(--or); padding: 6px 40px 18px; border-radius: 24px;
             transform: rotate(-2deg); box-shadow: 0 16px 50px rgba(255,122,26,.4); }""")
ft("#dish", {"opacity": 0, "scale": 0.5}, {"opacity": 1, "scale": 1, "duration": 0.4, "ease": "back.out(2.4)"}, M(52.6))
out("#dish", M(56.2))

# ================================================================ 3. the order (while typing)
REC = [(125.1, "📁", "ทำงานในโฟลเดอร์สามชั้นผัด"), (131.3, "🧩", "ใช้ Skill GivemeClip"), (133.9, "✂️", "ตัดให้กระชับ ตัด Dead Air"),
       (135.3, "🔤", "ตัวหนังสือ + อินโฟกราฟิก ไม่น่าเบื่อ"), (140.3, "🎵", "เพลงประกอบฟังสนุก"), (144.3, "🔊", "SFX จากในโฟลเดอร์"),
       (146.2, "🌿", "เก็บเสียงบรรยากาศเดิมไว้")]
rows = "".join(f'<div id="rr{k}" class="rrow"><div class="re">{e}</div><div>{txt}</div></div>' for k, (_, e, txt) in enumerate(REC))
add(f'<div id="rec" class="card"><div class="kick">✍️ สูตรคำสั่ง</div>{rows}</div>')
css.append("""#rec { left: 30px; top: 170px; width: 660px; padding: 24px 30px 26px; }
.rrow { display: flex; gap: 14px; align-items: center; margin-top: 12px; font-weight: 600; font-size: 29px; line-height: 1.25; opacity: 0; }
.re { flex: none; width: 50px; font-size: 32px; text-align: center; }""")
pop_in("#rec", M(120.6))
for k, (t, _, _) in enumerate(REC):
    ft(f"#rr{k}", {"opacity": 0, "x": -30}, {"opacity": 1, "x": 0, "duration": 0.35, "ease": "power3.out"}, M(t))
out("#rec", M(157.5))
add('<div id="tip" class="card"><div style="font-size:64px">💡</div><div><div class="kick">เคล็ดลับ</div>'
    '<div class="ttl" style="font-size:42px">สั่งงาน<span style="color:var(--or)">เหมือนสั่งพนักงาน 1 คน</span></div></div></div>')
css.append("""#tip { left: 720px; top: 200px; width: 740px; display: flex; gap: 26px; align-items: center; border: 3px solid var(--or); }""")
ft("#tip", {"opacity": 0, "scale": 0.7}, {"opacity": 1, "scale": 1, "duration": 0.45, "ease": "back.out(2)"}, M(150.1))
sfx("tech-ui-confirm", M(150.2), 0.3)
out("#tip", M(157.5))
sfx("send-swoosh", M(157.7), 0.4)

# ================================================================ 4. PDF freebie (while Claude works)
add('<div id="pdf" class="card"><div class="fg">📄</div><div><div class="kick">แจกฟรี! ใต้คลิปนี้</div>'
    '<div class="ttl" style="font-size:60px">PDF <span style="color:var(--or)">รวมคำสั่งตัดต่อ</span></div>'
    '<div style="font-weight:600;font-size:32px;opacity:.85">คิดไม่ออกว่าจะสั่งแบบไหน โหลดไปใช้ได้เลย</div></div></div>')
css.append("""#pdf { left: 330px; top: 130px; width: 1260px; display: flex; gap: 34px; align-items: center; padding: 34px 46px; border: 4px solid var(--or); }
.fg { font-size: 140px; line-height: 1; }""")
ft("#pdf", {"opacity": 0, "scale": 0.7, "rotation": -3}, {"opacity": 1, "scale": 1, "rotation": 0, "duration": 0.5, "ease": "back.out(2)"}, M(188.8))
sfx("kaching-1", M(188.9), 0.35)
out("#pdf", M(205.8))

# ================================================================ 5. waiting: Claude works (real-time clock)
add('<div id="wait" class="card"><div class="kick">⏳ Claude กำลังตัดต่อให้</div>'
    '<div class="ttl" style="font-size:40px">ทำงานไปแล้ว <span id="clk" style="color:var(--or)">1:11</span> นาที</div>'
    '<div class="bar2"><i id="prog"></i></div></div>')
css.append("""#wait { left: 30px; top: 170px; width: 620px; padding: 24px 30px 30px; }
.bar2 { margin-top: 16px; height: 14px; border-radius: 7px; background: rgba(255,255,255,.12); overflow: hidden; }
.bar2 i { display: block; height: 100%; width: 100%; background: linear-gradient(90deg, var(--or), var(--or2)); transform-origin: 0 50%; }""")
SENT = 157.7
pop_in("#wait", M(228.8))
hide("#prog", {"scaleX": 0.05})
# clock + bar follow the raw clock: one tween per kept piece, so the number reads right at any frame
segs = [p for p in PCS if p["b"] > 228.8 and p["a"] < 469.1]
for p in segs:
    a, b = max(p["a"], 228.8), min(p["b"], 469.1)
    e0, e1 = M(a), M(a) + (b - a) / p["speed"]
    tl.append(f'tl.fromTo({{v: {a - SENT:.2f}}}, {{v: {a - SENT:.2f}}}, {{v: {b - SENT:.2f}, duration: {max(0.04, e1 - e0):.3f}, ease: "none", immediateRender: false, '
              f'onUpdate: function() {{ const s = Math.floor(this.targets()[0].v); document.getElementById("clk").textContent = Math.floor(s / 60) + ":" + String(s % 60).padStart(2, "0"); }} }}, {e0:.3f});')
    to("#prog", {"scaleX": round(min(1, (b - SENT) / (469.1 - SENT)), 3), "duration": max(0.04, e1 - e0), "ease": "none"}, e0)
to("#wait", {"scale": 1.06, "duration": 0.2, "yoyo": True, "repeat": 1}, M(267.45))
out("#wait", M(469.0))

# ================================================================ 6. done + playback
add('<div id="done"><span>✅ ตัดเสร็จแล้ว!</span></div>')
css.append("""#done { position: absolute; left: 0; right: 0; top: 420px; text-align: center; z-index: 30; opacity: 0; }
#done span { display: inline-block; font-weight: 900; font-size: 96px; color: #111; background: var(--mint); padding: 6px 46px 22px; border-radius: 28px;
             box-shadow: 0 16px 60px rgba(62,230,176,.45); }""")
ft("#done", {"opacity": 0, "scale": 0.4}, {"opacity": 1, "scale": 1, "duration": 0.45, "ease": "back.out(2.5)"}, M(470.2))
sfx("tech-ui-confirm", M(470.2), 0.3)
out("#done", M(473.2))
add('<div id="play"><span class="dot"></span>ผลงานที่ Claude ตัดให้</div>')
css.append("""#play { position: absolute; left: 30px; top: 30px; z-index: 46; display: flex; gap: 14px; align-items: center; padding: 10px 26px 14px;
        border-radius: 999px; background: rgba(14,15,20,.88); font-weight: 700; font-size: 34px; opacity: 0; }
.dot { width: 18px; height: 18px; border-radius: 50%; background: #ff3b30; box-shadow: 0 0 0 6px rgba(255,59,48,.25); }""")
ft("#play", {"opacity": 0, "x": -30}, {"opacity": 1, "x": 0, "duration": 0.35}, M(477.2))
out("#play", M(511.0))

# ================================================================ 7. fix by asking
FIX = [(521.4, "🔊", "เสียงเอฟเฟกต์ดังไป"), (524.2, "🎙️", "เสียงบรรยายเบาไป"), (526.3, "🎬", "อยากแก้ช็อตไหน")]
chips = "".join(f'<div id="fx{k}" class="fxc"><span>{e}</span>{t}</div>' for k, (_, e, t) in enumerate(FIX))
add(f'<div id="fix" class="card"><div class="kick">อยากแก้ตรงไหน?</div><div class="ttl" style="font-size:58px">แค่<span style="color:var(--or)">พิมพ์สั่งแก้</span>ได้เลย</div>'
    f'<div class="fxs">{chips}</div></div>')
css.append("""#fix { left: 300px; top: 220px; width: 1320px; text-align: center; padding: 36px 40px 42px; }
.fxs { display: flex; gap: 20px; justify-content: center; margin-top: 26px; }
.fxc { display: flex; gap: 10px; align-items: center; padding: 10px 26px 14px; border-radius: 999px; background: #fff; color: #111; font-weight: 700; font-size: 32px; opacity: 0; }""")
ft("#shade", {"opacity": 0}, {"opacity": 1, "duration": 0.5}, M(517.0))
pop_in("#fix", M(517.0))
for k, (t, _, _) in enumerate(FIX):
    ft(f"#fx{k}", {"opacity": 0, "y": 20, "scale": 0.7}, {"opacity": 1, "y": 0, "scale": 1, "duration": 0.35, "ease": "back.out(2)"}, M(t))
out("#fix", M(531.6))

# ================================================================ 8. end card
add('<div id="next" class="card"><div class="kick">จบบทที่ 3</div><div class="ttl" style="font-size:92px">เจอกัน<span style="color:var(--or)">บทเรียนถัดไป!</span> 👋</div>'
    '<div class="prog"><span class="pd">บทที่ 3 ✓</span><span class="pl"></span><span class="pn">บทที่ 4</span></div></div>')
css.append("""#next { left: 300px; top: 300px; width: 1320px; text-align: center; padding: 46px 50px 54px; }
.prog { margin-top: 30px; display: flex; align-items: center; justify-content: center; gap: 18px; font-weight: 700; font-size: 36px; }
.pd { color: var(--mint); } .pn { padding: 6px 26px 10px; border-radius: 999px; background: var(--or); color: #111; }
.pl { width: 220px; height: 6px; border-radius: 3px; background: linear-gradient(90deg, var(--mint), var(--or)); }""")
pop_in("#next", M(535.7), y=40)

# ================================================================ audio + page
aud = [f'<audio id="vo" src="assets/voice.wav" data-start="0" data-duration="{T}" data-track-index="10" data-volume="1"></audio>']
for i, (n, at, vol) in enumerate(sorted(sounds, key=lambda s: s[1])):
    at = max(0, at)
    aud.append(f'<audio id="sx{i}" src="assets/sfx/{n}.wav" data-start="{at:.3f}" data-duration="2.0" data-track-index="{11 + i}" data-volume="{vol}"></audio>')
body += aud
html = f"""<!doctype html>
<html lang="th"><head><meta charset="utf-8">
<script src="{GSAP}"></script>
<style>
html, body {{ margin: 0; background: #000; }}
#root {{ position: relative; width: {W}px; height: {H}px; overflow: hidden; background: #000; }}
.abs {{ position: absolute; }}
{''.join(css)}
</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-width="{W}" data-height="{H}" data-duration="{T}" data-fps="{FPS}">
{chr(10).join(body)}
</div>
<script>
  window.__timelines = window.__timelines || {{}};
  const tl = gsap.timeline({{ paused: true }});
{chr(10).join('  ' + x for x in base)}
{chr(10).join('  ' + x for x in tl)}
  window.__timelines["main"] = tl;
</script>
</body></html>
"""
open(os.path.join(R, "index.html"), "w", encoding="utf-8").write(html)
print(f"index.html: {T:.2f} s, screen from {SCR:.2f} s, {len(CAP)} captions, {len(sounds)} sfx")
for t, n in STEPS:
    print(f"  step {n}: {M(t):.2f}")
