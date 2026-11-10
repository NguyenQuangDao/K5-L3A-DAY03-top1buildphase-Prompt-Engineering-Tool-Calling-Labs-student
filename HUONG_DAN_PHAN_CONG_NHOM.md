# HƯỚNG DẪN CHI TIẾT PHÂN CHIA CÔNG VIỆC NHÓM 3 NGƯỜI
## DAY 03 LAB: RESEARCH AGENT TOOL EVAL & EVIDENCE-DRIVEN OPTIMIZATION

Tài liệu này được thiết kế để từng thành viên trong nhóm 3 người có thể làm việc độc lập, song song, không bị xung đột mã nguồn (merge conflict), và bám sát timeline buổi Lab từ lúc bắt đầu cho đến khi nộp bài.

---

## 🗺️ TỔNG QUAN PHÂN CHIA VAI TRÒ & PHẠM VI FILE

| Thành viên | Vai trò chính | File phụ trách độc quyền | Mục tiêu cốt lõi |
| :--- | :--- | :--- | :--- |
| **Thành viên 1** | **Prompt & Eval Lead** | • `artifacts/system_prompt.md`<br>• `artifacts/tools.yaml`<br>• `artifacts/version_log.csv`<br>• `data/eval_group.json` | Tối ưu routing & args qua 3 vòng (`v0` → `v3`), viết 10 eval cases, ghi log thực nghiệm chuẩn xác. |
| **Thành viên 2** | **Tool & Testing Engineer** | • `tools/<ten_tool>/tool.py`<br>• `tools/<ten_tool>/TOOL.md`<br>• `tools/__init__.py`<br>• `tests/test_tools_todo.py` | Tạo tool mới (hướng tới >3 tools để lấy Bonus), giải quyết toàn bộ `pytest` (`0 failed, 0 skipped`). |
| **Thành viên 3** | **UI, Live Demo & Report Lead**| • `app.py` (Streamlit)<br>• `artifacts/REPORT.md`<br>• `artifacts/poster.html`<br>• `transcripts/*.json` | Dựng UI có hiển thị Tool Trace, mở link `cloudflared`, hoàn thiện Phần A trước 16:30 và Phần B trước khi nộp. |

---

## ⏰ LỊCH TRÌNH THEO CHECKPOINT (MILESTONES)

```
[14:30 - 15:00] ── Setup môi trường + Baseline v0 + Dựng khung Streamlit
[15:00 - 15:30] ── Chạy v1 (sửa prompt xấu) + Code Tool mới 1 + Khung Report A
[15:30 - 16:00] ── Chạy v2 + Hoàn thành test_tools_todo.py + Viết 10 eval cases
[16:00 - 16:30] ── CHỐT PHẦN A + Mở link Cloudflare Tunnel + Chuẩn bị Showdown
[16:30 - 17:00] ── DEMO & SHOWDOWN VỚI CÁC NHÓM KHÁC
[17:00 - 17:30] ── Chạy v3 + Bonus (Ollama local / Tools) + Hoàn thiện REPORT Phần B
```

---

## 👤 CHI TIẾT NHIỆM VỤ THÀNH VIÊN 1: PROMPT & EVAL LEAD

### 1. Trọng trách
- Chịu trách nhiệm về chất lượng quyết định của Model: Chọn đúng tool (`tool_routing_accuracy`), truyền đúng tham số (`argument_accuracy`), hỏi lại khi thiếu thông tin (`clarify`), từ chối khi ngoài phạm vi (`out_of_scope`).
- Quản lý nhật ký thực nghiệm `artifacts/version_log.csv`.

### 2. Các bước thực hiện từng bước

#### Bước 1: Setup & Chạy Baseline `v0` (Trước 15:00)
1. Di chuyển vào thư mục làm việc:
   ```bash
   cd starter_v0
   source .venv/bin/activate
   ```
2. Chạy preflight kiểm tra kết nối model:
   ```bash
   python scripts/preflight_provider.py --provider openrouter
   ```
3. Chạy baseline `v0`:
   ```bash
   python run_eval.py --provider openrouter --version v0 --suite base --eval-cases data/eval_base.json
   ```
4. Đọc file kết quả trong `runs/` (ví dụ `runs/v0_base_*.json`). Xem các chỉ số:
   - `summary.case_accuracy`
   - `summary.tool_routing_accuracy`
   - `summary.argument_accuracy`
   - Các case FAIL trong `results[*].result.failures` và `observed_mismatch`.

#### Bước 2: Tối ưu Version 1 (`v1`) - Loại bỏ bad prompt (15:00 - 15:30)
- **Vấn đề của `v0`**: File `artifacts/system_prompt.md` ban đầu chứa các chỉ dẫn xấu có chủ đích:
  - *"Whenever something is missing... do not ask them back — just make a sensible guess"* -> Khiến agent không bao giờ gọi `clarify`.
  - *"When the user wants to send... just go ahead and do it"* -> Khiến agent vi phạm guardrail của `send`.
  - *"Always finish the request in a single step"* -> Phá hỏng các case đa bước/đa tool.
- **Hành động**:
  1. Mở `artifacts/system_prompt.md`: Xóa toàn bộ các chỉ dẫn xấu trên.
  2. Viết lại quy tắc cốt lõi:
     - Nếu thiếu thông tin thiết yếu (tên người dùng, URL cụ thể, từ khóa chính) -> **Bắt buộc gọi `clarify`**, không được tự đoán.
     - Với hành động gửi tin / publish (`send`) -> Bắt buộc hỏi xác nhận từ người dùng (`clarify` dạng `yes_no`) trước khi gọi `send(confirmed=True)`.
     - Với câu hỏi ngoài phạm vi (code python, toán học) hoặc câu hỏi chào hỏi xã giao -> Không gọi tool nào (`no_tool`).
  3. Chạy eval cho `v1`:
     ```bash
     python run_eval.py --provider openrouter --version v1 --suite base --eval-cases data/eval_base.json
     ```
  4. Điền 1 dòng vào `artifacts/version_log.csv`.

#### Bước 3: Tối ưu Version 2 (`v2`) - Chuẩn hóa Routing & Tool Description (15:30 - 16:00)
- **Hành động trong `artifacts/tools.yaml` & `artifacts/system_prompt.md`**:
  1. Viết rõ quy tắc phân biệt tool:
     - Tin CỦA một người (có tên/handle) -> Dùng `timeline` (handle không có ký tự `@`).
     - Tìm kiếm bài viết/chủ đề trên mạng xã hội -> Dùng `social_search` (hỗ trợ `search_type: Top` hoặc `Latest`).
     - Tin tức chung trên web -> Dùng `lookup` (chú ý `topic: news` nếu là tin tức, `timeframe: day|week|month|year`).
     - Có sẵn URL cụ thể -> Dùng `fetch` để đọc nội dung.
  2. Định nghĩa ánh xạ tên người nổi tiếng sang Twitter handle trong `system_prompt.md` (ví dụ: Sam Altman -> `sama`, Elon Musk -> `elonmusk`, Andrej Karpathy -> `karpathy`).
  3. Chạy eval cho `v2`:
     ```bash
     python run_eval.py --provider openrouter --version v2 --suite base --eval-cases data/eval_base.json
     ```
  4. Điền `version_log.csv`.

#### Bước 4: Viết 10 Eval Cases vào `data/eval_group.json` (16:00 - 16:30)
Mở `data/eval_group.json`, thêm 10 cases (5 single-turn, 5 multi-turn) theo định dạng chuẩn:
- **5 Single-turn**:
  - 1 case test `timeline` với handle có khoảng trắng hoặc tên cần ánh xạ.
  - 1 case test `social_search` với `search_type="Top"`.
  - 1 case test `lookup` với `timeframe="month"`.
  - 1 case test `clarify` khi câu hỏi mơ hồ.
  - 1 case test gọi **Tool mới** do Thành viên 2 tạo ra.
- **5 Multi-turn (`turns: [...]`)**:
  - Test việc người dùng bổ sung thông tin sau khi agent hỏi lại.
  - Test việc người dùng đổi ý (ví dụ từ tìm web chuyển sang tìm Twitter).
  - Test việc người dùng sửa tham số (ví dụ: đổi từ 5 bài sang 10 bài).
- Kiểm tra eval nhóm:
  ```bash
  python run_eval.py --provider openrouter --version v2 --suite group --eval-cases data/eval_group.json
  ```

#### Bước 5: Chạy `v3` và Thử thách Local Model (Sau 16:30)
1. Tích hợp mô tả cho các tool mới từ Thành viên 2 vào `artifacts/tools.yaml`.
2. Chạy bản hoàn thiện `v3`:
   ```bash
   python run_eval.py --provider openrouter --version v3 --suite base --eval-cases data/eval_base.json
   python run_eval.py --provider openrouter --version v3 --suite group --eval-cases data/eval_group.json
   ```
3. *(Thử thách Local Model - Bonus)*: Nếu máy có Ollama:
   ```bash
   ollama pull qwen2.5:7b
   ollama pull llama3.2:3b
   python run_eval.py --provider ollama --model qwen2.5:7b --version v3-qwen7b --suite base --eval-cases data/eval_base.json
   python run_eval.py --provider ollama --model llama3.2:3b --version v3-llama3b --suite base --eval-cases data/eval_base.json
   ```
   Ghi nhận các lỗi đặc thù của model nhỏ (JSON lỗi, bịa tên tool, trả lời thẳng không gọi tool) vào mục B7 của `REPORT.md`.

---

## 👤 CHI TIẾT NHIỆM VỤ THÀNH VIÊN 2: TOOL & TESTING ENGINEER

### 1. Trọng trách
- Xây dựng ít nhất 1 tool mới (để đạt điểm thưởng bonus tối đa: **làm > 3 tools mới**).
- Viết unit test cho code của tool và đảm bảo `pytest` đạt **0 failed, 0 skipped**.
- Đảm bảo tính toàn vẹn của hợp đồng (`tests/test_tool_contract.py`).

### 2. Các bước thực hiện từng bước

#### Bước 1: Hoàn thành Unit Test có sẵn trong `tests/test_tools_todo.py` (Trước 15:30)
Đọc các mẫu test trong `tests/test_tools_examples.py`, sau đó thay thế toàn bộ `pytest.skip(TODO)` trong `tests/test_tools_todo.py`:
1. **`test_clarify_choice_returns_options_and_awaits_user`**:
   - Gọi hàm `ask_user(question="Chọn?", response_type="choice", options=["A", "B"])`.
   - Assert `result["awaiting_user"] is True` và `result["options"] == ["A", "B"]`.
2. **`test_format_sections_groups_items_by_section`**:
   - Truyền items có `section="A"`, `section="B"`, `section="A"`.
   - Assert markdown chứa `"## A"` và `"## B"`.
3. **`test_format_thread_numbers_items`**:
   - Chạy `template="thread"`, assert các dòng bắt đầu bằng `"1/"`, `"2/"`.
4. **`test_format_empty_items_does_not_crash`**:
   - Test với `items=[]` và `items=None`, không được văng Exception.
5. **`test_send_confirmed_posts_to_telegram`**:
   - Dùng `monkeypatch.setenv` đặt `TELEGRAM_BOT_TOKEN="mock"`, `TELEGRAM_CHAT_ID="123"`.
   - Dùng fixture `fake_http(FakeResponse({"ok": True}))`.
   - Gọi `send_telegram(text="Hello", confirmed=True)`, assert đúng request url và `status == "sent"`.
6. **`test_send_confirmed_without_env_returns_error_and_no_request`**:
   - Gọi `send_telegram(text="test", confirmed=True)` khi không có biến môi trường.
   - Assert trả về dict có `"error": "RuntimeError"` và không có HTTP request nào phát sinh.
7. **`test_lookup_without_timeframe_omits_time_range`**:
   - Mock HTTP với `fake_http`, gọi `web_search(query="test", timeframe=None)`.
   - Assert `time_range` không xuất hiện trong payload JSON gửi đi.
8. **`test_fetch_maps_firecrawl_response` & `test_fetch_truncates_markdown_to_4000_chars`**:
   - Mock Firecrawl JSON trả về, kiểm tra mapping sang `items[0]` và giới hạn độ dài ký tự 4000.
9. **`test_timeline_respects_limit_and_skips_items_without_id`** & **`test_social_search_passes_search_type`**:
   - Mock API RapidAPI, assert params `search_type` và lọc id.
10. **`test_policy_*`**:
    - Test hàm `search_company_policy` với query rỗng, lọc `policy_area`, và bóc tách `untrusted_text`.

Chạy kiểm tra thường xuyên:
```bash
pytest -v tests/test_tools_todo.py
```

#### Bước 2: Xây dựng các Tool Mới (15:30 - 16:30)
> **Mục tiêu điểm thưởng:** Tạo **>3 tool mới**. Nhóm có thể tận dụng và hoàn thiện các tool bonus có sẵn hoặc viết mới:

1. **Tool 1: `calculator` hoặc `currency_converter` (Local Tool đơn giản, cực kỳ hữu dụng)**:
   - Thư mục: `tools/calculator/`
   - File: `tool.py` (tính toán an toàn biểu thức toán học hoặc chuyển đổi tiền tệ).
   - File: `TOOL.md`: Khai báo frontmatter đầy đủ.
2. **Tool 2: `papers` (Tìm bài báo arXiv)**:
   - Đã có thư mục `tools/papers/tool.py`, kiểm tra và hoàn thiện logic.
3. **Tool 3: `paper_text` (Đọc text PDF arXiv)**:
   - Đã có thư mục `tools/paper_text/tool.py`.
4. **Tool 4: `policy` (Tra cứu chính sách nội bộ công ty)**:
   - Đã có thư mục `tools/policy/tool.py`.

#### Bước 3: Đăng ký Tool và Viết Unit Test
1. Mở `tools/__init__.py`, import hàm và đăng ký vào `TOOL_FUNCTIONS`:
   ```python
   from .calculator.tool import calculate
   TOOL_FUNCTIONS["calculator"] = calculate
   ```
2. Báo cho Thành viên 1 schema của tool để thêm vào `artifacts/tools.yaml`.
3. Mở `tests/test_tools_todo.py`, viết **ít nhất 3 tests** cho mỗi tool mới:
   - Test 1: Happy path (kết quả mong đợi).
   - Test 2: Input xấu từ model (chuỗi rỗng, số âm, sai kiểu dữ liệu).
   - Test 3: Nhánh lỗi (bắt lỗi, trả về dict `{"error": ...}` thay vì làm sập chương trình).
4. Kiểm tra hợp đồng:
   ```bash
   pytest tests/test_tool_contract.py
   pytest
   ```
   **Mục tiêu: Toàn bộ suite xanh, 0 failed, 0 skipped.**

---

## 👤 CHI TIẾT NHIỆM VỤ THÀNH VIÊN 3: UI, LIVE DEMO & REPORT LEAD

### 1. Trọng trách
- Xây dựng giao diện tương tác web (Streamlit UI).
- Expose ứng dụng ra internet qua Cloudflare Tunnel để demo trong buổi Showdown 16:30.
- Thu thập bằng chứng thực nghiệm (3 lượt transcript chat live).
- Soạn thảo và hoàn thiện tài liệu `artifacts/REPORT.md` (Phần A trước 16:30, Phần B trước khi nộp) và tạo `artifacts/poster.html`.

### 2. Các bước thực hiện từng bước

#### Bước 1: Xây dựng Streamlit UI (`app.py`) (Trước 15:30)
Tạo file `starter_v0/app.py` với các tính năng:
1. Giao diện Chatbot đa lượt (Multi-turn Chat) dùng `st.chat_message` và `st.session_state.messages`.
2. Khởi tạo `ResearchAgent` sử dụng provider OpenRouter (hoặc Ollama).
3. **Tính năng bắt buộc để ăn điểm demo**: Hiển thị rõ **Tool Call Inspector**:
   - Khi agent quyết định gọi tool, hiển thị một collapsible box (`st.status` hoặc `st.expander`):
     - Tên Tool được gọi.
     - Arguments model truyền vào.
     - Dữ liệu thô tool trả về.
     - Câu trả lời cuối cùng cho người dùng.
   - Thêm nút xác nhận nếu tool yêu cầu xác nhận (`needs_confirmation` như `send`).

Chạy thử nghiệm local:
```bash
streamlit run app.py
```

#### Bước 2: Cài đặt Cloudflare Tunnel để lấy link Public (15:30 - 16:00)
1. Cài đặt `cloudflared`:
   - macOS: `brew install cloudflared`
   - Windows: `winget install --id Cloudflare.cloudflared`
2. Khởi chạy tunnel trỏ vào cổng Streamlit (8501):
   ```bash
   cloudflared tunnel --url http://localhost:8501
   ```
3. Lệnh sẽ in ra đường link công khai dạng: `https://<random-id>.trycloudflare.com`.
4. Copy link này để sẵn sàng dán vào `REPORT.md` Phần A. Giữ terminal này chạy liên tục để không bị mất link.

#### Bước 3: Tạo Transcript Live Chat (16:00 - 16:20)
Chạy script `chat.py` (hoặc tương tác trực tiếp trên UI) để ghi lại ít nhất 3 kịch bản vào thư mục `transcripts/`:
```bash
python chat.py --provider openrouter --version v3
```
Thực hiện 3 kịch bản:
- **Kịch bản 1**: Nghiên cứu bình thường (Ví dụ: "Tìm tin tức AI hôm nay và tóm tắt").
- **Kịch bản 2**: Câu hỏi thiếu thông tin để kiểm tra `clarify` (Ví dụ: "Tóm tắt 5 tweet mới nhất" -> Agent hỏi lại của ai -> User trả lời "Của Elon Musk").
- **Kịch bản 3**: Thử nghiệm guardrail an toàn với Telegram (Ví dụ: "Đăng bản tin này lên Telegram" -> Agent hỏi xác nhận -> User trả lời "Đồng ý").

#### Bước 4: Hoàn thành REPORT.md Phần A & Poster (Trước 16:30 BẮT BUỘC)
Mở `artifacts/REPORT.md`, điền đầy đủ Phần A:
1. **A1. Agent làm được gì**: Tóm tắt 2-3 câu súc tích. Dán đường link Cloudflare Tunnel vừa tạo vào mục này.
2. **A2. Danh sách Tool**: Lập bảng gồm tên tool, công dụng, và đánh dấu tool nào nhóm tự viết thêm.
3. **A3. Câu hỏi mẫu**: Đưa ra 3-5 câu hỏi mẫu ấn tượng nhất để các nhóm khác test thử trong buổi Showdown.
4. *(Khuyến khích)* Tạo thêm file `artifacts/poster.html` hiển thị Phần A trực quan, đẹp mắt để trình chiếu trực tiếp.

#### Bước 5: Hoàn thiện REPORT.md Phần B (16:30 - 17:30)
Sau khi kết thúc phiên Showdown:
1. Lấy dữ liệu từ `artifacts/version_log.csv` và `runs/*.json` của Thành viên 1 để điền bảng **B1 (Version Evidence)** và **B2 (Failure Analysis)**.
2. Liệt kê 10 test case từ `data/eval_group.json` vào bảng **B3**.
3. Điền trích dẫn từ transcript vào bảng **B4 (Live Chat Evidence)**.
4. Tổng hợp bằng chứng unit test và bonus tool từ Thành viên 2 vào bảng **B5**.
5. Cả 3 thành viên cùng ngồi lại 10 phút để trả lời 4 câu hỏi suy ngẫm trong mục **B6 (Reflection)**.

---

## 🤝 NGUYÊN TẮC PHỐI HỢP & TRÁNH XUNG ĐỘT GIT (MERGE CONFLICT)

1. **Quy tắc sở hữu File (Strict Ownership)**:
   - Thành viên 2 KHÔNG tự tiện sửa `artifacts/tools.yaml`. Khi viết xong tool mới, Thành viên 2 gửi đoạn khai báo YAML cho Thành viên 1 copy vào.
   - Thành viên 1 KHÔNG sửa code trong `tools/` hay `tests/test_tools_todo.py`.
   - Thành viên 3 toàn quyền phụ trách `app.py`, `REPORT.md`, `poster.html`.
2. **Quy tắc đặt tên Tool**:
   - Nếu đổi tên tool hoặc thêm tool mới, phải khớp 100% giữa 3 nơi:
     1. Khóa trong `tools/__init__.py` (`TOOL_FUNCTIONS`)
     2. Khai báo `name` trong `artifacts/tools.yaml`
     3. Khai báo `expect.tool_calls[].name` trong file eval.
   - Chạy `pytest tests/test_tool_contract.py` trước mỗi lần commit.

---

## ✅ CHECKLIST KIỂM TRA TRƯỚC KHI NỘP BÀI (SUBMIT AUDIT)

Mỗi thành viên kiểm tra các hạng mục của mình trước 17:30:

- [ ] File `.env` và các API key **KHÔNG** được commit lên git.
- [ ] `artifacts/system_prompt.md` đã loại bỏ hoàn toàn các hướng dẫn xấu của starter.
- [ ] `artifacts/tools.yaml` mô tả chi tiết từng tool, nêu rõ khi nào dùng và khi nào không dùng.
- [ ] `artifacts/version_log.csv` có đủ ít nhất các phiên bản `v0`, `v1`, `v2`, `v3`.
- [ ] Có ít nhất 1 tool mới (hoặc >3 tools mới để nhận điểm thưởng bonus), có đầy đủ `TOOL.md` và đăng ký trong `tools/__init__.py`.
- [ ] `pytest tests/` chạy báo **0 failed, 0 skipped**.
- [ ] `data/eval_group.json` có đủ 10 cases tự viết (5 single turn, 5 multi turn).
- [ ] Có ít nhất 1 file transcript thực tế trong `transcripts/*.transcript.json`.
- [ ] UI Streamlit chạy được ổn định, có link demo.
- [ ] `artifacts/REPORT.md` hoàn thành đầy đủ cả Phần A và Phần B.
- [ ] Toàn bộ các file chạy eval `runs/*.json` đã được lưu lại đầy đủ làm bằng chứng.

