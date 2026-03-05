# Dual-LLM Meeting Skill（Codex CLI × Antigravity Opus 4.6）

> 在 **不将 Opus 4.6 从 Antigravity 单独抽离** 的前提下，构建一个可审计、可收敛、可落地的双模型会议系统。
>
> 核心机制：**Round-based 轮次会议 + Chair（主席）仲裁**，用结构化产物替代无边界群聊。

---

## 1) 背景与目标

你当前具备：
- **Codex CLI**（工程落地强，适合结构化执行）
- **Antigravity 内 Opus 4.6**（需保留在 UI 内，降低风控风险）
- **tmux**（天然适合作为会议总线）

你希望解决：
1. 两个模型方案经常冲突，缺少统一收敛机制。
2. 讨论过程不可审计、不可复现。
3. 结果要能直接指导工程执行（patch plan / tests / risk / 决策记录）。

---

## 2) 设计原则（为什么不是“自由群聊”）

自由群聊常见问题：
- 话题发散，上下文漂移。
- 讨论难以追责（谁在何时做了关键决定）。
- 输出偏观点，不是可执行计划。

本方案采用轮次制，确保：
- 每轮目标明确（对齐 → 对撞 → 收敛 → 可选执行）。
- 每轮强制结构化输出。
- 所有分歧转为 `conflicts[]` 可裁决条目。

---

## 3) 总体架构

### 3.1 三个核心角色

1. **Chair（主席 / Orchestrator）**
   - 负责编排轮次、管理议程、固化冲突、产出最终决策文档。
   - 建议用 Python 脚本实现。

2. **Codex Endpoint（工程落地者）**
   - 通过 `codex exec` 非交互执行。
   - 每轮输出结构化 JSON（重点：`patch_plan`、`tests`、`tradeoffs`）。

3. **Antigravity(Opus) Endpoint（架构审稿者）**
   - Opus 始终运行在 Antigravity UI 内。
   - 通过 tmux 投喂轮次议题并抓取回复。

> 关键点：Antigravity 端点被视为“受限 UI 端点”，由 Chair 严格控节奏，不让会话自由跑飞。

---

## 4) 强制角色协议

### 4.1 Codex（实现导向）
必填输出：
- `patch_plan`（文件级、步骤级修改计划）
- `tests`（可验证测试与验收步骤）
- `tradeoffs`（方案取舍）
- `open_questions`（最小化）

权限建议：
- Round 0–2：`read-only`
- Round 3（可选执行）：`workspace-write`

### 4.2 Opus（审稿导向）
必填输出：
- `risks`
- `conflicts`
- `open_questions`

职责边界：
- 做 critique / alternatives / 风险施压
- 不直接接管最终 patch plan

### 4.3 Chair（收敛导向）
- 统一议程 `agenda`
- 将分歧固化为 `conflicts[]`
- 只围绕冲突和澄清项提问
- 输出最终 `decision.md`

---

## 5) 标准产物目录

在仓库中创建：

```text
.meeting/
  agenda.md
  repo_snapshot.md
  transcript.md
  conflicts.md
  decision.md
  patch_plan.json
  tests.md
  risk_register.md
  rounds/
    codex_round1.json
    opus_round1.json
    codex_round2.json
    opus_round2.json
  schemas/
    round.schema.json
```

---

## 6) 会议轮次（推荐 2–3 轮）

### Round 0：上下文对齐
Chair：
- 产出 `repo_snapshot.md`（tree + 模块摘要 + 约束）
- 产出 `agenda.md`（目标/非目标/验收/硬约束）

Codex：
- 最小改动路径草案
- 初步风险与待澄清项

Opus：
- 审核验收标准与风险完整性

### Round 1：方案对撞
输入：`agenda + repo_snapshot + round0 摘要`
- Codex：`patch_plan v1 + tests v1`
- Opus：`critique + risks + alternatives`
- Chair：`conflicts v1`

### Round 2：冲突收敛（定稿）
输入：`conflicts v1`
- Codex：`patch_plan v2 + tests v2`
- Opus：`go/no-go + remaining risks`
- Chair：定稿 `decision.md + patch_plan.json + tests.md + risk_register.md`

### Round 3（可选）：自动执行
- 允许 Codex 按 `patch_plan` 真正改代码并跑测试
- Chair 记录 diff / commit / PR 信息

---

## 7) tmux 会议总线建议

### 7.1 面板布局
- Pane A：Chair（orchestrator）
- Pane B：Codex
- Pane C：Antigravity（Opus UI）

建议固定 pane id，避免依赖焦点切换。

### 7.2 Opus 抓取约定（关键）
为了让 `tmux capture-pane` 可稳定截取：
- Opus 每轮回复必须为 **JSON**（或严格标题块）
- 末尾必须输出结束标记：`<<<END_JSON>>>`

---

## 8) 统一输出 Schema（建议）

```json
{
  "assumptions": [],
  "proposal": [],
  "patch_plan": [
    {"file": "path", "change": "what/why", "steps": ["..."]}
  ],
  "tests": [],
  "tradeoffs": [
    {"option": "A", "pros": [], "cons": [], "decision": "pick/avoid"}
  ],
  "risks": [
    {"risk": "...", "impact": "low/med/high", "mitigation": "..."}
  ],
  "conflicts": [
    {"topic": "...", "options": ["A", "B"], "recommendation": "...", "reason": "..."}
  ],
  "open_questions": []
}
```

字段要求：
- Codex 重点必填：`patch_plan`, `tests`, `tradeoffs`
- Opus 重点必填：`risks`, `conflicts`, `open_questions`

---

## 9) Chair 工作流（落地顺序）

1. 构建 `repo_snapshot`
2. 生成 `agenda`
3. 触发 Codex Round N 并落盘
4. 投喂 Opus Round N 并抓取落盘
5. 聚合冲突并生成下一轮 prompt
6. 产出最终四件套：
   - `decision.md`
   - `patch_plan.json`
   - `tests.md`
   - `risk_register.md`

权限策略：默认只读，最终执行轮再升写权限。

---

## 10) 里程碑路线图

### M0（1 天内）
- 先跑通 Round 0–2
- Codex 输出 JSON + 落盘
- Opus 手工复制粘贴
- Chair 能产出 `decision.md`

### M1（2–3 天）
- tmux 半自动化：`send-keys` + `capture-pane`
- 自动 transcript / conflicts / decision

### M2（后续）
- 启用自动执行（按 `patch_plan` 改代码 + 跑测试）
- 自动沉淀 diff / commit / PR

---

## 11) 使用方式（输入 / 输出）

### 你每次需要提供
- repo 路径
- 问题描述
- 约束条件
- 验收标准

### Skill 产出
- `decision.md`（统一方案）
- `patch_plan.json`（执行清单）
- `tests.md`（验证步骤）
- `risk_register.md`（风险与缓释）
- `transcript.md`（会议纪要）

---

## 12) 可扩展项

- 增加 Gemini CLI 第三席（安全/性能专项审计）
- 自动 top-K 相关代码片段抽取（控制 token）
- 冲突仲裁策略升级（投票 / 置信度 / 成本函数）

---

## 13) 结论

在 “Opus 必须留在 Antigravity UI 内” 的约束下，**tmux 会议总线 + Chair 轮次仲裁** 是稳健、可审计、可落地的方案。

- Codex：负责可执行落地
- Opus：负责审稿挑错与风险施压
- Chair：负责冲突收敛与定稿

这套机制的目标不是让模型“聊得更久”，而是让系统**更快产出可执行最终方案**。
