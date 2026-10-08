#!/usr/bin/env python3
import argparse
import csv
from pathlib import Path


def to_int(value: str) -> int:
    if value is None:
        return 0
    value = str(value).strip()
    if not value:
        return 0
    return int(float(value))


def load_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def percent(used: int, requested: int) -> str:
    if requested <= 0:
        return "N/A"
    return f"{used / requested * 100:.1f}%"


def risk_level(cpu_ratio, mem_ratio, restarts, no_request):
    score = 0
    if no_request:
        score += 2
    if cpu_ratio is not None and cpu_ratio >= 0.8:
        score += 2
    if mem_ratio is not None and mem_ratio >= 0.8:
        score += 2
    if restarts >= 3:
        score += 1

    if score >= 4:
        return "高"
    if score >= 2:
        return "中"
    return "低"


def build_rows(pods, tops):
    top_map = {(row["namespace"], row["pod"]): row for row in tops}
    rows = []

    for pod in pods:
        key = (pod["namespace"], pod["pod"])
        top = top_map.get(key, {})

        cpu_request = to_int(pod.get("cpu_request_m"))
        mem_request = to_int(pod.get("memory_request_mib"))
        cpu_limit = to_int(pod.get("cpu_limit_m"))
        mem_limit = to_int(pod.get("memory_limit_mib"))
        restarts = to_int(pod.get("restarts"))
        cpu_used = to_int(top.get("cpu_used_m"))
        mem_used = to_int(top.get("memory_used_mib"))

        cpu_ratio = (cpu_used / cpu_request) if cpu_request > 0 else None
        mem_ratio = (mem_used / mem_request) if mem_request > 0 else None

        no_request = cpu_request <= 0 or mem_request <= 0
        no_limit = cpu_limit <= 0 or mem_limit <= 0
        high_cpu = cpu_ratio is not None and cpu_ratio >= 0.8
        high_mem = mem_ratio is not None and mem_ratio >= 0.8

        flags = []
        if no_request:
          flags.append("缺失request")
        if no_limit:
          flags.append("缺失limit")
        if high_cpu:
          flags.append("CPU偏高")
        if high_mem:
          flags.append("内存偏高")
        if restarts >= 3:
          flags.append("重启偏高")
        if not flags:
          flags.append("正常")

        rows.append(
            {
                "namespace": pod["namespace"],
                "pod": pod["pod"],
                "status": pod.get("status", ""),
                "cpu_request": cpu_request,
                "mem_request": mem_request,
                "cpu_used": cpu_used,
                "mem_used": mem_used,
                "cpu_usage": percent(cpu_used, cpu_request),
                "mem_usage": percent(mem_used, mem_request),
                "restarts": restarts,
                "risk": risk_level(cpu_ratio, mem_ratio, restarts, no_request),
                "flags": "、".join(flags),
            }
        )

    risk_order = {"高": 0, "中": 1, "低": 2}
    rows.sort(key=lambda x: (risk_order[x["risk"]], x["namespace"], x["pod"]))
    return rows


def render_report(rows):
    total = len(rows)
    no_request_count = sum("缺失request" in r["flags"] for r in rows)
    no_limit_count = sum("缺失limit" in r["flags"] for r in rows)
    high_cpu_count = sum("CPU偏高" in r["flags"] for r in rows)
    high_mem_count = sum("内存偏高" in r["flags"] for r in rows)
    restart_count = sum("重启偏高" in r["flags"] for r in rows)

    lines = [
        "# Kubernetes 工作负载巡检报告",
        "",
        "## 概览",
        "",
        f"- 工作负载总数：`{total}`",
        f"- 缺失 request：`{no_request_count}`",
        f"- 缺失 limit：`{no_limit_count}`",
        f"- CPU 偏高：`{high_cpu_count}`",
        f"- 内存偏高：`{high_mem_count}`",
        f"- 重启偏高：`{restart_count}`",
        "",
        "## 明细",
        "",
        "| namespace | pod | status | CPU使用/request | 内存使用/request | restarts | 风险等级 | 巡检结果 |",
        "|---|---|---|---|---|---:|---|---|",
    ]

    for row in rows:
        lines.append(
            f"| {row['namespace']} | {row['pod']} | {row['status']} | "
            f"{row['cpu_used']}m / {row['cpu_request']}m ({row['cpu_usage']}) | "
            f"{row['mem_used']}Mi / {row['mem_request']}Mi ({row['mem_usage']}) | "
            f"{row['restarts']} | {row['risk']} | {row['flags']} |"
        )

    lines.extend(
        [
            "",
            "## 建议",
            "",
            "1. 优先补齐缺失 request/limit 的工作负载，避免资源不可控。",
            "2. 对 CPU 或内存使用率持续偏高的工作负载做容量复核。",
            "3. 对重启次数偏高的工作负载补充日志、事件和发布变更排查。",
            "4. 把这类巡检接入日常治理流程，而不是只在故障后手工排查。",
            "",
        ]
    )
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Audit Kubernetes workloads from CSV files.")
    parser.add_argument("--pods", required=True, help="Path to pods.csv")
    parser.add_argument("--top", required=True, help="Path to top.csv")
    parser.add_argument("--output", required=True, help="Output markdown report path")
    args = parser.parse_args()

    pods = load_csv(Path(args.pods))
    tops = load_csv(Path(args.top))
    rows = build_rows(pods, tops)
    report = render_report(rows)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")
    print(f"报告已生成: {output_path}")


if __name__ == "__main__":
    main()
