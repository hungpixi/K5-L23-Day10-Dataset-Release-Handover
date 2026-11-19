# P2 — Human Visual Review & QC (Kiểm duyệt hình ảnh & Quản lý chất lượng)

- **Người phụ trách (Owner):** Bùi Văn Thịnh (`2A202604040` · `@buivanthinhtxt-del`)
- **Vai trò trong nhóm:** Phụ trách Pha 2 (P2), nhận danh sách ứng viên từ phần đối chiếu chéo (`qc/crosscheck/`), tổ chức kiểm duyệt hình ảnh bằng mắt người và xuất tệp `review_log.csv`.

---

## 1. Mục tiêu & Chuẩn đầu ra

1. **Duyệt ứng viên:** Nhận tệp `runs/r<seed>/candidates.json` (hoặc từ `qc/crosscheck/`), mở ảnh tương ứng trong `delivery/images/` để kiểm tra bằng mắt thật.
2. **Phân biệt lỗi và lệch tự nhiên:**
   - **Xác nhận lỗi (`confirmed`):** Khi nhãn sai lệch rõ ràng so với thực tế vật thể trong ảnh.
   - **Bác bỏ nghi ngờ (`rejected`):** Khi sự không khớp bắt nguồn từ lệch tự nhiên của COCO (vật thể bị che khuất một phần, đám đông `iscrowd`, hoặc mép ảnh).
3. **Chuẩn hóa tệp `review_log.csv`:**
   - Đúng cấu trúc 4 cột bắt buộc: `image,type,verdict,note`.
   - Cột `verdict` bắt buộc là `confirmed` hoặc `rejected`.
   - Cột `note` bắt buộc **dài $\ge 20$ ký tự**, mô tả cụ thể mắt thấy gì trong ảnh, tỷ lệ ghi chú không trùng lặp $\ge 70\%$.
4. **Đồng bộ với bộ kiểm tra:** Đảm bảo 100% lỗi gán nhãn trong `errors.json` có dòng `verdict=confirmed` tương ứng, giúp bài nộp vượt qua kiểm tra mã H3 trong `scripts/check_handover.py`.

---

## 2. Bảng hướng dẫn nhận diện các loại lỗi gán nhãn

| Loại lỗi (`type`) | Dấu hiệu khi mở ảnh | Kết luận (`verdict`) | Mẫu ghi chú gợi ý (`note` $\ge 20$ ký tự) |
|---|---|---|---|
| `class_swap` | Nhãn detection (YOLO) ghi sai lớp so với vật thể thực tế trong ảnh (ví dụ: ảnh xe tải nhưng ghi car, trong khi panoptic ghi truck đúng). | `confirmed` | `"mo anh xem thay xe tai nhung nhan detection ghi car; panoptic ghi truck dung"` |
| `category_swap` | Segment panoptic gán nhầm lớp, trong khi nhãn detection (YOLO) và vật thể thực tế là đúng. | `confirmed` | `"mo anh xem thay chu cho nhung segment panoptic ghi cat; detection ghi dog dung"` |
| `bbox_drift` | Hộp detection bị lệch tâm hoặc lệch kích thước rõ rệt khỏi vật thể thật trong ảnh. | `confirmed` | `"box detection bi lech tam ro ret khoi vat the; khong bao tron doi tuong"` |
| `missing_box` | Trong ảnh có vật thể lớn rõ ràng (có segment panoptic lớn) nhưng detection thiếu hẳn box. | `confirmed` | `"thieu han box detection cho mot vat the ro rang co segment panoptic lon"` |
| `instance_merge` | Hai vật thể cùng lớp đứng cạnh nhau bị gộp chung thành một segment duy nhất trong mask panoptic. | `confirmed` | `"hai vat the cung lop dung canh nhau bi gop chung thanh mot segment duy nhat"` |
| Lệch tự nhiên | Vật thể bị che khuất (occlusion), góc khuất hoặc đám đông; nhãn gán vẫn hợp lý. | `rejected` | `"box lech nhe so voi mask do vat the bi che khuat mot phan boi vat can; nhan hop ly"` |

---

## 3. Cấu trúc tệp mẫu `qc/review/review_template.csv`

```csv
image,type,verdict,note
000000000139,class_swap,confirmed,"mo anh xem thay xe tai nhung nhan detection ghi car; panoptic ghi truck dung"
000000000285,category_swap,confirmed,"mo anh xem thay chu cho nhung segment panoptic ghi cat; detection ghi dog dung"
000000000632,bbox_drift,confirmed,"box detection bi lech tam ro ret khoi vat the; khong bao tron doi tuong"
000000000724,missing_box,confirmed,"thieu han box detection cho mot vat the ro rang co segment panoptic lon"
000000000812,instance_merge,confirmed,"hai vat the cung lop dung canh nhau bi gop chung thanh mot segment duy nhat"
000000000955,bbox_drift,rejected,"box lech nhe so voi mask do vat the bi che khuat mot phan boi vat can; nhan hop ly"
```

---

## 4. Công cụ hỗ trợ kiểm duyệt `qc/review/review_tool.py`

Nhóm có thể sử dụng kịch bản hỗ trợ để duyệt danh sách ứng viên tương tác dòng lệnh:
```bash
python qc/review/review_tool.py --candidates runs/r<seed>/candidates.json --delivery runs/r<seed>/delivery --out runs/r<seed>/review_log.csv
```
Công cụ tự động hiển thị thông tin từng ca, kiểm tra độ dài ghi chú $\ge 20$ ký tự và lưu trực tiếp vào tệp `review_log.csv`.
