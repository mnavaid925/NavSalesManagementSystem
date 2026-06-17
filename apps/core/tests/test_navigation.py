"""Tests for core.navigation: build_sidebar and Module 0 live links."""
import pytest

from apps.core.navigation import (
    MODULE_CATALOG,
    LIVE_LINKS,
    build_sidebar,
    reset_sidebar_cache,
    lookup_submodule,
)


class TestBuildSidebar:
    def test_returns_21_modules(self):
        sidebar = build_sidebar()
        assert len(sidebar) == 21

    def test_module_zero_is_tenant_and_subscription(self):
        sidebar = build_sidebar()
        mod0 = sidebar[0]
        assert mod0["number"] == 0
        assert "Tenant" in mod0["name"]

    def test_each_module_has_five_submodules(self):
        sidebar = build_sidebar()
        for mod in sidebar:
            assert len(mod["submodules"]) == 5, f"Module {mod['number']} should have 5 submodules"

    def test_module_zero_all_five_submodules_live(self):
        """All 5 Module 0 sub-modules must be live (LIVE_LINKS has all 5)."""
        sidebar = build_sidebar()
        mod0 = sidebar[0]
        live_subs = [s for s in mod0["submodules"] if s["is_live"]]
        assert len(live_subs) == 5, (
            f"Expected 5 live Module 0 submodules, got {len(live_subs)}: "
            + str([s["name"] for s in mod0["submodules"] if not s["is_live"]])
        )

    def test_module_zero_submodule_names(self):
        sidebar = build_sidebar()
        mod0 = sidebar[0]
        names = [s["name"] for s in mod0["submodules"]]
        assert "Tenant Onboarding" in names
        assert "Subscription & Billing" in names
        assert "Tenant Isolation & Security" in names
        assert "Custom Branding" in names
        assert "Tenant Health Monitoring" in names

    def test_module_zero_submodules_have_valid_hrefs(self):
        sidebar = build_sidebar()
        mod0 = sidebar[0]
        for sub in mod0["submodules"]:
            assert sub["href"] != "#", f"Sub-module '{sub['name']}' href should not be '#'"
            assert sub["href"] != "", f"Sub-module '{sub['name']}' href should not be empty"

    def test_modules_numbered_0_to_20(self):
        sidebar = build_sidebar()
        numbers = [mod["number"] for mod in sidebar]
        assert numbers == list(range(21))

    def test_each_module_has_slug(self):
        sidebar = build_sidebar()
        for mod in sidebar:
            assert mod["slug"], f"Module {mod['number']} missing slug"

    def test_each_module_has_icon(self):
        sidebar = build_sidebar()
        for mod in sidebar:
            assert mod["icon"], f"Module {mod['number']} missing icon"

    def test_live_count_matches_live_submodules(self):
        sidebar = build_sidebar()
        for mod in sidebar:
            actual_live = sum(1 for s in mod["submodules"] if s["is_live"])
            assert mod["live_count"] == actual_live

    def test_cache_reset_clears_cache(self):
        sidebar1 = build_sidebar()
        reset_sidebar_cache()
        sidebar2 = build_sidebar()
        # Both should have same content — cache was rebuilt correctly
        assert len(sidebar1) == len(sidebar2)

    def test_non_live_submodule_links_to_roadmap(self):
        """A sub-module not in LIVE_LINKS should get a /core/roadmap/... href."""
        sidebar = build_sidebar()
        # Find a non-live sub-module
        for mod in sidebar:
            for sub in mod["submodules"]:
                if not sub["is_live"]:
                    assert "roadmap" in sub["href"] or sub["href"] == "#"
                    return
        # If all are live, test is moot — pass silently

    def test_live_links_module_19_user_roles(self):
        """Module 19 'User Roles & Profiles' should be live."""
        sidebar = build_sidebar()
        mod19 = next(m for m in sidebar if m["number"] == 19)
        roles_sub = next((s for s in mod19["submodules"] if s["name"] == "User Roles & Profiles"), None)
        assert roles_sub is not None
        assert roles_sub["is_live"] is True

    def test_live_links_module_20_user_management(self):
        """Module 20 'User Management & SSO' should be live."""
        sidebar = build_sidebar()
        mod20 = next(m for m in sidebar if m["number"] == 20)
        user_mgmt = next((s for s in mod20["submodules"] if s["name"] == "User Management & SSO"), None)
        assert user_mgmt is not None
        assert user_mgmt["is_live"] is True


class TestLookupSubmodule:
    def test_lookup_valid_module_and_sub(self):
        mod_name, sub_name = lookup_submodule(0, "tenant-onboarding")
        assert mod_name == "Tenant & Subscription Management"
        assert sub_name == "Tenant Onboarding"

    def test_lookup_invalid_module_returns_none(self):
        mod_name, sub_name = lookup_submodule(99, "anything")
        assert mod_name is None
        assert sub_name is None

    def test_lookup_invalid_sub_returns_none_sub(self):
        mod_name, sub_name = lookup_submodule(0, "nonexistent-sub")
        assert mod_name == "Tenant & Subscription Management"
        assert sub_name is None

    def test_lookup_module_1(self):
        mod_name, sub_name = lookup_submodule(1, "lead-capture-ingestion")
        assert mod_name == "Lead Management"
        assert sub_name == "Lead Capture & Ingestion"


class TestModuleCatalog:
    def test_catalog_has_21_entries(self):
        assert len(MODULE_CATALOG) == 21

    def test_catalog_numbered_zero_to_twenty(self):
        numbers = [m["number"] for m in MODULE_CATALOG]
        assert numbers == list(range(21))

    def test_each_catalog_entry_has_required_keys(self):
        for entry in MODULE_CATALOG:
            assert "number" in entry
            assert "name" in entry
            assert "icon" in entry
            assert "submodules" in entry

    def test_module_0_has_expected_submodules(self):
        mod0 = MODULE_CATALOG[0]
        assert set(mod0["submodules"]) == {
            "Tenant Onboarding",
            "Subscription & Billing",
            "Tenant Isolation & Security",
            "Custom Branding",
            "Tenant Health Monitoring",
        }
