# D4-3 自动化测试运行摘要

运行时间：2026-06-16

## 测试范围

本次自动化测试覆盖实验三已实现的两个 FastAPI PoC 服务：

- `reservation-service`：预约创建、查询、签到、取消、状态冲突、人数边界、指标接口。
- `member-service`：会员查询、权益查询、优惠券核销、营销授权、手机号脱敏、指标接口。

实验一中门店浏览、点单支付、总部运营、猫咪健康等完整业务在当前实验三 PoC 中尚未实现，因此本目录不伪造这些功能的自动化执行结果。

## 执行结果

```text
37 passed in 3.68s
```

生成文件：

- `reports/junit.xml`
- `reports/coverage-html/index.html`

## 覆盖率结果

```text
services/member/src/main.py          97%
services/reservation/src/main.py     95%
TOTAL                                96%
```

该结果满足 D4-1 中“行覆盖率 ≥ 70%”的目标。

## 测试类型分布

- 单元/API 测试：预约服务、会员服务的核心接口和异常分支。
- 属性测试：预约人数边界、特殊备注回写、会员升级积分、优惠券核销不为负。
- 集成测试：预约完整流程、会员权益流程、两个服务健康检查、Docker Compose 配置冒烟。
- 契约测试：会员权益接口和预约创建接口的字段契约。
- 性能测试脚本：`perf/reservation.js`，需要启动 Docker Compose 后用 k6 单独运行。
- 安全扫描配置：`security/zap-baseline.conf`，需要启动服务后用 OWASP ZAP 单独运行。

