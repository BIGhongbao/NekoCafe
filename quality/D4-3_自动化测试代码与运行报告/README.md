# D4-3 自动化测试代码与运行报告

本目录是实验四 D4-3 交付物，基于仓库中已有的两个 FastAPI 服务编写：

- `reservation-service`：预约创建、查询、签到、取消。
- `member-service`：会员查询、权益查询、优惠券核销、营销授权。

## 目录说明

```text
unit/         单元/API 测试，验证单个服务的接口、状态码和业务规则
property/     Hypothesis 属性测试，自动生成边界输入
contract/     契约测试，验证消费者期望的字段和状态码
integration/  集成/冒烟测试，验证两个服务都能被加载并完成核心链路
e2e/          Playwright 用户旅程脚本，占位说明完整前端未实现
perf/         k6 性能压测脚本
security/     OWASP ZAP baseline 配置
reports/      pytest、覆盖率、性能、安全等运行报告输出目录
```

## 运行前准备

在 PowerShell 中进入仓库内的 D4-3 目录：

```powershell
cd "quality\D4-3_自动化测试代码与运行报告"
python -m pip install -r requirements-test.txt
```

默认情况下，测试会自动向上找到仓库根目录并读取 `services/`。如果你把 D4-3 单独移动到别的位置，需要先指定实验三代码仓库位置：

```powershell
$env:D3_REPO="C:\Users\LENOVO\Desktop\软件工程\软件工程实验任务书_2026春\实验三_DevOps流水线与容器化部署\实验三_产出\D3-2_源代码与配置仓库"
```

## 运行自动化测试

运行全部可执行 pytest 测试：

```powershell
pytest
```

生成覆盖率 HTML 报告：

```powershell
pytest --cov="..\..\services" --cov-report=html:reports/coverage-html --cov-report=term-missing
```

只运行某一类：

```powershell
pytest unit
pytest property
pytest integration
pytest contract
```

## 性能和安全测试

先启动实验三服务：

```powershell
cd "C:\Users\LENOVO\Desktop\软件工程\软件工程实验任务书_2026春\实验三_DevOps流水线与容器化部署\实验三_产出\D3-2_源代码与配置仓库"
docker compose up -d --build
```

运行 k6：

```powershell
k6 run "quality\D4-3_自动化测试代码与运行报告\perf\reservation.js"
```

运行 ZAP baseline 示例：

```powershell
zap-baseline.py -t http://localhost:8081 -c security/zap-baseline.conf -r reports/zap-reservation.html
```

## 结果说明

本测试项目覆盖实验三已实现的预约服务和会员服务。实验一中门店浏览、点单支付、总部运营看板、猫咪健康等完整业务在当前 PoC 代码中尚未实现，因此只在 D4-2 中保留测试设计，D4-3 不伪造执行结果。
