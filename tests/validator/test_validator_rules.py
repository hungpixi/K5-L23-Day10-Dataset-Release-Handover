import hashlib
import json
import struct
import tempfile
import unittest
import zlib
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "validator"))
import validate  # noqa: E402


def _write_rgb_png(path: Path, width: int, height: int, rgb_rows: list[bytes]) -> None:
    """Write a minimal valid 8-bit RGB PNG using stdlib zlib only."""
    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    raw = b"".join(b"\x00" + row for row in rgb_rows)
    idat = zlib.compress(raw)
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")
    path.write_bytes(png)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _make_clean_delivery(root: Path) -> Path:
    delivery = root / "delivery"
    (delivery / "images").mkdir(parents=True)
    (delivery / "labels").mkdir(parents=True)
    (delivery / "masks").mkdir(parents=True)

    img = delivery / "images" / "img_01.jpg"
    img.write_bytes(b"fake-jpg-bytes")
    lbl = delivery / "labels" / "img_01.txt"
    lbl.write_text("0 0.5 0.5 0.4 0.4\n", encoding="utf-8")
    mask = delivery / "masks" / "img_01.png"
    # 4x4 RGB PNG: 4 pixels with segment id = 1 (R=1, G=0, B=0)
    row_seg = bytes([1, 0, 0] * 2 + [0, 0, 0] * 2)
    row_bg = bytes([0, 0, 0] * 4)
    _write_rgb_png(mask, 4, 4, [row_seg, row_seg, row_bg, row_bg])

    manifest = {
        "items": {
            "img_01": {
                "image": "images/img_01.jpg",
                "image_sha256": _sha256(img),
                "label": "labels/img_01.txt",
                "label_sha256": _sha256(lbl),
                "mask": "masks/img_01.png",
                "mask_sha256": _sha256(mask),
            }
        }
    }
    (delivery / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    (delivery / "metadata.json").write_text(
        json.dumps({"items": [{"image": "img_01", "scene_id": "sc_1", "split": "train", "job_id": "j1", "guideline_version": "v1.3"}]}),
        encoding="utf-8",
    )
    (delivery / "jobs.csv").write_text("job_id,guideline\nj1,v1.3\n", encoding="utf-8")
    (delivery / "classes.txt").write_text("0 person\n1 bicycle\n", encoding="utf-8")
    panoptic = {
        "categories": [{"id": 1, "name": "person", "isthing": 1}],
        "images": [{"id": 1, "file_name": "img_01.jpg", "width": 4, "height": 4}],
        "annotations": [{"image_id": 1, "file_name": "img_01.png", "segments_info": [{"id": 1, "category_id": 1, "area": 4, "bbox": [0, 0, 2, 2]}]}],
    }
    (delivery / "panoptic.json").write_text(json.dumps(panoptic), encoding="utf-8")
    return delivery


class ValidatorUnitTest(unittest.TestCase):
    def test_clean_delivery_has_zero_rule_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            delivery = _make_clean_delivery(Path(tmp))
            self.assertEqual(validate.check_rules(delivery), [])

    def test_missing_image_and_wrong_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            delivery = _make_clean_delivery(Path(tmp))
            (delivery / "images" / "img_01.jpg").unlink()
            errs = {(e["type"], e["target"]) for e in validate.check_rules(delivery)}
            self.assertIn(("missing_image", "img_01"), errs)

        with tempfile.TemporaryDirectory() as tmp:
            delivery = _make_clean_delivery(Path(tmp))
            (delivery / "images" / "img_01.jpg").write_bytes(b"tampered")
            errs = {(e["type"], e["target"]) for e in validate.check_rules(delivery)}
            self.assertIn(("wrong_hash", "img_01"), errs)

    def test_label_rules_invalid_class_oob_and_duplicate(self):
        with tempfile.TemporaryDirectory() as tmp:
            delivery = _make_clean_delivery(Path(tmp))
            lbl = delivery / "labels" / "img_01.txt"
            lbl.write_text(
                "99 0.5 0.5 0.2 0.2\n"
                "0 0.99 0.5 0.9 0.2\n"
                "1 0.5 0.5 0.25 0.25\n"
                "1 0.5 0.5 0.25 0.25\n",
                encoding="utf-8",
            )
            types = {e["type"] for e in validate.check_rules(delivery)}
            self.assertTrue({"invalid_class", "bbox_out_of_bounds", "duplicate_box"} <= types)

    def test_metadata_and_panoptic_rules(self):
        with tempfile.TemporaryDirectory() as tmp:
            delivery = _make_clean_delivery(Path(tmp))
            (delivery / "metadata.json").write_text(
                json.dumps({
                    "items": [
                        {"image": "img_01", "scene_id": "sc_1", "split": "train", "job_id": "j1", "guideline_version": "v1.2"},
                        {"image": "img_02", "scene_id": "sc_1", "split": "val", "job_id": "j1", "guideline_version": "v1.3"},
                    ]
                }),
                encoding="utf-8",
            )
            pan = json.loads((delivery / "panoptic.json").read_text(encoding="utf-8"))
            pan["annotations"][0]["segments_info"].append({"id": 2, "category_id": 999, "area": 100, "bbox": [0, 0, 2, 2]})
            (delivery / "panoptic.json").write_text(json.dumps(pan), encoding="utf-8")
            types = {e["type"] for e in validate.check_rules(delivery)}
            self.assertTrue({"scene_leak", "guideline_mismatch", "invalid_category_id", "thing_overlap"} <= types)


if __name__ == "__main__":
    unittest.main()
