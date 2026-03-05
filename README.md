# dual-llm-meeting

一个可复用的 Codex Skill 包，用于组织 **Codex CLI × Antigravity Opus** 的轮次制会议（Round-based），并输出可执行、可审计的工程结论。

## 当前开发状态

✅ 已实现内容：
- 标准 Skill 入口：`dual-llm-meeting/SKILL.md`
- 角色提示词模板：`dual-llm-meeting/references/prompt-contract.md`
- 结构化输出 Schema：`dual-llm-meeting/references/round.schema.json`
- 会议工作区初始化脚本：`dual-llm-meeting/scripts/init_meeting.py`
- 支持 **项目/问题分组工作区**：`<project>/.meeting/<workspace>/`

## 这次改进（你关心的点）

为了解决“不同项目、不同问题的产物混在一起”的问题：

- 产物不再只放在 `<project>/.meeting/` 根下，而是放在：
  - `<project>/.meeting/<workspace>/`
- `workspace` 由你在初始化时指定（建议用项目名或问题编号）
- 所有输出仍然在**项目目录内**，不会写到 skill 目录

---

## 功能说明

### 1) 轮次化会议流程（强制收敛）
- 支持 Round 0/1/2（可选 Round 3）
- 将分歧统一沉淀为 `conflicts`，由 Chair 仲裁
- 输出决策与执行材料，而非无限对话

### 2) 分组产物管理（按项目/问题隔离）
初始化后会生成：

```text
<project>/.meeting/<workspace>/
  agenda.md
  repo_snapshot.md
  transcript.md
  conflicts.md
  decision.md
  patch_plan.json
  tests.md
  risk_register.md
  workspace.md
  rounds/
    codex_round1.json
    opus_round1.json
    codex_round2.json
    opus_round2.json
  schemas/
    round.schema.json
```

### 3) 角色分工约束
- **Codex**：负责 `patch_plan`、`tests`、`tradeoffs`
- **Opus**：负责 `risks`、`conflicts`、`open_questions`
- **Chair**：负责议程编排、冲突收敛、最终定稿

### 4) tmux 总线约定
- 固定 3 个 pane：Chair / Codex / Antigravity(Opus)
- Opus 输出以 `<<<END_JSON>>>` 结束，便于 `tmux capture-pane` 稳定截取

---

## 快速开始

### 环境要求
- Python 3.8+
- tmux（推荐）
- Codex CLI
- Antigravity（Opus 在 UI 内）

### 初始化（按项目/问题命名 workspace）
在项目根目录执行：

```bash
python3 dual-llm-meeting/scripts/init_meeting.py --root . --workspace payment-retry-bugfix
```

例如：
- 项目 A 的登录问题：`--workspace project-a-login`
- 项目 A 的支付问题：`--workspace project-a-payment`
- 项目 B 的迁移问题：`--workspace project-b-migration`

这样不同任务会在不同子目录中独立产出，互不覆盖。

### 运行顺序
1. 填写 `.meeting/<workspace>/agenda.md` 与 `.meeting/<workspace>/repo_snapshot.md`
2. 进行 Round 0/1/2（每轮保存 JSON 到 `.meeting/<workspace>/rounds/`）
3. 基于冲突收敛结果更新：
   - `.meeting/<workspace>/decision.md`
   - `.meeting/<workspace>/patch_plan.json`
   - `.meeting/<workspace>/tests.md`
   - `.meeting/<workspace>/risk_register.md`

---

## 目录结构

```text
.
├── README.md
├── solution.md
└── dual-llm-meeting/
    ├── SKILL.md
    ├── references/
    │   ├── prompt-contract.md
    │   └── round.schema.json
    └── scripts/
        └── init_meeting.py
```

---

## 如何在 Codex 中使用该 Skill

当需求涉及“多模型会议收敛 / 双模型仲裁 / 可审计决策”时，触发本 Skill：
- 读取 `dual-llm-meeting/SKILL.md`
- 使用 `references/prompt-contract.md` 组装轮次 prompt
- 用 `references/round.schema.json` 校验输出
- 用 `scripts/init_meeting.py` 在项目目录创建 scoped workspace

---

## 开发建议（下一步）

- 增加自动 JSON 校验脚本（批量校验 `.meeting/<workspace>/rounds/*.json`）
- 增加 tmux 自动投喂/抓取脚本（`send-keys` + `capture-pane`）
- 增加 round 汇总器，自动生成 `decision.md` 初稿
