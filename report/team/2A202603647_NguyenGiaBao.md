# Báo cáo cá nhân — NguyenGiaBao-2A202603647

## 1. Thông tin thành viên

- Họ tên: Nguyễn Gia Bảo
- MSSV: 2A202603647
- Email: 26ai.baong5@vinuni.edu.vn
- GitHub: `Billy3005`
- Vai trò: Thành viên 2 — Tool & Testing Engineer; phụ trách bonus Step 7 (Small Local Model)

## 2. Phần việc phụ trách

- Viết tool mới cho agent (nhắm điểm thưởng "hơn 3 tool mới + UI").
- Viết unit test cho tool mới và hoàn thành challenge `tests/test_tools_todo.py` (0 failed, 0 skipped).
- Tìm và sửa bug trong tool có sẵn (Challenge+).
- Bonus Step 7: chạy và tối ưu agent trên model local nhỏ qua Ollama.

## 3. Đóng góp cụ thể

**Tool mới (4 tool, API miễn phí, không cần key):**

| Tool | Làm gì |
|---|---|
| `hn_search` | Tìm bài Hacker News, lọc `sort` (relevance/date) và `timeframe` (day…year) |
| `wiki` | Tóm tắt Wikipedia (en/vi) cho câu hỏi định nghĩa / kiến thức nền |
| `github_repos` | Tìm repo GitHub, lọc `language`, xếp theo sao |
| `hf_models` | Tìm model Hugging Face theo `task`, xếp theo downloads/likes/trending |

Mỗi tool có `tool.py` + `TOOL.md` đúng contract, đăng ký trong `tools/__init__.py` và `artifacts/tools.yaml` (mô tả rõ khi nào dùng / không dùng). Input xấu từ model (sai kiểu, ngoài enum, query rỗng) được chuẩn hoá bằng helper `clamp_int`, `pick_enum` trong `tools/_shared.py` hoặc trả error dict, không raise.

**Unit test — `pytest`: 121 passed, 0 failed, 0 skipped:**
- Điền hết 14 stub TODO (clarify, format, send, lookup, fetch, timeline, social_search, policy).
- 20 test cho 4 tool mới (happy path có mock HTTP, input xấu, nhánh lỗi).
- 4 test hồi quy/biên + 1 test offline cho provider Anthropic.

**Bug tìm được và sửa (mỗi bug có regression test FAIL trên code gốc, PASS sau sửa):**

| Bug | Hậu quả | Regression test |
|---|---|---|
| `send(confirmed="false")` | Chuỗi `"false"` là truthy → gửi thật lên Telegram (vượt guardrail) | `test_send_string_false_confirmation_does_not_send` |
| `format(items=["chuỗi"])` | Crash `AttributeError` thay vì trả kết quả | `test_format_string_items_from_model_are_rendered_not_crashed` |
| `timeline(limit=-1)` | `items[:-1]` → trả gần hết danh sách | `test_timeline_negative_limit_does_not_slice_from_end` |

**Khác:**
- Sửa provider Anthropic: SDK `anthropic` 2.x không nhận `temperature` (mọi lần gọi đều lỗi); đổi model mặc định sang Haiku 5.5, `max_tokens` 4096.
- Viết 7 eval case ban đầu cho tool mới (routing, args, ranh giới `hf_models` vs `lookup`).
- Xử lý môi trường: AVG antivirus chặn HTTPS làm `requests` lỗi SSL → dùng CA bundle gộp kho chứng chỉ Windows (chỉ trên máy, không commit).

**Step 7 — Small Local Model (`qwen2.5:3b`), mỗi vòng một giả thuyết:**

| Version | Thay đổi | case_accuracy |
|---|---|---:|
| `v3-qwen3b` | v3 nguyên bản | 0.55 |
| `v4-local` | chỉ giữ 7 tool lõi (giả thuyết: 14 tool gây nhiễu, model gọi nhầm `paper_text`, `hn_search`) | 0.70 |
| `v5-local` | + 5 ví dụ few-shot gọi tool (giả thuyết: model hỏi lại bằng chữ thay vì `clarify`) | 0.80 (multiturn giảm 0.83 → 0.67) |

Kết luận có bằng chứng: bớt tool không cần thiết là thay đổi rẻ và hiệu quả nhất cho model nhỏ; few-shot sửa lỗi "không gọi `clarify`" nhưng gây over-clarify ở hội thoại nhiều lượt. Chi tiết ở REPORT B7.

**Dọn repo và report:** bỏ theo dõi 8.991 file `node_modules`; tạo lại `analysis/base_runs.csv` (9 run, 200 dòng); bổ sung `version_log.csv`; viết REPORT B4 (ghi chú hash: transcript cũ thực chất dùng prompt v0; nguyên nhân CRLF trên Windows), B5 (unit test + bug), B6 (ý kiến Thành viên 2), B7.

## 4. Bằng chứng

- File/commit/PR:
  - PR #1 — tool mới + test + sửa bug: https://github.com/NguyenQuangDao/K5-L3A-DAY03-top1buildphase-Prompt-Engineering-Tool-Calling-Labs-student/pull/1 (commit `44149e3`, `31b5e0c`)
  - PR #6 — Step 7 + report: https://github.com/NguyenQuangDao/K5-L3A-DAY03-top1buildphase-Prompt-Engineering-Tool-Calling-Labs-student/pull/6 (commit `1c32178`, `04e697a`)
  - Code: `starter_v0/tools/{hn_search,wiki,github_repos,hf_models}/`, `starter_v0/tools/_shared.py`, `starter_v0/tests/test_tools_todo.py`, `starter_v0/tests/test_anthropic_provider.py`
  - Step 7: `starter_v0/artifacts/system_prompt_local.md`, `starter_v0/artifacts/tools_local.yaml`, `starter_v0/runs/v3-qwen3b_*`, `v4-local-qwen3b_*`, `v5-local-qwen3b_*`, `starter_v0/transcripts/v3_ollama_*.transcript.json`
- AI/công cụ đã dùng và cách tự kiểm tra kết quả:
  - Dùng AI coding assistant để hỗ trợ đọc code, viết tool/test và phân tích run JSON.
  - Tự kiểm tra: gọi thử 4 API thật để lấy đúng cấu trúc response trước khi code; chạy `pytest` sau mỗi thay đổi; trả code tool về bản gốc để xác nhận regression test thật sự FAIL; đối chiếu mọi số liệu trong report với `summary` của run JSON; đối chiếu hash artifact (phát hiện transcript cũ dùng prompt v0 và lỗi hash CRLF).

## 5. Tự đánh giá

- Hoàn thành đủ phần bắt buộc của vai trò (tool mới + ≥ 3 test/tool, `pytest` 0 failed/0 skipped) và các challenge (TODO test, Challenge+ sửa bug), cùng bonus "hơn 3 tool" (phần tool) và Step 7 (≥ 2 vòng tối ưu có log).
- Điểm mạnh: mọi kết luận đều có bằng chứng từ log/test; phát hiện được lỗi mà eval không bắt (bug `send`, hash version sai).
- Hạn chế: chưa chạy kiểm tra ngược `v5-local` trên model cloud (hết credit OpenRouter); transcript v3 trên model local cho kết quả kém nên không thay được bằng chứng B4; guardrail `send` vẫn chấp nhận chuỗi `"true"` (đã ghi nhận trong REPORT B5 và đề xuất cải tiến ở B6).
