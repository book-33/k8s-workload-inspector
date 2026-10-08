# k8s-workload-inspector

一个轻量的 Kubernetes 工作负载巡检项目，用来做资源基线检查、异常负载识别和简易报告输出。

这个项目适合放到 GitHub 作为公开作品，原因有三个：

1. 它和 `平台工程 / 云平台基础设施 / AI Infra` 都有关联。
2. 它能体现你对 `Kubernetes、资源治理、稳定性、自动化` 的理解。
3. 代码不重，但思路比较像真实生产场景里的巡检工具。

## 项目做什么

脚本会读取两份输入文件：

- `pods.csv`：工作负载的资源配置与运行信息
- `top.csv`：实时资源使用情况

然后输出一个 Markdown 报告，帮助你识别这些问题：

- 没有设置 CPU / 内存 request
- 没有设置 limit
- CPU 或内存使用率偏高
- 重启次数偏高
- 需要优先关注的工作负载

## 为什么这个项目适合转岗展示

如果你投 `云平台基础设施工程师`，可以把它讲成：

- 我对 Kubernetes 资源治理和平台规范有长期兴趣
- 我会把巡检经验沉淀成工具，而不是只靠人工排查
- 我关注 request / limit、资源利用率、稳定性风险和治理优先级

如果你投 `AI算力平台工程师`，可以把它讲成：

- 这是我从通用 K8s 资源治理向 AI Infra 迁移的起点
- 虽然它还不是 GPU 集群工具，但思路上已经在做平台巡检、资源视角分析和异常识别
- 后续可以继续扩展到 GPU 资源、训练作业、推理服务、任务队列等场景

## 目录结构

```text
k8s-workload-inspector/
├── README.md
├── scripts/
│   └── audit_k8s_workloads.py
└── examples/
    ├── pods.csv
    ├── top.csv
    └── sample_report.md
```

## 输入格式

### `pods.csv`

字段如下：

```csv
namespace,pod,cpu_request_m,memory_request_mib,cpu_limit_m,memory_limit_mib,restarts,status
```

说明：

- `cpu_request_m`：毫核，例如 `500`
- `memory_request_mib`：MiB，例如 `1024`
- `cpu_limit_m` / `memory_limit_mib`：limit 配置
- `restarts`：重启次数
- `status`：运行状态

### `top.csv`

字段如下：

```csv
namespace,pod,cpu_used_m,memory_used_mib
```

## 运行方式

在项目根目录执行：

```bash
python3 scripts/audit_k8s_workloads.py \
  --pods examples/pods.csv \
  --top examples/top.csv \
  --output examples/sample_report.md
```

执行后会在指定位置生成一份 Markdown 报告。

## 示例输出

报告会包含：

- 总工作负载数
- 缺失 request / limit 的数量
- 高 CPU / 高内存风险数量
- 高重启风险数量
- 每个工作负载的巡检结果表格

## 可以继续扩展什么

如果你想把这个项目再做得更像面试作品，可以继续加这些：

- 支持从 `kubectl get pod -o json` 直接解析
- 支持从 Prometheus 查询指标
- 支持 namespace 维度聚合
- 支持生成 HTML 报告
- 支持 GPU 字段，例如 `gpu_request`、`gpu_used`
- 支持训练作业 / 推理服务场景的异常规则

## 面试里可以怎么讲

你可以这样描述这个项目：

> 我做了一个轻量的 Kubernetes 工作负载巡检工具，核心目标不是替代完整监控系统，而是把日常平台治理里最常见的资源与稳定性问题快速暴露出来，比如 request/limit 缺失、高负载风险、重启异常等。这个项目体现的是我对平台治理和自动化的理解，也说明我愿意把运维经验沉淀成可复用工具。

