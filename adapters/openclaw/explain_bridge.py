"""解释桥接器：将解释能力接入 adapter 边界。

Phase 2.0: Shadow Mode - 伴随输出的 explain payload，
不修改 adapter 契约（write_back 仍接受 GateResult）。
"""

from dataclasses import dataclass
from typing import List

from core.governance.explainer_bundle import (
    ExplanationBundle,
    bundle_explanations,
)
from stores.protocols import GateResult
from core.governance.models import GovernanceRule


@dataclass(frozen=True)
class AdapterExplainOutput:
    """Adapter 边界的带解释输出包。

    Shadow Mode 产物，不改变 adapter 核心契约。
    使用场景：
    - 调试输出
    - 日志记录
    - 宿主旁路展示
    - 后续真实 hook 契约验证
    """
    decision: str
    matched_rules: List[str]
    explanation_bundle: ExplanationBundle | None
    raw_result: GateResult


class ExplainBridge:
    """解释桥接器：生成伴随输出的解释负载。

    Shadow Mode：默认关闭，通过 enable=True 显式开启。
    开启后，enhance_output() 返回包含 explanation_bundle 的完整结构。
    关闭时，explanation_bundle 为 None，保持最小侵入。

    不修改 adapter 契约：
    - write_back() 仍接受 GateResult
    - adapter 行为保持不变
    - bridge 只是额外生成一个解释输出包
    """

    def __init__(
        self,
        schema_rules_lookup: dict[str, GovernanceRule],
        enable: bool = False,
    ) -> None:
        """初始化解释桥接器。

        Args:
            schema_rules_lookup: 完整的规则查找表
            enable: 是否开启 Shadow Mode（默认关闭）
        """
        self._lookup = schema_rules_lookup
        self._enabled = enable

    def enable_shadow_mode(self) -> None:
        """开启 Shadow Mode。"""
        self._enabled = True

    def disable_shadow_mode(self) -> None:
        """关闭 Shadow Mode。"""
        self._enabled = False

    @property
    def enabled(self) -> bool:
        """返回当前 Shadow Mode 是否开启。"""
        return self._enabled

    def enhance_output(self, result: GateResult) -> AdapterExplainOutput:
        """增强输出，附加解释信息。

        Args:
            result: 原始 GateResult

        Returns:
            增强后的输出包（enabled=True 时包含 explanation_bundle）
        """
        explanation_bundle = None
        if self._enabled:
            explanation_bundle = bundle_explanations(
                decision=result.decision,
                matched_rule_ids=result.matched_rules,
                schema_rules_lookup=self._lookup,
                suggestions=result.suggestions,
            )

        return AdapterExplainOutput(
            decision=result.decision,
            matched_rules=result.matched_rules,
            explanation_bundle=explanation_bundle,
            raw_result=result,
        )
