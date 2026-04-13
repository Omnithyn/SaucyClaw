"""治理规则 YAML 装载器。

从 schemas/governance/*.yaml 加载规则、角色、任务类型定义，
返回类型安全的 dataclass 列表。

Phase 1.4: 最小装载器，仅做：
- YAML 解析
- 必填字段校验
- dataclass 构造
不做复杂 schema 验证、图数据库、版本管理。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from core.governance.models import Condition, GovernanceRule, RoleDefinition, TaskType


class SchemaError(ValueError):
    """治理 schema 解析失败。"""


# ---------------------------------------------------------------------------
# 规则加载
# ---------------------------------------------------------------------------

def load_rules(path: str | Path) -> list[GovernanceRule]:
    """从 rules.yaml 加载治理规则列表。

    支持 conditions 与 applies_when 两个条件列表。
    两者均为 AND-only 单层条件。
    """
    raw = _load_yaml(path)
    items = raw.get("rules", [])
    if not isinstance(items, list):
        raise SchemaError("'rules' 必须是列表")

    rules: list[GovernanceRule] = []
    for idx, item in enumerate(items):
        _require_keys(item, ["id", "task_type", "conditions", "severity", "on_hit"],
                      context=f"rules[{idx}]")

        conditions = [Condition(**c) for c in item["conditions"]]
        applies_raw = item.get("applies_when", [])
        if not isinstance(applies_raw, list):
            raise SchemaError(f"'applies_when' 在 rules[{idx}] 中必须是列表")
        applies_when = [Condition(**c) for c in applies_raw]

        rules.append(GovernanceRule(
            id=item["id"],
            task_type=item["task_type"],
            description=item.get("description", ""),
            conditions=conditions,
            severity=item["severity"],
            on_hit=item["on_hit"],
            applies_when=applies_when,
        ))
    return rules


# ---------------------------------------------------------------------------
# 角色加载
# ---------------------------------------------------------------------------

def load_roles(path: str | Path) -> list[RoleDefinition]:
    """从 roles.yaml 加载角色定义列表。"""
    raw = _load_yaml(path)
    items = raw.get("roles", [])
    if not isinstance(items, list):
        raise SchemaError("'roles' 必须是列表")

    roles: list[RoleDefinition] = []
    for idx, item in enumerate(items):
        _require_keys(item, ["id", "name"], context=f"roles[{idx}]")
        roles.append(RoleDefinition(
            id=item["id"],
            name=item["name"],
            capabilities=item.get("capabilities", []),
            permissions=item.get("permissions", {}),
            handoff_to=item.get("handoff_to", []),
        ))
    return roles


# ---------------------------------------------------------------------------
# 任务类型加载
# ---------------------------------------------------------------------------

def load_task_types(path: str | Path) -> list[TaskType]:
    """从 task_types.yaml 加载任务类型定义列表。"""
    raw = _load_yaml(path)
    items = raw.get("task_types", [])
    if not isinstance(items, list):
        raise SchemaError("'task_types' 必须是列表")

    types: list[TaskType] = []
    for idx, item in enumerate(items):
        _require_keys(item, ["id", "name"], context=f"task_types[{idx}]")
        types.append(TaskType(
            id=item["id"],
            name=item["name"],
            description=item.get("description", ""),
            required_roles=item.get("required_roles", []),
            review_required=item.get("review_required", False),
            blocking_rules=item.get("blocking_rules", []),
        ))
    return types


# ---------------------------------------------------------------------------
# 批量加载
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class GovernanceSchema:
    """治理 schema 集合。"""
    roles: list[RoleDefinition] = field(default_factory=list)
    task_types: list[TaskType] = field(default_factory=list)
    rules: list[GovernanceRule] = field(default_factory=list)


def load_governance(dir_path: str | Path) -> GovernanceSchema:
    """从目录一次性加载 roles / task_types / rules。

    不存在的文件会被跳过（空列表），而非报错。
    """
    base = Path(dir_path)
    roles = load_roles(base / "roles.yaml") if (base / "roles.yaml").exists() else []
    task_types = load_task_types(base / "task_types.yaml") if (base / "task_types.yaml").exists() else []
    rules = load_rules(base / "rules.yaml") if (base / "rules.yaml").exists() else []
    return GovernanceSchema(roles=roles, task_types=task_types, rules=rules)


# ---------------------------------------------------------------------------
# 内部工具
# ---------------------------------------------------------------------------

def _load_yaml(path: str | Path) -> dict[str, Any]:
    path = Path(path)
    if not path.exists():
        raise SchemaError(f"文件不存在: {path}")
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise SchemaError(f"YAML 根节点必须是映射: {path}")
    return data


def _require_keys(obj: dict[str, Any], keys: list[str], context: str) -> None:
    missing = [k for k in keys if k not in obj]
    if missing:
        raise SchemaError(f"{context} 缺少必填字段: {missing}")
