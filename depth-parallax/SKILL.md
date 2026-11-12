---
name: depth-parallax
description: Turn a still photo into a short 2.5D "3D motion" clip (depth parallax camera move — near objects move more than the background) using Depth Anything V2 locally on GPU. Use ONLY when the user asks for 3D/2.5D/parallax motion from a picture, or a still image needs to come alive in a reel and a plain Ken Burns zoom is not enough. Not for video input.
---

# Depth parallax (2.5D)

Run with a python that has torch (+CUDA), transformers, opencv and pillow (the GivemeClip whisper python works):

```
python scripts/parallax.py IN.jpg OUT.mp4 --motion dolly --duration 5
```

Options:
- `--motion` `dolly` (push in, default) · `pan-left` · `pan-right` · `up` · `orbit` (loops)
- `--duration` seconds (5) · `--fps` (30) · `--size` WxH (`1080x1920` vertical; `1920x1080` landscape; `1080x830` a split-screen top half)
- `--strength` 0.5 subtle … 1 normal … 2 strong (more = more edge stretching)
- `--save-depth depth.png` to check the depth map (white = near)

Notes:
- Output is silent H.264. ~11 s for a 2.6 s clip on an RTX 4050.
- The model (~100 MB) downloads on first run into the Hugging Face cache (`HF_HOME` moves it).
- Best on photos with a clear subject in front of a background. Thin details (hair, fences) can smear: lower `--strength`.
- It is 2.5D (the camera moves a little), not a model you can turn 360°.
