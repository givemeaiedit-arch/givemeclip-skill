---
name: givemeclip
description: "GivemeClip: cut a raw Thai talking-head recording (retakes, flubs, dead air) into a professional vertical 9:16 short (15-60 s) that follows a script file (สคิป.txt / สคริปต์), with Thai captions, motion graphics on the spoken lines, PiP of the original, split screen, 2.5D '3D' photos, SFX, a music bed ducked under the voice, speed-up and -14 LUFS delivery. Use when the user says GivemeClip, ตัดคลิป, 'ตัดคลิปจากไฟล์ดิบ', hands over a raw .mp4/.MOV plus a script, or asks to re-cut/fix one of these clips. Builds on the ghost-editor and depth-parallax skills; tested on Windows."
---

# GivemeClip

One raw recording + one script in, one finished vertical short out. Built on
[ghost-editor](https://github.com/kurbaitaev/ghost-editor) (MIT: take selection, frame-exact cuts, HyperFrames
composition, SFX library) and the bundled `depth-parallax` skill (photo -> 2.5D camera move).

`G=<skills>/givemeclip/scripts/gmc.py`; always run `PYTHONUTF8=1 python3 "$G" ...`. Paths come from environment
variables (INSTALL.md): `GMC_GHOST_EDITOR`, `GMC_WHISPER_PY`, `GMC_FW_PY` (faster-whisper; defaults to the whisper
python), `GMC_MEDIAPIPE_PY`, `GMC_PARALLAX`.
The project folder `P` must be an ASCII path (e.g. `D:/reels/<name>`): OpenCV cannot open Thai paths on Windows.

## Steps

0. `gmc.py doctor --fix` — ghost-editor, the whisper python (+ silero-vad, CUDA), faster-whisper, the mediapipe
   python, depth-parallax, ffmpeg, bash, the SFX kit (restores files stuck as `*.wav.tmp.wav`), free disk (~15 GB).
1. `gmc.py prep <source.mp4> <P> --script <script.txt>` — links the source, makes a frame-exact proxy + voice wavs,
   silero VAD speech islands, ONE batched faster-whisper pass over the whole file (`scripts/fw_batch.py`: large-v3,
   GPU fp16, batch 16, word times -> `build/fw.json`; CPU int8 when there is no NVIDIA GPU), split back into the VAD
   islands as `build/islands.json` (`"src": "fw"`, token pieces glued into whole syllables), and a per-frame face scan
   in parallel, then prints the island table. Start it in the background (5 min source: ~7.5 min proxy).
   Always use this batched transcript. `prep --exact` (openai-whisper, fp32, one pass per island: ~17 min for 97 s
   of Thai) replaces it only when the user asks. Batched word times are coarser (a drawn-out word can land in the
   next island); cut times still come from the audio (plan_cut trims by VAD), so check takes by ear / frame.
2. Read the table (`gmc.py islands <P>`) against the script. Whisper Thai garbles words and loops (`นี่นี่นี่…`):
   use it for TIMES and to recognise the line, never as caption text. Pick the LAST fluent take of each line that
   looks at the lens (check a frame of each candidate).
3. Write `<P>/cut.json` (`templates/cut_example.json`): `pieces` in raw seconds, one per script line, note `L<n> <line>`.
   - A dict piece with `"b"` past the words keeps a gesture after the line (a hand pulling the split screen down).
   - plan_cut trims silence inside a piece: for a full-screen scene, start it over the end of the line instead of
     holding a silent piece.
   - `"tight": 1.3` alternates wide/tight framing at take changes (reads as a second camera).
4. `gmc.py cut <P>` — plan_cut, assemble (alt plate), voice_smooth, qa_cut. LOOK at `build/cutsheet.jpg`: on an
   off-centre speaker qa_cut flags "turn" on every frame; trust the pictures.
5. `gmc.py reel <P>` — `<P>/reel` with plate, voice, face.json and `reel.py` copied from `templates/reel_example.py`.
   Adapt it: `LINES` = the script split into caption phrases (exact script text; phrase times come from the island
   tokens by character share), then the scene blocks keyed to `S(key, i)` / `SE(key, i)` (phrase start / end) and
   `E(key)` / `END(key)` (piece). Blocks in the example, each self-contained: title slam, raw-file grid, dead-air
   editor (real waveform + VAD gaps collapsing with blade sounds), volume slider, captions that switch on at a line,
   PiP of the original running to the end with a RAW timecode, split screen (image -> 3D -> workflow timeline),
   comment-box CTA, Fluent emoji pops, punch-ins. Run `PYTHONUTF8=1 python3 reel.py`: it prints face-on-screen %,
   full-screen seconds and every beat, and fails on a graphic over the face.
6. `gmc.py snap <P>/reel 0.6,2,5,...` — snapshots + one sheet. Look at every beat, fix, re-snap.
7. `gmc.py render <P>/reel <out.mp4> [--speed 1.15] [--bed music.wav --bed-at <s> --bed-from <s> --bed-db -15]` —
   HyperFrames render, speed-up, music bed ducked under the voice (sidechain), -14 LUFS / TP -1.5, H.264 1080x1920
   30 fps, then QA (length, LUFS, true peak, black, frozen frames). With `--bed`, set `music=None` in reel.py so two
   beds don't stack. `--bed-at` is in pre-speed seconds. `--no-render` re-delivers the last master.

3D from a photo (2.5D, not a 360° model: say so):
`<whisper python> <skills>/depth-parallax/scripts/parallax.py in.png out.mp4 --motion orbit --duration 2.6 --size 1080x830 --strength 1.4`

## Windows fixes built into gmc.py
- Thai json written as cp874 by child scripts: gmc sets `PYTHONUTF8=1` everywhere and repairs islands.json.
- ghost-editor `finals.py` imports `fcntl` (macOS/Linux only): gmc renders with `hf.sh render` and encodes itself.
- `hf.sh` hands HyperFrames a `.sh` ffmpeg wrapper that Node cannot spawn on Windows (`spawn EFTYPE`): gmc passes
  ffmpeg.exe (the wrapper only made audio byte-identical between renders).
- `.sh` scripts run through Git Bash, not WSL bash.

## Thai text rendering — always
Vowels and tone marks must never overlap (ซ้ำ, น้ำ, ทั้ง, ปั้น: the tone mark sits ABOVE ำ / ั, not on it).
- EVERY time text goes into a clip, run the check: `gmc.py thai <file|dir> [--fix]` (`scripts/thai_check.py`).
  It finds wrong typing order (ำ before the tone, tone before ั/ิ/ี/ุ…, doubled marks, a mark with no consonant) and
  render methods that collide (drawtext, subtitles=, ass= without shaping=complex, PIL without RAQM, cv2.putText).
  `gmc.py snap` and `gmc.py render` run it on P/reel automatically: order errors are fixed in place, anything else
  stops the run (`--force` only if the user says so).
- Burning ASS with ffmpeg: use `ass=file.ass:fontsdir=...:shaping=complex`. The plain `subtitles=` filter (and
  `shaping=simple`) skips Thai mark positioning and stacks ้ on top of ำ. Use complex for snapshots too.
- ffmpeg `drawtext` has no Thai shaping: don't use it for Thai. PIL only with `layout_engine=ImageFont.Layout.RAQM`
  (check `features.check('raqm')`); otherwise render the text in HTML/Chrome (HyperFrames), which shapes Thai correctly.
- Type Thai in logical order (consonant, upper vowel, tone mark, then ำ), never ำ before the tone mark.
- Before sending a preview, zoom into one frame that has ้/่ with ำ or ั and check the marks.

## Working with the user
- Use only the files they name; making many "raw files" out of the source's own frames is fine. Say when a picture
  carries someone else's watermark.
- Send a preview, take their notes, change `reel.py` (it is the state of the edit) and re-render.
- Report numbers that were measured, and say what was not checked by ear (music level under the voice).
