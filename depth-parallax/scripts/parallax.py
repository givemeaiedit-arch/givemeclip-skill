"""Depth parallax (2.5D): still image -> short video with a 3D-feeling camera move.

Depth Anything V2 (Small) estimates depth; near pixels move more than far ones.
Images are read with PIL so Thai/non-ASCII paths work (OpenCV only does the remap).

Usage:
  parallax.py IN.jpg OUT.mp4 [--motion dolly|pan-left|pan-right|up|orbit]
              [--duration 5] [--fps 30] [--size 1080x1920] [--strength 1.0]
              [--save-depth depth.png]
"""
import argparse, os, subprocess, sys

pass  # model cache: set HF_HOME to move it (default ~/.cache/huggingface)

import numpy as np
import cv2
from PIL import Image


def estimate_depth(img: Image.Image) -> np.ndarray:
    import torch
    from transformers import pipeline
    dev = 0 if torch.cuda.is_available() else -1
    pipe = pipeline("depth-estimation", model="depth-anything/Depth-Anything-V2-Small-hf", device=dev)
    d = np.asarray(pipe(img)["depth"].resize(img.size, Image.BICUBIC), dtype=np.float32)
    d = (d - d.min()) / max(1e-6, d.max() - d.min())  # 1 = near, 0 = far
    k = max(3, (min(img.size) // 120) | 1)
    return cv2.GaussianBlur(d, (k, k), 0)  # soften edges -> less tearing


def cover(img: Image.Image, w: int, h: int, over: float) -> Image.Image:
    """Scale to cover w*over x h*over, center-crop."""
    W, H = int(w * over), int(h * over)
    s = max(W / img.width, H / img.height)
    r = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
    l, t = (r.width - W) // 2, (r.height - H) // 2
    return r.crop((l, t, l + W, t + H))


def ease(t):  # smooth in-out
    return t * t * (3 - 2 * t)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input"); ap.add_argument("output")
    ap.add_argument("--motion", default="dolly", choices=["dolly", "pan-left", "pan-right", "up", "orbit"])
    ap.add_argument("--duration", type=float, default=5.0)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--size", default="1080x1920")
    ap.add_argument("--strength", type=float, default=1.0, help="parallax amount (0.5 subtle .. 2 strong)")
    ap.add_argument("--save-depth")
    a = ap.parse_args()

    w, h = map(int, a.size.lower().split("x"))
    over = 1.15
    src = cover(Image.open(a.input).convert("RGB"), w, h, over)
    depth = estimate_depth(src)
    if a.save_depth:
        Image.fromarray((depth * 255).astype(np.uint8)).save(a.save_depth)

    S = np.asarray(src)[:, :, ::-1].copy()  # BGR for cv2
    SH, SW = S.shape[:2]
    # output pixel grid in source coords (centered crop of the overscanned image)
    xs, ys = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
    cx, cy = SW / 2, SH / 2
    dx0, dy0 = xs - w / 2, ys - h / 2
    margin = (over - 1) / 2 * min(w, h) * 0.9  # max pixel shift before edges show
    amp = margin * a.strength
    d_full = depth  # sampled at approx positions below
    n = max(1, round(a.duration * a.fps))

    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24",
                           "-s", f"{w}x{h}", "-r", str(a.fps), "-i", "-", "-c:v", "libx264", "-preset", "medium",
                           "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", a.output],
                          stdin=subprocess.PIPE)
    # depth looked up at the un-moved position (cheap inverse-warp approximation)
    D = cv2.remap(d_full, (cx + dx0).astype(np.float32), (cy + dy0).astype(np.float32), cv2.INTER_LINEAR)
    for i in range(n):
        t = ease(i / max(1, n - 1))
        zoom, sx, sy = 1.0, 0.0, 0.0
        if a.motion == "dolly":
            zoom = 1 + 0.08 * a.strength * t            # camera moves forward
            dz = 0.06 * a.strength * t                  # near things grow faster
            scale = zoom * (1 + dz * D)
            mx, my = cx + dx0 / scale, cy + dy0 / scale
        else:
            if a.motion == "pan-left":  sx = amp * (2 * t - 1)
            if a.motion == "pan-right": sx = -amp * (2 * t - 1)
            if a.motion == "up":        sy = amp * (2 * t - 1)
            if a.motion == "orbit":
                ang = 2 * np.pi * (i / n); sx, sy = amp * np.cos(ang), amp * 0.5 * np.sin(ang)
            # near (D=1) moves full amount, far (D=0) moves 30%
            f = 0.3 + 0.7 * D
            mx, my = cx + dx0 + sx * f, cy + dy0 + sy * f
        frame = cv2.remap(S, mx.astype(np.float32), my.astype(np.float32), cv2.INTER_LINEAR,
                          borderMode=cv2.BORDER_REFLECT)
        ff.stdin.write(frame.tobytes())
    ff.stdin.close()
    sys.exit(ff.wait())


if __name__ == "__main__":
    main()
