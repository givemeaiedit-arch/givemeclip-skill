# -*- coding: utf-8 -*-
"""Thai mark check: catches text that will draw vowels / tone marks on top of each other.

    python3 thai_check.py <file or dir> ... [--fix]

1. Typing order (in the text itself), per Thai cluster:
   - tone mark (่ ้ ๊ ๋) or ์ typed BEFORE an upper/lower vowel (ั ิ ี ึ ื ุ ู ็)  -> fix: vowel first, then tone
   - ำ typed BEFORE the tone mark (นำ้ instead of น้ำ)                       -> fix: tone first, then ำ
   - two tone marks / two upper vowels in one cluster, ็ with a tone mark, a mark with no consonant under it
2. Render method (in .py .sh .bat .ps1 .ass .html .js files that carry Thai):
   - ffmpeg drawtext (no Thai shaping), the plain subtitles= filter, ass= without shaping=complex,
     PIL ImageFont without the RAQM layout engine, cv2.putText (no Thai at all)
--fix rewrites rule-1 order errors in place (rule-2 findings need a human). Exit 1 when anything is found."""
import os, re, sys

TONE = "่้๊๋"                     # ่ ้ ๊ ๋
THANTHAKHAT = "์"                                # ์
UPPER = "ัิีึื็"        # ั ิ ี ึ ื ็
LOWER = "ฺุู"                          # ุ ู ฺ
VOWEL = UPPER + LOWER
SARA_AM = "ำ"                                    # ำ
NIKHAHIT = "ํ"                                   # ํ
MARKS = TONE + THANTHAKHAT + VOWEL + NIKHAHIT
CONS = "".join(chr(c) for c in range(0x0E01, 0x0E2F))  # ก..ฮ
EXT = (".py", ".sh", ".bat", ".ps1", ".ass", ".ssa", ".srt", ".vtt", ".html", ".htm", ".js", ".json", ".txt", ".md", ".css")
SKIP_DIRS = {"node_modules", ".git", "snaps", "frames", "__pycache__"}
THAI = re.compile("[฀-๿]")


def fix_text(s):
    """reorder marks inside each cluster: vowel, then tone / ์, then ำ"""
    prev = None
    while prev != s:
        prev = s
        s = re.sub(f"([{TONE}{THANTHAKHAT}])([{VOWEL}])", r"\2\1", s)
        s = re.sub(f"({SARA_AM})([{TONE}])", r"\2\1", s)
    return s


def order_errors(line):
    errs = []
    for m in re.finditer(f"[{TONE}{THANTHAKHAT}][{VOWEL}]", line):
        errs.append((m.start(), "tone/์ typed before the vowel", m.group()))
    for m in re.finditer(f"{SARA_AM}[{TONE}]", line):
        errs.append((m.start(), "ำ typed before the tone mark", m.group()))
    for m in re.finditer(f"[{TONE}][{TONE}]|[{UPPER}][{UPPER}]|[{LOWER}][{LOWER}]", line):
        errs.append((m.start(), "two marks of the same row stacked", m.group()))
    for m in re.finditer(f"็[{TONE}]|[{TONE}]็", line):
        errs.append((m.start(), "็ with a tone mark", m.group()))
    for m in re.finditer(f"(?<![{CONS}{MARKS}{SARA_AM}])[{MARKS}]", line):
        errs.append((m.start(), "mark with no consonant under it", m.group()))
    return errs


METHOD = [
    (re.compile(r"drawtext\s*="), "ffmpeg drawtext has no Thai shaping: use ass=...:shaping=complex or HTML/HyperFrames"),
    (re.compile(r"(?<![\w.])subtitles\s*="), "the subtitles= filter stacks ้ on ำ: use ass=file.ass:fontsdir=...:shaping=complex"),
    (re.compile(r"cv2\.putText"), "cv2.putText cannot draw Thai: render the text in HTML or PIL+RAQM"),
]


def method_errors(text, path):
    errs = []
    for i, line in enumerate(text.splitlines(), 1):
        for rx, why in METHOD:
            if rx.search(line):
                errs.append((i, why))
        if re.search(r"""(?:^|[\s"',;\]])ass=\S""", line) and "shaping=complex" not in line:
            errs.append((i, "ass= filter without shaping=complex: add :shaping=complex"))
    if path.endswith(".py") and re.search(r"ImageFont\.truetype", text) and "RAQM" not in text:
        errs.append((0, "PIL ImageFont without layout_engine=ImageFont.Layout.RAQM: Thai marks will collide"))
    return errs


def files(paths):
    for p in paths:
        if os.path.isdir(p):
            for root, dirs, fs in os.walk(p):
                dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
                for f in fs:
                    if f.lower().endswith(EXT):
                        yield os.path.join(root, f)
        elif os.path.exists(p):
            yield p


def check(paths, fix=False, quiet=False):
    """-> number of findings left (after --fix)"""
    out = lambda *a: quiet or print(*a)
    n = 0
    for f in files(paths):
        try:
            text = open(f, encoding="utf-8").read()
        except (UnicodeDecodeError, OSError):
            continue
        if not THAI.search(text):
            continue
        if fix:
            new = fix_text(text)
            if new != text:
                open(f, "w", encoding="utf-8", newline="").write(new)
                out(f"  fixed mark order in {f}")
                text = new
        for i, line in enumerate(text.splitlines(), 1):
            for col, why, s in order_errors(line):
                n += 1
                ctx = line[max(0, col - 6): col + 6].strip()
                out(f"  {f}:{i}: {why}: '{ctx}' {ascii(s)}")
        if f.lower().endswith((".py", ".sh", ".bat", ".ps1", ".ass", ".ssa", ".html", ".htm", ".js")):
            for i, why in method_errors(text, f):
                n += 1
                out(f"  {f}:{i}: {why}")
    return n


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    if not a:
        print(__doc__); sys.exit(0)
    n = check(a, "--fix" in sys.argv)
    print(f"thai check: {n} finding(s)" + ("" if n else " - marks OK"))
    sys.exit(1 if n else 0)
