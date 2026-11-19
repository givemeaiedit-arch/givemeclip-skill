# GivemeClip

สกิลสำหรับ [Claude Code](https://claude.com/claude-code) ใช้ตัดคลิปพูดหน้ากล้องภาษาไทย (มีเทคซ้ำ พูดผิด ช่วงเงียบ)
ได้ทุกรูปแบบคลิป สกิลจะดูขนาดคลิปแล้วเลือกวิธีเอง

- **คลิปสั้นแนวตั้ง 9:16** ตามไฟล์สคริปต์: ซับไทย กราฟิกเคลื่อนไหวตามคำพูด จอเล็กของต้นฉบับ แบ่งครึ่งจอ รูปเป็น 3D (2.5D)
- **บทเรียน / อัดจอ / แนวนอน 16:9 ความยาวเต็ม**: ตัดช่วงเงียบ เร่งช่วงพิมพ์และช่วงรอพร้อมป้าย "เร่ง x" ซูมไปที่จุดที่สอน
  กล้องเล็กกรอบสวย แถบขั้นตอน ซับไทย และการ์ด infographic ที่ขึ้นตามจังหวะพูด

ทั้งสองแบบมีเพลงเบา ๆ ที่หลบใต้เสียงพูด เสียงพูดที่ปรับให้ชัด เสียงเอฟเฟกต์ และไฟล์ส่งมอบที่ -14 LUFS

A Claude Code skill that turns a raw Thai recording into a finished clip: a 9:16 short from a talking-head take plus a
script, or a full-length 16:9 lesson / screen recording with zooms, fast-forwards, captions and infographic cards.
Built on [ghost-editor](https://github.com/kurbaitaev/ghost-editor) (MIT) and HyperFrames.

## ในนี้มีอะไร

| โฟลเดอร์ | หน้าที่ |
|---|---|
| `givemeclip/` | สกิลหลัก: `SKILL.md`, `scripts/gmc.py` (คลิปสั้น: doctor / prep / islands / cut / reel / snap / render), `scripts/lesson.py` (บทเรียน: prep / cut / reel / bed), แม่แบบ `templates/reel_example.py` และ `templates/lesson_reel.py` |
| `depth-parallax/` | สกิลทำรูปนิ่งเป็นภาพเคลื่อนไหวแบบ 2.5D (Depth Anything V2) |
| `INSTALL.md` | คู่มือติดตั้งภาษาไทยทีละขั้น |

## ติดตั้งเร็ว ๆ

ให้ Claude Code อ่านไฟล์นี้กับ `INSTALL.md` แล้วสั่งว่า "ติดตั้งสกิล GivemeClip ให้หน่อย" หรือทำเองตาม [INSTALL.md](INSTALL.md)

## ผลจากงานแรก (วัดจริง)

- คลิปสั้น: ต้นฉบับ 5:01 นาที → คลิป 24.3 วิ · -14.0 LUFS · true peak -1.4 dBFS · เห็นหน้าคนพูด 81% · ภาพดำ/ภาพค้าง 0
- บทเรียน: ต้นฉบับ 5:12 → 2:51 นาที (-14.1 LUFS) และ 9:10 → 3:37 นาที (-13.6 LUFS) · ภาพดำ 0

ทดสอบบน Windows 11 + RTX 4050 ส่วน macOS/Linux ยังไม่ได้ทดสอบ

## License

MIT (ไฟล์ในรีโปนี้) · ghost-editor, HyperFrames, Depth Anything V2, เสียงเอฟเฟกต์และเพลง ใช้ตามสัญญาอนุญาตของแต่ละโปรเจกต์
