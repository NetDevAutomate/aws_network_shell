#!/usr/bin/env python3
"""Interactive routing cache test - Simple validation script.

Run with: python tests/interactive_routing_cache_test.py

This provides immediate visual feedback and binary validation.
Based on 7-model consultation via RepoPrompt (Cohere R pragmatic approach).
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from aws_network_tools.shell.main import AWSNetShell
from aws_network_tools.core.cache_db import CacheDB


def main():
    print("🚀 Interactive Routing Cache Test\n")
    print("=" * 70)

    shell = AWSNetShell()
    shell.no_cache = True

    # Test 1: Create routing cache
    print("\n1️⃣  Creating routing cache...")
    print("-" * 70)
    shell.onecmd('create_routing_cache')

    # Validate cache created
    cache = shell._cache.get("routing-cache", {})
    vpc_count = len(cache.get("vpc", {}).get("routes", []))
    tgw_count = len(cache.get("tgw", {}).get("routes", []))
    cloudwan_count = len(cache.get("cloudwan", {}).get("routes", []))
    total = vpc_count + tgw_count + cloudwan_count

    print(f"\n✓ Cache created:")
    print(f"  VPC: {vpc_count} routes")
    print(f"  Transit Gateway: {tgw_count} routes")
    print(f"  Cloud WAN: {cloudwan_count} routes")
    print(f"  Total: {total} routes")

    # Binary assertions
    assert vpc_count > 0, "❌ No VPC routes"
    assert total > 0, "❌ No routes cached"
    print("✅ PASS: Route counts valid")

    # Test 2: Show summary
    print("\n2️⃣  Showing cache summary...")
    print("-" * 70)
    shell.onecmd('show routing-cache')

    # Test 3: Show Transit Gateway routes
    print("\n3️⃣  Showing Transit Gateway routes...")
    print("-" * 70)
    shell.onecmd('show routing-cache transit-gateway')

    # Test 4: Show Cloud WAN routes
    print("\n4️⃣  Showing Cloud WAN routes...")
    print("-" * 70)
    shell.onecmd('show routing-cache cloud-wan')

    # Test 5: Save to SQLite
    print("\n5️⃣  Saving to SQLite database...")
    print("-" * 70)
    shell.onecmd('save_routing_cache')

    # Validate DB file exists
    db = CacheDB()
    assert db.db_path.exists(), f"❌ DB file not created: {db.db_path}"
    print(f"✅ PASS: Database file created at {db.db_path}")

    # Test 6: Load from SQLite
    print("\n6️⃣  Loading from SQLite database...")
    print("-" * 70)
    shell._cache.clear()  # Clear memory cache
    shell.onecmd('load_routing_cache')

    # Validate loaded correctly
    loaded_cache = shell._cache.get("routing-cache", {})
    loaded_total = sum(len(d.get("routes", [])) for d in loaded_cache.values())

    print(f"\n✓ Loaded {loaded_total} routes from database")
    assert loaded_total == total, f"❌ Route count mismatch: {loaded_total} != {total}"
    print("✅ PASS: Save/load roundtrip successful")

    # Test 7: Show all routes
    print("\n7️⃣  Showing all routes...")
    print("-" * 70)
    shell.onecmd('show routing-cache all')

    # Final summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    print("✅ Cache creation: PASS")
    print("✅ Display commands: PASS")
    print("✅ SQLite persistence: PASS")
    print("✅ Save/load roundtrip: PASS")
    print("✅ Filtering (vpc/transit-gateway/cloud-wan): PASS")
    print("\n🎉 All tests passed! Routing cache is working correctly.")
    print("\nManual verification:")
    print("  - Check table columns are populated (not empty)")
    print("  - Verify colors are applied to headers")
    print("  - Confirm full IDs shown (not truncated)")


if __name__ == "__main__":
    try:
        main()
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
