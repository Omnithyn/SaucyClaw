"""最小 retry 机制

定义可重试错误类型，实现有限次 retry，记录 retry 信息。

Retry 策略：
- 可重试：网络错误、HTTP 5xx、Timeout
- 不可重试：HTTP 4xx、payload 错误、pre-send failure
- 最大重试：2 次（总共最多 3 次尝试）
- 重试间隔：固定 1000 ms
- 不引入消息队列
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RetryConfig:
    """Retry 配置

    - max_retries: 最大重试次数（默认 2，总共最多 3 次尝试）
    - retry_delay_ms: 重试间隔毫秒（默认 1000）
    """
    max_retries: int = 2
    retry_delay_ms: int = 1000


@dataclass(frozen=True)
class RetryableErrorType:
    """可重试错误类型"""
    NETWORK = "network"  # Connection refused, Connection timeout
    HTTP_5XX = "http_5xx"  # 500, 502, 503, 504
    TIMEOUT = "timeout"  # Request timeout


def is_retryable_error(error: str, status_code: int | None) -> bool:
    """判断是否可重试错误

    可重试：
    - 网络错误（Connection refused, Connection reset, Timeout）
    - HTTP 5xx（500, 502, 503, 504）

    不可重试：
    - HTTP 4xx（400, 401, 403, 404）
    - payload 构造错误
    - pre-send failure
    """
    if error is None:
        return False

    # 网络错误可重试
    network_errors = [
        "Connection refused",
        "Connection reset",
        "Connection timeout",
        "Timeout",
        "timed out",
        "[Errno 61]",  # Connection refused (macOS)
        "[Errno 111]",  # Connection refused (Linux)
    ]
    for net_err in network_errors:
        if net_err in error:
            return True

    # HTTP 5xx 可重试
    if status_code is not None and 500 <= status_code < 600:
        return True

    # 其他情况不可重试
    return False


def with_retry(
    send_func: Any,
    config: RetryConfig = RetryConfig(),
) -> tuple[Any, int, bool]:
    """包装发送函数，添加 retry 机制

    参数：
    - send_func: 发送函数（无参数，返回 WakeResult）
    - config: retry 配置

    返回：
    - result: 最终 WakeResult
    - attempts: 尝试次数
    - retried: 是否进行了重试
    """
    attempts = 1
    last_result = None

    while attempts <= config.max_retries + 1:
        result = send_func()

        # 成功，直接返回
        if result.success:
            return result, attempts, attempts > 1

        # 检查是否可重试
        if not is_retryable_error(result.error, result.status_code):
            # 不可重试，直接返回失败
            return result, attempts, False

        # 可重试但已达到最大次数
        if attempts > config.max_retries:
            return result, attempts, True

        # 等待后重试
        last_result = result
        attempts += 1
        time.sleep(config.retry_delay_ms / 1000.0)

    # 理论上不会到这里
    return last_result, attempts, True


def build_retry_result(
    result: Any,
    attempts: int,
    retried: bool,
) -> Any:
    """构建包含 retry 信息的 SendResult

    参数：
    - result: WakeResult
    - attempts: 尝试次数
    - retried: 是否进行了重试

    返回：
    - 包含 retry 信息的 SendResult 结构
    """
    from adapters.openclaw.notification_adapter import WakeResult

    if isinstance(result, WakeResult):
        return WakeResult(
            gateway=result.gateway,
            success=result.success,
            error=result.error,
            status_code=result.status_code,
            # retry 信息通过 wrapper 传递，不改 WakeResult 结构
        )

    return result


# Retry 说明

"""
## Retry 机制说明

### 可重试错误

| 错误类型 | 示例 | 可重试 |
|---------|------|--------|
| 网络错误 | Connection refused, Connection timeout | ✅ |
| HTTP 5xx | 500, 502, 503, 504 | ✅ |
| Timeout | Request timed out | ✅ |

### 不可重试错误

| 错误类型 | 示例 | 可重试 |
|---------|------|--------|
| HTTP 4xx | 400, 401, 403, 404 | ❌ |
| payload 错误 | Invalid payload format | ❌ |
| pre-send failure | Decision mismatch | ❌ |

### Retry 配置

- max_retries: 2（总共最多 3 次尝试）
- retry_delay_ms: 1000（固定 1 秒间隔）
- 不做指数退避
- 不引入消息队列

### Retry 结果记录

retry 信息记录在 NotificationEvidence 中：
- attempts: 尝试次数
- retried: 是否进行了重试
- final_error: 最终错误（retry 后仍失败时）
"""