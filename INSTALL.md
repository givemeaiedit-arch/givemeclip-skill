# ติดตั้งสกิล GivemeClip

สกิลสำหรับ Claude Code ใช้ตัดคลิปพูดหน้ากล้องภาษาไทย (มีเทคซ้ำ พูดผิด ช่วงเงียบ) ให้เป็นคลิปสั้นแนวตั้ง 9:16 ตามไฟล์สคริปต์
ได้ทั้งซับไทย กราฟิกเคลื่อนไหว จอเล็ก แบ่งจอ รูปเป็น 3D เพลง และเสียงเอฟเฟกต์

ทดสอบแล้วบน Windows 11 + RTX 4050 · macOS / Linux ควรใช้ได้ แต่ยังไม่ได้ทดสอบ

ลำดับในไฟล์นี้ตรงกับคู่มือ PDF เล่ม 0 "เริ่มจากศูนย์จนได้คลิปแรก" (บท 2–6)

---

## ทางลัด: ให้ Claude ติดตั้งให้

ถ้ามี Claude Code อยู่แล้ว (ทำขั้น 0 เสร็จแล้ว) วางข้อความนี้ในช่องพิมพ์ได้เลย

```text
ติดตั้งสกิล GivemeClip จาก https://github.com/givemeaiedit-arch/givemeclip-skill ให้หน่อย
ทำตาม INSTALL.md ในนั้น วางสกิลไว้ใน .claude/skills ของโฟลเดอร์นี้
ถ้าต้องดาวน์โหลดหรือติดตั้งอะไร ถามก่อนทุกครั้ง เสร็จแล้วรัน gmc.py doctor ให้ดูด้วย
```

Claude จะทำขั้น 1–6 ข้างล่างให้ และจะถามก่อนทุกครั้งที่ต้องดาวน์โหลดหรือติดตั้ง
ถ้าอยากทำเอง ให้ทำตามขั้นข้างล่างทีละขั้น

---

## 0. สมัคร Claude และลงแอป

1. สมัครที่ **claude.ai** จะใช้บัญชี Google หรืออีเมลก็ได้ บัญชีใหม่ต้องยืนยันเบอร์มือถือที่รับ SMS ได้
2. เลือกแพ็กเกจ **Pro ขึ้นไป** เพราะแพ็กเกจ Free ใช้ Claude Code ไม่ได้ (ดูราคาล่าสุดที่ claude.com/pricing)
3. ดาวน์โหลด **แอป Claude สำหรับ Windows** ที่ claude.com/download เปิดแอป ล็อกอิน แล้วกดแท็บ **Code**
4. **เลือกโมเดล Opus 5.5** ระดับความคิด (effort) **อย่างน้อยต่ำ–ปานกลาง** ที่ปุ่มชื่อโมเดล มุมขวาล่างใต้ช่องพิมพ์
   (ถ้าใช้แบบบรรทัดคำสั่ง พิมพ์ `/model`) งานตัดคลิปต้องเลือกเทคและวางฉากหลายขั้น โมเดลเล็กกว่านี้จะพลาดบ่อยกว่า
   ตั้งสูงขึ้นงานจะละเอียดขึ้น แต่ช้าลงและกินโควตามากขึ้น

ถ้าถนัดบรรทัดคำสั่ง จะลง Claude Code ผ่าน PowerShell แทนก็ได้ (ไม่ต้องเปิดแบบ Administrator)

```powershell
irm https://claude.ai/install.ps1 | iex
```

## 1. สิ่งที่ต้องมีในเครื่อง

| ของที่ต้องมี | ใช้ทำอะไร | หมายเหตุ |
|---|---|---|
| Windows 10 (1809+) หรือ 11 | | แรม 16 GB ขึ้นไปจะตัดวิดีโอได้สบาย |
| Python 3.12 | ถอดเสียง หาช่วงพูด สแกนหน้า ทำรูป 3D | ตอนติดตั้งให้ติ๊ก "Add to PATH" |
| Node.js 20 ขึ้นไป | เรนเดอร์กราฟิก (HyperFrames) | |
| ffmpeg 6.1 ขึ้นไป | ตัดต่อ แปลงไฟล์ ปรับเสียง | |
| Git for Windows | ดึงสกิลจาก GitHub และใช้ Git Bash | |
| การ์ดจอ NVIDIA | ถอดเสียงเร็วขึ้นหลายเท่า | ไม่บังคับ |
| พื้นที่ว่าง | | ราว 10 GB สำหรับโปรแกรม + 15 GB ต่องาน |

ลงทั้งหมดได้ด้วย winget (พิมพ์ทีละบรรทัดใน PowerShell)

```powershell
winget install Python.Python.3.12
winget install OpenJS.NodeJS.LTS
winget install Gyan.FFmpeg
winget install Git.Git
```

ลงเสร็จแล้วให้ **ปิดแอป Claude หรือหน้าต่าง PowerShell แล้วเปิดใหม่** ไม่งั้นจะยังมองไม่เห็นโปรแกรมที่เพิ่งลง

## 2. วางไฟล์สกิล

```bash
git clone https://github.com/givemeaiedit-arch/givemeclip-skill D:/claude-skills/givemeclip-skill
```

คัดลอก 2 โฟลเดอร์ไปไว้ในโฟลเดอร์สกิลของ Claude Code

```text
D:/claude-skills/givemeclip-skill/givemeclip      →  <โฟลเดอร์งาน>/.claude/skills/givemeclip
D:/claude-skills/givemeclip-skill/depth-parallax  →  <โฟลเดอร์งาน>/.claude/skills/depth-parallax
```

ถ้าอยากให้ใช้ได้ทุกโปรเจกต์ ให้วางไว้ที่ `%USERPROFILE%\.claude\skills\` แทน

## 3. ติดตั้ง ghost-editor (โอเพนซอร์ส MIT)

GivemeClip ใช้ [ghost-editor](https://github.com/kurbaitaev/ghost-editor) เป็นเครื่องมือตัดต่อเบื้องหลัง
ต้องวางไว้ใน path ภาษาอังกฤษล้วน เพราะ OpenCV บน Windows เปิด path ภาษาไทยไม่ได้

```bash
git clone https://github.com/kurbaitaev/ghost-editor D:/claude-skills/ghost-editor
```

ดึงคลังเสียงเอฟเฟกต์ เพลง และอีโมจิ (ประมาณ 60 MB) แนะนำ `--licensed-only` จะดึงเฉพาะของที่มีสัญญาอนุญาตชัดเจน

```bash
python D:/claude-skills/ghost-editor/scripts/library_restore.py --licensed-only
```

HyperFrames (ตัวเรนเดอร์กราฟิก) ไม่ต้องลงแยก สคริปต์จะเรียกผ่าน `npx` เองตอนใช้ครั้งแรก ขอแค่มี Node.js

## 4. สร้าง Python 2 ชุด

**ชุดที่ 1 สำหรับถอดเสียง, VAD และ 3D** (torch + CUDA) ดาวน์โหลดรวมหลาย GB

```bash
python -m venv D:/venvs/whisper
```

```bash
D:/venvs/whisper/Scripts/python.exe -m pip install torch --index-url https://download.pytorch.org/whl/cu128
```

```bash
D:/venvs/whisper/Scripts/python.exe -m pip install openai-whisper silero-vad==6.2.3 transformers opencv-python pillow numpy
```

เครื่องที่ไม่มีการ์ดจอ NVIDIA ให้ลง torch แบบปกติแทน (`pip install torch` ไม่ต้องใส่ `--index-url`) ใช้ได้ แต่ถอดเสียงช้ากว่า

**ชุดที่ 2 สำหรับสแกนใบหน้า** (mediapipe)

```bash
python -m venv D:/venvs/mp
```

```bash
D:/venvs/mp/Scripts/python.exe -m pip install mediapipe==0.10.21 opencv-contrib-python==4.11.0.86 numpy
```

## 5. ตั้งค่า path (ทำครั้งเดียว)

```bash
setx GMC_GHOST_EDITOR "D:/claude-skills/ghost-editor"
```

```bash
setx GMC_WHISPER_PY "D:/venvs/whisper/Scripts/python.exe"
```

```bash
setx GMC_MEDIAPIPE_PY "D:/venvs/mp/Scripts/python.exe"
```

ตั้งเสร็จแล้วให้ปิดแล้วเปิด Claude Code ใหม่ ส่วน `GMC_PARALLAX` ไม่ต้องตั้ง ถ้าวาง depth-parallax ไว้ข้าง givemeclip

## 6. ตรวจความพร้อม

```bash
python .claude/skills/givemeclip/scripts/gmc.py doctor --fix
```

ทุกบรรทัดควรขึ้น `ok` แบบนี้ (ผลจริงจากเครื่องที่ทดสอบ ตัดมาบางบรรทัด)

```text
  ok    ghost-editor at D:/claude-skills/ghost-editor
  ok    silero-vad + whisper in that venv (CUDA True)
  ok    depth-parallax
  ok    SFX kit 78/78
  ok    D: free 40.3 GB
```

ถ้ามีบรรทัด `MISS` จะบอกวิธีแก้ไว้ในบรรทัดเดียวกัน ส่วน `--fix` จะซ่อมไฟล์เสียงเอฟเฟกต์ที่ค้างเป็นชื่อ `*.wav.tmp.wav` ให้ (เจอบน Windows)

## 7. ใช้งาน

สร้างโฟลเดอร์ต่อหนึ่งคลิป แล้ววางไฟล์ดิบ สคริปต์ และรูปประกอบไว้ข้างใน

```text
D:\คลิป\สอนตัดต่อ\
   ├─ ต้นฉบับ.MP4      คลิปดิบ พูดผิด พูดซ้ำได้
   ├─ สคิป.txt          บทพูด + วงเล็บบอกภาพที่อยากได้
   └─ รูป 001.png       รูปประกอบ (ถ้ามี)
```

สคริปต์เขียนบรรทัดละหนึ่งประโยค ใส่ข้อความที่พูดในเครื่องหมายคำพูด แล้วตามด้วยวงเล็บบอกภาพ

```text
"Claude AI" (โชว์ตัวหนังสือแบบ Motion อลังการ)
"และเพิ่มวีดีโอต้นฉบับ เป็นจอเล็กๆ" (จอเล็กมุมซ้าย)
"ทำเป็น model 3d" (เปลี่ยนรูปเป็น 3D แล้ว Pan 2 วินาที)
```

แล้วสั่งใน Claude Code (เช็คก่อนว่าเลือก Opus 5.5 ระดับความคิดอย่างน้อยต่ำ–ปานกลางแล้ว)

```text
GivemeClip ตัดคลิปจาก D:\คลิป\สอนตัดต่อ\ต้นฉบับ.MP4 ตามไฟล์ D:\คลิป\สอนตัดต่อ\สคิป.txt
ยาวไม่เกิน 40 วิ ใช้เฉพาะไฟล์ในโฟลเดอร์นี้ ส่งพรีวิวให้ดูก่อนเรนเดอร์จริง
```

เวลาที่ใช้ (วัดจากงานแรก ไฟล์ดิบ 5 นาที → คลิป 24 วิ)

| ขั้น | เวลา |
|---|---|
| ทำ proxy + ไฟล์เสียง | 7.5 นาที |
| ถอดเสียงไทยทีละช่วง (GPU) · สแกนหน้ารันคู่ขนาน | 17 นาที (สแกนหน้า 25 นาที) |
| ตัด plate | 9.5 นาที |
| เรนเดอร์ + ไฟล์ส่งมอบ | 3–4 นาที |

## ติดปัญหา

| อาการ | ลองทำแบบนี้ |
|---|---|
| ไม่มีแท็บ Code หรือใช้ Claude Code ไม่ได้ | เช็คว่าเป็นแพ็กเกจ Pro ขึ้นไป แล้วล็อกอินใหม่ |
| `'irm' is not recognized` | เปิด CMD อยู่ ให้เปิด PowerShell แทน |
| หาโปรแกรมไม่เจอ ทั้งที่เพิ่งลง | ปิดแล้วเปิดแอป Claude / PowerShell ใหม่ |
| ไฟล์ JSON ภาษาไทยอ่านไม่ออก | gmc.py ตั้ง `PYTHONUTF8=1` ให้อยู่แล้ว ถ้ารันสคริปต์ ghost-editor เอง ให้ตั้งค่านี้ก่อน |
| `spawn EFTYPE` ตอน snapshot หรือ render | ใช้ `gmc.py snap` / `gmc.py render` แทนการเรียก hf.sh ตรง ๆ |
| `No module named 'fcntl'` | finals.py ของ ghost-editor ใช้บน Windows ไม่ได้ ให้ใช้ `gmc.py render` แทน |
| OpenCV เปิดไฟล์ไม่ได้ | ย้ายโฟลเดอร์งานไปไว้ใน path ภาษาอังกฤษ เช่น `D:/reels/ชื่องาน` (gmc.py prep ทำให้เอง) |
| ถอดเสียงช้ามาก | ไม่มีการ์ดจอ NVIDIA หรือยังไม่ได้ลงไดรเวอร์ |
| ผลออกมาไม่ละเอียด ข้ามขั้น หรือเลือกเทคแปลก ๆ | เช็คว่าใช้ Opus 5.5 ระดับความคิดอย่างน้อยต่ำ–ปานกลาง ถ้ายังไม่ดีให้เพิ่มระดับ |
| ดิสก์เต็มกลางทาง | เคลียร์ให้ว่างอย่างน้อย 15 GB แล้วสั่งให้ทำต่อ |

## คู่มือ PDF

| เล่ม | ไฟล์ | เหมาะกับ |
|---|---|---|
| 0 | GivemeClip-Start.pdf | มือใหม่ เริ่มจากสมัคร Claude จนได้คลิปแรก |
| 1 | GivemeClip-Guide.pdf | ส่งให้ Claude อ่านแล้วติดตั้งให้ + ภาพรวมของสกิล |
| 2 | วิธีใช้ Skill.pdf | เบื้องหลังการทำงานทีละขั้นจากงานแรก |
| 3 | GivemeClip-Techniques.pdf | เทคนิคตัดคลิปแบบอื่น และคำสั่งตัวอย่าง 27 แบบ |
