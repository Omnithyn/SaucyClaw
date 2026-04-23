"""Runtime Package Readiness — 执行就绪判定。

N2.1 — RuntimePackage-Driven Governance Realignment

根据 CompilationReport 判定 RuntimePackage 是否可安全执行：

Execute Readiness 三种模式：
- full：完整执行（is_complete=True，无信息丢失）
- warning：警告执行（Preview 类型存在，部分信息丢失，不阻止执行）
- review：审核执行（关键字段丢失，需人工审核）

Source of Truth：
- RuntimePackage.compilation_report 是运行时判定的正式输入
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from ontology.authoring_package import RuntimePackage


# ─── Readiness Level ───


@dataclass(frozen=True)
class ExecuteReadiness:
    """执行就绪状态。

    Attributes:
        level: 就绪层级（full / warning / review / blocked）
        can_execute: 是否可执行
        requires_review: 是否需要人工审核
        preview_warnings: Preview 类型警告列表
        lost_field_warnings: 丢失字段警告列表
        blocked_reasons: 阻止执行的原因列表
        summary: 就绪摘要
    """

    level: Literal["full", "warning", "review", "blocked"]
    can_execute: bool
    requires_review: bool = False
    preview_warnings: list[str] = field(default_factory=list)
    lost_field_warnings: list[str] = field(default_factory=list)
    blocked_reasons: list[str] = field(default_factory=list)
    summary: str = ""


# ─── Readiness Checker ───


@dataclass(frozen=True)
class RuntimeReadinessChecker:
    """Runtime Package 执行就绪检查器。

    根据 CompilationReport 判定执行模式。

    判定规则：
    - is_complete=True → full（完整执行）
    - preview_types>0 → warning（警告执行，记录但不阻止）
    - information_loss_notes 包含关键字段 → review（审核执行）
    - reserved_elements 存在 → blocked（阻止执行）

    Attributes:
        critical_fields: 关键字段列表（丢失则需审核）
    """

    critical_fields: list[str] = field(
        default_factory=lambda: [
            "subject_type",
            "object_type",
            "establishment_condition",
            "trigger",
            "condition",
        ]
    )

    def check_readiness(
        self,
        runtime_package: RuntimePackage,
    ) -> ExecuteReadiness:
        """检查 RuntimePackage 执行就绪状态。

        Args:
            runtime_package: 运行时包

        Returns:
            ExecuteReadiness
        """
        report = runtime_package.compilation_report

        if report is None:
            return ExecuteReadiness(
                level="full",
                can_execute=True,
                summary="无编译报告，默认完整执行",
            )

        # 1. Blocked 检查（检查是否有严重警告）
        # CompilationReport 没有 compilation_errors 字段
        # 使用 warnings 中的特定标记来判断
        blocked_warnings = [
            w for w in report.warnings
            if "阻止" in w or "blocked" in w.lower()
        ]
        if blocked_warnings:
            return ExecuteReadiness(
                level="blocked",
                can_execute=False,
                blocked_reasons=blocked_warnings,
                summary=f"阻止执行警告 {len(blocked_warnings)} 个",
            )

        # 2. Review 检查（关键字段丢失）
        critical_loss = []
        for element_id, note in report.information_loss_notes.items():
            for critical_field in self.critical_fields:
                if critical_field in note:
                    critical_loss.append(f"{element_id}: {note}")

        if critical_loss:
            return ExecuteReadiness(
                level="review",
                can_execute=True,
                requires_review=True,
                lost_field_warnings=critical_loss,
                summary=f"关键字段丢失 {len(critical_loss)} 个，需人工审核",
            )

        # 3. Warning 检查（Preview 类型）
        if report.preview_types > 0:
            preview_warnings = []
            for element_id, note in report.information_loss_notes.items():
                preview_warnings.append(f"Preview 元素 {element_id}: {note}")

            return ExecuteReadiness(
                level="warning",
                can_execute=True,
                preview_warnings=preview_warnings,
                summary=f"Preview 类型 {report.preview_types} 个，部分信息丢失",
            )

        # 4. Full 执行
        return ExecuteReadiness(
            level="full",
            can_execute=True,
            summary="完整编译，无信息丢失",
        )


# ─── Convenience Function ───


def check_runtime_readiness(
    runtime_package: RuntimePackage,
) -> ExecuteReadiness:
    """便捷就绪检查函数。

    Args:
        runtime_package: 运行时包

    Returns:
        ExecuteReadiness
    """
    checker = RuntimeReadinessChecker()
    return checker.check_readiness(runtime_package)


# ─── Judgment Mode Adapter ───


def adapt_readiness_to_judgment_mode(
    readiness: ExecuteReadiness,
) -> Literal["auto", "review", "block"]:
    """将 Readiness 映射到 Judgment 执行模式。

    Args:
        readiness: 执行就绪状态

    Returns:
        "auto" / "review" / "block"
    """
    if not readiness.can_execute:
        return "block"

    if readiness.requires_review:
        return "review"

    return "auto"
