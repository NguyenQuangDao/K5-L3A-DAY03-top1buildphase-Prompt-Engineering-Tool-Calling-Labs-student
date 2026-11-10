# Team

## Thông tin nhóm

- Tên nhóm: top1buildphase
- Lớp: L3A
- Repo nhóm: `K5-L3A-DAY03-top1buildphase-Prompt-Engineering-Tool-Calling-Labs-student` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt: https://github.com/NguyenQuangDao/K5-L3A-DAY03-top1buildphase-Prompt-Engineering-Tool-Calling-Labs-student — nhánh `main` — commit chốt: commit cuối cùng trên `main` trước deadline

## Thành viên

| STT | Họ tên               | MSSV        | Email                       | GitHub           | Vai trò                                                                                           |
| --: | -------------------- | ----------- | --------------------------- | ---------------- | ------------------------------------------------------------------------------------------------- |
|   1 | Nguyễn Vũ Thành Long | 2A202603635 | 26ai.longnvt2@vinuni.edu.vn | `nvl191`         | Prompt & Eval Lead: `system_prompt.md`, `tools.yaml`, v0–v3, `version_log.csv`, `eval_group.json` |
|   2 | Nguyễn Gia Bảo       | 2A202603647 | 26ai.baong5@vinuni.edu.vn   | `Billy3005`      | Tool & Testing Engineer: 4 tool mới, unit test, sửa bug tool, Small Local Model (Step 7)          |
|   3 | Nguyễn Quang Đạo     | 2A202603614 | 26ai.daonq2@vinuni.edu.vn   | `NguyenQuangDao` | UI, Live Demo & Report Lead: `app.py`, `ui_components/`, poster, REPORT, deploy                   |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

## NguyenGiaBao-2A202603647

Báo cáo chi tiết: [report/team/2A202603647_NguyenGiaBao.md](report/team/2A202603647_NguyenGiaBao.md)

### Phần việc phụ trách

- Thành viên 2 — Tool & Testing Engineer: viết tool mới, unit test cho tool, sửa bug tool có sẵn.
- Bonus Step 7 — Small Local Model Challenge: tối ưu prompt/tools cho model nhỏ chạy Ollama.

### Đóng góp cụ thể

- 4 tool mới (bonus "hơn 3 tool"): `hn_search`, `wiki`, `github_repos`, `hf_models` — mỗi tool có `tool.py` + `TOOL.md`, đăng ký trong `tools/__init__.py` và `tools.yaml`, xử lý input xấu từ model (sai kiểu, ngoài enum, query rỗng) bằng error dict.
- Unit test: điền hết 14 stub TODO + 20 test cho tool mới + 4 test hồi quy/biên → `pytest`: **121 passed, 0 failed, 0 skipped**.
- Tìm và sửa 3 bug trong tool có sẵn, mỗi bug có regression test: `send(confirmed="false")` vẫn gửi thật; `format` crash khi `items` là chuỗi; `timeline`/`social_search` với `limit=-1` cắt sai.
- Sửa provider Anthropic (SDK 2.x không nhận `temperature`, model mặc định Haiku 5.5) + test offline.
- 7 eval case ban đầu cho tool mới trong `data/eval_group.json`.
- Step 7: `qwen2.5:3b` v3 0.55 → `v4-local` (7 tool lõi) 0.70 → `v5-local` (few-shot) 0.80; bảng đếm lỗi model nhỏ và trả lời câu hỏi bonus trong REPORT B7.
- Dọn repo: bỏ theo dõi 8.991 file `node_modules`; tạo lại `analysis/base_runs.csv` từ 9 run; bổ sung `version_log.csv`; REPORT B4 (ghi chú hash), B5 (unit test + bug), B6 (ý kiến Thành viên 2), B7.

### Bằng chứng

- PR #1 (tool mới + test + sửa bug): https://github.com/NguyenQuangDao/K5-L3A-DAY03-top1buildphase-Prompt-Engineering-Tool-Calling-Labs-student/pull/1
- PR #6 (Step 7 + report): https://github.com/NguyenQuangDao/K5-L3A-DAY03-top1buildphase-Prompt-Engineering-Tool-Calling-Labs-student/pull/6
- Commit: `44149e3`, `31b5e0c`, `1c32178`, `04e697a`
- Run: `starter_v0/runs/v3-qwen3b_*`, `v4-local-qwen3b_*`, `v5-local-qwen3b_*`; transcript `starter_v0/transcripts/v3_ollama_*.transcript.json`

## NguyenQuangDao-2A202603614

Báo cáo chi tiết: [report/team/2A202603614_NguyenQuangDao.md](report/team/2A202603614_NguyenQuangDao.md)

### Phần việc phụ trách

- Thành viên 3 — UI, Live Demo & Report Lead: xây dựng giao diện tương tác `starter_v0/app.py`, phát triển bộ custom React components (`starter_v0/ui_components/`), thiết kế poster thuyết trình `artifacts/poster.html`, đóng gói hạ tầng Docker & Devcontainer, triển khai Streamlit Cloud.
- Quản trị kho mã nguồn (Repo Owner), điều phối và hoàn thiện Báo cáo tổng kết nhóm (`artifacts/REPORT.md`, `report/team/group_report.md`).
- Đồng thực hiện và kiểm chứng 2 vòng tối ưu `v4` & `v5` đưa Agent đạt điểm tuyệt đối 100% trên cả 2 bộ test Base (20/20) và Group (10/10).

### Đóng góp cụ thể

- **AI Research Operations Console (`starter_v0/app.py`):**
  - Xây dựng ứng dụng Streamlit hoàn chỉnh hỗ trợ 5 providers (OpenRouter, Ollama, Gemini, OpenAI, Anthropic), nạp sẵn các preset mô hình phổ biến.
  - Tích hợp lớp `UIProviderAdapter` tự động xử lý lỗi token limit `HTTP 402` trên OpenRouter bằng cơ chế hạ `max_tokens` thông minh và fallback khi gặp rate-limit `HTTP 429`.
  - Quản lý vòng lặp agent tương tác đa lượt (`run_interactive_agent_turn`), nạp động 14 công cụ từ schema `tools.yaml`, tự động lưu vết transcript theo chuẩn JSON của `chat.py`.
- **Bộ Custom React Components (`starter_v0/ui_components/`):**
  - Xây dựng bộ giao diện mở rộng bằng React + Vite + TypeScript + Tailwind CSS + shadcn/ui kết nối 2 chiều với Streamlit.
  - Triển khai các component: `WelcomeScreen` (thông số & prompt mẫu), `ToolCallInspector` (thanh tra trực quan từng round gọi tool, đối số, kết quả thô, thời gian phản hồi), `ConfirmationCard` (thẻ phê duyệt hành động gửi Telegram), và `ClarifyOptions` (nút chọn làm rõ).
  - Khử trùng lặp sự kiện bằng `event_id` trong `consume_component_event` nhằm triệt tiêu hiện tượng duplicate action khi Streamlit rerun.
- **Cơ chế An toàn 2 Lớp & Human-in-the-Loop cho Tool `send`:**
  - Thiết lập phòng vệ Zero-Trust ở tầng UI: `execute_single_tool` cưỡng bức `confirmed=False` nếu chưa có sự phê duyệt từ người dùng, ngăn chặn hoàn toàn việc mô hình tự ý gửi dữ liệu ra ngoài (như đã kiểm chứng ở log `v3_openrouter_20261110T105249646669.transcript.json`).
  - Hỗ trợ modal xác thực `@st.dialog` cho phép người dùng chọn **Approve & Send** (`confirmed=True`) hoặc **Reject Action** (`status: rejected_by_user`).
- **Showdown Presentation Poster (`starter_v0/artifacts/poster.html` - 640 dòng):**
  - Thiết kế poster tương tác HTML/CSS giao diện tối (Dark Mode), responsive, trực quan hoá kiến trúc 14 tools, quy trình evidence-driven pipeline (v0–v5), bảng đo lường và 6 câu hỏi mẫu trước deadline 16:30.
- **Đóng gói Hạ tầng & Deploy Cloud:**
  - Viết `Dockerfile` chuẩn Python 3.11-slim kèm healthcheck, `docker-compose.yml` chạy local 1 lệnh, `.devcontainer/devcontainer.json` cho Codespaces / Dev Containers.
  - Triển khai phiên bản Live Demo trực tiếp lên Streamlit Cloud: https://k5-l3a-day03-top1buildphase.streamlit.app/.
- **Tối ưu hóa v4 & v5 (100% Base & Group Suites):**
  - Đồng thực hiện phiên bản `v4` (`system_prompt.md` - sửa dứt điểm R12 và M06) và `v5` (`tools.yaml` - sửa G08 bằng cách đưa `sort` vào required cho `github_repos`).
  - Đưa độ chính xác lên mức tuyệt đối: **20/20 Base cases (1.00)** và **10/10 Group cases (1.00)** với 0 lỗi provider.
- **Transcripts & Báo cáo:**
  - Thu thập và chuẩn hoá 5 bộ transcript JSON thực tế phục vụ minh chứng cho Phần B4.
  - Đồng tác giả biên soạn Phần A, B4, B5, B6 trong `REPORT.md` / `group_report.md`. Review và merge toàn bộ PR #1 đến PR #8.

### Bằng chứng

- **PRs & Commits chính:**
  - PR #2 (App UI + React ui_components + Docker): commit `0c0a103`
  - Commit `62acf45`: Thêm `.devcontainer/devcontainer.json`
  - PR #4 (Cập nhật Live Demo URL, docs, poster HTML 14 tools): commit `2f16c81`
  - PR #7 (Dọn dẹp frontend node_modules trong gitignore): commit `100753e`
  - PR #8 (Cập nhật final report, nạp runs v4/v5 đạt 100% metrics): commit `44e9fba`
  - Review & Merge commits: `58aff1f` (PR #1), `f81697e` (PR #2), `14d3a68` (PR #3), `2db21c3` (PR #4), `c1c923d` (PR #5), `1b42332` (PR #6), `27bd812` (PR #7), `53aa0fc` (PR #8).
- **Mã nguồn & Hạ tầng:**
  - UI & Components: `starter_v0/app.py`, `starter_v0/ui_components/**`, `starter_v0/.streamlit/config.toml`
  - Containerization: `Dockerfile`, `docker-compose.yml`, `.devcontainer/devcontainer.json`
  - Poster: `starter_v0/artifacts/poster.html`
- **Địa chỉ Triển khai Live Demo:** https://k5-l3a-day03-top1buildphase.streamlit.app/
- **Run JSONs (Đạt 100% Tuyệt đối):** `starter_v0/runs/v4_B_base_openrouter_20261110T160309218282.json`, `starter_v0/runs/v5_B_base_openrouter_20261110T160447011852.json`, `starter_v0/runs/v5_B_group_openrouter_20261110T160406570224.json`
- **Transcript Logs Thực tế:** `starter_v0/transcripts/live_research.transcript.json`, `starter_v0/transcripts/live_clarify.transcript.json`, `starter_v0/transcripts/live_confirmation.transcript.json`, `starter_v0/transcripts/v3_openrouter_20261110T105249646669.transcript.json`, `starter_v0/transcripts/v3_openrouter_20261110T112336428327.transcript.json`

## NguyenVuThanhLong-2A202603635

Báo cáo chi tiết: [report/team/2A202603635_NguyenVuThanhLong.md](report/team/2A202603635_NguyenVuThanhLong.md)

### Phần việc phụ trách

- Thành viên 1 — Prompt & Eval Lead: phụ trách tối ưu system prompt qua bốn vòng `v0`–`v3`, tập trung vào lựa chọn đúng tool (routing), truyền chính xác tham số (argument), làm rõ thông tin còn thiếu (`clarify`), xác nhận trước hành động gửi (`send`) và không gọi tool khi yêu cầu ngoài phạm vi (`no_tool`).
- Cập nhật và chuẩn hóa mô tả, ràng buộc tham số của các tool trong `starter_v0/artifacts/tools.yaml`.
- Xây dựng 10 eval case nhóm (5 single-turn, 5 multi-turn) trong `starter_v0/data/eval_group.json`.
- Quản lý nhật ký thay đổi và kết quả thực nghiệm qua `starter_v0/artifacts/version_log.csv`.
- Phụ trách các artifact liên quan đến prompt và evaluation, bao gồm `starter_v0/artifacts/system_prompt.md`, `tools.yaml`, `eval_group.json` và `version_log.csv`.
- Thực hiện bonus benchmark và so sánh hai mô hình local `qwen2.5:7b` và `llama3.2:3b` thông qua Ollama trên cùng base evaluation suite.

### Đóng góp cụ thể

- **Tối ưu System Prompt qua bốn phiên bản (`v0`–`v3`):**
  - Thực hiện bốn vòng tối ưu trên cùng model `gpt-4o-mini` và base evaluation suite gồm 20 test case, không có provider error.
  - `v0` — Baseline starter đạt 13/20 case (0.65). Prompt ban đầu có các chỉ dẫn chưa phù hợp, khuyến khích model tự suy đoán thông tin và cố gắng hoàn thành tác vụ trong một bước.
  - `v1` — Điều chỉnh prompt để yêu cầu hỏi lại khi thiếu thông tin thiết yếu, xác nhận dạng `yes_no` trước `send(confirmed=True)`, cho phép phối hợp nhiều tool và không gọi tool khi yêu cầu ngoài phạm vi. Case Accuracy tăng lên 18/20 (0.90).
  - `v2` — Chuẩn hóa tool descriptions và routing trong `tools.yaml`: phân biệt `timeline`, `social_search`, `lookup` và `fetch`; bổ sung mapping tên người sang handle như Sam Altman → `sama`, Elon Musk → `elonmusk`, Andrej Karpathy → `karpathy`. Case Accuracy đạt 17/20 (0.85).
  - `v3` — Bổ sung quy tắc ưu tiên nguồn được chọn ở lượt mới nhất khi người dùng chuyển đổi nguồn tìm kiếm. Case Accuracy tăng trở lại 18/20 (0.90).
  - Kết quả tổng hợp:

  | Version | Case Accuracy | Tool Routing | Argument | Multi-turn |
  |---|---:|---:|---:|---:|
  | `v0` | 0.65 | 0.75 | 0.65 | 1.00 |
  | `v1` | 0.90 | 0.95 | 0.90 | 0.8333 |
  | `v2` | 0.85 | 0.90 | 0.85 | 0.6667 |
  | `v3` | 0.90 | 0.95 | 0.90 | 0.8333 |

  - Cải thiện Case Accuracy từ 65% ở baseline lên 90% ở v3, tương đương tăng 25 điểm phần trăm.

- **Phân tích lỗi và tối ưu theo evaluation evidence:**
  - Phân tích 7 case fail ở baseline, tiêu biểu gồm query news bị thêm từ không cần thiết (`R03`), gọi `send` ngoài phạm vi (`R08`, `R14`), tự suy đoán tài khoản/URL (`R10`, `R11`), sai bước xác nhận (`R12`) và sai query hoặc thiếu tham số tìm kiếm đồng thời web/social (`R13`).
  - Theo dõi ba mismatch trong run v2: `R12_confirm_before_send` (sai loại clarify), `M02_carryover_timeframe` (gọi thừa `social_search`) và `M06_switch_tool` (tiếp tục gọi tool nguồn cũ sau khi người dùng đổi sang web).
  - Phân tích các lỗi còn mở ở v3: `R12_confirm_before_send` (chưa hỏi xác nhận `yes_no` đúng thời điểm) và `M06_switch_tool` (vẫn gọi thêm `social_search` sau khi chuyển sang web).
  - Đối chiếu từng mismatch với expected output và run JSON; không xem các lỗi là đã khắc phục khi chưa có kết quả evaluation xác nhận.

- **Xây dựng Evaluation Dataset nhóm (`eval_group.json`):**
  - Xây dựng 10 eval case gồm 5 single-turn và 5 multi-turn, kiểm tra ánh xạ handle, tìm kiếm social Top, lookup theo tháng, clarify khi thiếu tài khoản, tool mới `github_repos`, chuyển đổi nguồn tìm kiếm, sửa limit và duy trì ngữ cảnh qua nhiều lượt.
  - Group suite v3 đạt **9/10 case (0.90)**, với Tool Routing 1.00, Argument 0.90 và Multi-turn 0.80.
  - Phân tích case còn fail `G08_multiturn_correct_limit`: model cập nhật đúng `limit=10` nhưng bỏ mất `sort="stars"` đã có từ ngữ cảnh trước.
  - Kết quả được ghi nhận trong run `v3_B_group_openai_20261110T113603572758.json`.

- **Bonus — Benchmark Small Local Models qua Ollama:**
  - Chạy hai mô hình local trên cùng base suite 20 case với cấu hình prompt v3, không có provider error.
  - `qwen2.5:7b` đạt **16/20 case (0.80)**; lỗi tiêu biểu liên quan đến thiếu clarify/xác nhận ở `R10`–`R12` và query web dư từ ở `R13`.
  - `llama3.2:3b` đạt **5/20 case (0.25)**; lỗi tập trung ở routing (`R02`, `R04`, `R05`), enum/tham số, clarify và gọi tool ngoài phạm vi.
  - Kết quả cho thấy `qwen2.5:7b` đạt độ chính xác cao hơn `llama3.2:3b` trên bộ evaluation này. Chi tiết được ghi nhận trong REPORT B7 và hai run JSON tương ứng.

- **Version Tracking & Thực nghiệm:**
  - Duy trì `starter_v0/artifacts/version_log.csv`, ghi nhận các phiên bản v0–v3, artifact version, prompt/tools hash, lý do thay đổi, giả thuyết, metric trước/sau và run tương ứng.
  - Đối chiếu kết quả evaluation với summary trong run JSON, đảm bảo có thể truy vết thay đổi và kết quả qua từng phiên bản.

- **Phối hợp và bàn giao cho nhóm:**
  - Tiếp nhận mô tả/schema tool mới do Thành viên 2 cung cấp và cập nhật vào `tools.yaml`, đảm bảo thống nhất tên tool với registry và expected output của evaluation.
  - Bàn giao version log, evaluation dataset và run JSON để Thành viên 3 tổng hợp bằng chứng trong báo cáo nhóm.
  - Đóng góp cá nhân được xác định theo các artifact và run v0–v3 cùng hai benchmark Ollama; các phiên bản v4/v5 đạt 100% được ghi nhận là kết quả tiếp nối của nhóm.

### Bằng chứng

- **Git Commit:**
  - Commit `6bc6dd8512c2097817c50bf3f52d07ba1580fd6c` (`update member 1`) trên nhánh `long-branch`.

- **Prompt & Evaluation Artifacts:**
  - System Prompt: `starter_v0/artifacts/system_prompt.md`.
  - Tool Descriptions: `starter_v0/artifacts/tools.yaml`.
  - Version Tracking: `starter_v0/artifacts/version_log.csv`.
  - Group Evaluation Dataset: `starter_v0/data/eval_group.json`.

- **Base Evaluation Runs (v0–v3):**
  - `starter_v0/runs/v0_B_base_openai_20261110T102720056843.json`
  - `starter_v0/runs/v1_B_base_openai_20261110T111004215616.json`
  - `starter_v0/runs/v2_B_base_openai_20261110T111540830676.json`
  - `starter_v0/runs/v3_B_base_openai_20261110T113536460431.json`

- **Group Evaluation Run:**
  - `starter_v0/runs/v3_B_group_openai_20261110T113603572758.json`

- **Ollama Benchmark Runs:**
  - `starter_v0/runs/v3-qwen7b_B_base_ollama_20261110T141156322981.json`
  - `starter_v0/runs/v3-llama3b_B_base_ollama_20261110T141654783121.json`

- **AI & Công cụ hỗ trợ:**
  - Sử dụng AI assistant hỗ trợ đọc run JSON, rà soát mismatch, soạn và điều chỉnh prompt, đề xuất evaluation case.
  - Tự đối chiếu metric với summary trong run JSON, kiểm tra danh sách case trong evaluation dataset và artifact hash trong version log.
