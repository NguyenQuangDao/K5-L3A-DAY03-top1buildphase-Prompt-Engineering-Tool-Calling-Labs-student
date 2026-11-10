# Team

## Thông tin nhóm

- Tên nhóm: top1buildphase
- Lớp: L3A
- Repo nhóm: `K5-L3A-DAY03-top1buildphase-Prompt-Engineering-Tool-Calling-Labs-student` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt: https://github.com/NguyenQuangDao/K5-L3A-DAY03-top1buildphase-Prompt-Engineering-Tool-Calling-Labs-student — nhánh `main` — commit chốt: commit cuối cùng trên `main` trước deadline

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Nguyễn Vũ Thành Long | 2A202603635 | 26ai.longnvt2@vinuni.edu.vn | `nvl191` | Prompt & Eval Lead: `system_prompt.md`, `tools.yaml`, v0–v3, `version_log.csv`, `eval_group.json` |
|   2 | Nguyễn Gia Bảo | 2A202603647 | 26ai.baong5@vinuni.edu.vn | `Billy3005` | Tool & Testing Engineer: 4 tool mới, unit test, sửa bug tool, Small Local Model (Step 7) |
|   3 | Nguyễn Quang Đạo | 2A202603614 | _(tự điền)_ | `NguyenQuangDao` | UI, Live Demo & Report Lead: `app.py`, `ui_components/`, poster, REPORT, deploy |

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
