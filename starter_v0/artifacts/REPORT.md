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
- Evaluation runs for Member 1 (v0–v3): `openai` / `gpt-4o-mini`; all four base runs measured 20 cases with no provider errors. The optional Ollama challenge was not run.
- UI provider presets: `openrouter` (`openai/gpt-4o-mini`, `nvidia/nemotron-3.5-lightning:free`, `cohere/command-r7b-12-2024`) and `ollama` (`qwen2.5:7b`, `llama3.2:3b`). The evaluation results above were run with the OpenAI API provider and `gpt-4o-mini`.

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
| `hn_search` | Tìm story Hacker News, sắp xếp theo liên quan hoặc thời gian và lọc khoảng thời gian. | Có (tool nhóm thêm) |
| `wiki` | Tìm bài Wikipedia và lấy đoạn giới thiệu; phù hợp kiến thức nền ổn định. | Có (tool nhóm thêm) |
| `github_repos` | Tìm repository công khai trên GitHub; hỗ trợ lọc ngôn ngữ và sắp xếp. | Có (tool nhóm thêm) |
| `hf_models` | Tìm model trên Hugging Face Hub, lọc theo task và sắp xếp theo downloads/likes/trending/recent. | Có (tool nhóm thêm) |

> **Ghi chú đồng bộ:** Hiện tại `tools/__init__.py` và `artifacts/tools.yaml` có 14 tool: 6 Core, 4 Bonus và 4 tool nhóm thêm (`hn_search`, `wiki`, `github_repos`, `hf_models`). Bảng trên gồm các tool được khai báo trong schema; chi tiết hành vi/runtime thuộc phần triển khai của Thành viên 2.

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

Dữ liệu dưới đây lấy từ các run OpenAI thực tế và đối chiếu với `artifacts/version_log.csv`. Cả v0–v3 dùng `gpt-4o-mini`, cùng bộ base 20 case; không có lỗi provider. OpenRouter run cũ không dùng làm đường so sánh vì các phiên bản được ghi trong version log chạy bằng OpenAI.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| `v0` | Baseline starter (`v0+pf0c107a9d7a1+t8db0ba629f52`) | Đo khả năng định tuyến tool, chọn tham số, xử lý thiếu thông tin và giới hạn hành động trước khi sửa prompt. | N/A | `case_accuracy`: **0.65 (13/20)**; `tool_routing`: **0.75**; `argument`: **0.65**; `multiturn`: **1.00** | `runs/v0_B_base_openai_20261110T102720056843.json` |
| `v1` | `artifacts/system_prompt.md` (`v1+p69796db64a79+t8db0ba629f52`) | Thay các chỉ dẫn cố ý sai bằng quy tắc làm rõ thông tin, định tuyến research, giới hạn hành động và xử lý đa lượt. | `case_accuracy`: 0.65 (13/20) | `case_accuracy`: **0.90 (18/20)**; `tool_routing`: **0.95**; `argument`: **0.90**; `multiturn`: **0.8333** | `runs/v1_B_base_openai_20261110T111004215616.json` |
| `v2` | `artifacts/tools.yaml` (`v2+p69796db64a79+t0156c6acb3c5`) | Làm rõ công dụng, trường hợp dùng/không dùng và quy ước tham số trong mô tả tool. | `case_accuracy`: 0.90 (18/20) | `case_accuracy`: **0.85 (17/20)**; `tool_routing`: **0.90**; `argument`: **0.85**; `multiturn`: **0.6667** | `runs/v2_B_base_openai_20261110T111540830676.json` |
| `v3` | `artifacts/system_prompt.md` (`v3+pc95531b2d8b5+te19d85b877e0`) | Thêm quy tắc lượt mới đổi nguồn sẽ thay thế nguồn cũ, tránh gọi thêm nguồn đã bị bỏ. | `case_accuracy`: 0.85 (17/20) | `case_accuracy`: **0.90 (18/20)**; `tool_routing`: **0.95**; `argument`: **0.90**; `multiturn`: **0.8333** | `runs/v3_B_base_openai_20261110T113536460431.json` |

Run group v3: **9/10 passed (0.90)**, `tool_routing=1.00`, `argument=0.90`, `multiturn=0.80`; xem `runs/v3_B_group_openai_20261110T113603572758.json`.

## B2. Failure Analysis

Các lỗi dưới đây là những lỗi còn lại trong kết quả cuối v3 (base và group), không phải lỗi của baseline v0:

| Case ID | Suite / Failure | Actual Tool Calls | What Failed | Root Cause Hypothesis |
|---|---|---|---|---|
| `R12_confirm_before_send` | Base v3 · `wrong_arg_value` | `clarify(response_type="text")` | Eval mong `clarify(response_type="yes_no")`; model hỏi nội dung bản tin trước. | Prompt vẫn để model ưu tiên làm rõ nội dung thiếu trước câu hỏi xác nhận. Cần nêu rõ thứ tự theo hợp đồng eval: yêu cầu gửi → hỏi xác nhận `yes_no` trước; chỉ hỏi nội dung sau khi người dùng xác nhận nếu nội dung vẫn thiếu. |
| `M06_switch_tool` | Base v3 · `extra_tool_call` | `lookup(query="OpenAI", topic="news", timeframe="week", max_results=5)` và `social_search(query="OpenAI", search_type="Top", limit=5)` | Lượt mới yêu cầu bỏ Twitter và tìm web, nhưng model vẫn gọi `social_search` từ ngữ cảnh cũ. | Quy tắc mới chưa đủ mạnh để ngăn tool call nguồn cũ. Cần ưu tiên rõ các mệnh lệnh hủy/đổi nguồn ở lượt mới nhất; không gọi tool bị hủy. |
| `G08_multiturn_correct_limit` | Group v3 · `wrong_arg_value` | `github_repos(query="RAG", language="python", limit=10)` | Eval mong thêm `sort="stars"`; model không truyền `sort` trong tool call. | Mô tả mặc định trong tool chưa khiến model phát tham số mặc định tường minh. Có thể sửa mô tả/schema để nói rõ cần truyền `sort="stars"` khi người dùng yêu cầu repo nhiều sao nhất. |

## B3. Team Eval Cases

File `data/eval_group.json` có đúng 10 case (5 single-turn, 5 multi-turn). Kết quả dưới đây lấy từ run OpenAI v3 group; 9 case đạt, G08 còn fail do thiếu `sort="stars"`:

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| `G01_timeline_name_to_handle` | **[Single-turn]** Map Andrej Karpathy sang `karpathy`; giữ `limit=7`. | `timeline(screenname="karpathy", limit=7)` | **PASS** |
| `G02_social_search_top` | **[Single-turn]** Tìm chủ đề AI safety, phổ biến nhất và `limit=4`. | `social_search(query="AI safety", search_type="Top", limit=4)` | **PASS** |
| `G03_lookup_month_news` | **[Single-turn]** Tin AI tháng này. | `lookup(query="AI", topic="news", timeframe="month")` | **PASS** |
| `G04_clarify_missing_account` | **[Single-turn]** Thiếu tài khoản tweet thì hỏi lại, không đoán. | `clarify(response_type="text")` | **PASS** |
| `G05_new_tool_github_repos` | **[Single-turn]** Tìm repo Python LLM agent nhiều sao nhất. | `github_repos(query="LLM agent", language="python", sort="stars", limit=3)` | **PASS** |
| `G06_multiturn_clarify_then_timeline` | **[Multi-turn]** Bổ sung Sam Altman sau khi hỏi thiếu tài khoản; giữ `limit=5`. | `timeline(screenname="sama", limit=5)` | **PASS** |
| `G07_multiturn_switch_web_to_social` | **[Multi-turn]** Đổi web sang Twitter; chỉ tìm social Top. | `social_search(query="AI", search_type="Top")` | **PASS** |
| `G08_multiturn_correct_limit` | **[Multi-turn]** Đổi limit từ 5 thành 10, giữ query/language. | `github_repos(query="RAG", language="python", sort="stars", limit=10)` | **FAIL** — thiếu `sort="stars"` |
| `G09_multiturn_carryover_news_timeframe` | **[Multi-turn]** Đổi chủ đề sang robotics nhưng giữ web news và timeframe day; không gọi social. | `lookup(query="robotics", topic="news", timeframe="day")` | **PASS** |
| `G10_multiturn_clarify_then_fetch_url` | **[Multi-turn]** Bổ sung URL ở lượt sau và chỉ fetch đúng URL đó. | `fetch(url="https://example.com/research/article")` | **PASS** |

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

> **Phạm vi phần này:** Nhận xét kỹ thuật của Thành viên 1 dựa trên eval OpenAI v0–v3 và group v3. Kết luận thống nhất của cả nhóm vẫn cần các thành viên xác nhận.

- **Which fixes belonged in `system_prompt.md`?**
  - Quy tắc ứng xử tổng quát thuộc prompt: hỏi khi thiếu thông tin, không đoán tài khoản/URL, tránh tool cho yêu cầu ngoài phạm vi, xác nhận trước hành động gửi, và xử lý lượt mới nhất cùng ngữ cảnh liên quan. Ở v0, các case thiếu thông tin và ngoài phạm vi là lỗi; v1 nâng accuracy từ 0.65 lên 0.90.
  - Ở v3, lỗi `M06_switch_tool` vẫn gọi thêm `social_search` dù lượt mới yêu cầu bỏ Twitter. Quy tắc ưu tiên nguồn mới đã được thêm nhưng chưa đủ để sửa lỗi đó.
  - *Ý kiến thống nhất của nhóm (Thành viên 1, 2, 3 điền xác nhận):* `[Chờ nhóm xác nhận]`

- **Which fixes belonged in `tools.yaml`?**
  - Mô tả/schema tool nên làm rõ công dụng, trường hợp không dùng, enum và cách biểu diễn tham số. v2 cập nhật `tools.yaml`, nhưng base accuracy giảm từ 0.90 xuống 0.85; vì vậy không thể kết luận thay đổi này cải thiện metric tổng thể. Group v3 còn lỗi G08 do model bỏ `sort="stars"` khỏi tool call dù schema có default.
  - *Ý kiến thống nhất của nhóm (Thành viên 1, 2, 3 điền xác nhận):* `[Chờ nhóm xác nhận]`

- **Which failure needed manual review instead of automatic grading?**
  - Eval Phase B đối chiếu tool calls và tham số với expected; nó không đánh giá độ chính xác/chất lượng nội dung trả lời sau khi tool chạy. Vì vậy cần người đọc kiểm tra chất lượng bản tóm tắt, mức độ phù hợp của nguồn và trích dẫn. Với các case như G08, đồng thời cần phân biệt tham số default của implementation với tham số model đã phát ra: run JSON cho thấy model không gửi `sort`, nên case strict-args vẫn fail.
  - *Ý kiến thống nhất của nhóm (Thành viên 1, 2, 3 điền xác nhận):* `[Chờ nhóm xác nhận]`

- **What would you improve next?**
  - Theo phạm vi Thành viên 1: tiếp tục sửa từng giả thuyết riêng cho ba lỗi còn lại (R12, M06, G08), chạy lại cùng provider/model và bộ case để đo trước/sau, rồi cập nhật `version_log.csv`. Chưa nên ghi các lỗi này là đã khắc phục khi run vẫn fail.
  - *Ý kiến thống nhất của nhóm (Thành viên 1, 2, 3 điền xác nhận):* `[Chờ nhóm xác nhận]`

## B7. Small Local Model Challenge (bonus)

> **Trạng thái:** Nhóm không thực hiện bonus local-model challenge theo quyết định hiện tại; lệnh `ollama` không có trong môi trường đã kiểm tra. Không có run JSON local, vì vậy không có benchmark hoặc lỗi đặc thù model nhỏ để thống kê. Các kết quả cloud v0–v3 được ghi ở B1.

Không có số liệu để điền bảng lỗi local (hallucinated tool, JSON lỗi, không gọi tool, bỏ sót clarify, gọi lặp). Các câu hỏi so sánh local với cloud trong bonus này **N/A — chưa thử nghiệm**.
