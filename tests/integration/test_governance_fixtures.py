"""基于真实 YAML fixture 的治理规则集批量回归测试。"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from core.engine.orchestrator import GovernanceEngine
from core.governance.loader import load_governance
from stores.file.evidence.store import FileEvidenceStore
from stores.file.memory.store import FileMemoryStore


# ---------------------------------------------------------------------------
# 配置
# ---------------------------------------------------------------------------

SCHEMAS_DIR = Path(__file__).parent.parent.parent / "schemas" / "governance"
FIXTURES_DIR = Path(__file__).parent.parent / "fixtures" / "governance_cases"

# 自动发现所有 YAML fixture
FIXTURE_FILES = sorted(FIXTURES_DIR.glob("*.yaml"))
FIXTURE_NAMES = [f.stem for f in FIXTURE_FILES]


# ---------------------------------------------------------------------------
# 核心测试逻辑
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("fixture_file", FIXTURE_FILES, ids=FIXTURE_NAMES)
def test_governance_fixture(fixture_file: Path, tmp_path: Path):
    """对每个治理场景 fixture，验证实际决策与预期一致。"""
    # 1. 加载完整治理 schema
    schema = load_governance(SCHEMAS_DIR)
    assert len(schema.rules) >= 5  # 确保规则集已加载

    # 2. 读取 fixture
    with open(fixture_file) as f:
        fixture = yaml.safe_load(f)

    expected = fixture.pop("expected")

    # 3. 构造引擎并执行
    evidence_store = FileEvidenceStore(tmp_path / "evidence")
    memory_store = FileMemoryStore(tmp_path / "memory")
    engine = GovernanceEngine(
        rules=schema.rules,
        evidence_store=evidence_store,
        memory_store=memory_store,
    )

    result = engine.process_event(fixture)

    # 4. 断言决策和规则匹配
    assert result.decision == expected["decision"], (
        f"{fixture_file.name}: 决策 {result.decision} != 期望 {expected['decision']}"
    )
    assert set(result.matched_rules) == set(expected["matched_rules"]), (
        f"{fixture_file.name}: 触发规则 {result.matched_rules} != 期望 {expected['matched_rules']}"
    )
