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
