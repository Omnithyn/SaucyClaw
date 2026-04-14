"""Hook Contract 探针文件：定义外部接入契约。

Phase 2.3: 固定外部接入契约，为未来对接真实 OpenClaw 或其他 runtime 提供统一接口草图。

本文件仅包含 Protocol 定义，不参与实际运行。
"""

from __future__ import annotations

from typing import Protocol, TYPE_CHECKING

from stores.protocols import GateResult

if TYPE_CHECKING:
    from adapters.openclaw.explain_bridge import AdapterExplainOutput
    from adapters.openclaw.shadow_runtime import ShadowRunResult


class HostOutputSink(Protocol):
    """宿主输出接收协议。

    对应 OpenClawHostAdapter.write_back 的契约。
    真实宿主若存在等价回写点，应遵守此协议。
    """

    def write_back(self, gate_result: GateResult) -> None:
        """回写治理决策到宿主。

        Args:
            gate_result: 原始治理决策结果
        """
        ...

    @property
    def write_back_log(self) -> list[GateResult]:
        """只读访问已回写的决策日志。"""
        ...


class ExplainPayload(Protocol):
    """解释输出契约。

    对应 ExplainBridge.enhance_output 的契约。
    任何解释桥接器都应遵守此协议。
    """

    def enhance_output(self, result: GateResult) -> AdapterExplainOutput:
        """生成增强输出。

        Args:
            result: 原始 GateResult

        Returns:
            增强后的输出包（包含解释信息）
        """
        ...

    @property
    def enabled(self) -> bool:
        """Shadow Mode 开关状态。

        注：当前 ExplainBridge 实现使用 _enabled 内部属性，
        未暴露公开 enabled property。此 Protocol 项为未来
        真实集成预留契约占位。
        """
        ...


class GovernanceProcessor(Protocol):
    """治理处理接口。

    对应 GovernanceEngine.process_event 的契约。
    任何治理处理器都应遵守此协议。
    """

    def process_event(self, raw_event: dict) -> GateResult:
        """处理原始事件，返回治理决策。

        Args:
            raw_event: 原始事件

        Returns:
            治理决策结果
        """
        ...


class ShadowOutput(Protocol):
    """Shadow 输出协议。

    对应 ShadowRuntime.process_and_write 的契约。
    外围接入模板应遵守此协议。
    """

    def process_and_write(self, raw_event: dict) -> ShadowRunResult:
        """执行治理决策并回写宿主。

        Args:
            raw_event: 原始事件

        Returns:
            Shadow 运行结果
        """
        ...
