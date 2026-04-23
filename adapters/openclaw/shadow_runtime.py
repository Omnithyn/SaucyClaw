"""Shadow Runtime：外围接入模板。

Phase 2.2: 把 Shadow Mode 从"手工调用示例"变成"可复用运行时入口"。

核心流程：
1. engine.process_event(raw_event) → GateResult
2. 若有 bridge，则 bridge.enhance_output(result) → AdapterExplainOutput
3. adapter.write_back(result) — 保持原契约
4. 返回 ShadowRunResult

保证：
- 零 core 改动
- 零 adapter 契约改动
- 不声称真实 hook 已接入
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from stores.protocols import GateResult

if TYPE_CHECKING:
    from adapters.openclaw.adapter import OpenClawHostAdapter
    from adapters.openclaw.explain_bridge import (
        AdapterExplainOutput,
        ExplainBridge,
    )
    from core.engine.orchestrator import GovernanceEngine


@dataclass(frozen=True)
class ShadowRunResult:
    """Shadow Mode 运行结果。

    Attributes:
        gate_result: 原始治理决策结果
        enhanced_output: 增强输出（bridge 开启时包含解释信息）
    """
    gate_result: GateResult
    enhanced_output: AdapterExplainOutput | None


class ShadowRuntime:
    """Shadow Mode 运行时外围接入模板。

    封装 Hook C（外围包装）的标准流程，提供可复用的运行入口。
    """

    def __init__(
        self,
        engine: GovernanceEngine,
        adapter: OpenClawHostAdapter,
        explain_bridge: ExplainBridge | None = None,
    ) -> None:
        """初始化 Shadow 运行时。

        Args:
            engine: 治理引擎
            adapter: 宿主适配器器
            explain_bridge: 解释桥接器（可选，默认 None）
        """
        self._engine = engine
        self._adapter = adapter
        self._explain_bridge = explain_bridge

    def process_and_write(self, raw_event: dict) -> ShadowRunResult:
        """执行治理决策并回写宿主。

        核心流程：
        1. engine.process_event(raw_event) → GateResult
        2. 若有 bridge，则 bridge.enhance_output(result) → AdapterExplainOutput
        3. adapter.write_back(result)
        4. 返回 ShadowRunResult

        Args:
            raw_event: 原始事件

        Returns:
            Shadow 运行结果
        """
        result: GateResult = self._engine.process_event(raw_event)

        enhanced: AdapterExplainOutput | None = None
        if self._explain_bridge is not None:
            enhanced = self._explain_bridge.enhance_output(result)

        self._adapter.write_back(result)

        return ShadowRunResult(
            gate_result=result,
            enhanced_output=enhanced,
        )
