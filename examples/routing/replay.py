"""Replay fixed candidate configurations with the Python standard library."""
import argparse
import difflib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE.parents[1] / "dashboard" / "template.html"


def read(name):
    return json.loads((HERE / name).read_text())


def route(message, rules):
    for label, keywords in rules.items():
        for word in keywords:
            if word in message.lower().split():
                return label, word
    return "general", None


def replay():
    tasks = read("cases.json")
    configs = [("baseline", None), ("candidate-a", "baseline"), ("candidate-b", "baseline")]
    cases = [dict(id=t["id"], title=t["text"], group=t["expected"], context="期望类别 " + t["expected"],
                  series={}, trials={}, evidence={"runs": []}) for t in tasks]
    versions = []
    explanations = ["精确关键词路由。", "扩大匹配，优先尝试 my。", "为账单和账户各补一个具体关键词。"]
    for idx, (vid, parent) in enumerate(configs):
        config = read(vid + ".json")
        fixed = []
        lost = []
        for target, case in zip(tasks, cases):
            label, matched = route(target["text"], config)
            correct = int(label == target["expected"])
            case["series"][vid] = correct
            case["trials"][vid] = [correct]
            if parent and case["series"][parent] != correct:
                (fixed if correct else lost).append(case["id"])
            result = {"label": label, "matched": matched}
            case["evidence"]["runs"].append(dict(id=vid, version=vid, trial=1, seed="固定", official=correct,
                messages=[{"role":"user","content":target["text"]},{"role":"assistant","content":label}],
                calls=[{"message":1,"actor":"本地规则","label":"route","request":{"text":target["text"],"rules":config},"response":result}],
                analysis=f"命中 {matched!r}，输出 {label}；期望 {target['expected']}。"))
        score = sum(c["series"][vid] for c in cases)
        accepted = bool(parent and fixed and not lost)
        cfg = (HERE / (vid + ".json")).read_text()
        previous = (HERE / (parent + ".json")).read_text() if parent else ""
        versions.append(dict(id=vid,parent=parent,status=("accepted" if accepted else "rejected") if parent else "baseline",
            complete=True,metrics={"accuracy":score/len(cases)},surface="路由词表",change=explanations[idx],
            hypothesis=explanations[idx],problemStatement="invoice 和 unlock 未被基线识别。",risk="通用词可能抢占其他类别。",
            diff="".join(difflib.unified_diff(previous.splitlines(True),cfg.splitlines(True),fromfile=parent or "empty",tofile=vid)),
            config=cfg,gates=[],interpretation=f"{score}/{len(cases)}。修好 {fixed}，退步 {lost}。"))
    best = next(v["id"] for v in reversed(versions) if v["status"] in ("baseline","accepted"))
    return dict(title="CodeFree-Evolution · 配置回放",scope="固定的六条合成路由样例。候选由人预置，本页各结果由 replay.py 实际计算。",
        notice="门槛：相对父版至少修好一道题，且原先正确的题全部保持。此例演示记录与晋升，未运行模型搜索。",
        versions=versions,best=best,cases=cases,defaultCase="T3",metrics=[dict(key="accuracy",label="正确率",min=0,max=1,unit="%")],
        caseMetric=dict(label="是否正确",min=0,max=1,direction="higher"),review=dict(summary="采用具体词，保留父版作为比较基准。",rules=[]),
        problems=[dict(id="routing",title="两个类别缺少关键词",summary="在不干扰另两类请求的前提下扩展词表。",
            evidence="T2 与 T4 的输入在基线词表中无匹配。",conclusion="具体词修好 T2 和 T4，六个样例均通过。",
            caseIds=["T2","T4"],versionIds=["candidate-a","candidate-b"])])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--html", type=Path, help="write a standalone dashboard")
    args = parser.parse_args()
    data = replay()
    for v in data["versions"]:
        print(v["id"], v["status"], v["interpretation"])
    if args.html:
        page = TEMPLATE.read_text()
        marker = '<script id="report-data" type="application/json">'
        start = page.index(marker) + len(marker)
        end = page.index("</script>", start)
        args.html.write_text(page[:start]+json.dumps(data,ensure_ascii=False).replace("<",r"\u003c")+page[end:])
