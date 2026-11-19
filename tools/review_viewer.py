#!/usr/bin/env python3
"""Công cụ xem ảnh cho Pha 2 và đề ẩn — KHÔNG phải validator.

Vẽ box detection và viền segment panoptic của cùng một ảnh cạnh nhau, phóng to
ảnh nhỏ, để người review nhìn ra bên nào ghi sai. Dùng Pillow + numpy: theo
RULES.md, Pillow chỉ được dùng cho công cụ xem ảnh của nhóm, không dùng trong
`validator/`.

Chỉ đọc thư mục delivery được truyền vào (không đọc `_private/`, `data_source/`).

Dùng:
  # một ảnh
  python3 tools/review_viewer.py runs/r3007/delivery --image 000000000139

  # cả hàng đợi ứng viên -> PNG + khung review_log.csv (verdict để TRỐNG cho người xem)
  python3 tools/review_viewer.py runs/r3007/delivery \
      --candidates runs/r3007/candidates.json --out-dir runs/r3007/review_queue

  # lọc theo loại, giới hạn số ca, chia việc cho từng người
  python3 tools/review_viewer.py runs/r3007/delivery --candidates c.json \
      --out-dir q --type class_swap --limit 20 --shard 1/3
"""

from __future__ import annotations

import argparse
import colorsys
import csv
import json
import re
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

FONT_CANDIDATES = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
)
MIN_SIDE = 720          # phóng ảnh nhỏ (COCO có ảnh ~240x320) lên tối thiểu bằng này
DET_COLOR = (54, 211, 102)      # xanh: box detection
PAD = 14
HEADER_H = 34


def load_font(size: int) -> ImageFont.FreeTypeFont:
    for path in FONT_CANDIDATES:
        if Path(path).is_file():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def stem(name: str) -> str:
    return Path(name).stem


def read_classes(path: Path) -> dict[int, str]:
    names: dict[int, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        parts = line.strip().split(maxsplit=1)
        if len(parts) == 2 and parts[0].isdigit():
            names[int(parts[0])] = parts[1].strip()
    return names


def read_yolo(path: Path) -> list[tuple[int, list[float]]]:
    rows: list[tuple[int, list[float]]] = []
    if not path.is_file():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if len(parts) != 5:
            continue
        try:
            rows.append((int(parts[0]), [float(v) for v in parts[1:]]))
        except ValueError:
            continue
    return rows


def seg_color(sid: int) -> tuple[int, int, int]:
    """Màu ổn định theo id segment, tách xa màu xanh của box detection."""
    hue = ((sid * 0.6180339887) % 1.0) * 0.85 + 0.52   # tránh dải xanh lá
    r, g, b = colorsys.hsv_to_rgb(hue % 1.0, 0.95, 1.0)
    return (int(r * 255), int(g * 255), int(b * 255))


def outline_mask(ids: np.ndarray, sid: int) -> np.ndarray:
    """Pixel biên của một segment: thuộc segment nhưng có láng giềng 4 khác id."""
    m = ids == sid
    if not m.any():
        return m
    inner = (
        np.pad(m[1:, :], ((0, 1), (0, 0)))
        & np.pad(m[:-1, :], ((1, 0), (0, 0)))
        & np.pad(m[:, 1:], ((0, 0), (0, 1)))
        & np.pad(m[:, :-1], ((0, 0), (1, 0)))
    )
    return m & ~inner


def label_box(draw: ImageDraw.ImageDraw, xy: tuple[float, float], text: str,
              color: tuple[int, int, int], font: ImageFont.FreeTypeFont,
              bounds: tuple[int, int] | None = None) -> None:
    x, y = xy
    l, t, r, b = draw.textbbox((0, 0), text, font=font)
    w, h = r - l, b - t
    y = max(0.0, y - h - 5)
    if bounds:                       # kéo nhãn vào trong khung, đừng để chữ bị cắt ở mép phải
        x = min(max(0.0, x), max(0.0, bounds[0] - w - 8))
        y = min(y, max(0.0, bounds[1] - h - 7))
    draw.rectangle([x, y, x + w + 7, y + h + 6], fill=color)
    draw.text((x + 3, y + 2), text, fill=(10, 20, 35), font=font)


def panel(base: Image.Image, title: str, font_t: ImageFont.FreeTypeFont) -> Image.Image:
    """Thêm dải tiêu đề phía trên một panel."""
    out = Image.new("RGB", (base.width, base.height + HEADER_H), (12, 26, 48))
    out.paste(base, (0, HEADER_H))
    ImageDraw.Draw(out).text((8, 8), title, fill=(236, 242, 250), font=font_t)
    return out


class Delivery:
    """Đọc lô một lần, phục vụ nhiều ảnh."""

    def __init__(self, root: Path):
        self.root = root
        self.items = json.loads((root / "manifest.json").read_text(encoding="utf-8"))["items"]
        pan = json.loads((root / "panoptic.json").read_text(encoding="utf-8"))
        self.classes = read_classes(root / "classes.txt")
        self.cat = {c["id"]: c for c in pan.get("categories", [])}
        self.ann = {stem(a["file_name"]): a for a in pan.get("annotations", [])}
        self.size = {stem(i["file_name"]): (i["width"], i["height"]) for i in pan.get("images", [])}
        meta_path = root / "metadata.json"
        self.meta = {}
        if meta_path.is_file():
            self.meta = {m["image"]: m for m in json.loads(meta_path.read_text(encoding="utf-8"))["items"]}
        self.jobs = {}
        jobs_path = root / "jobs.csv"
        if jobs_path.is_file():
            with jobs_path.open(encoding="utf-8", newline="") as f:
                self.jobs = {r["job_id"]: r for r in csv.DictReader(f)}

    def cat_name(self, cid: int) -> str:
        """Tên category; ảnh dính lỗi invalid_category_id vẫn phải xem được, không được văng KeyError."""
        cat = self.cat.get(cid)
        return cat["name"] if cat else f"category_id {cid} (KHÔNG có trong categories)"

    def render(self, name: str, zoom_to: str | None = None, focus: str | None = None) -> Image.Image:
        entry = self.items.get(name)
        if entry is None:
            raise KeyError(f"{name} không có trong manifest.json của lô")
        img_path = self.root / entry["image"]
        if not img_path.is_file():
            raise FileNotFoundError(f"thiếu file ảnh: {entry['image']} (có thể chính là lỗi missing_image)")
        photo = Image.open(img_path).convert("RGB")
        w, h = photo.size
        scale = max(1.0, MIN_SIDE / min(w, h))
        sw, sh = int(w * scale), int(h * scale)
        big = photo.resize((sw, sh), Image.LANCZOS)
        # cỡ chữ theo chiều cao panel, có trần: ảnh phóng x9 mà nhân chữ theo scale thì nhãn che hết vật
        font = load_font(max(12, min(26, sh // 28)))
        font_t = load_font(19)

        # --- panel trái: box detection ---
        det = big.copy()
        d = ImageDraw.Draw(det)
        boxes: list[tuple[int, tuple[float, float, float, float]]] = []
        for cls, (xc, yc, bw, bh) in read_yolo(self.root / entry["label"]):
            x1, y1 = (xc - bw / 2) * sw, (yc - bh / 2) * sh
            x2, y2 = (xc + bw / 2) * sw, (yc + bh / 2) * sh
            boxes.append((cls, (x1, y1, x2, y2)))
            d.rectangle([x1, y1, x2, y2], outline=DET_COLOR, width=max(2, int(scale)))
            label_box(d, (x1, y1), f"{self.classes.get(cls, f'class {cls}')} ({cls})", DET_COLOR, font, (sw, sh))
        det_plain = big.copy()          # chỉ box, không chữ — dùng cho panel phóng to
        dpl = ImageDraw.Draw(det_plain)
        for _, (x1, y1, x2, y2) in boxes:
            dpl.rectangle([x1, y1, x2, y2], outline=DET_COLOR, width=max(2, int(scale)))

        # --- panel phải: viền segment panoptic ---
        pano = pano_plain = big.copy()
        ann = self.ann.get(name)
        segs: list[tuple[int, dict]] = []
        if ann and entry.get("mask") and (self.root / entry["mask"]).is_file():
            rgb = np.asarray(Image.open(self.root / entry["mask"]).convert("RGB")).astype(np.int64)
            ids = rgb[:, :, 0] + rgb[:, :, 1] * 256 + rgb[:, :, 2] * 65536
            over = np.asarray(pano).copy()
            for seg in ann.get("segments_info", []):
                if not self.cat.get(seg["category_id"], {}).get("isthing", 1):
                    continue        # chỉ vẽ vật đếm được (thing); nền (stuff) để yên
                segs.append((seg["id"], seg))
                edge = outline_mask(ids, seg["id"])
                if not edge.any():
                    continue
                ys, xs = np.nonzero(edge)
                ys = np.clip((ys * scale).astype(int), 0, sh - 1)
                xs = np.clip((xs * scale).astype(int), 0, sw - 1)
                col = seg_color(seg["id"])
                for dy in range(max(1, int(scale))):
                    for dx in range(max(1, int(scale))):
                        over[np.clip(ys + dy, 0, sh - 1), np.clip(xs + dx, 0, sw - 1)] = col
            pano = Image.fromarray(over)
            pano_plain = pano.copy()    # chỉ viền segment, không chữ
            dp = ImageDraw.Draw(pano)
            for sid, seg in segs:
                bx, by, bw_, bh_ = seg["bbox"]
                crowd = " [crowd]" if seg.get("iscrowd") else ""
                label_box(dp, (bx * scale, by * scale),
                          f"{self.cat_name(seg['category_id'])}{crowd} · area={seg['area']}",
                          seg_color(sid), font, (sw, sh))

        # --- ghép hai panel + dải thông tin ---
        m = self.meta.get(name, {})
        job = self.jobs.get(m.get("job_id", ""), {})
        info = (f"{name}  |  {w}x{h}px (phóng x{scale:.1f})  |  scene={m.get('scene_id', '?')} "
                f"split={m.get('split', '?')} job={m.get('job_id', '?')} "
                f"guideline ảnh={m.get('guideline_version', '?')} / job={job.get('guideline', '?')}  |  "
                f"{len(boxes)} box detection vs {len(segs)} segment thing")
        left = panel(det, f"DETECTION (YOLO) — {len(boxes)} box", font_t)
        right = panel(pano, f"PANOPTIC (mask) — {len(segs)} segment thing", font_t)
        canvas = Image.new("RGB", (left.width + right.width + PAD * 3,
                                   left.height + PAD * 2 + 30), (12, 26, 48))
        canvas.paste(left, (PAD, PAD))
        canvas.paste(right, (PAD * 2 + left.width, PAD))
        ImageDraw.Draw(canvas).text((PAD, left.height + PAD + 7), info,
                                    fill=(190, 205, 225), font=load_font(17))

        if zoom_to:
            crop = self.zoom(det_plain, pano_plain, boxes, segs, scale, focus)
            if crop is not None:
                strip = panel(crop, f"PHÓNG TO vùng nghi vấn ({zoom_to})", font_t)
                out = Image.new("RGB", (max(canvas.width, strip.width + PAD * 2),
                                        canvas.height + strip.height + PAD), (12, 26, 48))
                out.paste(canvas, (0, 0))
                out.paste(strip, (PAD, canvas.height))
                canvas = out
        return canvas

    def zoom(self, det: Image.Image, pano: Image.Image, boxes, segs, scale: float,
             focus: str | None = None) -> Image.Image | None:
        """Cắt vùng nghi vấn ở CẢ HAI panel rồi phóng to thêm.

        Cắt từ ảnh đã vẽ chứ không từ ảnh trần: panel phóng to mà không có box và
        viền segment thì không giúp người xem quyết được bên nào ghi sai.

        `focus` là tên lớp lấy từ `evidence` của ứng viên. Có nó thì chỉ cắt quanh
        vật đang bị nghi, thay vì bao cả ảnh — ảnh COCO 15 box mà cắt theo tất cả
        thì panel phóng to bằng đúng ảnh gốc, chẳng để làm gì.
        """
        xs: list[float] = []
        ys: list[float] = []
        for cls, (x1, y1, x2, y2) in boxes:
            if focus and self.classes.get(cls, "") != focus:
                continue
            xs += [x1, x2]
            ys += [y1, y2]
        for _, seg in segs:
            if focus and self.cat_name(seg["category_id"]) != focus:
                continue
            bx, by, bw_, bh_ = seg["bbox"]
            xs += [bx * scale, (bx + bw_) * scale]
            ys += [by * scale, (by + bh_) * scale]
        if not xs and focus:                       # không tìm thấy lớp đó: lùi về cắt toàn ảnh
            return self.zoom(det, pano, boxes, segs, scale, None)
        if not xs:
            return None
        pad = 24
        x1, y1 = max(0, int(min(xs) - pad)), max(0, int(min(ys) - pad))
        x2, y2 = min(det.width, int(max(xs) + pad)), min(det.height, int(max(ys) + pad))
        if x2 - x1 < 8 or y2 - y1 < 8:
            return None
        f = min(6.0, max(1.0, 760 / max(1, x2 - x1)))
        crops = [im.crop((x1, y1, x2, y2)).resize(
            (int((x2 - x1) * f), int((y2 - y1) * f)), Image.LANCZOS) for im in (det, pano)]
        out = Image.new("RGB", (crops[0].width * 2 + PAD, crops[0].height), (12, 26, 48))
        out.paste(crops[0], (0, 0))
        out.paste(crops[1], (crops[0].width + PAD, 0))
        return out


def focus_class(cand: dict) -> str | None:
    """Lấy tên lớp đang bị nghi từ `evidence` để panel phóng to cắt đúng vật.

    Khớp với ba dạng evidence validator sinh ra:
      class_swap   "box=dog, segment=person"
      bbox_drift   "lớp carrot, IoU box/segment thấp"
      missing_box  "segment book lớn không có box"
    """
    ev = cand.get("evidence", "")
    for pattern in (r"box=([^,]+),", r"lớp ([^,]+),", r"segment (.+?) lớn không có box"):
        m = re.search(pattern, ev)
        if m and m.group(1).strip():
            return m.group(1).strip()
    return None


def shard_filter(cases: list[dict], spec: str | None) -> list[dict]:
    if not spec:
        return cases
    i, n = (int(x) for x in spec.split("/"))
    return [c for k, c in enumerate(cases) if k % n == (i - 1) % n]


def main() -> int:
    ap = argparse.ArgumentParser(description="Xem ảnh: box detection vs segment panoptic")
    ap.add_argument("delivery", help="thư mục delivery của lô")
    ap.add_argument("--image", help="xem một ảnh (tên không đuôi)")
    ap.add_argument("--candidates", help="candidates.json: render cả hàng đợi")
    ap.add_argument("--out", help="file PNG ra (chế độ --image)")
    ap.add_argument("--out-dir", help="thư mục ra (chế độ --candidates)")
    ap.add_argument("--type", action="append", help="chỉ lấy loại ứng viên này (lặp được)")
    ap.add_argument("--limit", type=int, help="giới hạn số ca")
    ap.add_argument("--shard", help="chia việc, ví dụ 2/3 = người thứ 2 trong 3 người")
    ap.add_argument("--no-zoom", action="store_true", help="bỏ panel phóng to")
    args = ap.parse_args()

    delivery = Path(args.delivery)
    dv = Delivery(delivery)

    if args.image:
        out = Path(args.out or f"{args.image}_review.png")
        img = dv.render(args.image, None if args.no_zoom else "xem ảnh")
        out.parent.mkdir(parents=True, exist_ok=True)
        img.save(out)
        print(f"-> {out}")
        return 0

    if not args.candidates:
        ap.error("cần --image hoặc --candidates")
    out_dir = Path(args.out_dir or "review_queue")
    out_dir.mkdir(parents=True, exist_ok=True)
    cases = json.loads(Path(args.candidates).read_text(encoding="utf-8"))["candidates"]
    if args.type:
        keep = set(args.type)
        cases = [c for c in cases if c["type"] in keep]
    cases.sort(key=lambda c: (-float(c.get("score", 0)), c["type"], c["target"]))
    cases = shard_filter(cases, args.shard)
    if args.limit:
        cases = cases[: args.limit]

    rows = []
    for k, c in enumerate(cases, 1):
        name, kind = c["target"], c["type"]
        png = out_dir / f"{k:03d}_{kind}_{name}.png"
        try:
            dv.render(name, None if args.no_zoom else kind, focus_class(c)).save(png)
        except (KeyError, FileNotFoundError, OSError) as exc:
            print(f"[bỏ qua] {name}: {exc}")
            continue
        rows.append({"image": name, "type": kind, "verdict": "", "note": "",
                     "_png": png.name, "_evidence": c.get("evidence", "")})
        print(f"[{k}/{len(cases)}] {png.name}")

    todo = out_dir / "review_log_todo.csv"
    with todo.open("w", encoding="utf-8", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["image", "type", "verdict", "note"])
        for r in rows:
            wr.writerow([r["image"], r["type"], "", ""])
    (out_dir / "queue.md").write_text(
        "# Hàng đợi review\n\n"
        "Mở PNG, nhìn vật, rồi điền `verdict` (`confirmed`/`rejected`) và `note` "
        "(**thấy gì** trong ảnh, ≥ 20 ký tự) vào `review_log_todo.csv`.\n\n"
        "| # | ảnh | loại | dấu hiệu máy nêu | PNG |\n|---|---|---|---|---|\n"
        + "".join(f"| {k} | `{r['image']}` | {r['type']} | {r['_evidence']} | [{r['_png']}]({r['_png']}) |\n"
                 for k, r in enumerate(rows, 1)),
        encoding="utf-8")
    print(f"\n{len(rows)} ca -> {out_dir}/  (khung: {todo.name}, mục lục: queue.md)")
    print("verdict để TRỐNG: người trong nhóm phải mở ảnh rồi tự điền (RULES.md).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
