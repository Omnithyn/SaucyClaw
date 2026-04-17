"""测试 OpenHarness 和 Hermes 宿主 profile。

M11 — OpenHarness Recon & Skeleton Profile
"""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
import sys
sys.path.insert(0, str(PROJECT_ROOT))


class TestOpenHarnessProfile:
    """测试 OpenHarness 宿主 profile。"""

    def test_profile_name(self):
        from adapters.openharness.profile import OpenHarnessProfile

        profile = OpenHarnessProfile()
        assert profile.name == "openharness"

    def test_profile_capabilities(self):
        from adapters.openharness.profile import OpenHarnessProfile
        from adapters.host_protocols import HostMode

        profile = OpenHarnessProfile()
        caps = profile.capabilities

        assert HostMode.SHADOW in caps.modes
        assert HostMode.NOTIFICATION in caps.modes
        assert HostMode.HOOKS_LIVE in caps.modes
        assert caps.supports_shadow is True
        assert caps.supports_notification is True
        assert caps.supports_hooks_live is True

    def test_profile_entry_points(self):
        from adapters.openharness.profile import OpenHarnessProfile
        from adapters.host_protocols import HostMode

        profile = OpenHarnessProfile()

        assert profile.get_entry_point(HostMode.SHADOW) == "adapters.openharness.shadow_runtime"
        assert profile.get_entry_point(HostMode.NOTIFICATION) == "adapters.openharness.notification_adapter"
        assert profile.get_entry_point(HostMode.HOOKS_LIVE) == "adapters.openharness.hooks_adapter"

    def test_profile_maturity(self):
        from adapters.openharness.profile import OpenHarnessProfile
        from adapters.host_protocols import HostMode

        profile = OpenHarnessProfile()

        assert "概念验证" in profile.get_maturity(HostMode.SHADOW)
        assert "概念验证" in profile.get_maturity(HostMode.NOTIFICATION)
        assert "概念验证" in profile.get_maturity(HostMode.HOOKS_LIVE)

    def test_profile_validation_status(self):
        from adapters.openharness.profile import OpenHarnessProfile
        from adapters.host_protocols import HostMode

        profile = OpenHarnessProfile()

        # All modes are not yet validated
        assert profile.is_validated(HostMode.SHADOW) is False
        assert profile.is_validated(HostMode.NOTIFICATION) is False
        assert profile.is_validated(HostMode.HOOKS_LIVE) is False

    def test_profile_to_dict(self):
        from adapters.openharness.profile import OpenHarnessProfile

        profile = OpenHarnessProfile()
        d = profile.to_dict()

        assert d["name"] == "openharness"
        assert "shadow" in d["capabilities"]
        assert "notification" in d["capabilities"]
        assert "hooks_live" in d["capabilities"]


class TestHermesProfile:
    """测试 Hermes Agent 宿主 profile。"""

    def test_profile_name(self):
        from adapters.hermes.profile import HermesProfile

        profile = HermesProfile()
        assert profile.name == "hermes"

    def test_profile_capabilities(self):
        from adapters.hermes.profile import HermesProfile
        from adapters.host_protocols import HostMode

        profile = HermesProfile()
        caps = profile.capabilities

        assert HostMode.SHADOW in caps.modes
        assert HostMode.NOTIFICATION in caps.modes
        assert HostMode.HOOKS_LIVE in caps.modes
        assert caps.supports_shadow is True
        assert caps.supports_notification is True
        assert caps.supports_hooks_live is True

    def test_profile_entry_points(self):
        from adapters.hermes.profile import HermesProfile
        from adapters.host_protocols import HostMode

        profile = HermesProfile()

        assert profile.get_entry_point(HostMode.SHADOW) == "adapters.hermes.shadow_runtime"
        assert profile.get_entry_point(HostMode.NOTIFICATION) == "adapters.hermes.notification_adapter"
        assert profile.get_entry_point(HostMode.HOOKS_LIVE) == "adapters.hermes.hooks_adapter"

    def test_profile_maturity(self):
        from adapters.hermes.profile import HermesProfile
        from adapters.host_protocols import HostMode

        profile = HermesProfile()

        assert "概念验证" in profile.get_maturity(HostMode.SHADOW)
        assert "概念验证" in profile.get_maturity(HostMode.NOTIFICATION)
        assert "概念验证" in profile.get_maturity(HostMode.HOOKS_LIVE)

    def test_profile_validation_status(self):
        from adapters.hermes.profile import HermesProfile
        from adapters.host_protocols import HostMode

        profile = HermesProfile()

        # All modes are not yet validated
        assert profile.is_validated(HostMode.SHADOW) is False
        assert profile.is_validated(HostMode.NOTIFICATION) is False
        assert profile.is_validated(HostMode.HOOKS_LIVE) is False

    def test_profile_to_dict(self):
        from adapters.hermes.profile import HermesProfile

        profile = HermesProfile()
        d = profile.to_dict()

        assert d["name"] == "hermes"
        assert "shadow" in d["capabilities"]
        assert "notification" in d["capabilities"]
        assert "hooks_live" in d["capabilities"]
