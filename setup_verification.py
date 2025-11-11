#!/usr/bin/env python3
"""
PDSA Project Setup Verification Script
Run this script to verify the complete project setup
"""

import os
import sys
import json
from pathlib import Path

def check_directory_structure():
    """Check if all required directories exist"""
    print("🔍 Checking directory structure...")
    
    required_dirs = [
        "shared/frontend",
        "shared/backend", 
        "shared/database",
        "games/eight_queens/algorithms",
        "games/eight_queens/frontend", 
        "games/eight_queens/api",
        "games/eight_queens/tests",
        "games/eight_queens/docs",
        "games/snake_ladder",
        "games/traffic_simulation",
        "games/traveling_salesman", 
        "games/tower_hanoi"
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        print("❌ Missing directories:")
        for dir_path in missing_dirs:
            print(f"   - {dir_path}")
        return False
    else:
        print("✅ All directories present")
        return True

def check_required_files():
    """Check if all required files exist"""
    print("🔍 Checking required files...")
    
    required_files = [
        "README.md",
        "requirements.txt",
        "package.json",
        ".env.example",
        ".env",
        "tailwind.config.js",
        "shared/frontend/index.html",
        "shared/frontend/js/main.js",
        "shared/backend/main.py",
        "shared/backend/config.py",
        "shared/database/connection.py",
        "shared/database/schema.sql",
        "games/eight_queens/README.md",
        "games/snake_ladder/README.md",
        "games/traffic_simulation/README.md",
        "games/traveling_salesman/README.md",
        "games/tower_hanoi/README.md",
        "PROJECT_STRUCTURE.md"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    else:
        print("✅ All required files present")
        return True

def test_template_structure():
    """Test if template structure is complete"""
    print("🔍 Testing template structure...")
    
    try:
        # Check if all game modules have required folders
        games = ['eight_queens', 'snake_ladder', 'traffic_simulation', 'traveling_salesman', 'tower_hanoi']
        required_folders = ['algorithms', 'frontend', 'api', 'tests', 'docs']
        
        for game in games:
            for folder in required_folders:
                folder_path = Path(f"games/{game}/{folder}")
                if not folder_path.exists():
                    print(f"❌ Missing folder: {folder_path}")
                    return False
        
        print(f"✅ Template structure complete - all {len(games)} games have required folders")
        return True
        
    except Exception as e:
        print(f"❌ Template structure test failed: {e}")
        return False

def test_python_dependencies():
    """Test if required Python packages can be imported"""
    print("🔍 Testing Python dependencies...")
    
    required_packages = [
        ("fastapi", "FastAPI web framework"),
        ("uvicorn", "ASGI server"), 
        ("mysql.connector", "MySQL connector"),
        ("dotenv", "Environment variables")
    ]
    
    missing_packages = []
    for package, description in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"   ✅ {package} - {description}")
        except ImportError:
            print(f"   ❌ {package} - {description} (Not installed)")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n💡 To install missing packages:")
        print(f"   pip install -r requirements.txt")
        return False
    else:
        print("✅ All Python dependencies available")
        return True

def generate_setup_summary():
    """Generate setup summary"""
    print("\n" + "="*60)
    print("📋 PDSA PROJECT SETUP SUMMARY")
    print("="*60)
    
    checks = [
        ("Directory Structure", check_directory_structure()),
        ("Required Files", check_required_files()),
        ("Template Structure", test_template_structure())
    ]
    
    all_passed = all(result for _, result in checks)
    
    print("\n📊 Template Status:")
    for name, result in checks:
        status = "✅ PASS" if result else "❌ FAIL" 
        print(f"   {name:<25} {status}")
    
    # Check dependencies but don't fail on them for template
    print("\n📦 Dependencies (for reference):")
    test_python_dependencies()
    
    if all_passed:
        print(f"\n🎉 TEMPLATE COMPLETE! Ready for team collaboration!")
        print(f"\n📝 Next Steps:")
        print(f"   1. Push this structure to GitHub")
        print(f"   2. Team members clone and create feature branches")
        print(f"   3. Install dependencies: pip install -r requirements.txt")
        print(f"   4. Start developing individual game modules")
        print(f"\n🚀 All 5 game modules ready for development!")
        return True
    else:
        print(f"\n⚠️  TEMPLATE INCOMPLETE - Please fix the issues above")
        return False

def main():
    """Main function"""
    print("🔧 PDSA Project Setup Verification")
    print("="*60)
    
    # Change to project root directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Run all checks
    success = generate_setup_summary()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()