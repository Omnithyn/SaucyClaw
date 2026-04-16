"""OpenClaw 真实宿主集成 PoC 实验包。

本包提供 notification 线路的验证实验能力，用于测试 mock/real gateway 通知发送。

## 包组成与成熟度

| 文件 | 职责 | 成熟度 | 说明 |
|------|------|--------|------|
| `run_poc.py` | PoC runner | **PoC/experiment** | 验证 notification 线路的实验脚本 |
| `mock_gateway.py` | Mock server | **PoC/experiment** | 本地 mock gateway 服务器 |
| `notification_contract.py` | 契约定义 | **PoC/experiment** | 验证用的契约结构（SendResult/NotificationEvidence） |
| `notification_retry.py` | Retry 机制 | **PoC/experiment** | 最小 retry 实现，尚未正式化 |

## 正式工程面 vs PoC/experiment

**正式工程面（在 `adapters/openclaw/`）：**
- `OpenClawNotificationAdapter` — HTTP gateway 发送适配器
- `WakeResult` — 发送结果结构（adapter 核心返回值）
- `OpenClawCommandNotificationAdapter` — Command gateway 发送适配器

**PoC/experiment（在本包）：**
- `NotificationEvidence` — 验证记录结构（用于 PoC evidence 保存）
- `SendResult` — 验证用的包装结构（包含 retry 信息）
- `RetryConfig` / `with_retry` — 最小 retry 实现
- `run_poc` — 验证脚本入口

## 外部调用方式

- **正式 notification 线接入**：使用 `adapters.openclaw.notification_adapter.OpenClawNotificationAdapter`
- **PoC 验证运行**：使用 `experiments.openclaw_poc.run_poc:main()`

## 当前状态

notification 线路处于 **最小可靠投递版（M6）** 成熟度：
- ✅ mock/real 模式支持
- ✅ evidence 保存（含 pre-send failure 区分）
- ✅ 最小 retry 机制
- ❌ 不夸大为"正式生产接入完成"
"""

from experiments.openclaw_poc.notification_contract import (
    SendInput,
    SendResult,
    NotificationPayload,
    NotificationEvidence,
    CONTRACT_VERSION,
    CONTRACT_MATURITY,
)
from experiments.openclaw_poc.notification_retry import (
    RetryConfig,
    RetryableErrorType,
    is_retryable_error,
    with_retry,
)

__all__ = [
    # Contract (PoC/experiment)
    "SendInput",
    "SendResult",
    "NotificationPayload",
    "NotificationEvidence",
    "CONTRACT_VERSION",
    "CONTRACT_MATURITY",
    # Retry (PoC/experiment)
    "RetryConfig",
    "RetryableErrorType",
    "is_retryable_error",
    "with_retry",
]