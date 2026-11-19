# Dùng AI — prompt, chỗ AI sai, cách kiểm lại

> Ghi theo [RULES.md](../RULES.md) mục "Dùng AI". Mỗi người tự ghi phần mình vào bảng dưới.
> Nguyên tắc nhóm: AI được viết code và giải thích khái niệm; **không** thay việc xem ảnh —
> mọi dòng `confirmed`/`rejected` trong `review_log.csv` là kết luận của người trong nhóm.

## Nguyễn Quốc Hưng (`2A202603324`) — P6 Security, Hidden-test Prep, Reporting

Công cụ: Claude Code (Opus 5), ngày 19/11/2026. Không dán ảnh nào của lô vào công cụ AI.

### 1. Hỏi phần P6 phụ thuộc pha nào

- **Prompt:** *"Phần của tôi (P6: security.md, chuẩn bị đề ẩn, REPORT.md) có cần đợi các pha P1–P5 không?"*
- **AI trả lời ban đầu:** `security.md` chỉ cần lô v1 tồn tại, không phụ thuộc P1–P5.
- **Chỗ phải kiểm lại:** câu đó nghe hợp lý nhưng README không nói rõ H17 kiểm những gì. Đọc thẳng
  mã nguồn `scripts/check_handover.py:243–249` thì thấy điều kiện thật: ≥ 3 mục `##` mỗi mục ≥ 80 ký tự
  (sau khi bỏ khoảng trắng), mục có chữ "khuôn mặt" phải chứa chữ "hold", phải nêu một tên ảnh **có trong
  `manifest.json` của lô v1** (biến `man`), và không còn chuỗi `<<`. Vậy đúng là không cần lô v2 —
  nhưng **tên ảnh phải khớp manifest v1**, chi tiết này AI không tự nói ra.
- **Kết luận:** dùng được, sau khi đã đối chiếu mã nguồn.

### 2. Nhờ AI viết công cụ xem ảnh `tools/review_viewer.py`

- **Prompt:** *"Viết công cụ chỉ đọc delivery, vẽ box YOLO và viền segment panoptic của cùng một ảnh
  cạnh nhau, phóng to ảnh nhỏ, render cả hàng đợi candidates.json ra PNG kèm khung review_log.csv
  để trống verdict."*
- **Chỗ AI sai / phải chỉnh (tìm ra bằng cách render rồi mở ảnh ra nhìn, không tin code chạy xong là đúng):**
  1. **Cỡ chữ nhân theo hệ số phóng** — ảnh 120×80 phóng ×9 thì nhãn cao 64 px, che gần hết vật.
     Sửa: kẹp theo chiều cao panel, `max(12, min(26, sh // 28))`.
  2. **Nhãn ở mép phải bị cắt chữ** (`car · area=16…`). Sửa: kéo nhãn vào trong khung trước khi vẽ.
  3. **Panel "phóng to" cắt từ ảnh trần**, không có box lẫn viền segment — tức là vô dụng đúng chỗ
     cần nhìn kỹ nhất. Sửa: cắt từ hai ảnh đã vẽ và đặt cạnh nhau.
  4. **Văng `KeyError: 126` trên ảnh `000000009590`.** Code tra `self.cat[seg["category_id"]]["name"]`,
     mà ảnh này có segment `category_id=126` không nằm trong `categories` — chính là lỗi luật
     `invalid_category_id` mà validator vừa bắt. Nghĩa là công cụ **bỏ qua đúng những ảnh đang có lỗi**.
     Sửa: tra bằng `.get()` và in thẳng `category_id 126 (KHÔNG có trong categories)` lên nhãn.
     Lỗi này chỉ lộ ra khi chạy trên lô thật, bộ fixture tự tạo không có ca đó.
- **Cách kiểm lại:** chạy trên ảnh của lô luyện tập rồi đối chiếu bằng mắt: số box vẽ ra phải khớp
  số dòng trong `labels/<ảnh>.txt`, số segment thing vẽ ra phải khớp `segments_info` của ảnh đó
  trong `panoptic.json` (lọc `isthing`). Verdict trong `review_log_todo.csv` để **trống** — công cụ
  không tự chấm.

### 3. Lỗ hổng AI phát hiện trong validator (đã báo nhóm)

Khi đọc `validator/validate.py` (phần `cross_check_candidates`), thấy nó chỉ sinh ba loại ứng viên:
`class_swap`, `bbox_drift`, `missing_box`. Hai loại còn lại trong `scripts/metrics.py:SEMANTIC_TYPES` —
`category_swap` và `instance_merge` — **không bao giờ được sinh**.

- Hậu quả: rubric mục 2 có 3 điểm cho việc phân biệt đúng `class_swap` / `category_swap`, và F1 nhóm
  `cross_check_review` (5 điểm mục 1) sẽ mất recall ở `instance_merge`.
- **Cách kiểm lại:** `grep -n "candidates.append" validator/validate.py` → ba chỗ, đúng ba loại.
  Đối chiếu với `scripts/metrics.py` (5 loại).
- Cách đi vòng đã ghi vào `security/hidden_test_checklist.md`: người xem ảnh được **sửa cột `type`**
  từ `class_swap` sang `category_swap` khi ảnh cho thấy panoptic sai, và tự thêm dòng `instance_merge`.
  Việc sửa gốc ở `qc/crosscheck/` (issue #3).

### 4. Số liệu trong `REPORT.md`

Không nhờ AI đoán số. Mọi con số lấy từ file thật: `score_findings.py` ghi `report.md`, validator in
số ứng viên, `check_handover.py` in mã H1–H17. Prompt dùng là *"chạy các lệnh này rồi dán kết quả
nguyên văn vào REPORT.md"*, không phải *"REPORT.md nên ghi F1 khoảng bao nhiêu"*.

---

## `<Tên thành viên khác>` — `<phần phụ trách>`

- **Prompt:**
- **Chỗ AI sai:**
- **Cách kiểm lại:**
