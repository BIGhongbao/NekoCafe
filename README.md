# NekoCafe DevOps and Quality Engineering PoC

本仓库是《软件工程》课程 NekoCafe 猫咪主题餐饮预约平台的代码与质量工程交付仓库。

当前仓库同时覆盖：

- 实验三 D3-2：源代码与配置仓库，展示 DevOps 流水线、容器化部署、Helm 配置和可观测性配置。
- 实验四 D4-3：自动化测试代码与运行报告，展示质量工程测试体系、覆盖率报告、契约测试、属性测试、性能脚本和安全扫描配置。

## 项目范围

实验三 PoC 选取两个核心微服务落地：

- `services/reservation`：预约与排队上下文的最小实现，支持预约创建、查询、签到、取消、健康检查和 Prometheus 指标。
- `services/member`：会员与权益上下文的最小实现，支持会员查询、权益查询、优惠券核销、营销授权、健康检查和 Prometheus 指标。

实验一中完整业务还包括门店浏览、点单支付、总部运营、猫咪健康、报表导出等能力。当前仓库没有伪造这些尚未实现的功能，实验四自动化测试只覆盖已实现的 PoC 服务；未实现需求保留在 D4-2 测试设计文档中。

## 技术栈

- Python 3.12
- FastAPI + Uvicorn
- Pytest + pytest-cov
- Hypothesis
- Docker / Docker Compose
- GitHub Actions
- Helm 3
- Prometheus + Grafana
- k6
- OWASP ZAP baseline

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
│   ├── ci.yml
│   └── cd.yml
├── infra/
│   ├── helm/nekocafe/
│   └── observability/
├── scripts/
├── docs/
├── quality/
│   └── D4-3_自动化测试代码与运行报告/
├── docker-compose.yml
├── Makefile
└── README.md
```

## 本地运行实验三服务

安装服务依赖并运行基础测试：

```powershell
make test
```

启动完整 PoC 环境：

```powershell
make up
```

启动后访问：

```text
reservation-service: http://localhost:8081/healthz
member-service:      http://localhost:8082/healthz
Prometheus:          http://localhost:9090
Grafana:             http://localhost:3000  admin/admin
```

快速接口验证：

```powershell
curl http://localhost:8081/healthz
curl http://localhost:8082/healthz

curl -X POST http://localhost:8081/reservations `
  -H "Content-Type: application/json" `
  -d '{"member_id":"m001","store_id":"store-bj-001","table_id":"t08","reserved_at":"2026-06-05T18:30:00+08:00","party_size":2}'

curl http://localhost:8082/members/m001/benefits
curl -X POST http://localhost:8082/members/m001/coupons/redeem
```

## 实验四 D4-3 自动化测试

D4-3 测试项目位于：

```text
quality/D4-3_自动化测试代码与运行报告/
```

它包含：

- `unit/`：预约服务和会员服务的单元/API 测试。
- `property/`：基于 Hypothesis 的属性测试。
- `integration/`：API 旅程测试和 Docker Compose 配置冒烟测试。
- `contract/`：接口契约测试。
- `e2e/`：Playwright API 用户旅程脚本。
- `perf/`：k6 性能测试脚本。
- `security/`：OWASP ZAP baseline 配置。
- `reports/`：JUnit XML、覆盖率 HTML 和测试摘要。

运行 D4-3 测试：

```powershell
cd "quality\D4-3_自动化测试代码与运行报告"
python -m pip install -r requirements-test.txt
python -m pytest
```

生成覆盖率报告：

```powershell
python -m pytest --cov="..\..\services" --cov-report=html:reports/coverage-html --cov-report=term-missing
```

当前本地验证结果：

```text
37 passed
TOTAL coverage: 96%
```

报告文件：

```text
quality/D4-3_自动化测试代码与运行报告/reports/junit.xml
quality/D4-3_自动化测试代码与运行报告/reports/coverage-html/index.html
quality/D4-3_自动化测试代码与运行报告/reports/test-summary.md
```

## 性能测试和安全扫描

先启动服务：

```powershell
docker compose up -d --build
```

运行 k6 预约接口压测：

```powershell
k6 run "quality\D4-3_自动化测试代码与运行报告\perf\reservation.js"
```

运行 ZAP baseline 示例：

```powershell
zap-baseline.py -t http://localhost:8081 -c "quality\D4-3_自动化测试代码与运行报告\security\zap-baseline.conf" -r "quality\D4-3_自动化测试代码与运行报告\reports\zap-reservation.html"
```

## 常用命令

```powershell
make test       # 运行两个服务自带 pytest
make build      # 构建两个服务镜像
make up         # 启动完整 PoC 环境
make down       # 停止并清理本地容器和卷
make scan       # Trivy 扫描 HIGH/CRITICAL 漏洞
make helm-lint  # 校验 Helm values
make rollback   # 展示 Helm 回滚命令
```

## DevOps 对应关系

- D3-3：两个服务的 Dockerfile 支持容器化构建、非 root 用户和健康检查。
- D3-4：`.github/workflows/ci.yml` 和 `cd.yml` 覆盖测试、构建、扫描、部署、回滚。
- D3-5：`infra/helm/nekocafe` 提供 dev/staging/prod values 和 Helm Chart。
- D3-6：`infra/observability` 提供 Prometheus 抓取、告警规则和 Grafana Dashboard。
- D4-3：`quality/D4-3_自动化测试代码与运行报告` 提供自动化测试代码和运行报告。

## Secret 管理

`.env` 不提交仓库，只提交 `.env.example`。CI/CD 使用 GitHub Secrets 或 OIDC 注入镜像仓库、Kubeconfig、Prometheus 地址等敏感配置。Kubernetes 生产环境使用 Secret 或 Vault 注入数据库、Redis、消息队列和第三方平台密钥。
