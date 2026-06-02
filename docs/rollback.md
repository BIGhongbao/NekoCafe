# Rollback Guide

生产环境采用金丝雀发布。触发以下条件时回滚：

- 核心接口 P95 > 350ms 持续 5 分钟。
- HTTP 5xx 错误率 > 1% 持续 3 分钟。
- Pod Ready 数不足持续 2 分钟。
- DLQ 核心事件新增 > 10 条/5 分钟。

## Helm 回滚

```bash
helm history nekocafe -n nekocafe-prod
helm rollback nekocafe <REVISION> -n nekocafe-prod
kubectl rollout status deploy/nekocafe-reservation-service -n nekocafe-prod --timeout=120s
kubectl rollout status deploy/nekocafe-member-service -n nekocafe-prod --timeout=120s
```

## 金丝雀降权

```bash
helm upgrade --install nekocafe infra/helm/nekocafe \
  -n nekocafe-prod \
  -f infra/helm/nekocafe/values-prod.yaml \
  --set rollout.canaryWeight=0
```
