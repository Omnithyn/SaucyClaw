"""测试宿主抽象协议和 OpenClaw profile。

M10 — Runtime-Neutral Host Abstraction
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestHostMode:
    """测试 HostMode 枚举。"""

    def test_shadow_mode_exists(self):
        from adapters.host_protocols import HostMode
        assert HostMode.SHADOW.value == "shadow"

    def test_notification_mode_exists(self):
        from adapters.host_protocols import HostMode
        assert HostMode.NOTIFICATION.value == "notification"

    def test_hooks_live_mode_exists(self):
        from adapters.host_protocols import HostMode
        assert HostMode.HOOKS_LIVE.value == "hooks_live"


class TestHostWakeResult:
    """测试 HostWakeResult 统一结果结构。"""

    def test_basic_result(self):
        from adapters.host_protocols import HostWakeResult

        result = HostWakeResult(
            gateway="test",
            success=True,
        )
        assert result.success is True
        assert result.error is None
        assert result.run_id is None

    def test_result_with_run_id(self):
        from adapters.host_protocols import HostWakeResult

        result = HostWakeResult(
            gateway="openclaw-hooks",
            success=True,
            run_id="abc-123",
            status_code=200,
        )
        assert result.run_id == "abc-123"

    def test_result_with_error(self):
        from adapters.host_protocols import HostWakeResult

        result = HostWakeResult(
            gateway="test",
            success=False,
            error="HTTP 401",
            status_code=401,
        )
        assert result.success is False
        assert result.error == "HTTP 401"

    def test_result_is_frozen(self):
        from adapters.host_protocols import HostWakeResult

        result = HostWakeResult(gateway="test", success=True)
        with pytest.raises(Exception):
            result.success = False  # type: ignore


class TestHostCapabilities:
    """测试 HostCapabilities 能力声明。"""

    def test_shadow_only_capabilities(self):
        from adapters.host_protocols import HostCapabilities, HostMode

        caps = HostCapabilities(
            modes=[HostMode.SHADOW],
            supports_shadow=True,
        )
        assert caps.supports_shadow is True
        assert caps.supports_notification is False
        assert caps.supports_hooks_live is False

    def test_full_capabilities(self):
        from adapters.host_protocols import HostCapabilities, HostMode

        caps = HostCapabilities(
            modes=[HostMode.SHADOW, HostMode.NOTIFICATION, HostMode.HOOKS_LIVE],
            supports_shadow=True,
            supports_notification=True,
            supports_hooks_live=True,
        )
        assert len(caps.modes) == 3


class TestOpenClawProfile:
    """测试 OpenClaw 宿主 profile。"""

    def test_profile_name(self):
        from adapters.openclaw.profile import OpenClawProfile

        profile = OpenClawProfile()
        assert profile.name == "openclaw"

    def test_profile_capabilities(self):
        from adapters.openclaw.profile import OpenClawProfile
        from adapters.host_protocols import HostMode

        profile = OpenClawProfile()
        caps = profile.capabilities

        assert HostMode.SHADOW in caps.modes
        assert HostMode.NOTIFICATION in caps.modes
        assert HostMode.HOOKS_LIVE in caps.modes
        assert caps.supports_shadow is True
        assert caps.supports_notification is True
        assert caps.supports_hooks_live is True

    def test_profile_entry_points(self):
        from adapters.openclaw.profile import OpenClawProfile
        from adapters.host_protocols import HostMode

        profile = OpenClawProfile()

        assert profile.get_entry_point(HostMode.SHADOW) == "adapters.openclaw.shadow_runtime"
        assert profile.get_entry_point(HostMode.NOTIFICATION) == "adapters.openclaw.notification_adapter"
        assert profile.get_entry_point(HostMode.HOOKS_LIVE) == "adapters.openclaw.hooks_adapter"

    def test_profile_maturity(self):
        from adapters.openclaw.profile import OpenClawProfile
        from adapters.host_protocols import HostMode

        profile = OpenClawProfile()

        assert "正式工程面" in profile.get_maturity(HostMode.SHADOW)
        assert "正式工程面" in profile.get_maturity(HostMode.NOTIFICATION)
        assert "MVP" in profile.get_maturity(HostMode.HOOKS_LIVE)

    def test_profile_validation_status(self):
        from adapters.openclaw.profile import OpenClawProfile
        from adapters.host_protocols import HostMode

        profile = OpenClawProfile()

        assert profile.is_validated(HostMode.SHADOW) is True
        assert profile.is_validated(HostMode.NOTIFICATION) is True
        assert profile.is_validated(HostMode.HOOKS_LIVE) is True

    def test_profile_to_dict(self):
        from adapters.openclaw.profile import OpenClawProfile

        profile = OpenClawProfile()
        d = profile.to_dict()

        assert d["name"] == "openclaw"
        assert "shadow" in d["capabilities"]
        assert "notification" in d["capabilities"]
        assert "hooks_live" in d["capabilities"]
