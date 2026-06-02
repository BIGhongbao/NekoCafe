# NekoCafe DevOps PoC

本目录是实验三 D3-2“源代码与配置仓库”的交付物。它按照实验二最终选型“微服务 + 事件驱动 + CQRS”进行最小可运行实现，PoC 范围限定为两个服务：

- `services/reservation`：对应实验二 BC-2“预约与排队上下文”，提供预约创建、查询、核销、取消、健康检查和指标接口。
- `services/member`：对应实验二 BC-4“会员与权益上下文”，提供会员查询、权益查询、优惠券核销、营销授权、健康检查和指标接口。

## 为什么采用 Monorepo

实验三要求同时交付源代码、Dockerfile、CI/CD、Helm、多环境配置和可观测性配置。两个 PoC 服务放在同一个仓库中，可以让评审者一次 clone 后在 30 分钟内完成本地启动和验证；服务边界仍通过独立目录、独立 Dockerfile、独立端口和独立 Helm Deployment 表达。

## 技术栈

- Python 3.12
- FastAPI + Uvicorn
- pytest
- Docker / Docker Compose
- GitHub Actions
- Helm 3
- Prometheus + Grafana

## 本地运行

```bash
make test
make up
```

启动后访问：

```text
reservation: http://localhost:8081/healthz
member:      http://localhost:8082/healthz
Prometheus:          http://localhost:9090
Grafana:             http://localhost:3000  admin/admin
```

## 快速接口验证

```bash
curl http://localhost:8081/healthz
curl http://localhost:8082/healthz

curl -X POST http://localhost:8081/reservations \
  -H "Content-Type: application/json" \
  -d '{"member_id":"m001","store_id":"store-bj-001","table_id":"t08","reserved_at":"2026-06-05T18:30:00+08:00","party_size":2}'

curl http://localhost:8082/members/m001/benefits
curl -X POST http://localhost:8082/members/m001/coupons/redeem
```

## 目录结构

```text
D3-2_源代码与配置仓库/
├── services/
│   ├── reservation/
│   │   ├── src/
│   │   ├── tests/
│   │   └── Dockerfile
│   └── member/
│       ├── src/
│       ├── tests/
│       └── Dockerfile
├── .github/workflows/
├── infra/
│   ├── helm/nekocafe/
│   ├── k8s-manifests/
│   └── observability/
├── scripts/
├── docs/
├── docker-compose.yml
├── Makefile
├── .editorconfig
├── .pre-commit-config.yaml
└── README.md
```

## 常用命令

```bash
make test       # 运行两个服务的 pytest
make build      # 构建两个服务镜像
make up         # 本地启动完整 PoC 栈
make down       # 停止并清理本地容器和卷
make scan       # Trivy 扫描 HIGH/CRITICAL 漏洞
make helm-lint  # 校验 dev/staging/prod 三套 Helm values
make rollback   # 展示 Helm 回滚命令
```

## DevOps 对应关系

- D3-3：两个服务的 `Dockerfile` 支持多阶段构建、测试阶段、非 root 用户和健康检查。
- D3-4：`.github/workflows/ci.yml` 和 `cd.yml` 覆盖测试、构建、扫描、部署、回滚。
- D3-5：`infra/helm/nekocafe` 提供 dev/staging/prod 三套 values，`infra/k8s-manifests` 保留原生 K8s 清单说明。
- D3-6：`infra/observability` 提供 Prometheus 抓取、告警规则和 Grafana Dashboard。

## Secret 管理

`.env` 不提交仓库，仓库只提供 `.env.example`。CI/CD 使用 GitHub Secrets 或 OIDC 注入镜像仓库、Kubeconfig、Prometheus 地址等敏感配置。Kubernetes 生产环境使用 Secret 或 Vault 注入数据库、Redis、消息队列和第三方平台密钥。
