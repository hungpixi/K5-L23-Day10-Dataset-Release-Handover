# Checklist đề ẩn — 40 phút

> Chủ: Nguyễn Quốc Hưng (`2A202603324` · `@Soraxolo`) — P6 Hidden-test Prep.
> In ra hoặc mở sẵn file này **trước** khi giảng viên phát đề. Trong 40 phút không có thời gian đọc tài liệu.

## 0. Phải xong TRƯỚC khi nhận đề (nếu còn thiếu là mất điểm mục 1 và 2)

- [ ] `validator/validate.py` chạy sạch trên lô luyện tập **và** lô sạch (`runs/clean`).
- [ ] `tools/review_viewer.py` chạy được: `python3 tools/review_viewer.py runs/r<seed>/delivery --image <một ảnh>`.
- [ ] Mỗi người đã **tự tay** review ít nhất 5 ca ở seed luyện tập, biết `confirmed`/`rejected` ghi thế nào.
- [ ] Chia trước ai xem phần nào của hàng đợi (`--shard 1/3`, `2/3`, `3/3`).
- [ ] Biết trước ngưỡng ứng viên của nhóm (số ca tối đa xem hết trong ~20 phút).

## 1. Nhận đề (phút 0–2)

Tải `de_an.zip` ở tab **Releases** của repo đề (`VinUni-AI20k/K5-L23-Day10-Dataset-Release-Handover`) hoặc lấy từ LMS/nhóm chat, giải nén **vào thư mục gốc repo nhóm** → được thư mục `delivery/` (tên ảnh dạng `img_0001`).

```bash
unzip -q de_an.zip -d . && ls delivery | head
mkdir -p submission/de_an
```

**Không `git add delivery/`** (đã có trong `.gitignore`, đừng dùng `git add -A -f`).

## 2. Chạy validator (phút 2–5)

Ghi lỗi luật ra `rules.json` **chứ không ghi trực tiếp** vào `errors.json`, vì bước 5 sẽ gộp lại:

```bash
python3 validator/validate.py delivery --out submission/de_an/rules.json --candidates submission/de_an/candidates.json
```

- Số lỗi luật in ra màn hình: **chụp/ghi lại ngay**, dùng cho `REPORT.md`.
- `score_findings.py` **không chấm được đề ẩn** (không có đáp án trong tay nhóm). Đừng mất thời gian chạy.

## 3. Render hàng đợi xem ảnh (phút 5–8)

```bash
python3 tools/review_viewer.py delivery --candidates submission/de_an/candidates.json --out-dir runs/de_an_queue
```

Chia việc — mỗi người một shard, mở thư mục `runs/de_an_queue/` rồi xem PNG:

```bash
python3 tools/review_viewer.py delivery --candidates submission/de_an/candidates.json --out-dir runs/de_an_queue_p1 --shard 1/3
```

Nếu hàng đợi quá lớn (không xem hết trong 20 phút): lọc theo loại hoặc `--limit`, ưu tiên ca `score` cao, và **ghi lại đã bỏ bao nhiêu ca** để nói thật trong `REPORT.md`.

## 4. Xem ảnh và ghi `review_log.csv` (phút 8–28) — việc của người, không của AI

Mỗi dòng: `image,type,verdict,note`.

- `note` phải nói **thấy gì trong ảnh**, ≥ 20 ký tự, mỗi dòng viết khác nhau. Ghi "có lỗi" / "OK" chỉ được nửa điểm; chép giống nhau thì H3 FAIL.
- Ứng viên máy ghi `class_swap` chỉ là **một trong hai** khả năng. Mở ảnh rồi quyết:
  - vật đúng là cái panoptic ghi → detection sai → `class_swap`;
  - vật đúng là cái detection ghi → panoptic sai → **sửa cột `type` thành `category_swap`**.
- Hai vật cùng lớp bị gộp thành một segment → `instance_merge` (tự thêm dòng; validator hiện **không** sinh ứng viên loại này).
- Lệch tự nhiên của COCO (vật bị che, crowd, box sát nhau) → `rejected` kèm lý do. Hàng đợi không có dòng `rejected` nào là dấu hiệu nhóm đang báo thừa.
- Chỉ được ghi 5 loại gán nhãn: `class_swap`, `bbox_drift`, `missing_box`, `category_swap`, `instance_merge`. Ghi loại lỗi luật vào đây thì `merge_review.py` dừng với lỗi.

Lưu thành `submission/de_an/review_log.csv`.

## 5. Chốt `errors.json` (phút 28–31)

```bash
python3 scripts/merge_review.py --rules submission/de_an/rules.json --review submission/de_an/review_log.csv --out submission/de_an/errors.json
```

Kiểm nhanh: mọi lỗi gán nhãn trong `errors.json` đều phải có một dòng `confirmed` trong `review_log.csv` — nếu không, giảng viên **bỏ** lỗi đó ra trước khi chấm.

```bash
python3 - <<'PY'
import csv, json
err = json.load(open("submission/de_an/errors.json"))["errors"]
SEM = {"class_swap","bbox_drift","missing_box","category_swap","instance_merge"}
rows = list(csv.DictReader(open("submission/de_an/review_log.csv", encoding="utf-8")))
ok = {(r["type"].strip(), r["image"].strip()) for r in rows
      if r["verdict"].strip() == "confirmed" and len(r["note"].strip()) >= 20}
thieu = [e for e in err if e["type"] in SEM and (e["type"], e["target"]) not in ok]
print("tổng:", len(err), "| gán nhãn thiếu dòng confirmed/ghi chú <20 ký tự:", thieu or "không")
print("số dòng rejected:", sum(1 for r in rows if r["verdict"].strip() == "rejected"))
PY
```

## 6. `trace.json` (phút 31–36)

Đọc `delivery/incoming/ticket.md` và `delivery/guideline/changelog.md`, rồi ghi `submission/de_an/trace.json`:

| Khoá | Nghĩa |
|---|---|
| `tier_a` | ảnh trong các **cảnh ticket nêu**, thuộc job có guideline **cũ** (theo `jobs.csv`), có ≥ 1 **box detection** thuộc lớp bị đổi quy tắc |
| `tier_b` | ảnh **khác** cũng thoả (job guideline cũ + có lớp đó) mà ticket chưa nêu |
| `notify` | mã `annotator` **và** `reviewer` của các job chứa ảnh tầng a và b |

Bẫy: guideline lấy theo **job** trong `jobs.csv`, **không** lấy `guideline_version` ghi ở từng ảnh (chính nó có thể là lỗi `guideline_mismatch`). `tier_a` và `notify` không được rỗng.

## 7. Nộp (phút 36–40)

```bash
git status --short                      # KHÔNG được thấy delivery/
git add submission/de_an tools validator security reporting
git commit -m "P6: de an - errors, review_log, trace"
git push origin main
```

Mỗi người tự commit phần mình đã review (rubric mục 6 đòi ≥ 2 commit/người, đúng tên và email của mình).

## Hỏng việc thường gặp trong 40 phút

| Triệu chứng | Xử lý nhanh |
|---|---|
| Validator chết vì tên ảnh lạ (`img_0001`) | Validator chỉ được đọc từ `manifest.json`, không đoán theo tên — đã kiểm trước ở lô luyện tập |
| `merge_review.py` dừng với "type không phải lỗi gán nhãn" | Trong `review_log.csv` có dòng ghi loại lỗi luật — xoá dòng đó |
| Hàng đợi 200+ ca | `--limit` + ưu tiên `score` cao, ghi rõ trong `REPORT.md` là đã bỏ bao nhiêu |
| Ảnh quá nhỏ không nhìn rõ | Viewer đã phóng tối thiểu 720px và có panel cắt vùng nghi vấn |
| Hết giờ | Thà ít lỗi mà `confirmed` chắc, hơn là báo thừa: F1 trừ báo thừa như bỏ sót |
