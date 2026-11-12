# GivemeClip

สกิลสำหรับ [Claude Code](https://claude.com/claude-code) ใช้ตัดคลิปพูดหน้ากล้องภาษาไทย (มีเทคซ้ำ พูดผิด ช่วงเงียบ)
ให้เป็นคลิปสั้นแนวตั้ง 9:16 ตามไฟล์สคริปต์ ได้ทั้งซับไทย กราฟิกเคลื่อนไหวตามคำพูด จอเล็กของต้นฉบับ แบ่งครึ่งจอ
รูปเป็น 3D (2.5D) เพลงที่หลบใต้เสียงพูด เสียงเอฟเฟกต์ และไฟล์ส่งมอบที่ -14 LUFS พร้อมลง Reels / TikTok / Shorts

A Claude Code skill that turns a raw Thai talking-head recording plus a script into a finished 9:16 short.
Built on [ghost-editor](https://github.com/kurbaitaev/ghost-editor) (MIT) and HyperFrames.

## ในนี้มีอะไร

| โฟลเดอร์ | หน้าที่ |
|---|---|
| `givemeclip/` | สกิลหลัก: `SKILL.md`, `scripts/gmc.py` (คำสั่ง doctor / prep / islands / cut / reel / snap / render), แม่แบบฉาก `templates/reel_example.py` |
| `depth-parallax/` | สกิลทำรูปนิ่งเป็นภาพเคลื่อนไหวแบบ 2.5D (Depth Anything V2) |
| `INSTALL.md` | คู่มือติดตั้งภาษาไทยทีละขั้น |

## ติดตั้งเร็ว ๆ

ให้ Claude Code อ่านไฟล์นี้กับ `INSTALL.md` แล้วสั่งว่า "ติดตั้งสกิล GivemeClip ให้หน่อย" หรือทำเองตาม [INSTALL.md](INSTALL.md)

## ผลจากงานแรก (วัดจริง)

ต้นฉบับ 5:01 นาที → คลิป 24.3 วิ · -14.0 LUFS · true peak -1.4 dBFS · เห็นหน้าคนพูด 81% · ภาพดำ/ภาพค้าง 0

ทดสอบบน Windows 11 + RTX 4050 ส่วน macOS/Linux ยังไม่ได้ทดสอบ

## License

MIT (ไฟล์ในรีโปนี้) · ghost-editor, HyperFrames, Depth Anything V2, เสียงเอฟเฟกต์และเพลง ใช้ตามสัญญาอนุญาตของแต่ละโปรเจกต์
