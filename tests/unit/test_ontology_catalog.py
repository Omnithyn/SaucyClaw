"""Ontology Catalog 单元测试。"""

from ontology.catalog import CatalogIndex, OntologyCatalog
from ontology.schema import ContextType, EventType, FactType, OntologySchema


def _make_schema():
    """创建测试用 Schema。"""
    return OntologySchema(
        event_types=[
            EventType(
                id="tool-invocation",
                name="工具调用",
                description="Agent 调用工具",
                subject_type="agent-role",
            ),
            EventType(
                id="task-assignment",
                name="任务分配",
                description="任务分配给 Agent",
                subject_type="agent-role",
                object_type="task-type",
            ),
        ],
        context_types=[
            ContextType(
                id="session-context",
                name="会话上下文",
                description="会话环境",
            )
        ],
        fact_types=[
            FactType(
                id="review-requirement",
                name="审查要求",
                description="需要审查",
                subject_type="agent-role",
            )
        ],
    )


class TestCatalogFromSchema:
    def test_build_from_schema(self):
        """从 OntologySchema 构建 Catalog。"""
        schema = _make_schema()
        catalog = OntologyCatalog.from_schema(schema)
        assert catalog.get_event_type("tool-invocation") is not None
        assert catalog.get_context_type("session-context") is not None
        assert catalog.get_fact_type("review-requirement") is not None

    def test_lookup_existing_types(self):
        """查找已存在的类型。"""
        catalog = OntologyCatalog.from_schema(_make_schema())
        et = catalog.get_event_type("tool-invocation")
        assert et is not None
        assert et.name == "工具调用"

    def test_lookup_missing_types(self):
        """查找不存在的类型返回 None。"""
        catalog = OntologyCatalog.from_schema(_make_schema())
        assert catalog.get_event_type("nonexistent") is None
        assert catalog.get_context_type("nonexistent") is None
        assert catalog.get_fact_type("nonexistent") is None


class TestCatalogExistenceChecks:
    def test_has_methods(self):
        """存在性检查。"""
        catalog = OntologyCatalog.from_schema(_make_schema())
        assert catalog.has_event_type("tool-invocation") is True
        assert catalog.has_event_type("nonexistent") is False
        assert catalog.has_context_type("session-context") is True
        assert catalog.has_fact_type("review-requirement") is True


class TestCatalogIndex:
    def test_index_by_category(self):
        """按分类索引。"""
        catalog = OntologyCatalog.from_schema(_make_schema())
        index = catalog.index_by_category()
        assert "event" in index
        assert "context" in index
        assert "fact" in index
        assert len(index["event"]) == 2
        assert len(index["context"]) == 1
        assert len(index["fact"]) == 1

    def test_catalog_index_structure(self):
        """索引条目结构。"""
        catalog = OntologyCatalog.from_schema(_make_schema())
        index = catalog.index_by_category()
        first_event = index["event"][0]
        assert isinstance(first_event, CatalogIndex)
        assert first_event.type_id in ("tool-invocation", "task-assignment")
        assert first_event.category == "event"


class TestCatalogStats:
    def test_all_type_ids(self):
        """获取所有类型 ID。"""
        catalog = OntologyCatalog.from_schema(_make_schema())
        ids = catalog.all_type_ids()
        assert "tool-invocation" in ids["event"]
        assert "task-assignment" in ids["event"]
        assert "session-context" in ids["context"]
        assert "review-requirement" in ids["fact"]

    def test_type_count(self):
        """类型数量统计。"""
        catalog = OntologyCatalog.from_schema(_make_schema())
        counts = catalog.type_count()
        assert counts["event"] == 2
        assert counts["context"] == 1
        assert counts["fact"] == 1

    def test_empty_catalog(self):
        """空 Catalog 统计。"""
        catalog = OntologyCatalog()
        counts = catalog.type_count()
        assert counts["event"] == 0
        assert counts["context"] == 0
        assert counts["fact"] == 0
