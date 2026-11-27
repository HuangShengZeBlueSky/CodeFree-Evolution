# CodeFree-Evolution

**Code-free self-evolution for a configurable agent harness.** Three Markdown skills run the improvement loop: a monitor evaluates the current agent, an attributor locates failures in execution traces, and an optimizer proposes a complete configuration. A separate dashboard lets a human inspect the evidence behind each promotion.

**用三个 Skill 驱动 Agent 自进化。** 用户给出任务、预算和允许修改的配置字段。一个具备模型调用、文件操作和命令执行能力的宿主加载这些 Skill，调用现有评测器。搜索期间固定代码、模型权重、任务和评分器，只演化运行时已经支持的配置，例如工具说明、记忆写入规则或校验参数。

| Role | Input | Handoff |
| --- | --- | --- |
| [Monitor · 监控](skills/train-surface-search/SKILL.md) | Experiment contract, parent configuration, budget | Complete runs, paired scores, regressions and a promotion decision |
| [Attributor · 归因](skills/attribute-surface-search/SKILL.md) | Parent trajectories across failed and successful trials | Case-level evidence, mechanism groups and a frozen repair scope |
| [Optimizer · 优化](skills/evo-surface-search/SKILL.md) | Parent, scope, attribution report and prior feedback | Loadable candidate configuration, diff, predicted trigger and a falsification condition |

The monitor sends the same parent and scope back for another attempt, or selects the parent for the next round. The [handoff contract](skills/train-surface-search/references/handoff-contract.md) defines what each role must deliver. The dashboard consumes those decisions after evaluation.

## Try the dashboard

Download [the standalone dashboard](dashboard/index.html) and open it in a browser. Select a candidate to inspect its parent and configuration diff. Select a case to compare its inputs, outputs and matched rules across versions. The [empty template](dashboard/template.html) and [data contract](dashboard/data-contract.md) support other benchmarks.

With Python 3, replay the six synthetic routing cases from the repository root:

```sh
python3 examples/routing/replay.py --html dashboard/index.html
```

The demo takes two **prewritten** configurations and evaluates both against the same parent. The baseline solves 4/6. Candidate A adds the broad word `my`, breaks two previously correct cases and is rejected at 2/6. Candidate B adds `invoice` and `unlock`, preserves the four baseline successes and is promoted at 6/6. The per-case tool records in the dashboard come from the deterministic Python router. This replay demonstrates selection and inspection; it makes no LLM requests.

## Start an evolution run

1. Connect a configurable agent, a fixed evaluation command and a trace exporter. The example replay works independently of these services.
2. Give the three skill directories to your agent host. Start the monitor with the instruction below and point it to your benchmark. Supply your split, budget and gate in advance.
3. Review the experiment contract, then let the monitor dispatch the attribution and optimization roles. Each round writes a complete candidate, a diff, the observed triggers and paired evaluation results. Use development traces for diagnosis, a separate selection set for promotion, and an untouched test set for the final evaluation.

> 使用实验监控 Skill，从当前父配置开始。在 experiment.md 中记录已有的加载、运行、评分命令、允许改动的字段、预算和晋升规则。每轮把训练轨迹交给归因 Skill，再把归因和本轮固定的问题范围交给优化 Skill。按同一批选型案例评测父版与候选，将改善、退步、触发证据和保留决定交给看板。若现有配置无法表达修复，记录缺口并结束该尝试。

The archived protocol targets a Pydantic-style YAML harness. Map its fields and commands to your runtime before running a new benchmark. The optional experiment-config helper requires PyYAML. The three role specifications and dashboard are complementary: **code-free** describes how candidates are changed during evolution. Running the model, loading configurations and evaluating tasks remain responsibilities of the host and benchmark.
