"""Notification 线路最小契约定义

定义 notification 线路的正式最小契约，明确输入、输出、payload、evidence 的结构。

契约成熟度：最小可靠投递版（M6）
- 不夸大为"正式生产接入完成"
- 保持克制，不做大系统
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SendInput:
    """发送输入 — send_decision() 的输入参数

    必需字段：
    - gate_result: 治理引擎的决策结果
    - session_context: 会话上下文（至少包含 session_id）

    可选字段：
    - explanation_summary: 可读的治理解释
    - metadata: 其他元数据
    """
    gate_result: Any  # GateResult from stores.protocols
    session_context: dict[str, str]
    explanation_summary: str | None = None
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class SendResult:
    """发送结果 — send_decision() 的返回值

    必需字段：
    - gateway: 发送到的 gateway 名称
    - success: 是否成功
    - error: 错误信息（成功时为 None）

    可选字段：
    - status_code: HTTP 状态码（仅 HTTP send）
    - attempts: 发送尝试次数（含 retry）
    - retried: 是否进行了重试
    - final_error: 最终错误（retry 后）
    """
    gateway: str
    success: bool
    error: str | None
    status_code: int | None = None
    attempts: int = 1
    retried: bool = False
    final_error: str | None = None


@dataclass(frozen=True)
class NotificationPayload:
    """通知载荷 — 发送到 gateway 的 payload 结构

    契约定义：对应 OpenClawPayload 结构

    必需字段：
    - event: 事件类型（"governance-decision"）
    - instruction: 指令文本（包含 [governance|Block/Allow]）
    - timestamp: ISO 8601 时间戳

    可选字段：
    - text: 可读摘要
    - sessionId: 会话 ID
    - projectPath: 项目路径
    - projectName: 项目名称
    - context: 上下文对象
    """
    event: str
    instruction: str
    timestamp: str
    text: str | None = None
    sessionId: str | None = None
    projectPath: str | None = None
    projectName: str | None = None
    context: dict[str, str] | None = None


@dataclass(frozen=True)
class NotificationEvidence:
    """通知证据 — 验证记录结构

    区分两类：
    - A. 已发送类：payload != None，必须有 payload 文件
    - B. 发送前失败类：payload == None，标记为 pre-send failure

    必需字段：
    - scenario: 场景名称
    - mode: 运行模式（"mock" / "real")
    - timestamp: ISO 8601 时间戳
    - success: 是否成功
    - error: 错误信息（成功时为 None）

    可选字段：
    - payload: 实际发送的 payload（发送前失败时为 None）
    - gateway_url: gateway URL（发送前失败时为空）
    - gateway: gateway 名称（发送前失败时为空）
    - status_code: HTTP 状态码
    - attempts: 发送尝试次数（含 retry）
    - retried: 是否进行了重试
    """
    scenario: str
    mode: str  # "mock" / "real"
    timestamp: str
    success: bool
    error: str | None
    payload: NotificationPayload | None = None
    gateway_url: str = ""
    gateway: str = ""
    status_code: int | None = None
    attempts: int = 1
    retried: bool = False


# 契约说明

CONTRACT_VERSION = "M6-minimal-reliable"
CONTRACT_MATURITY = "最小可靠投递版"

"""
## 契约成熟度说明

当前 notification 线路处于"最小可靠投递版"成熟度：

- ✅ 已完成：
  - mock/real 模式支持
  - evidence 保存
  - pre-send failure 区分
  - 最小 retry 机制（M6）

- ❌ 未完成（不属于 M6 范围）：
  - 消息队列
  - 持久化 outbox
  - tracing 平台
  - UI 管理面
  - 正式 OpenClaw 插件

## 必需 vs 可选说明

SendInput:
- gate_result: 必需（治理引擎输出）
- session_context: 必需（至少 session_id）
- explanation_summary: 可选（增强可读性）
- metadata: 可选（扩展信息）

SendResult:
- gateway: 必需（发送目标）
- success: 必需（成功标志）
- error: 必需（错误信息，成功时 None）
- status_code: 可选（仅 HTTP send）
- attempts: 可选（retry 后才有）
- retried: 可选（retry 后才有）
- final_error: 可选（retry 后才有）

NotificationEvidence:
- scenario: 必需（场景标识）
- mode: 必需（运行模式）
- timestamp: 必需（时间记录）
- success: 必需（成功标志）
- error: 必需（错误信息）
- payload: 可选（发送前失败时 None）
- gateway_url: 可选（发送前失败时空）
- gateway: 可选（发送前失败时空）
- status_code: 可选（仅 HTTP send）
- attempts: 可选（retry 后才有）
- retried: 可选（retry 后才有）
"""