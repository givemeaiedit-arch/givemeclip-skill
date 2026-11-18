"""Fast Thai transcript: faster-whisper BatchedInferencePipeline on GPU (whole file, one pass).
usage: fw_batch.py <audio.wav> <out.json> [--model large-v3] [--batch 16]
Writes <out.json> (list of {start,end,text,words}) and <out.json>.txt (readable, written as it goes)."""
import sys, json, time, argparse
from faster_whisper import WhisperModel, BatchedInferencePipeline

ap = argparse.ArgumentParser()
ap.add_argument("audio"); ap.add_argument("out")
ap.add_argument("--model", default="large-v3")
ap.add_argument("--batch", type=int, default=16)
ap.add_argument("--lang", default="th")
a = ap.parse_args()

t = time.time()
try:
    model = WhisperModel(a.model, device="cuda", compute_type="float16")
except Exception as e:                                # no NVIDIA GPU / CUDA libs: slower, same output format
    print("CUDA not available for faster-whisper (", e, ") -> CPU int8", flush=True)
    model = WhisperModel(a.model, device="cpu", compute_type="int8")
pipe = BatchedInferencePipeline(model=model)
segs, info = pipe.transcribe(a.audio, language=a.lang, batch_size=a.batch, word_timestamps=True)
out = []
with open(a.out + ".txt", "w", encoding="utf-8") as f:
    for s in segs:
        words = [{"start": round(w.start, 2), "end": round(w.end, 2), "word": w.word, "probability": round(w.probability, 3)}
                 for w in (s.words or [])]
        out.append({"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip(), "words": words})
        f.write(f"{s.start:7.1f}-{s.end:7.1f}  {s.text.strip()}\n"); f.flush()
json.dump(out, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("done", len(out), "segments in", round(time.time() - t), "s")
