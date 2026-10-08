# Kubernetes 工作负载巡检报告

## 概览

- 工作负载总数：`5`
- 缺失 request：`1`
- 缺失 limit：`2`
- CPU 偏高：`4`
- 内存偏高：`4`
- 重启偏高：`1`

## 明细

| namespace | pod | status | CPU使用/request | 内存使用/request | restarts | 风险等级 | 巡检结果 |
|---|---|---|---|---|---:|---|---|
| ads | bid-worker-9f2d1c | Running | 660m / 600m (110.0%) | 980Mi / 1024Mi (95.7%) | 2 | 高 | CPU偏高、内存偏高 |
| live | stream-gateway-2a1c9e | Running | 350m / 300m (116.7%) | 430Mi / 512Mi (84.0%) | 4 | 高 | 缺失limit、CPU偏高、内存偏高、重启偏高 |
| recommend | recall-engine-5c7f2a | Running | 760m / 800m (95.0%) | 1850Mi / 2048Mi (90.3%) | 1 | 高 | CPU偏高、内存偏高 |
| search | query-service-7b8d5d | Running | 420m / 500m (84.0%) | 860Mi / 1024Mi (84.0%) | 0 | 高 | CPU偏高、内存偏高 |
| ecommerce | order-risk-6b3e1a | Running | 140m / 0m (N/A) | 220Mi / 0Mi (N/A) | 0 | 中 | 缺失request、缺失limit |

## 建议

1. 优先补齐缺失 request/limit 的工作负载，避免资源不可控。
2. 对 CPU 或内存使用率持续偏高的工作负载做容量复核。
3. 对重启次数偏高的工作负载补充日志、事件和发布变更排查。
4. 把这类巡检接入日常治理流程，而不是只在故障后手工排查。
