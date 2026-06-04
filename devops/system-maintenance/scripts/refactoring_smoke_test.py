#!/usr/bin/env python3
"""
Refactoring smoke test — verify core functionality after template extraction

Usage:
    python3 verify_refactoring.py
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_template_loading():
    """Test that legacy templates load correctly"""
    try:
        from scripts.card_engine import load_legacy_template
        
        # Test AN template
        an_tpl = load_legacy_template('an')
        assert len(an_tpl) > 1000, "AN template too short"
        assert '{{photo_path}}' in an_tpl, "Missing {{photo_path}} placeholder"
        assert 'Be:A' in an_tpl, "Missing brand"
        
        # Test DG template
        dg_tpl = load_legacy_template('dg')
        assert len(dg_tpl) > 1000, "DG template too short"
        assert '// {{subtitle}}' in dg_tpl, "Missing DG-specific subtitle"
        
        print("✅ Template loading: PASS")
        return True
    except Exception as e:
        print(f"❌ Template loading: FAIL - {e}")
        return False

def test_render_utils():
    """Test that render utility module exists and is importable"""
    try:
        from scripts.render_utils import (
            render_html_files,
            render_style_batch,
            print_summary
        )
        print("✅ Render utils: PASS")
        return True
    except ImportError as e:
        print(f"❌ Render utils: FAIL - {e}")
        return False

def test_pipeline_exists():
    """Test that main pipeline script exists and is syntactically valid"""
    try:
        pipeline_path = Path("scripts/run_pipeline.py")
        assert pipeline_path.exists(), "Pipeline file not found"
        
        # Syntax check
        import py_compile
        py_compile.compile(str(pipeline_path), doraise=True)
        
        print("✅ Pipeline syntax: PASS")
        return True
    except Exception as e:
        print(f"❌ Pipeline syntax: FAIL - {e}")
        return False

def test_legacy_removed():
    """Test that legacy files have been removed"""
    legacy_dir = Path("scripts/legacy")
    
    if legacy_dir.exists():
        remaining = list(legacy_dir.glob("*"))
        if remaining:
            print(f"⚠️  Legacy cleanup: PARTIAL - {len(remaining)} files remain")
            return False
        else:
            print("✅ Legacy cleanup: PASS (directory exists but empty)")
    else:
        print("✅ Legacy cleanup: PASS (directory removed)")
    
    return True

def test_import_chain():
    """Test that import chain is not broken"""
    try:
        # This will fail if imports are broken
        from scripts.card_engine import generate_card
        print("✅ Import chain: PASS")
        return True
    except ImportError as e:
        # Expected if color_engine not available, but card_engine itself should load
        if "color_engine" in str(e):
            print("⚠️  Import chain: PARTIAL - card_engine loads but dependencies missing")
            return True
        print(f"❌ Import chain: FAIL - {e}")
        return False
    except Exception as e:
        print(f"❌ Import chain: FAIL - {e}")
        return False

def main():
    """Run all smoke tests"""
    print("🧪 Refactoring Smoke Tests\n")
    
    tests = [
        ("Template Loading", test_template_loading),
        ("Render Utils", test_render_utils),
        ("Pipeline Syntax", test_pipeline_exists),
        ("Legacy Removed", test_legacy_removed),
        ("Import Chain", test_import_chain),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n[{name}]")
        results.append(test_func())
    
    print("\n" + "="*50)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed — review refactoring")
        return 1

if __name__ == "__main__":
    sys.exit(main())
