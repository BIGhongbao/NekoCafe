# Runbook

## 健康检查

```bash
curl http://localhost:8081/healthz
curl http://localhost:8082/healthz
curl http://localhost:8081/readyz
curl http://localhost:8082/readyz
```

## 常见故障

### 服务启动失败

1. 查看容器状态：`docker compose ps`
2. 查看日志：`docker compose logs reservation-service member-service`
3. 检查端口 8081、8082 是否被占用。

### P95 延迟超阈值

1. 在 Grafana 查看 `NekoCafe DevOps Overview`。
2. 检查 Prometheus 查询：`histogram_quantile(0.95, rate(nekocafe_http_request_duration_seconds_bucket[5m]))`
3. 若生产金丝雀版本触发阈值，执行 `scripts/rollback.sh prod nekocafe`。

### 错误率超 1%

1. 查看 5xx 日志中的 `traceId`。
2. 用 `traceId` 关联 API Gateway、reservation-service、member-service 日志。
3. 如果新版本错误率持续 3 分钟超阈值，回滚到上一稳定版本。
