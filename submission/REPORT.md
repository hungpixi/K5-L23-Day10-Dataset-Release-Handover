# Báo cáo nhóm <<XX>>

> Chủ bút: Nguyễn Quốc Hưng (`2A202603324` · `@Soraxolo`) — P6 Reporting.
> Mọi con số trong file này lấy từ file thật (`report.md` do `score_findings.py` ghi, màn hình của
> `validator/validate.py` và `check_handover.py`). Chỗ nào còn `<<...>>` là **chưa chạy xong**, không
> được điền bằng phỏng đoán ([RULES.md](../RULES.md) — Trung thực của số liệu).

## 1. Số liệu luyện tập

| Lô | F1 `rule_detectable` | F1 `cross_check_review` | F1 tổng | Nguồn |
|---|---|---|---|---|
| seed luyện tập **9007** (250 ảnh) | **≈ 1,0** | `<<chờ review>>` | ≈ 0,8 (mới nộp lỗi luật) | `runs/r9007/report.md` |
| seed thử **4242** (250 ảnh) | **≈ 1,0** | — | ≈ 0,8 (mới nộp lỗi luật) | `runs/r4242/report.md` |
| lô sạch, seed 5 `--no-faults` (50 ảnh pool `calib`) | **0 lỗi luật báo ra** — đúng kỳ vọng | — | — | màn hình validator |

F1 tổng ≈ 0,8 ở hai seed là do `errors.json` lúc đo **chưa có lỗi gán nhãn nào** (chưa review xong),
không phải do validator bắt sai lỗi luật. Lỗi luật đạt ≈ 1,0 trên **cả hai** seed và không báo thừa
một lỗi nào trên lô sạch — đạt mốc CP1.

- **Số lỗi luật trên seed 9007:** **14** — `wrong_hash` 2, `missing_image` 1, `invalid_class` 2,
  `bbox_out_of_bounds` 2, `duplicate_box` 1, `scene_leak` 1, `guideline_mismatch` 2,
  `invalid_category_id` 1, `thing_overlap` 2. (Seed 4242: 13, phân bố tương tự.)
- **Số ứng viên lỗi gán nhãn:** lô sạch **7 ca / 50 ảnh** (1 `class_swap`, 6 `missing_box`);
  seed 9007 **27 ca / 250 ảnh** (10 `class_swap`, 1 `bbox_drift`, 16 `missing_box`).
- **Ngưỡng đã chọn:** ghép box ↔ segment theo **IoU giữa mask và box** `PAIR_MIN_MASK_IOU = 0.5`,
  `missing_box` chỉ xét segment thing có diện tích ≥ 0,5 % diện tích ảnh (`MISSING_BOX_MIN_FRAC = 0.005`).
- **Cách chọn ngưỡng (không đọc `_private/`):** đo trên **lô sạch** — lô không gài lỗi nên mọi ứng viên
  ở đó đều là báo thừa. Hạ ngưỡng xuống thì số ứng viên trên lô sạch tăng, đó là FP thấy trước được;
  nâng ngưỡng lên thì hàng đợi nhỏ nhưng bắt đầu bỏ sót box lệch nhẹ. Ở mức đang dùng, lô sạch còn
  **7 ca / 50 ảnh = 0,14 ca mỗi ảnh**, và hàng đợi seed 9007 còn **27 ca / 250 ảnh**; chia 6 người thì
  mỗi người 4–5 ca, xem hết trong ~20 phút của đề ẩn.

## 2. Vì sao báo hết ứng viên làm F1 giảm?

Vì F1 trừ **báo thừa** đúng như trừ **bỏ sót**: `F1 = 2·TP / (2·TP + FP + FN)`. Mỗi ứng viên nhận thêm
mà không phải lỗi thật làm FP tăng 1, tức mẫu số tăng 1 trong khi TP không đổi.

Bằng chứng của nhóm là lô sạch: lô đó **không gài lỗi nào**, nên **7** ứng viên trên 50 ảnh của nó
đều là FP — tỉ lệ **0,14 ca/ảnh**. Quy tỉ lệ đó ra 250 ảnh thì **khoảng 35 ca** của một lô là lệch
tự nhiên của COCO (vật bị che, `iscrowd`, box sát nhau), trong khi hàng đợi seed 9007 chỉ có **27 ca**.
Nói cách khác: *phần lớn hàng đợi là lệch tự nhiên, không phải lỗi* — nhận hết hàng đợi là tự nộp
hàng chục FP. Đó là con số nhóm dựa vào để **không** báo thừa, và nó đo được mà không cần đáp án.

Lưu ý khi đọc hai con số này: lô sạch dùng 50 ảnh của pool `calib`, **khác** 250 ảnh luyện tập, nên
0,14 ca/ảnh là *ước lượng tỉ lệ nhiễu*, không phải số đếm trực tiếp trên lô 9007.

Tính cụ thể trên seed luyện tập: hàng đợi `<<n_queue>>` ca, trong đó người xem ảnh xác nhận
`<<n_conf>>` ca là lỗi thật.
- Nhận hết hàng đợi: TP = `<<n_conf>>`, FP = `<<n_queue − n_conf>>` ⇒ precision `<<>>`, F1 `<<>>`.
- Chỉ nhận ca đã `confirmed`: TP = `<<n_conf>>`, FP = `<<>>` ⇒ precision `<<>>`, F1 `<<>>`.

Đó cũng là lý do nhóm **giữ lại các dòng `rejected`** trong `review_log.csv`: mỗi dòng `rejected` là
một FP đã tránh được, và là bằng chứng nhóm phân biệt được lỗi gán nhãn với lệch tự nhiên.

## 3. Quyết định và lineage

- `release_id` v1: **`lab250_a16d6c28bb2d`** (seed 9007).
- QC v1: **14/250 = 5,6 %** *chỉ tính lỗi luật, chưa cộng lỗi gán nhãn đã `confirmed`* ⇒ vượt ngưỡng 2 %
  ⇒ **HOLD**. Thêm lỗi gán nhãn chỉ làm tỉ lệ cao hơn, nên quyết định không đổi. Con số cuối cùng ghi
  vào `README.txt` của v2 phải lấy từ `errors.json` **sau** khi review xong.
- Lineage: `decision HOLD` cho `lab250_a16d6c28bb2d`, rồi `release lab250_a16d6c28bb2d_v2` với `parent`
  là lô v1.
- `python3 scripts/lineage.py impact --release-id lab250_a16d6c28bb2d` → `R-021: affected=True action=review_or_retrain`.

**Vì sao `R-021` phải xem lại hoặc train lại?** `R-021` là run đã train **trên lô v1**, tức đã học từ
chính những nhãn sai mà QC vừa tìm ra. Sửa dataset ở v2 không đi ngược vào trọng số đã học: tham số của
model là kết quả của các bước cập nhật trên dữ liệu cũ, không phải một con trỏ tới dataset. Cho nên lô v2
chỉ sửa được **các run về sau**; `R-021` phải (a) đánh giá lại trên tập val sạch để xem sai lệch có đáng
kể không, hoặc (b) train lại trên v2. Để nguyên và coi như đã sửa là sai: model vẫn giữ hành vi đã học
từ nhãn lỗi, và số liệu báo cáo của `R-021` không còn tương ứng với dataset nào đang tồn tại.

## 4. Hash chứng minh gì, không chứng minh gì?

`manifest.csv` ghi `sha256` của từng file trong v2. Chạy lại `pack_release.py` cho ra đúng mã trong
`.sha256` (H8, H15).

**Chứng minh được:**
- File bên nhận **đúng từng byte** với file bên giao: không hỏng khi copy/zip, không bị cắt ngắn, không bị thay bằng file khác.
- v1 **không bị ghi đè**: hash nhãn trong `delivery/` vẫn khớp `manifest.json`, và `release_id` (12 ký tự đầu sha256 của `manifest.json` + `metadata.json`) không đổi (H1).
- Một file đã bị **sửa sau khi lập manifest** — đây là cách H8 phát hiện việc chỉnh tay nhãn trong v2.

**Không chứng minh được:**
- **Nhãn đúng.** Hash chỉ nói byte không đổi, không nói box đặt đúng vật hay class ghi đúng. Một lô sai nhãn toàn bộ vẫn có hash khớp hoàn hảo.
- **Ai làm ra file.** sha256 không có khoá, không có chữ ký; ai cũng tính lại được. Người sửa nhãn rồi lập lại `manifest.csv` thì hash lại khớp — nên hash chống **tai nạn** (hỏng, lẫn file), không chống **cố ý** sửa. Muốn chống cố ý thì cần ký (HMAC/GPG) hoặc manifest giữ ở nơi người giao không ghi được.
- **Thứ tự đúng-sai giữa hai bản.** Hai bản khác hash chỉ cho biết chúng khác nhau, không cho biết bản nào mới hoặc bản nào đúng; cái đó phải tra lineage.
- **Ảnh khớp với nhãn.** Hash tính riêng từng file, không kiểm quan hệ giữa `images/x.jpg` và `labels/x.txt`.

Vì vậy `check_handover.py` PASS chỉ nghĩa là lô v2 **đúng định dạng và nhất quán**, không nghĩa là nhãn đúng.

## 5. Truy vết

Tiêu chí nhóm dùng cho `trace.json`:

| Khoá | Tiêu chí |
|---|---|
| `tier_a` | ảnh thuộc các **cảnh ticket nêu**, nằm trong job có guideline **cũ** theo `jobs.csv`, và có ≥ 1 **box detection** thuộc lớp bị `changelog.md` đổi quy tắc |
| `tier_b` | ảnh **khác** cũng thoả hai điều kiện trên (job guideline cũ + có box lớp đó) nhưng ticket chưa nêu |
| `notify` | `annotator` **và** `reviewer` của mọi job chứa ảnh tầng a và b |

**Vì sao lấy guideline theo job, không theo ảnh?** `metadata.json` ghi `guideline_version` cho từng ảnh,
nhưng trường đó **chính là chỗ có thể sai** — `guideline_mismatch` được định nghĩa là ảnh ghi guideline
khác guideline của job nó thuộc về. Lấy theo ảnh thì mọi ảnh bị lỗi `guideline_mismatch` sẽ bị xếp sai
tầng, và tệ hơn: tiêu chí truy vết lại dựa vào đúng dữ liệu mà QC vừa kết luận là không tin được.
Guideline ghi ở đầu job là mức người gán thật sự nhận việc, nên đó là mức dùng để khoanh vùng.

Phân biệt hai tầng: **tier_a** là phần team AI đã báo — khoanh đúng để trả lời ticket; **tier_b** là phần
**cùng nguyên nhân mà chưa ai báo** — không mở ra thì lô v3 lại hỏng y như vậy. Ticket chỉ là triệu chứng
của một cảnh; nguyên nhân (job theo guideline cũ) rộng hơn cảnh đó.

## 6. Bug hoặc điểm chưa rõ trong lab (nếu có)

**Khoảng trống trong validator của nhóm (không phải bug của lab).** `validator/validate.py` ở phần
`cross_check_candidates` chỉ sinh ba loại ứng viên — `class_swap`, `bbox_drift`, `missing_box` — trong
khi `scripts/metrics.py` tính điểm trên năm loại (`SEMANTIC_TYPES`), thiếu `category_swap` và
`instance_merge`. Ảnh hưởng: mục 2 của rubric có 3 điểm cho việc phân biệt `class_swap` / `category_swap`,
và recall của nhóm `cross_check_review` mất phần `instance_merge`.

Cách nhóm xử lý:
1. Người xem ảnh được **sửa cột `type`** từ `class_swap` sang `category_swap` khi ảnh cho thấy panoptic
   là bên ghi sai (`merge_review.py` lấy loại từ `review_log.csv`, nên lỗi vẫn vào `errors.json` đúng loại).
2. Thêm dấu hiệu `instance_merge` ở `qc/crosscheck/` (issue #3): một segment thing có pixel nằm trong
   **hai** box cùng lớp.

`<<Điểm chưa rõ khác, nếu có, kèm lệnh tái hiện.>>`
