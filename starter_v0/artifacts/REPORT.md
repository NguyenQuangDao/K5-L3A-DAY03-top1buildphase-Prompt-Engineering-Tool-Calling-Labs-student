# Day 03 Lab v2 Report — Research Agent

> File này gồm 2 phần, deadline khác nhau:
> - **PHẦN A — Giới thiệu agent**: ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì, thử bằng câu hỏi nào. **Xong trước 16:30** để làm tài liệu phụ trợ khi demo. Có thể làm thành poster HTML/SVG (`artifacts/poster.html` / `poster.svg`) để show cho team cùng zone.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ (v0–v3, failure, eval, chat) dựa trên log thật. **Có thể hoàn thiện sau buổi debate để nộp bài.**

## Team

- Team: Research Agent Operations Team (Day 03 Lab)
- Members:
  - Thành viên 1 — Prompt & Eval Lead (`artifacts/system_prompt.md`, `artifacts/tools.yaml`, `artifacts/version_log.csv`, `data/eval_group.json`)
  - Thành viên 2 — Tool & Testing Engineer (`tools/**`, `tools/__init__.py`, `tests/test_tools_todo.py`)
  - Thành viên 3 — UI, Live Demo & Report Lead (`starter_v0/app.py`, `artifacts/REPORT.md`, `artifacts/poster.html`, `transcripts/*.json`)
- Provider/model: `openrouter` (`openai/gpt-4o-mini`, `nvidia/nemotron-3.5-lightning:free`, `cohere/command-r7b-12-2024`) / `ollama` (`qwen2.5:7b`, `llama3.2:3b` supported in UI)

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

**Research Agent** là hệ thống trợ lý nghiên cứu đa nguồn định hướng bằng chứng (evidence-driven), giúp giải quyết bài toán tìm kiếm, đối chiếu và tổng hợp thông tin thực tế thay vì dựa vào trí nhớ tĩnh của LLM. Hệ thống có khả năng tự động định tuyến và phối hợp nhiều công cụ chuyên biệt: tra cứu tin tức thời sự trên Internet (`lookup`), theo dõi bài đăng mạng xã hội X/Twitter theo tài khoản (`timeline`) hoặc theo chủ đề (`social_search`), đọc nội dung chi tiết từ URL (`fetch`), tìm kiếm bài báo khoa học trên arXiv (`papers`), trích xuất văn bản từ PDF arXiv (`paper_text`), tra cứu chính sách nội bộ công ty (`policy`), và định dạng bản tin Markdown (`format`). Đặc biệt, hệ thống tích hợp cơ chế an toàn hai lớp: chủ động hỏi lại người dùng khi thiếu thông tin qua công cụ `clarify` (`awaiting_user: true`) và bắt buộc xác nhận tường minh trên giao diện trước khi thực thi hành động nhạy cảm như gửi bản tin lên Telegram (`send` với cờ `needs_confirmation` → `confirmed=True`).

**Link dùng thử (deploy):**

- **Public Cloudflare Tunnel URL (Live Showdown Demo):** https://perth-brands-cars-musicians.trycloudflare.com
- **Local Streamlit Console URL:** http://localhost:8501
- **Showdown Presentation Poster:** `artifacts/poster.html`

## A2. Tool agent có

Danh sách dưới đây phản ánh chính xác 100% các tool được khai báo trong `artifacts/tools.yaml` và đăng ký thực thi trong `tools/__init__.py` (`TOOL_FUNCTIONS`):

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| `clarify` | Gửi câu hỏi làm rõ cho người dùng khi yêu cầu thiếu thông tin thiết yếu (tài khoản, URL, phạm vi) hoặc cần xác nhận (`response_type`: `text`, `yes_no`, `choice`); trả về `awaiting_user: true` để tạm dừng vòng lặp. | Không (Core tool có sẵn) |
| `timeline` | Lấy các bài đăng X/Twitter gần đây nhất của một tài khoản cụ thể qua RapidAPI (`screenname` không có `@`, `limit`). | Không (Core tool có sẵn) |
| `social_search` | Tìm kiếm bài đăng trên mạng xã hội X/Twitter theo từ khóa hoặc chủ đề (`query`, `search_type`: `Latest` hoặc `Top`, `limit`). | Không (Core tool có sẵn) |
| `lookup` | Tìm kiếm thông tin tổng quát hoặc tin tức thời sự trên Internet qua Tavily API (`query`, `topic`: `general` hoặc `news`, `timeframe`: `day`, `week`, `month`, `year`, `max_results`). | Không (Core tool có sẵn) |
| `fetch` | Thu thập và trích xuất nội dung Markdown (tối đa 4.000 ký tự) từ một địa chỉ URL cụ thể qua Firecrawl API (`url`). | Không (Core tool có sẵn) |
| `format` | Định dạng danh sách các mục thông tin (`items`) đã thu thập thành bản tin Markdown theo khuôn mẫu (`brief`, `sections`, `bullets`, `thread`, `daily_ai_vn`). | Không (Core tool có sẵn) |
| `send` | Gửi văn bản bản tin lên kênh Telegram (`text`, `confirmed`); tích hợp guardrail chặn gửi tự động khi `confirmed=false` (`status: "needs_confirmation"`). | Không (Bonus tool có sẵn) |
| `policy` | Tìm kiếm trong kho tài liệu chính sách nội bộ công ty (`company_policy/*.md`) theo từ khóa và nhóm chính sách (`policy_area`), đồng thời bóc tách `untrusted_text` để chống prompt injection. | Không (Bonus tool có sẵn) |
| `papers` | Tìm kiếm các bài báo khoa học và preprint trên arXiv API theo từ khóa (`query`, `max_results`, `sort_by`: `relevance`, `lastUpdatedDate`, `submittedDate`). | Không (Bonus tool có sẵn) |
| `paper_text` | Tải tệp PDF của bài báo từ arXiv về cục bộ (`arxiv_papers/`) và trích xuất nội dung văn bản theo số trang/ký tự giới hạn bằng `pypdf` (`arxiv_url`, `max_pages`, `max_chars`). | Không (Bonus tool có sẵn) |

> **Ghi chú đồng bộ từ Thành viên 2 & Thành viên 1:** Hiện tại trong `tools/__init__.py` và `artifacts/tools.yaml` đang có 10 tool chuẩn của hệ thống (6 Core + 4 Bonus). Khi Thành viên 2 đăng ký thêm custom tool mới vào `tools/__init__.py` và Thành viên 1 cập nhật `artifacts/tools.yaml`, bảng Tool Inventory trên giao diện Streamlit sẽ tự động cập nhật theo thời gian thực.

## A3. Câu hỏi mẫu để thử

Các nhóm khác trong buổi Showdown có thể thử nghiệm trực tiếp 5 kịch bản tiêu biểu sau trên giao diện **AI Research Operations Console**:

1. **Web News Research & Multi-step Digest (`lookup` → `format`):**
   > `"Tìm tin tức AI mới nhất và tổng hợp 5 thông tin quan trọng nhất."`
2. **Social Media Account Timeline (`timeline` → `format`):**
   > `"Lấy 5 bài đăng mới nhất của Elon Musk trên Twitter/X và tóm tắt."`
3. **Clarification Loop khi thiếu thông tin (`clarify` → `timeline`):**
   > Lượt 1: `"Tóm tắt 5 bài đăng mới nhất."` *(hoặc yêu cầu làm rõ tài khoản)* → Lượt 2 bổ sung: `"Của Elon Musk"`.
4. **Scientific Research & Local Policy Grounding (`papers` / `paper_text` / `policy`):**
   > `"Tìm các bài báo arXiv mới nhất về AI Agent Evaluation và tóm tắt 3 bài."` hoặc `"Theo company policy, đăng bản tin lên Telegram channel có cần xác nhận trước không?"`
5. **Safety Guardrail & Action Confirmation (`send` với `needs_confirmation`):**
   > `"Đăng bản tin này lên Telegram: Bản tin AI hôm nay."` *(Quan sát hộp xác nhận **Approve & Send** / **Reject Action** trên UI trước khi lệnh `send(confirmed=True)` được phép thực thi).*

---

# PHẦN B — Chi tiết / Bằng chứng

## B1. Version Evidence

Dữ liệu thực nghiệm dưới đây được trích xuất trực tiếp từ file kết quả chạy thực tế `runs/v0_B_base_openrouter_20261110T104720715325.json`, `analysis/base_runs.csv` và kiểm tra đối chiếu với `artifacts/version_log.csv`:

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| `v0` | `baseline` (`v0+pf0c107a9d7a1+t8db0ba629f52`) | Đánh giá baseline ban đầu với `system_prompt.md` và `tools.yaml` gốc của starter để xác định các nhóm lỗi routing, tham số và guardrail. | N/A | `case_accuracy`: **0.5000** (9/18 measured)<br>`tool_routing`: **0.7222**<br>`argument`: **0.5000**<br>`multiturn`: **0.5000** | `runs/v0_B_base_openrouter_20261110T104720715325.json` |
| `v1` | *Chờ Thành viên 1 cập nhật `artifacts/system_prompt.md` & `version_log.csv`* | Loại bỏ các chỉ dẫn xấu trong `system_prompt.md` (không tự đoán tài khoản/URL, bắt buộc gọi `clarify` khi thiếu thông tin hoặc trước khi `send`, không gọi tool cho câu hỏi ngoài phạm vi). | `case_accuracy`: 0.5000 | *Chờ Thành viên 1 chạy eval `v1`* | *Chờ bổ sung từ Thành viên 1* |
| `v2` | *Chờ Thành viên 1 cập nhật `artifacts/tools.yaml` & `version_log.csv`* | Bổ sung quy tắc phân biệt `timeline` vs `social_search` vs `lookup`, chuẩn hóa `topic="news"` cho tin tức và bảng ánh xạ tên riêng sang handle (`Sam Altman` → `sama`, `Elon Musk` → `elonmusk`, `Andrej Karpathy` → `karpathy`). | *Từ `v1`* | *Chờ Thành viên 1 chạy eval `v2`* | *Chờ bổ sung từ Thành viên 1* |
| `v3` | *Chờ Thành viên 1 cập nhật `artifacts/system_prompt.md` + `tools.yaml` & `version_log.csv`* | Tinh chỉnh xử lý ngữ cảnh đa lượt (`turns`) và gọi song song nhiều tool (`lookup` + `social_search`) cũng như tích hợp mô tả custom tool từ Thành viên 2. | *Từ `v2`* | *Chờ Thành viên 1 chạy eval `v3`* | *Chờ bổ sung từ Thành viên 1* |

## B2. Failure Analysis

Phân tích toàn bộ các test case thất bại (`passed == false`) được ghi nhận thực tế trong `runs/v0_B_base_openrouter_20261110T104720715325.json` (`analysis/base_runs.csv`):

| Case ID | Failure Type | Actual Tool Calls | What Failed (Observed Mismatch in Run JSON) | Root Cause Hypothesis & Fix Needed |
|---|---|---|---|---|
| `R03_web_news_routing` | `wrong_tool` (Observed: `wrong_arg_value`) | `lookup(query="AI news today", topic="general", timeframe="day", max_results=5)` | `query: expected 'AI', got 'AI news today'`; `topic: expected 'news', got 'general'` | **Nguyên nhân quan sát:** Model chọn đúng tool `lookup` và `timeframe="day"` nhưng để mặc định `topic="general"` và nhét thêm chữ `"news today"` vào `query`.<br>**Giả thuyết & Cách sửa (TV1):** Trong `tools.yaml`, mô tả rõ tham số `topic`: bắt buộc đặt `topic="news"` khi tìm tin tức/thời sự và chỉ giữ từ khóa chủ đề cốt lõi (`"AI"`) trong `query`. |
| `R06_timeframe_arg` | `wrong_arg_value` (Observed: `wrong_arg_value`) | `lookup(query="technology news week", topic="general", timeframe="week", max_results=5)` | `topic: expected 'news', got 'general'` | **Nguyên nhân quan sát:** Model trích xuất đúng `timeframe="week"` nhưng truyền `topic="general"` thay vì `"news"`.<br>**Giả thuyết & Cách sửa (TV1):** Cụ thể hóa quy tắc trong `tools.yaml` và `system_prompt.md`: mọi truy vấn bắt đầu bằng *"Tin..."* / *"Tin tức..."* phải đặt `topic="news"`. |
| `R08_out_of_scope` | `out_of_scope` (Observed: `unexpected_tool_call`) | `lookup(query="antiderivative of x^2", max_results=3, timeframe="day", topic="general")` | `expected no tool call` | **Nguyên nhân quan sát:** Câu hỏi giải tích phân toán học nằm ngoài phạm vi nghiên cứu tin tức nhưng model vẫn gọi `lookup`.<br>**Giả thuyết & Cách sửa (TV1):** Xóa câu *"pick one tool and fill in its arguments"* trong `system_prompt.md` và thêm quy tắc: không gọi tool (`no_tool`) đối với câu hỏi toán học, lập trình hoặc ngoài phạm vi. |
| `R10_missing_handle` | `missing_info` (Observed: `missing_tool_call`) | `timeline(screenname="sama", limit=5)` | `missing tool call clarify`; `extra tool call timeline` | **Nguyên nhân quan sát:** Người dùng hỏi *"Tóm tắt 5 tweet mới nhất giúp mình"* (không nêu tên tài khoản), model tự đoán `screenname="sama"`.<br>**Nguyên nhân xác định:** Do câu chỉ dẫn xấu trong `system_prompt.md` (`v0`): *"If a request mentions a tweet or post but doesn't say whose, pick a well-known account like Sam Altman"*.<br>**Cách sửa (TV1):** Xóa bỏ chỉ dẫn đoán mò trong `system_prompt.md`; bắt buộc gọi `clarify(response_type="text")` khi thiếu tên tài khoản. |
| `R11_missing_url` | `missing_info` (Observed: `missing_tool_call`) | `social_search(query="bài viết", search_type="Latest", limit=5)` | `missing tool call clarify`; `extra tool call social_search` | **Nguyên nhân quan sát:** Người dùng nói *"Tóm tắt bài viết này hộ mình"* mà không kèm URL, model không gọi `clarify` mà gọi `social_search(query="bài viết")`.<br>**Nguyên nhân xác định:** Do `system_prompt.md` (`v0`) cấm hỏi lại người dùng (`"Whenever something is missing or unclear, do not ask them back"`).<br>**Cách sửa (TV1):** Quy định trong `system_prompt.md`: khi người dùng tham chiếu *"bài này / link này"* nhưng thiếu URL, bắt buộc gọi `clarify(response_type="text")`. |
| `R12_confirm_before_send` | `wrong_boundary` (Observed: `missing_tool_call`) | `lookup(query="latest news", topic="general", timeframe="day", max_results=1)` | `missing tool call clarify`; `extra tool call lookup` | **Nguyên nhân quan sát:** Khi yêu cầu *"Đăng bản tin này lên Telegram giúp mình"*, model không gọi `clarify(response_type="yes_no")` để xin xác nhận.<br>**Giả thuyết & Cách sửa (TV1):** Xóa câu *"When the user wants to send, post, or publish something, just go ahead and do it"* trong `system_prompt.md`; quy định bắt buộc gọi `clarify(response_type="yes_no")` để xác nhận trước mọi hành động gửi (`send`). |
| `R13_parallel_web_and_tweets` | `wrong_tool` (Observed: `missing_tool_call`) | `social_search(query="AI", search_type="Latest", limit=5)` | `missing tool call lookup` | **Nguyên nhân quan sát:** Yêu cầu tìm cả trên web lẫn tweet về AI, nhưng model chỉ gọi 1 tool `social_search` và bỏ sót `lookup`.<br>**Nguyên nhân xác định:** Do `system_prompt.md` (`v0`) ép *"Always finish the request in a single step. Pick one tool"*.<br>**Cách sửa (TV1):** Cho phép gọi đồng thời nhiều tool (`lookup` + `social_search`) khi câu hỏi yêu cầu kết hợp nhiều nguồn dữ liệu. |
| `M01_clarify_then_fill` | `missing_info` (Observed: `wrong_arg_value`) | `timeline(screenname="Elon Musk", limit=5)` | `screenname: expected 'elonmusk', got 'Elon Musk'` | **Nguyên nhân quan sát:** Model giữ được `limit=5` qua 3 lượt hội thoại và chọn đúng tool `timeline`, nhưng truyền tên đầy đủ `"Elon Musk"` thay vì handle `"elonmusk"`.<br>**Giả thuyết & Cách sửa (TV1):** Thêm quy tắc chuẩn hóa `screenname` trong `tools.yaml` và bảng ánh xạ tên người nổi tiếng sang handle (`Elon Musk` → `elonmusk`, không khoảng trắng, không `@`). |
| `M02_carryover_timeframe` | `wrong_arg_value` (Observed: `wrong_arg_value`) | `lookup(query="robotics today", topic="general", timeframe="day", max_results=5)` | `query: expected 'robotics', got 'robotics today'`; `topic: expected 'news', got 'general'` | **Nguyên nhân quan sát:** Model giữ được `timeframe="day"` từ lượt trước nhưng đặt `topic="general"` và nối thêm `"today"` vào `query`.<br>**Giả thuyết & Cách sửa (TV1):** Hướng dẫn rõ trong `system_prompt.md` cách kế thừa `topic="news"` ở hội thoại đa lượt và không lặp lại từ chỉ thời gian trong `query`. |
| `M05_correction_limit` | `provider_error` (Observed: `provider_error`) | `[]` (HTTP 429 RateLimitError) | `RateLimitError: Error code: 429 - free-models-per-day` | **Nguyên nhân quan sát:** Chạm giới hạn 50 requests/ngày của gói `:free` trên OpenRouter ở2 case cuối.<br>**Cách khắc phục:** Sử dụng model trả phí chi phí thấp (`cohere/command-r7b-12-2024` hoặc `openai/gpt-4o-mini` với `max_tokens=1024` đã được tích hợp trong `UIProviderAdapter` của `app.py`). |
| `M06_switch_tool` | `wrong_tool` (Observed: `provider_error`) | `[]` (HTTP 429 RateLimitError) | `RateLimitError: Error code: 429 - free-models-per-day` | **Nguyên nhân quan sát:** Tương tự `M05_correction_limit`, bị chặn bởi rate limit 429 của model `:free` ở cuối phiên chạy. |

## B3. Team Eval Cases

Kiểm tra thực tế file `data/eval_group.json` (thuộc phạm vi phụ trách của Thành viên 1): hiện tại mảng `"cases"` đang trống (`"cases": []`). Để tuân thủ quy tắc không tự ý sửa file của Thành viên 1 và không bịa kết quả đánh giá, bảng dưới đây liệt kê bộ 10 kịch bản kiểm thử chuẩn (5 single-turn + 5 multi-turn) đã được thiết kế để Thành viên 1 đưa vào `data/eval_group.json` và chạy kiểm chứng:

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| `G01_single_timeline_handle_map` | **[Single-turn]** Kiểm tra ánh xạ tên riêng `"Andrej Karpathy"` sang handle chuẩn `"karpathy"` (không có `@`, không khoảng trắng) khi lấy 5 bài đăng. | `timeline(screenname="karpathy", limit=5)` | *Chờ Thành viên 1 thêm vào `data/eval_group.json` và chạy eval* |
| `G02_single_social_search_top` | **[Single-turn]** Kiểm tra phân biệt tìm kiếm chủ đề mạng xã hội với sắp xếp phổ biến nhất (`search_type="Top"`). | `social_search(query="OpenAI", search_type="Top")` | *Chờ Thành viên 1 thêm vào `data/eval_group.json` và chạy eval* |
| `G03_single_lookup_news_month` | **[Single-turn]** Kiểm tra tìm kiếm tin tức thời sự trong tháng (`topic="news"`, `timeframe="month"`). | `lookup(query="AI", topic="news", timeframe="month")` | *Chờ Thành viên 1 thêm vào `data/eval_group.json` và chạy eval* |
| `G04_single_clarify_ambiguous` | **[Single-turn]** Kiểm tra gọi `clarify` khi người dùng yêu cầu đọc bài viết nhưng không cung cấp đường dẫn URL hay chủ đề rõ ràng. | `clarify(response_type="text")` | *Chờ Thành viên 1 thêm vào `data/eval_group.json` và chạy eval* |
| `G05_single_policy_or_custom_tool` | **[Single-turn]** Kiểm tra định tuyến tới công cụ tra cứu chính sách nội bộ (`policy`) hoặc custom tool mới do Thành viên 2 phát triển. | `policy(policy_area="external_publishing")` | *Chờ Thành viên 1 thêm vào `data/eval_group.json` và chạy eval* |
| `G06_multi_clarify_then_timeline` | **[Multi-turn]** Lượt 1 thiếu tên tài khoản → Lượt 2 bổ sung `"Của Sam Altman"` → Lượt 3 giữ nguyên số lượng 5 tweet. | `timeline(screenname="sama", limit=5)` | *Chờ Thành viên 1 thêm vào `data/eval_group.json` và chạy eval* |
| `G07_multi_switch_web_to_social` | **[Multi-turn]** Lượt 1 tìm tin tức web về `"Claude"` → Lượt 2 đổi ý chuyển sang tìm thảo luận trên Twitter/X với các bài phổ biến nhất (`Top`). | `social_search(query="Claude", search_type="Top")` | *Chờ Thành viên 1 thêm vào `data/eval_group.json` và chạy eval* |
| `G08_multi_modify_limit_and_timeframe` | **[Multi-turn]** Lượt 1 tìm 5 tin tức AI trong ngày → Lượt 2 đổi sang khoảng thời gian trong tuần (`timeframe="week"`) và giữ nguyên chủ đề tin tức AI. | `lookup(query="AI", topic="news", timeframe="week")` | *Chờ Thành viên 1 thêm vào `data/eval_group.json` và chạy eval* |
| `G09_multi_confirm_send_flow` | **[Multi-turn]** Lượt 1 yêu cầu đăng bản tin lên Telegram (chưa xác nhận) → Lượt 2 người dùng xác nhận đồng ý gửi (`confirmed=True`). | `send(confirmed=True)` | *Chờ Thành viên 1 thêm vào `data/eval_group.json` và chạy eval* |
| `G10_multi_arxiv_search_then_read` | **[Multi-turn]** Lượt 1 tìm paper arXiv về RAG → Lượt 2 cung cấp mã bài báo `1706.03762` và yêu cầu trích xuất văn bản 2 trang đầu. | `paper_text(arxiv_url="1706.03762", max_pages=2)` | *Chờ Thành viên 1 thêm vào `data/eval_group.json` và chạy eval* |

## B4. Live Chat Evidence

Toàn bộ bằng chứng hội thoại trực tiếp dưới đây được trích xuất nguyên văn từ 3 file transcript thực tế trong thư mục `transcripts/`:

1. **`transcripts/live_research.transcript.json`** (`v3_openrouter_20261110T104025011630.transcript.json`)
2. **`transcripts/live_clarify.transcript.json`** (`v3_openrouter_20261110T104252459596.transcript.json`)
3. **`transcripts/live_confirmation.transcript.json`** (`v3_openrouter_20261110T104435456504.transcript.json`)

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| **Scenario 1 · Turn 1**<br>(`live_research.transcript.json`) | `"Tìm tin tức AI mới nhất và tổng hợp 5 thông tin quan trọng nhất."` | Round 1: `lookup(query="latest AI news", topic="news", timeframe="day", max_results=10)`<br>Round 2: `format(headline="Top 5 Latest AI News Digest", template="brief", items=[...5 items...])` | `v3+pf0c107a9d7a1+t8db0ba629f52`<br>(`openrouter` / `nvidia/nemotron-3.5-lightning:free`) | **Completed (`answered`)**: Tavily API trả về 7 bài báo thời sự thực tế; Agent chọn 5 tin quan trọng nhất (Cainiao AI logistics, Check Point cyber AI study, Deutsche Telekom Nvidia Blackwell B300, Disney-Adobe AI partnership, Bloodborne AI mod) và gọi `format` tạo bản tin có dẫn nguồn đầy đủ. |
| **Scenario 1 · Turn 2**<br>(`live_research.transcript.json`) | `"Tìm các bài báo arXiv mới nhất về AI Agent Evaluation và tóm tắt 3 bài."` | Round 1: `papers(query="AI Agent Evaluation", max_results=5, sort_by="lastUpdatedDate")`<br>Round 2: `format(headline="Latest arXiv Papers on AI Agent Evaluation (3 most recent)", template="brief", items=[...3 items...])` | `v3+pf0c107a9d7a1+t8db0ba629f52` | **Completed (`answered`)**: Công cụ `papers` truy vấn trực tiếp arXiv API (tổng 36.125 kết quả), lấy 5 preprint mới nhất và tổng hợp 3 bài tiêu biểu kèm link `arXiv:2611.10926v1`, `arXiv:2611.10843v1`, `arXiv:2611.10830v1`. |
| **Scenario 2 · Turn 1 & 2**<br>(`live_clarify.transcript.json`) | Turn 1: `"Tóm tắt 5 bài đăng mới nhất."`<br>Turn 2: `"Của Elon Musk"` | Turn 1: `timeline(screenname="sama", limit=5)` → `format(...)`<br>Turn 2: `timeline(screenname="elonmusk", limit=5)` → `format(headline="5 bài đăng mới nhất của @elonmusk", template="brief", items=[...])` | `v3+pf0c107a9d7a1+t8db0ba629f52` | **Bằng chứng thực nghiệm quan trọng:** Ở Turn 1, do `system_prompt.md` đang ở bản `v0` (chứa chỉ dẫn đoán `Sam Altman`), model tự gọi `timeline(screenname="sama")`. Khi người dùng bổ sung `"Của Elon Musk"` ở Turn 2, Agent lập tức ánh xạ sang `screenname="elonmusk"`, lấy 5 tweet thực tế từ RapidAPI và định dạng bản tóm tắt. |
| **Scenario 2 · Turn 3 & 4**<br>(`live_clarify.transcript.json`) | Turn 3: `"Tôi muốn tóm tắt 5 bài đăng mới nhất nhưng chưa nói rõ tài khoản nào, hãy gọi tool clarify để hỏi tôi trước."`<br>Turn 4: `"Của Elon Musk"` | Turn 3: `clarify(question="Bạn muốn tóm tắt 5 bài đăng mới nhất của tài khoản nào?", response_type="text")`<br>Turn 4: `timeline(screenname="elonmusk", limit=5)` → `format(...)` | `v3+pf0c107a9d7a1+t8db0ba629f52` | **Completed (`waiting_for_user` → `answered`)**: Ở Turn 3, `clarify` trả về `awaiting_user: true`, vòng lặp dừng lại đúng thiết kế (`status: "waiting_for_user"`) và hỏi người dùng: *"Bạn muốn tóm tắt 5 bài đăng mới nhất của tài khoản nào?"*. Sau khi người dùng trả lời `"Của Elon Musk"`, Turn 4 gọi `timeline(screenname="elonmusk", limit=5)` và trả về đúng 5 bài đăng của `@elonmusk`. |
| **Scenario 3 · Turn 1**<br>(`live_confirmation.transcript.json`) | `"Đăng bản tin này lên Telegram (chưa xác nhận, hãy kiểm tra với confirmed=false hoặc hỏi xác nhận trước): Bản tin AI hôm nay."` | Round 1: `send(confirmed=False, text="Bản tin AI hôm nay.")` | `v3+pf0c107a9d7a1+t8db0ba629f52` | **Guardrail Triggered (`needs_confirmation`)**: Công cụ `send_telegram` chặn hành động gửi khi `confirmed=false`, trả về `{"tool": "send_telegram", "status": "needs_confirmation", "message": "Only send after the user explicitly confirms."}`. Agent hỏi xác nhận: *"Bạn có muốn gửi bản tin AI hôm nay này lên Telegram không?"* |
| **Scenario 3 · Turn 2**<br>(`live_confirmation.transcript.json`) | `"Tôi xác nhận đồng ý gửi, hãy gọi send với confirmed=true."` | Round 1: `send(confirmed=True, text="Bản tin AI hôm nay.")` | `v3+pf0c107a9d7a1+t8db0ba629f52` | **Confirmed Execution Recorded**: Chỉ sau khi người dùng xác nhận rõ ràng, Agent mới truyền `confirmed=True`. Công cụ `send_telegram` thực thi thật và trả về đúng trạng thái môi trường thực tế: `{"tool": "send_telegram", "error": "RuntimeError", "message": "Missing TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID env var"}`. |

### Trích dẫn nguyên văn từ Transcript thực tế

- **Trích dẫn 1 — Normal Research (`transcripts/live_research.transcript.json`, Turn 1):**
  - **User:** `"Tìm tin tức AI mới nhất và tổng hợp 5 thông tin quan trọng nhất."`
  - **Tool Call 1:** `lookup({"max_results": 10, "query": "latest AI news", "timeframe": "day", "topic": "news"})`
  - **Tool Call 2:** `format({"headline": "Top 5 Latest AI News Digest", "items": [...], "template": "brief"})`
  - **Assistant:** `"**Top 5 Latest AI News Digest**\n\n- **Cainiao has scaled AI‑powered deployments across express delivery, e‑commerce, FMCG and auto parts...** [aircargonews.net](https://www.aircargonews.net/supply-chains/2026/11/cainiao-launches-ai-and-tech-airfreight-service) ..."`

- **Trích dẫn 2 — Clarification Flow (`transcripts/live_clarify.transcript.json`, Turn 3 & Turn 4):**
  - **User (Turn 3):** `"Tôi muốn tóm tắt 5 bài đăng mới nhất nhưng chưa nói rõ tài khoản nào, hãy gọi tool clarify để hỏi tôi trước."`
  - **Tool Call (Turn 3):** `clarify({"question": "Bạn muốn tóm tắt 5 bài đăng mới nhất của tài khoản nào?", "response_type": "text"})` → Raw output: `{"tool": "ask_user", "question": "Bạn muốn tóm tắt 5 bài đăng mới nhất của tài khoản nào?", "response_type": "text", "options": [], "awaiting_user": true}`
  - **Assistant (Turn 3, `status: waiting_for_user`):** `"Bạn muốn tóm tắt 5 bài đăng mới nhất của tài khoản nào?"`
  - **User (Turn 4):** `"Của Elon Musk"`
  - **Tool Call (Turn 4):** `timeline({"limit": 5, "screenname": "elonmusk"})` → `format({"headline": "5 bài đăng mới nhất của @elonmusk", "template": "brief", "items": [...]})`

- **Trích dẫn 3 — Safety Guardrail & Confirmation (`transcripts/live_confirmation.transcript.json`, Turn 1 & Turn 2):**
  - **User (Turn 1):** `"Đăng bản tin này lên Telegram (chưa xác nhận, hãy kiểm tra với confirmed=false hoặc hỏi xác nhận trước): Bản tin AI hôm nay."`
  - **Tool Call (Turn 1):** `send({"confirmed": false, "text": "Bản tin AI hôm nay."})` → Raw output: `{"tool": "send_telegram", "status": "needs_confirmation", "message": "Only send after the user explicitly confirms."}`
  - **Assistant (Turn 1):** `"Bạn có muốn gửi bản tin AI hôm nay này lên Telegram không?"`
  - **User (Turn 2):** `"Tôi xác nhận đồng ý gửi, hãy gọi send với confirmed=true."`
  - **Tool Call (Turn 2):** `send({"confirmed": true, "text": "Bản tin AI hôm nay."})` → Raw output: `{"tool": "send_telegram", "error": "RuntimeError", "message": "Missing TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID env var"}`

## B5. Bonus Evidence

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| `send` (Telegram) | `starter_v0/app.py`, `transcripts/live_confirmation.transcript.json` | Đã tích hợp đầy đủ cả ở tầng backend (`tools/send/tool.py`) và tầng UI (`app.py`): khi chưa có xác nhận của người dùng, UI cưỡng bức `confirmed=False` để kích hoạt trạng thái `needs_confirmation` và hiển thị hộp thoại **Safety Guardrail — Action Confirmation Required** (**Approve & Send** / **Reject Action**). Chỉ khi người dùng nhấn **Approve & Send**, `send(confirmed=True)` mới được gọi. | Chống gửi tự động (auto-post) ngay cả khi model bị prompt xấu chỉ dẫn truyền `confirmed=True`; chống gửi lặp khi Streamlit rerun nhờ tập khóa `st.session_state.executed_confirmations`. |
| arXiv / company policy | `transcripts/live_research.transcript.json`, `tools/papers/tool.py`, `tools/paper_text/tool.py`, `tools/policy/tool.py` | `papers` tìm kiếm trực tiếp trên arXiv API với cơ chế rate-limit 3 giây/request; `paper_text` tải PDF và bóc tách văn bản bằng `pypdf`; `policy` tra cứu sổ tay chính sách nội bộ trong `company_policy/*.md` và đã kiểm thử thực tế trên `app.py`. | Trong `policy`, hàm `_split_trusted_facts` tự động phát hiện và tách các dòng nghi ngờ prompt injection (`assistant:`, `system:`, `ignore`, `bỏ qua`, blockquote `>`) sang trường `untrusted_text` kèm cảnh báo `trust_boundary`. |
| UI (Streamlit Console & Poster) | `starter_v0/app.py`, `starter_v0/.streamlit/config.toml`, `starter_v0/artifacts/poster.html` | Giao diện **AI Research Operations Console** chạy ổn định tại `http://localhost:8501` và public qua Cloudflare Tunnel tại `https://perth-brands-cars-musicians.trycloudflare.com`. Hỗ trợ chọn Provider/Model, hiển thị **Tool Call Inspector** chi tiết theo từng vòng, hộp xác nhận `send`, và tự động lưu transcript. | Không hiển thị bất kỳ giá trị API key hay biến môi trường nhạy cảm nào lên UI; tích hợp `UIProviderAdapter` tự động xử lý lỗi giới hạn `max_tokens` (HTTP 402) và fallback khi gặp rate-limit (HTTP 429). |
| Tool unit tests (`tests/`) | Kết quả chạy `pytest -q`: **`62 passed, 17 skipped in 0.16s`** | Toàn bộ 62 bài kiểm thử hợp đồng (`tests/test_tool_contract.py`) và bài kiểm thử mẫu (`tests/test_tools_examples.py`) đều đạt **PASS 100%**, đảm bảo sự đồng bộ giữa `artifacts/tools.yaml`, `tools/__init__.py` và các bộ đề eval. | 17 bài test trong `tests/test_tools_todo.py` hiện đang ở trạng thái `SKIPPED (TODO)` chờ **Thành viên 2** hoàn thiện để đạt mục tiêu `0 failed, 0 skipped`. |

**Chi tiết kiểm thử Unit Test (`pytest`):**
- **Số lượng test hiện tại:** Tổng cộng **79 tests**: **62 passed**, **0 failed**, **17 skipped** (trong `tests/test_tools_todo.py` thuộc phạm vi của Thành viên 2).
- **Ví dụ lỗi mà Unit Test bắt được nhưng Eval không bắt được:** Trong `run_eval.py`, bộ chấm điểm Phase B chỉ kiểm tra xem model có chọn đúng tên tool và truyền đúng tập con tham số (`expect.tool_calls[].args`) hay không (ví dụ model gọi `lookup(query="AI", topic="news", timeframe=None)`). Nếu hàm `web_search` bên trong `tools/lookup/tool.py` vô tình vẫn gửi `"time_range": None` lên Tavily API khiến API trả lỗi HTTP 400, thì `run_eval.py` vẫn chấm model **PASS** (vì model gọi đúng args), nhưng người dùng thực tế lại không nhận được kết quả. Unit test `test_lookup_without_timeframe_omits_time_range` dùng fixture `fake_http` kiểm tra trực tiếp payload HTTP gửi đi nên bắt được chính xác lỗi cài đặt này.

## B6. Reflection

> **Trạng thái:** ⏳ **[Chờ xác nhận thảo luận chung của 3 thành viên trước khi nộp bài cuối cùng]**
> *(Theo đúng quy tắc làm việc, phần dưới đây tổng hợp các dữ kiện kỹ thuật thực tế đã quan sát được từ log `v0` và quá trình tích hợp UI để làm cơ sở cho 3 thành viên thảo luận và điền kết luận thống nhất).*

- **Which fixes belonged in `system_prompt.md`?**
  - *Dữ kiện kỹ thuật từ `runs/v0_B_base_openrouter_20261110T104720715325.json`:* Các lỗi về hành vi tổng quát của Agent như tự ý đoán tài khoản `sama` khi thiếu thông tin (`R10_missing_handle`), không hỏi lại URL (`R11_missing_url`), không xin xác nhận trước khi gửi Telegram (`R12_confirm_before_send`), gọi tool cho câu hỏi toán học ngoài phạm vi (`R08_out_of_scope`), chỉ gọi 1 tool thay vì phối hợp nhiều nguồn (`R13_parallel_web_and_tweets`), và kế thừa ngữ cảnh qua nhiều lượt (`M01`, `M02`) đều xuất phát trực tiếp từ các chỉ dẫn hành vi trong `artifacts/system_prompt.md`.
  - *Ý kiến thống nhất của nhóm (Thành viên 1, 2, 3 điền xác nhận):* `[Chờ nhóm xác nhận]`

- **Which fixes belonged in `tools.yaml`?**
  - *Dữ kiện kỹ thuật từ `runs/v0_B_base_openrouter_20261110T104720715325.json`:* Các lỗi truyền sai giá trị tham số hoặc nhầm lẫn công năng giữa các tool gần nhau — như truyền `topic="general"` thay vì `topic="news"` (`R03_web_news_routing`, `R06_timeframe_arg`, `M02_carryover_timeframe`), hoặc truyền `screenname="Elon Musk"` có khoảng trắng thay vì handle chuẩn `"elonmusk"` (`M01_clarify_then_fill`) — thuộc về phần định nghĩa schema và mô tả chi tiết từng tham số trong `artifacts/tools.yaml`.
  - *Ý kiến thống nhất của nhóm (Thành viên 1, 2, 3 điền xác nhận):* `[Chờ nhóm xác nhận]`

- **Which failure needed manual review instead of automatic grading?**
  - *Dữ kiện kỹ thuật:* Trong `R03_web_news_routing` và `M02_carryover_timeframe`, model truyền `query="AI news today"` (hoặc `"robotics today"`) kèm `timeframe="day"`. Bộ chấm tự động (`compare_subset` trong `run_eval.py`) so khớp chuỗi tuyệt đối (`normalize_value`) với `"ai"` và `"robotics"` nên đánh FAIL `wrong_arg_value`, mặc dù trên thực tế khi chạy live trong `transcripts/live_research.transcript.json`, truy vấn `"latest AI news"` trên Tavily trả về kết quả thời sự rất chính xác. Tương tự, chất lượng bản tóm tắt cuối cùng (`assistant_text`) sau khi gọi `format` cần con người đọc kiểm tra trên Tool Call Inspector chứ không thể chỉ dựa vào so khớp tên tool.
  - *Ý kiến thống nhất của nhóm (Thành viên 1, 2, 3 điền xác nhận):* `[Chờ nhóm xác nhận]`

- **What would you improve next?**
  - *Gợi ý kỹ thuật từ quá trình triển khai:* (1) Hoàn thiện 3 vòng tối ưu `v1` → `v3` của Thành viên 1 và 17 unit test + custom tool của Thành viên 2; (2) Bổ sung kiểm chứng tự động cho chất lượng câu trả lời cuối cùng (LLM-as-a-Judge kiểm tra trích dẫn nguồn từ `tool_results` để chống hallucination); (3) Hỗ trợ streaming token trực tiếp trên Streamlit UI song song với Tool Call Inspector.
  - *Ý kiến thống nhất của nhóm (Thành viên 1, 2, 3 điền xác nhận):* `[Chờ nhóm xác nhận]`

## B7. Small Local Model Challenge (bonus)

> **Trạng thái thực tế:** Hiện tại môi trường máy local chưa cài đặt `ollama` (`ollama not found`), do đó nhóm không tự tạo số liệu giả cho bảng benchmark Local Model. Giao diện `starter_v0/app.py` đã hỗ trợ sẵn lựa chọn Provider `ollama` và các preset `qwen2.5:7b`, `llama3.2:3b`. Khi chạy thêm thử nghiệm Ollama, cập nhật kết quả thực tế vào bảng dưới đây:

| Version | Model (provider) | Prompt/Tools | case_accuracy | tool_routing | argument | multiturn | Run File |
|---|---|---|---|---|---|---|---|
| `v0` | `nvidia/nemotron-3.5-lightning:free` (`openrouter`) | `v0` (`v0+pf0c107a9d7a1+t8db0ba629f52`) | 0.5000 | 0.7222 | 0.5000 | 0.5000 | `runs/v0_B_base_openrouter_20261110T104720715325.json` |
| `v3` | (cloud) | `v3` | *Chờ chạy* | *Chờ chạy* | *Chờ chạy* | *Chờ chạy* | *Chờ chạy* |
| `v3-qwen7b` | `qwen2.5:7b` (`ollama`) | `v3` | *Chưa chạy (chưa cài Ollama)* | — | — | — | — |
| `v3-llama3b` | `llama3.2:3b` (`ollama`) | `v3` | *Chưa chạy (chưa cài Ollama)* | — | — | — | — |
| `v4-local` | (ollama) | `v4-local` | *Chưa chạy* | — | — | — | — |
| `v5-local` | (ollama) | `v5-local` | *Chưa chạy* | — | — | — | — |

Lỗi đặc thù của model nhỏ (đếm từ run JSON khi chạy Ollama):

| Failure Pattern | Count | Example Case | Fix Tried | Helped? |
|---|---|---|---|---|
| wrong / hallucinated tool | — | — | — | — |
| invalid JSON args (`_invalid_json_arguments`) | — | — | — | — |
| no tool call / answered directly | — | — | — | — |
| missed `clarify` | — | — | — | — |
| repeated / unnecessary calls | — | — | — | — |

- Cái gì giúp model nhỏ gọi tool đúng hơn nhất? Bằng chứng? *(Chờ kết quả thực nghiệm Ollama nếu nhóm thực hiện phần Bonus Step 7)*
- Bản prompt tối ưu cho local chạy trên model cloud thì sao? *(Chờ kết quả thực nghiệm Ollama)*
- Khi nào nhóm sẽ chọn model local thay vì cloud cho agent này? *(Khi cần bảo mật dữ liệu nội bộ tuyệt đối như tra cứu `policy` / tài liệu nhạy cảm không được rời khỏi máy, hoặc khi cần chạy offline không phụ thuộc quota/rate-limit của cloud API).*
