# DAY10 — TEAM BOARD

> Bảng theo dõi tiến độ thực tế của nhóm (được cập nhật từ GitHub Issues & Pull Requests bởi `.github/workflows/team-progress.yml`).
> - **Issues:** https://github.com/hungpixi/K5-L23-Day10-Dataset-Release-Handover/issues
> - **Pull Requests:** https://github.com/hungpixi/K5-L23-Day10-Dataset-Release-Handover/pulls
> - **Actions:** https://github.com/hungpixi/K5-L23-Day10-Dataset-Release-Handover/actions

## Phân công 6 thành viên

| Thành viên | MSSV | GitHub | Vai trò chính | Phase | Issue hiện tại | Trạng thái |
|---|---|---|---|---|---|---|
| Phạm Phú Nguyễn Hưng | `2A202604062` | `@hungpixi` | Lead · Validator (9 luật) + CI + Integration | P0–P1, Integration | `#1`, `#2`, `#9`, `#10` | Đang thiết lập |
| Đỗ Anh Hoàng | `2A202604061` | `@AnhHoangDepTrai` | Cross-check Detection ↔ Panoptic | P2 | `#3` | Chưa nhận |
| Bùi Văn Thịnh | `2A202604040` | `@buivanthinhtxt-del` | Visual Review & QC (`review_log.csv`) | P2 | `#4` | Chưa nhận |
| Nguyễn Xuân Việt | `2A202604045` | `@ngxuanviet` | Release Gate (2% + Lineage) & Dataset v2 Handover | P3–P4 | `#5`, `#6` | Chưa nhận |
| Hoàng Trọng Trà | `2A202603342` | `@trahoangdev` | Ticket Traceability (`tier_a`, `tier_b`, `notify`) | P5 | `#7` | Chưa nhận |
| Nguyễn Quốc Hưng | `2A202603324` | `@Soraxolo` | Security (`security.md`), Hidden-test Prep & Reporting | P6 | `#8` | Chưa nhận |

<!-- TEAM_PROGRESS_START -->
_Cập nhật tự động từ GitHub API lúc 2026-11-19 10:01 UTC_

| # | Issue | Assignees | Labels | State |
|---|---|---|---|---|
| [#1](https://github.com/hungpixi/K5-L23-Day10-Dataset-Release-Handover/issues/1) | P0 — Setup repository & Team Onboarding | @hungpixi | `phase:P0`, `type:docs`, `priority:P0`, `status:done` | DONE |
| [#2](https://github.com/hungpixi/K5-L23-Day10-Dataset-Release-Handover/issues/2) | P1 — Implement & Verify 9 Validator Rules | @hungpixi | `phase:P1`, `type:code`, `priority:P0`, `status:in-progress` | DONE |
| [#3](https://github.com/hungpixi/K5-L23-Day10-Dataset-Release-Handover/issues/3) | P2 — Detection/Panoptic Cross-check & Candidates Tuning | _Chưa assign_ | `phase:P2`, `type:code`, `priority:P0`, `status:ready` | OPEN |
| [#4](https://github.com/hungpixi/K5-L23-Day10-Dataset-Release-Handover/issues/4) | P2 — Human Visual Review & QC (review_log.csv) | _Chưa assign_ | `phase:P2`, `type:review`, `type:qc`, `priority:P0`, `status:ready` | OPEN |
| [#5](https://github.com/hungpixi/K5-L23-Day10-Dataset-Release-Handover/issues/5) | P3 — Release Gate (2% Threshold) & Lineage | _Chưa assign_ | `phase:P3`, `type:qc`, `priority:P1`, `status:ready` | OPEN |
| [#6](https://github.com/hungpixi/K5-L23-Day10-Dataset-Release-Handover/issues/6) | P4 — Dataset v2, Manifest & Handover (check_handover.py) | _Chưa assign_ | `phase:P4`, `type:code`, `type:qc`, `priority:P0`, `status:ready` | OPEN |
| [#7](https://github.com/hungpixi/K5-L23-Day10-Dataset-Release-Handover/issues/7) | P5 — Ticket Traceability (tier_a, tier_b, notify) | _Chưa assign_ | `phase:P5`, `type:code`, `priority:P1`, `status:ready` | OPEN |
| [#8](https://github.com/hungpixi/K5-L23-Day10-Dataset-Release-Handover/issues/8) | P6 — Security (security.md), Hidden-test Prep & Reporting | @Soraxolo | `phase:P6`, `type:docs`, `type:qc`, `priority:P1`, `status:ready` | OPEN |
| [#9](https://github.com/hungpixi/K5-L23-Day10-Dataset-Release-Handover/issues/9) | Integration + Regression Verification | @hungpixi | `phase:P6`, `type:code`, `type:qc`, `priority:P0`, `status:ready` | OPEN |
| [#10](https://github.com/hungpixi/K5-L23-Day10-Dataset-Release-Handover/issues/10) | Final Handover + Presentation & LMS Submission | @hungpixi | `phase:P6`, `type:docs`, `priority:P0`, `status:ready` | OPEN |
| [#11](https://github.com/hungpixi/K5-L23-Day10-Dataset-Release-Handover/issues/11) | Individual contribution evidence — Phạm Phú Nguyễn Hưng (2A202604062) | @hungpixi | `type:qc`, `status:ready` | OPEN |
| [#12](https://github.com/hungpixi/K5-L23-Day10-Dataset-Release-Handover/issues/12) | Individual contribution evidence — Đỗ Anh Hoàng (2A202604061) | _Chưa assign_ | `type:qc`, `status:ready` | OPEN |
| [#13](https://github.com/hungpixi/K5-L23-Day10-Dataset-Release-Handover/issues/13) | Individual contribution evidence — Bùi Văn Thịnh (2A202604040) | _Chưa assign_ | `type:qc`, `status:ready` | OPEN |
| [#14](https://github.com/hungpixi/K5-L23-Day10-Dataset-Release-Handover/issues/14) | Individual contribution evidence — Nguyễn Xuân Việt (2A202604045) | _Chưa assign_ | `type:qc`, `status:ready` | OPEN |
| [#15](https://github.com/hungpixi/K5-L23-Day10-Dataset-Release-Handover/issues/15) | Individual contribution evidence — Hoàng Trọng Trà (2A202603342) | @trahoangdev | `type:qc`, `status:ready` | OPEN |
| [#16](https://github.com/hungpixi/K5-L23-Day10-Dataset-Release-Handover/issues/16) | Individual contribution evidence — Nguyễn Quốc Hưng (2A202603324) | @Soraxolo | `type:qc`, `status:ready` | OPEN |

**Pull Requests:** 0 total (0 open, 0 merged)
<!-- TEAM_PROGRESS_END -->
