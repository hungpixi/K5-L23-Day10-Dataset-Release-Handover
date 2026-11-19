# Bảo mật khi làm việc

> Lô đang nói tới: `lab250_a16d6c28bb2d` (250 ảnh COCO val2017, seed luyện tập `9007`), bàn giao v2 cho team AI.
> Người viết: Nguyễn Quốc Hưng (`2A202603324` · `@Soraxolo`) — P6.

## 1. Ca USB: hết giờ, muốn chép lô về nhà làm tiếp

**Không chép.** Việc đúng là để lô ở chỗ nó đang nằm — máy trong phòng lab / storage của dự án — rồi
xin thêm giờ, xin quyền truy cập từ xa (VPN + tài khoản của chính mình), hoặc giao lại phần chưa xong
cho người có quyền làm tiếp. Nếu thật sự cần làm ngoài giờ thì người quản lý dự án phải mở quyền, và
việc mở quyền đó được ghi lại.

Lý do không phải là "sợ mất USB" mà là **lô rời khỏi vùng được kiểm soát thì không ai còn truy vết được
nó**: không biết đã có bao nhiêu bản, bản nào mới, ai đã mở. Với lô này, mỗi ảnh gắn với `scene_id`,
`job_id`, người gán và người kiểm trong `jobs.csv` — tức là dữ liệu có **danh tính người lao động**
kèm theo, ngoài bản thân ảnh.

Vì sao mấy cách "lách" cũng sai, dù trông vô hại:
- **Gửi email cá nhân:** dữ liệu nằm trên server của bên thứ ba, ngoài kiểm soát của dự án, giữ bản sao
  vô thời hạn và tìm kiếm được; xoá mail không xoá được bản đã được index.
- **Nhờ người khác làm hộ:** người đó không được phân công vào job này. Nhật ký sẽ ghi tên họ trong khi
  việc là của mình — lần sau truy vết một lỗi sẽ chỉ sai người, đúng kiểu `trace.json` phải chỉ ra ai
  cần sửa.
- **Chép vào máy cá nhân "chỉ xem thôi":** máy cá nhân không có kiểm soát truy cập, không mã hoá đĩa,
  có thể đang đồng bộ thư mục lên cloud riêng. Một lần chép là một bản sao mất dấu vĩnh viễn.

Chốt lại: **thà chậm tiến độ và báo chậm, hơn là tạo một bản sao không ai quản.** Chậm thì xin thêm giờ
được; bản sao rò ra ngoài thì không thu lại được.

## 2. Năm việc: được hay không

| Việc | Kết luận | Vì sao |
|---|---|---|
| Mở job được giao trên máy công ty | **Được** | Đúng người, đúng việc, đúng máy đã được kiểm soát. Đây chính là cách làm chuẩn: quyền gắn với job trong `jobs.csv`, mọi thao tác đi qua hệ thống nên có nhật ký. |
| Chụp màn hình gửi người quen | **Không** | Ảnh màn hình vẫn là dữ liệu của dự án, kể cả khi "chỉ một ảnh cho vui". Người quen không ký cam kết bảo mật, không có nghĩa vụ gì; qua Zalo/Messenger là ra ngoài vùng kiểm soát và không xoá lại được. Muốn hỏi nghiệp vụ thì hỏi trong kênh nội bộ của dự án. |
| Chép lô ra USB | **Không** | Như mục 1: tạo bản sao không quản được, không mã hoá, dễ mất. Nếu quy trình thật sự cần chuyển dữ liệu offline thì phải là thiết bị do dự án cấp, có mã hoá, có ghi nhận ai mượn và trả khi nào. |
| Dán nhãn thật lên chatbot | **Không** | Nội dung dán vào dịch vụ bên thứ ba có thể được lưu và dùng để huấn luyện; nhãn thật của dự án là tài sản khách hàng. Ở lab này ảnh COCO là dữ liệu công khai nên được dán để hỏi (và nhóm đã ghi lại trong [`submission/prompts.md`](../submission/prompts.md)), nhưng đó là **ngoại lệ của dữ liệu công khai**, không phải quy tắc chung. Với dữ liệu thật của dự án thì không. |
| Đưa tài khoản CVAT cho đồng nghiệp | **Không** | Dùng chung tài khoản là xoá sạch khả năng truy vết: nhật ký ghi một tên nhưng hai người thao tác, nên không còn biết ai sửa nhãn nào. Đồng nghiệp cần làm thì xin cấp tài khoản riêng và gán vào job — mất vài phút, và vẫn giữ được `annotator`/`reviewer` đúng người. |

Một sợi chỉ chung cho cả năm việc: **quyền đi theo job và theo người, và mọi thao tác phải để lại dấu.**
Việc nào phá vỡ một trong hai điều đó thì không được, dù động cơ có tốt.

## 3. Ca khuôn mặt: thấy mặt người rõ trong lô, guideline yêu cầu làm mờ

**Việc tôi làm:** dừng, không sửa ảnh, chụp lại bằng chứng (tên ảnh, `job_id`, `scene_id`), đặt lô ở
trạng thái **Hold** và báo người phụ trách dữ liệu / người quản lý dự án (và DPO nếu dự án có), kèm danh
sách ảnh nghi vấn để họ quyết. Ghi việc này vào lineage như một `decision` để sau còn tra lại được.

**Trạng thái lô:** **Hold** — không bàn giao, không đưa vào train, cho tới khi người phụ trách có quyết
định về cách xử lý ảnh có mặt người.

**Báo ai:** người phụ trách lô / quản lý dự án (và người gán + người kiểm của job đó theo `jobs.csv`,
để họ biết guideline đang bị áp sai từ đâu).

**Vì sao không tự làm mờ:** làm mờ là **sửa dữ liệu gốc**, và một người gán nhãn không có quyền quyết
định điều đó. Ba hậu quả cụ thể:
1. Mất bằng chứng. Sau khi làm mờ thì không ai kiểm được guideline đã bị vi phạm ở mức nào, bao nhiêu
   ảnh, từ job nào — tức là mất luôn khả năng truy vết **nguyên nhân**, chỉ còn chữa triệu chứng.
2. Phá tính nhất quán của lô. Ảnh bị làm mờ lệch phân phối so với ảnh còn lại, và hash không còn khớp
   `manifest.json` — đúng cái mà H1 phát hiện là "v1 bị sửa". Lô v1 là bản gốc, bản sửa phải là v2.
3. Sai thẩm quyền. Mức độ làm mờ, có cần xin lại sự đồng ý của người trong ảnh hay phải xoá hẳn, là
   quyết định pháp lý/hợp đồng, không phải quyết định kỹ thuật của người đang review.

**Vì sao không tự xoá ảnh:** xoá là huỷ bằng chứng và làm hụt lô (ảnh đã nằm trong `manifest.json`,
`metadata.json`, và đã thuộc một `scene_id` — xoá một ảnh làm cảnh đó rách). Nếu cuối cùng phải loại
ảnh thì loại ở **v2** kèm lý do trong `rework_queue.csv` và phần Ghi chú của `README.txt`, chứ không
xoá trong v1.

**Ví dụ thật trong lô này:** ảnh **`000000004395`** (`job_id` `J02`, `scene_id` `scene_454`, split
`train`, người gán `A03`, người kiểm `Q01`). Ảnh chụp cận một người đàn ông mặc sơ mi và cà vạt, **mặt
nhìn thẳng rõ từng nét** — mắt, mũi, miệng đều nhận ra được; một box `person` phủ gần trọn khung
(99,6 % × 99,6 % kích thước ảnh) và segment panoptic `person` chiếm 64 % diện tích. Đây là ảnh nhận
dạng được danh tính, đúng loại guideline đòi làm mờ.

Ảnh này nằm trong `manifest.json` của lô v1 và **không dính lỗi nào** trong `errors.json` của nhóm, nên
nó ở lại lô v2 — tức ví dụ này vẫn kiểm được sau khi bàn giao. Trong lô còn nhiều ảnh tương tự, ví dụ
`000000001296` (2 người, segment lớn nhất 70 % khung) và `000000016598` (58 %); đây không phải ca cá biệt
mà là **một phần đáng kể của lô**, nên việc xử lý phải theo quy trình chứ không chữa từng ảnh.

> COCO val2017 là dữ liệu công khai, dùng được cho lab. Nhưng cấu hình quyền và cách xử lý ở trên là
> cách nhóm sẽ làm với lô thật của dự án, nơi ảnh người không phải dữ liệu công khai.
