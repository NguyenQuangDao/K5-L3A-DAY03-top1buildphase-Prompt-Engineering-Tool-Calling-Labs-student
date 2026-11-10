# Báo cáo cá nhân — NguyenVuThanhLong-2A202603635

## 1. Thông tin thành viên

- Họ tên: Nguyễn Vũ Thành Long
- MSSV: 2A202603635
- Email: longnvthe181660@fpt.edu.vn
- GitHub: `nvl191`
- Vai trò: Thành viên 1 — Prompt & Eval Lead; có thực hiện bonus so sánh model local qua Ollama

## 2. Phần việc phụ trách

- Tối ưu prompt qua 4 vòng (`v0` → `v3`): chọn đúng tool, truyền đúng tham số, hỏi lại khi thiếu thông tin (`clarify`), không gọi tool khi ngoài phạm vi.
- Cập nhật mô tả tool trong `artifacts/tools.yaml`.
- Viết 10 eval case nhóm (5 single-turn, 5 multi-turn) trong `data/eval_group.json`.
- Duy trì nhật ký thực nghiệm `artifacts/version_log.csv`.
- Bonus: chạy và so sánh model local qua Ollama (`qwen2.5:7b`, `llama3.2:3b`) trên base suite.

## 3. Đóng góp cụ thể

**Tối ưu prompt qua các version (base suite, 20 case, `gpt-4o-mini`):**

| Version | Thay đổi chính | case_accuracy |
|---|---|---:|
| `v0` | Baseline starter (prompt có chỉ dẫn xấu) | 0.65 |
| `v1` | Gỡ chỉ dẫn xấu; thêm quy tắc `clarify` / xác nhận trước `send` / không gọi tool khi ngoài phạm vi | 0.90 |
| `v2` | Chuẩn hóa routing và mô tả tool trong `tools.yaml` | 0.85 |
| `v3` | Cập nhật mô tả tool, chỉnh prompt theo lỗi còn lại | 0.90 |

Mỗi vòng thay đổi một nhóm vấn đề chính để có thể đối chiếu kết quả giữa các version. Group suite v3 đạt **9/10**.

**Vì sao v2 giảm điểm (3 case fail trong run v2):**

| Case | Mismatch |
|---|---|
| `R12_confirm_before_send` | Gọi `clarify(response_type="text")` để hỏi nội dung thay vì hỏi xác nhận `yes_no` |
| `M02_carryover_timeframe` | Gọi thừa `social_search` ngoài `lookup` |
| `M06_switch_tool` | Gọi thừa `social_search` sau khi người dùng đổi sang web |

Đây là các mismatch ghi nhận trong run v2; chỉ một lần chạy chưa đủ chứng minh thay đổi `tools.yaml` là nguyên nhân duy nhất của mức giảm 0.05.

**Eval case nhóm (`data/eval_group.json`):** 10 case tự viết (5 single-turn, 5 multi-turn). Kết quả group v3: 9/10; case còn fail là `G08_multiturn_correct_limit` (thiếu `sort="stars"`).

**Các lỗi còn mở ở v3 (ghi nhận, chưa xem là đã sửa):**

| Case | Triệu chứng |
|---|---|
| `R12_confirm_before_send` | Model hỏi xin nội dung bản tin bằng `clarify(response_type="text")`, trong khi yêu cầu đang cần xác nhận gửi nên expected là `clarify(response_type="yes_no")` |
| `M06_switch_tool` | Sau khi người dùng chuyển từ Twitter sang web, model gọi đúng `lookup` nhưng vẫn gọi thêm `social_search` theo ngữ cảnh cũ |
| `G08_multiturn_correct_limit` | Thiếu `sort="stars"` sau khi người dùng sửa tham số |

**Bonus — Small Local Model (Ollama, base suite):**

| Model | Kết quả | case_accuracy |
|---|---|---:|
| `qwen2.5:7b` | 16/20 | 0.80 |
| `llama3.2:3b` | 5/20 | 0.25 |

Lỗi tập trung ở clarify/confirmation, định tuyến tool và chuẩn hóa tham số. Chi tiết ở REPORT B7.

## 4. Bằng chứng

- File/commit/PR:
  - Commit: `6bc6dd8512c2097817c50bf3f52d07ba1580fd6c` (`update member 1`, nhánh `long-branch`)
  - Code/dữ liệu: `artifacts/system_prompt.md`, `artifacts/tools.yaml`, `artifacts/version_log.csv`, `data/eval_group.json` (xem B1–B3)
  - Run: các file JSON của `v0`–`v3` (base và group) và các run Ollama trong `starter_v0/runs/`; artifact/hash từng version ghi trong `version_log.csv`

## 5. Tự đánh giá

- Hoàn tất bốn vòng có log và run tương ứng, cùng 10 case nhóm và bonus Ollama với hai model.
- Điểm mạnh: mỗi vòng chỉ đổi một nhóm chính nên đối chiếu được kết quả; các vấn đề chưa khắc phục được ghi rõ thay vì xem là đã sửa.
- Hạn chế: còn 3 vấn đề mở (`R12_confirm_before_send`, `M06_switch_tool`, `G08_multiturn_correct_limit`); v2 giảm 0.05 so với v1; eval chạy trên một model cloud nên chưa kiểm chứng chéo.
- Hướng tiếp theo: làm rõ thứ tự xác nhận khi `send`, ưu tiên tuyệt đối nguồn được chọn ở lượt mới nhất và giữ lại tham số không bị người dùng sửa; sau đó chạy lại eval để đo tác động.