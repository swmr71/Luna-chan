#!/usr/bin/env python3
"""
Luna-chan セットアップ検証スクリプト
環境変数、API キー、ファイル構成を確認
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def check_env_file():
    """環境変数ファイルをチェック"""
    print("📋 Checking environment variables...")
    
    if not Path(".env").exists():
        print("  ❌ .env file not found. Create it from .env.example")
        return False
    
    load_dotenv()
    
    required = ["GOOGLE_API_KEY", "PVE_ENDPOINT", "PVE_USER", "PVE_TOKEN_NAME", "PVE_TOKEN_VALUE"]
    missing = []
    
    for key in required:
        value = os.getenv(key)
        if not value:
            missing.append(key)
            print(f"  ❌ {key} is not set")
        else:
            masked = value[:20] + "..." if len(value) > 20 else value
            print(f"  ✅ {key}: {masked}")
    
    return len(missing) == 0

def check_files():
    """必須ファイルをチェック"""
    print("\n📂 Checking required files...")
    
    required_files = [
        "main.py",
        "luna.py",
        "tools.py",
        "luna_config.json",
        "luna_memory.md",
        "requirements.txt"
    ]
    
    all_exist = True
    for file in required_files:
        if Path(file).exists():
            size = Path(file).stat().st_size
            print(f"  ✅ {file} ({size} bytes)")
        else:
            print(f"  ❌ {file} is missing")
            all_exist = False
    
    return all_exist

def check_dependencies():
    """Python 依存パッケージをチェック"""
    print("\n🔧 Checking Python dependencies...")
    
    dependencies = [
        "google.generativeai",
        "proxmoxer",
        "dotenv"
    ]
    
    all_available = True
    for package in dependencies:
        try:
            __import__(package.split(".")[0])
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} not installed")
            all_available = False
    
    if not all_available:
        print("\n  💡 Install with: pip install -r requirements.txt")
    
    return all_available

def check_luna_config():
    """Luna 設定をチェック"""
    print("\n🌙 Checking Luna configuration...")
    
    import json
    
    try:
        with open("luna_config.json", "r") as f:
            config = json.load(f)
            name = config.get("name", "Unknown")
            relationship = config.get("relationship", "Unknown")
            print(f"  ✅ Luna: {name} ({relationship})")
            print(f"  ✅ Created: {config.get('background', {}).get('created_date', 'N/A')}")
    except Exception as e:
        print(f"  ❌ Failed to load config: {e}")
        return False
    
    return True

def main():
    print("=" * 60)
    print("🌙 Luna-chan Setup Verification")
    print("=" * 60)
    
    checks = [
        ("Environment Variables", check_env_file),
        ("Required Files", check_files),
        ("Python Dependencies", check_dependencies),
        ("Luna Configuration", check_luna_config)
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"  ❌ Error: {e}")
            results.append((check_name, False))
    
    print("\n" + "=" * 60)
    print("📊 Summary:")
    print("=" * 60)
    
    all_passed = True
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {check_name}")
        if not result:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n✨ All checks passed! Ready to run:\n")
        print("  python main.py\n")
        return 0
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
