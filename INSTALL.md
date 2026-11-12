# ติดตั้งสกิล GivemeClip

สกิลสำหรับ Claude Code ใช้ตัดคลิปพูดหน้ากล้องภาษาไทย (มีเทคซ้ำ พูดผิด ช่วงเงียบ) ให้เป็นคลิปสั้นแนวตั้ง 9:16 ตามไฟล์สคริปต์
ได้ทั้งซับไทย กราฟิกเคลื่อนไหว จอเล็ก แบ่งจอ รูปเป็น 3D เพลง และเสียงเอฟเฟกต์

ทดสอบแล้วบน Windows 11 + RTX 4050 ส่วน macOS/Linux ควรใช้ได้ แต่ยังไม่ได้ทดสอบ

## 1. สิ่งที่ต้องมีก่อน

| โปรแกรม | หมายเหตุ |
|---|---|
| Claude Code | https://claude.com/claude-code |
| Python 3.12 | ตอนติดตั้งให้ติ๊ก "Add to PATH" |
| Node.js 20 ขึ้นไป | HyperFrames ใช้เรนเดอร์กราฟิก |
| ffmpeg 6.1 ขึ้นไป | `winget install Gyan.FFmpeg` หรือ BtbN build |
| Git for Windows | ต้องมี Git Bash ด้วย |
| การ์ดจอ NVIDIA | ไม่บังคับ แต่ถ้าไม่มี การถอดเสียงจะช้ากว่าหลายเท่า |
| พื้นที่ว่าง | ประมาณ 15 GB ต่อหนึ่งงาน (ไฟล์ proxy + plate) |

## 2. วางไฟล์สกิล

ดึงไฟล์จาก GitHub แล้วคัดลอก 2 โฟลเดอร์ไปไว้ในโฟลเดอร์สกิลของ Claude Code

```bash
git clone https://github.com/givemeaiedit-arch/givemeclip-skill D:/claude-skills/givemeclip-skill
```

```text
D:/claude-skills/givemeclip-skill/givemeclip      →  <โปรเจกต์ของคุณ>/.claude/skills/givemeclip
D:/claude-skills/givemeclip-skill/depth-parallax  →  <โปรเจกต์ของคุณ>/.claude/skills/depth-parallax
```

ถ้าอยากให้ใช้ได้ทุกโปรเจกต์ ให้วางไว้ที่ `%USERPROFILE%\.claude\skills\` แทน

## 3. ติดตั้ง ghost-editor (โอเพนซอร์ส MIT)

ต้องวางไว้ใน path ที่เป็นภาษาอังกฤษล้วน เพราะ OpenCV บน Windows เปิด path ภาษาไทยไม่ได้

```bash
git clone https://github.com/kurbaitaev/ghost-editor D:/claude-skills/ghost-editor
```

```bash
cd D:/claude-skills/ghost-editor && python scripts/library_restore.py
```

คำสั่งที่สองดึงคลังเสียงเอฟเฟกต์ เพลง และอีโมจิมาเก็บไว้ หลังจากนั้นทำตาม `docs/INSTALL.md` ของ ghost-editor ส่วน Node / HyperFrames

## 4. สร้าง Python 2 ชุด

**ชุดที่ 1 สำหรับถอดเสียง, VAD และ 3D** (torch + CUDA)

```bash
python -m venv D:/venvs/whisper
```

```bash
D:/venvs/whisper/Scripts/python.exe -m pip install torch --index-url https://download.pytorch.org/whl/cu128
```

```bash
D:/venvs/whisper/Scripts/python.exe -m pip install openai-whisper silero-vad==6.2.3 transformers opencv-python pillow numpy
```

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

ทุกบรรทัดควรขึ้น `ok` ถ้ามีบรรทัด `MISS` จะบอกวิธีแก้ไว้ในบรรทัดเดียวกัน

## 7. ใช้งาน

เปิด Claude Code ในโฟลเดอร์โปรเจกต์ แล้วพิมพ์ เช่น

```text
GivemeClip ตัดคลิปจาก D:\งาน\ต้นฉบับ.MP4 ตามไฟล์ D:\งาน\สคิป.txt ยาวไม่เกิน 40 วิ
```

สคริปต์ควรมีบรรทัดที่พูด และวงเล็บบอกว่าช่วงนั้นต้องการภาพอะไร เช่น

```text
"Claude AI" (โชว์ตัวหนังสือแบบ Motion)
"และเพิ่มวีดีโอต้นฉบับ เป็นจอเล็กๆ" (เพิ่มจอเล็กๆ มุมซ้าย)
"ทำเป็น model 3d" (เปลี่ยนรูปเป็น 3D แล้ว Pan 2 วินาที)
```

Claude จะถอดเสียง เลือกเทคที่ดีที่สุด ตัด ประกอบฉาก ส่งพรีวิวให้ดู แล้วเรนเดอร์ไฟล์ส่งมอบที่ -14 LUFS ให้

## เวลาที่ใช้ (วัดจริงจากงานแรก ต้นฉบับ 5 นาที → คลิป 24 วิ)

| ขั้น | เวลา |
|---|---|
| ทำ proxy + เสียง | 7.5 นาที |
| ถอดเสียงไทยทีละช่วง (GPU) | 17 นาที (สแกนหน้ารันคู่ขนาน 25 นาที) |
| ตัด plate | 9.5 นาที |
| เรนเดอร์ + ไฟล์ส่งมอบ | 3–4 นาที |
