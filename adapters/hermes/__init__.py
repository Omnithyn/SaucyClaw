"""Hermes Agent 适配器包（skeleton）。

M11 — 只定义 profile，adapter 实现待后续阶段完成。

当前已确认能力：
- shadow: 可通过 mock 回调事件实现（待实现）
- notification: 可通过 Channel / webhook 实现（待实现）
- hooks_live: 可通过 hook 脚本 + HTTP 端点实现（待实现，接入方式与 OpenHarness 不同）
"""

from adapters.hermes.profile import HermesProfile

__all__ = ["HermesProfile"]
