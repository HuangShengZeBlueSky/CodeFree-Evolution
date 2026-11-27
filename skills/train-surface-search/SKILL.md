---
name: train-surface-search
description: 统一确定一份实验 Markdown 配置，调度归因与优化，运行真实评测、反馈和晋升。
---

# 实验监控

你负责配置与运行；归因负责解释失败并选 Target，优化负责产出完整候选。

公开配置版的实验边界：固定运行时、工具实现、数据划分与评分器。候选只修改 experiment.md 预先列出的声明式字段。若假设超出当前配置能力，记录缺口并交回监控。

```mermaid
flowchart TD
    A["沿用已确认要求；补齐缺项，写入唯一 experiment.md"] --> B["准备完整、全组件开启的 Parent YAML；验证实际加载"]
    B --> C["运行或恢复 Parent，收齐训练轨迹"]
    C --> D["交归因：同一配置、Parent、全部 case/trial"]
    D --> E{"有可处理的归因与 scope？"}
    E -->|有| F["交优化：归因、scope、Parent、历史反馈"]
    E -->|无| K["按配置结束或重新选题，记录原因"]
    F --> G["收齐候选、真实 diff、加载证据"]
    G --> H["按配置真实评测，检查请求送达和组件触发"]
    H --> I{"按配置判定"}
    I -->|继续 attempt| J["完整反馈交优化；保持本轮 Parent 与 scope"]
    J --> F
    I -->|进入下一轮| L["晋升候选或保留 Parent"]
    L --> C
    I -->|预算或停止条件满足| K
```

所有实验参数由你先沟通或采用合理默认，全部写入 MD；其他角色不另设默认。新实验默认记忆、压缩、任务技能、参数校验、业务校验、结果增强全部开启且有实际内容，只有用户明确要求消融才关闭。运行时仍须对缺字段报错，不能隐式补齐。

- 配置实验时读[单 MD 配置合同](references/experiment-config.md)。
- 派发和接收任务时读[三角色交接](references/handoff-contract.md)。
- 启动、评测与恢复时读[执行与验收](references/execution.md)。
