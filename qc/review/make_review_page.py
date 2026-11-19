"""Generate a local HTML visual-review gallery (stdlib only) for P2 candidates."""
from __future__ import annotations

import argparse
import html
import json
from pathlib import Path


def read_yolo_boxes(label_path: Path) -> list[tuple[int, float, float, float, float]]:
    if not label_path.is_file():
        return []
    boxes = []
    for line in label_path.read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if len(parts) == 5:
            try:
                boxes.append((int(parts[0]), *(float(x) for x in parts[1:])))
            except ValueError:
                pass
    return boxes


def load_classes(classes_path: Path) -> dict[int, str]:
    out: dict[int, str] = {}
    if not classes_path.is_file():
        return out
    for line in classes_path.read_text(encoding="utf-8").splitlines():
        parts = line.strip().split(maxsplit=1)
        if len(parts) == 2 and parts[0].isdigit():
            out[int(parts[0])] = parts[1].strip()
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Build local HTML gallery for P2 human visual review")
    ap.add_argument("--run", default="runs/r9007", help="run directory containing delivery/ and candidates.json")
    ap.add_argument("--out", help="output HTML path (default: <run>/review_gallery.html)")
    args = ap.parse_args()

    run_dir = Path(args.run)
    delivery = run_dir / "delivery"
    cands_path = run_dir / "candidates.json"
    if not cands_path.is_file():
        raise SystemExit(f"Missing {cands_path}")

    cands = json.loads(cands_path.read_text(encoding="utf-8")).get("candidates", [])
    classes = load_classes(delivery / "classes.txt")
    out_path = Path(args.out) if args.out else (run_dir / "review_gallery.html")

    cards = []
    for idx, c in enumerate(cands, start=1):
        stem = c["target"]
        img_rel = f"delivery/images/{stem}.jpg"
        boxes = read_yolo_boxes(delivery / "labels" / f"{stem}.txt")
        rects = []
        for cls_id, xc, yc, w, h in boxes:
            x = (xc - w / 2) * 100
            y = (yc - h / 2) * 100
            rw = w * 100
            rh = h * 100
            cname = html.escape(classes.get(cls_id, str(cls_id)))
            rects.append(
                f'<rect x="{x:.2f}%" y="{y:.2f}%" width="{rw:.2f}%" height="{rh:.2f}%" '
                f'fill="none" stroke="#ff2e63" stroke-width="2"/>'
                f'<text x="{x:.2f}%" y="{max(4.0, y):.2f}%" fill="#ff2e63" font-size="12" font-weight="bold">{cname}</text>'
            )
        cards.append(
            f'<div class="card">'
            f'<h3>#{idx} — {html.escape(stem)} <span>[{html.escape(c["type"])}]</span></h3>'
            f'<p>{html.escape(c.get("evidence", ""))}</p>'
            f'<div class="wrap"><img src="{img_rel}" alt="{html.escape(stem)}"/>'
            f'<svg viewBox="0 0 100 100" preserveAspectRatio="none">{"".join(rects)}</svg></div>'
            f'</div>'
        )

    doc = f"""<!doctype html>
<html lang="vi"><head><meta charset="utf-8"><title>Day 10 Visual Review — {html.escape(run_dir.name)}</title>
<style>
body{{font-family:system-ui,sans-serif;margin:20px;background:#f7f8fa;color:#111}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(360px,1fr));gap:16px}}
.card{{background:#fff;border:1px solid #ddd;border-radius:8px;padding:12px}}
.card h3{{margin:0 0 6px;font-size:15px}} .card span{{color:#0b57d0}}
.wrap{{position:relative;width:100%}} .wrap img{{width:100%;display:block;border-radius:4px}}
.wrap svg{{position:absolute;inset:0;width:100%;height:100%;pointer-events:none}}
</style></head><body>
<h1>P2 Visual Review ({html.escape(run_dir.name)}) — {len(cands)} candidates</h1>
<p>Xem ảnh thật và ghi <code>confirmed</code> hoặc <code>rejected</code> kèm mô tả &ge; 20 ký tự vào <code>review_log.csv</code>.</p>
<div class="grid">{"".join(cards)}</div></body></html>"""
    out_path.write_text(doc, encoding="utf-8")
    print(f"Wrote {out_path} ({len(cands)} candidates)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
