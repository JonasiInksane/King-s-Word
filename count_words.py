import re
from pathlib import Path

base = Path(r"c:\Users\jonas\Programming\Story\Story\chapters")

def word_count(path):
    text = path.read_text(encoding="utf-8")
    return len(re.findall(r"\b\w+\b", text))

pairs = []
for n in range(20, 26):
    orig = base / f"chapter-{n:02d}.md"
    alt = base / f"chapter-{n:02d}-alt-propulsion.md"
    pairs.append((orig, alt))

print(f"{'Filename':<45} {'Words':>8}")
print("-" * 55)
for orig, alt in pairs:
    for p in (orig, alt):
        wc = word_count(p) if p.exists() else None
        label = str(wc) if wc is not None else "MISSING"
        print(f"{p.name:<45} {label:>8}")

print()
print("Pair comparison (% diff: alt vs original, positive = alt longer)")
print(f"{'Chapter':<8} {'Original':>10} {'Alt':>10} {'Diff':>10} {'% Diff':>10}")
print("-" * 50)
for orig, alt in pairs:
    o_w = word_count(orig) if orig.exists() else 0
    a_w = word_count(alt) if alt.exists() else 0
    diff = a_w - o_w
    pct = (diff / o_w * 100) if o_w else float("nan")
    ch = orig.stem.replace("chapter-", "")
    print(f"{ch:<8} {o_w:>10} {a_w:>10} {diff:>+10} {pct:>+9.2f}%")
