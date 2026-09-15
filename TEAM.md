# TEAM - Day04, K4-L3B

**Lam nhom.** Moi nguoi tu viet va commit phan INDIVIDUAL cua minh.

## Thong tin bai nop

- Ten nhom: BuiLeThaiSon
- Nguoi dai dien / MSSV: Bui Le Thai Son - 02880
- Ten repo: `K4-L3B-Day04-BuiLeThaiSon-PromptEngineeringToolCalling`
- URL repo, nhanh nop, commit chot: https://github.com/sonbui69000-hue/K4-L3B-Day04-BuiLeThaiSon-PromptEngineeringToolCalling, `main`, `311580e`
- Deadline ap dung va link thong bao doi han neu co: Mac dinh 23:59 ngay lam lab, Asia/Ho_Chi_Minh; khong co thong bao doi han.

## Thanh vien

| Ho va ten | MSSV | GitHub | Vai tro va cong viec | File/commit/PR |
|---|---|---|---|---|
| Bui Le Thai Son | 02880 | sonbui69000-hue | Ca nhan 1 thanh vien: cai dat provider, chay eval v0-v3, phan tich loi, sua `system_prompt.md`, sua `tools.yaml`, viet `eval_group.json`, tao bonus loaner inventory tool, tao UI chat, luu transcript, hoan thien report. | `starter_v0/artifacts/system_prompt.md`, `starter_v0/artifacts/tools.yaml`, `starter_v0/data/eval_group.json`, `starter_v0/ui_server.py`, `starter_v0/tools/check_loaner_inventory/`, `starter_v0/helpdesk_data/loaners.json`, `starter_v0/data/eval_bonus.json`, `starter_v0/artifacts/version_log.csv`, `starter_v0/runs/`, `starter_v0/transcripts/` |

## Nhan xet chung

- Ket qua va bang chung: Base v0 tang tu 21/30 len v3 30/30; group dat 9/10; adversarial dat 10/12; bonus loaner inventory dat 5/5. Evidence nam trong `starter_v0/runs/` va `starter_v0/artifacts/version_log.csv`.
- Thay doi hieu qua nhat: v2 sua `tools.yaml`, lam ro category cua KB, lookup user, environment, confirmation boundary; accuracy base tang tu 0.7333 len 0.9333.
- Gioi han con lai: adversarial con 2 case stale/role-spoof confirmation co the van goi action thay vi clarify; group run con 1 loi `policy_area` trong case external-tools policy; adversarial con 2 case stale/role-spoof confirmation.
- Cach phan cong va tich hop: Nhom 1 nguoi nen tat ca phan viec duoc thuc hien va kiem tra boi Bui Le Thai Son; dung run JSON, transcript UI `starter_v0/transcripts/v3_openrouter_ui_20260915T203625184631.transcript.json` va version log lam bang chung.

## INDIVIDUAL

### Bui Le Thai Son - 02880

- Phan viec va file/commit/PR: Thuc hien toan bo lab, gom prompt/tool iteration, eval base/group/adversarial, group eval cases, UI, transcript va report. File chinh: `system_prompt.md`, `tools.yaml`, `eval_group.json`, `eval_bonus.json`, `ui_server.py`, `check_loaner_inventory`, `REPORT.md`, `version_log.csv`.
- Quyet dinh, kho khan va cach xu ly: Bat dau tu loi wrong tool/missing info/wrong boundary; chia thanh cac lan sua nho v1-v3 de co evidence ro. Khi adversarial thap, bo sung rule ve fake confirmation, stale confirmation, secret trong ticket va internal ID khi web search; them bonus tool loaner inventory doc du lieu gia lap.
- Dieu da hoc: Tool calling can prompt va schema cung ro; automatic score chi la diem dau, van phai doc tool calls/tool results de biet co goi sai action hay lo du lieu khong.
- AI/cong cu da dung va cach kiem tra: Dung Codex ho tro doc repo, sua artifact, tao UI va tong hop report; kiem tra bang `run_eval.py`, run JSON, transcript UI va CSV parse.
