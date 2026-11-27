# 工作台的数据接入

替换 [HTML](template.html) 的 `report-data`，或沿用项目服务提供同等内容。
这是报告层结构，不是评测平台的强制协议；不要让用户改 Bench 来适配报告。

| 层级 | 内容与示例字段 |
| --- | --- |
| 实验 | `title, scope, notice, best, companion?`；明确快照边界、覆盖与证据缺项 |
| 指标 | `metrics[{key,label,min,max,unit}]`；当前模板百分比用 0–1 值配 `unit:"%"` |
| 任务指标 | `caseMetric{label,min,max,direction}`；direction 为 `higher` 或 `lower`，不强制成功率 |
| 版本 | `versions[{id,parent,status,complete,metrics, ...}]`；按实际生成顺序，晋升以权威记录为准 |
| 决策内容 | `problemStatement,surfaceReason,change,hypothesis,risk,interpretation,gates[],diff,diffExplanation,original,config,source` |
| Gate | `{name,parent,candidate,decision,reason}`，三个展示值可为明确单位的文字，不混 Target 和全量 |
| 问题 | `problems[{id,title,summary,surfaceSummaries?,evidence,conclusion,caseIds[],versionIds[],limit?}]`；summary 用中文解释机制，surfaceSummaries 按修改面概括实际措施 |
| Case | `{id,title,group,series:{version:数值或null},trials:{version:向量},commonFailure,context,evidenceUrl}` |
| 证据组 | `evidence` 或 `evidenceUrl` → `{runs:[{id,version,trial,seed,official,analysis,note,messages,calls,contexts,source,auditUrl?}]}` |
| 调用与上下文 | `calls[{message,actor,label,request,response,source}]`；`contexts[{title,visibility,content}]` |
| 经验审查 | `review{summary,rules:[{title,current,recommended,text,reason,source}],current,risk,design,causal}` |

未保存的原始分析不能补造为原文；本次从 diff 提取的解释标明“本次审查”。
缺失 trial 用 null 留空，不当成失败。可比集合由数据适配器核对任务、条件与实际 seed 后提供。
连续指标较多时，模板保留逐 case current / 历史最优比较；需要散点图可替换优势矩阵的绘图，不改变其含义。
无独立 User、无 Policy 或无继承时，以实际参与者、规则与并列版本代替，不凭空补齐概念。
可用 `surfaceLabels`、版本 `shortLabel`、case `displayTitle` 提供简短中文展示名；完整原始标识仍保留，别名不参与计算。
