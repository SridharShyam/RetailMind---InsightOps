#!/usr/bin/env python3
"""
Setup script to organize your existing model files into the FastAPI structure
"""
import os
import shutil
from pathlib import Path

def setup_project():
    """Setup project structure and move files"""
    
    print("🚀 Setting up RetailMind AI Backend...")
    print("=" * 60)
    
    # Define directories
    directories = [
        "app/api",
        "app/api/v1",
        "app/models",
        "app/services",
        "app/schemas",
        "app/core",
        "app/utils",
        "data",
        "tests"
    ]
    
    # Create directories
    print("\n📁 Creating directories...")
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {directory}")
    
    # Files to move to app/models/
    model_files = [
        "analyzer.py",
        "competitive_analyzer.py",
        "forecasting.py",
        "inventory_risk.py",
        "load_data.py",
        "pricing.py",
        "recommendations.py",
        "risk_engine.py",
        "seasonality_detector.py",
        "simulator.py",
        "synergy_analyzer.py"
    ]
    
    # Check and move model files
    print("\n📦 Moving model files to app/models/...")
    current_dir = Path(".")
    
    for file in model_files:
        source = current_dir / file
        destination = Path("app/models") / file
        
        if source.exists():
            if not destination.exists():
                shutil.copy2(source, destination)
                print(f"  ✓ Copied {file}")
            else:
                print(f"  → {file} already exists in destination")
        else:
            print(f"  ⚠ {file} not found in current directory")
    
    # Create empty __init__.py files
    print("\n📝 Creating __init__.py files...")
    init_files = [
        "app/__init__.py",
        "app/api/__init__.py",
        "app/api/v1/__init__.py",
        "app/core/__init__.py",
        "app/utils/__init__.py",
        "tests/__init__.py"
    ]
    
    for init_file in init_files:
        init_path = Path(init_file)
        if not init_path.exists():
            init_path.write_text('"""Package initialization"""')
            print(f"  ✓ {init_file}")
    
    # Check for data file
    print("\n💾 Checking for data file...")
    data_file = "synthetic_retail_inventory_with_products_10k.csv"
    source_data = current_dir / data_file
    dest_data = Path("data") / data_file
    
    if source_data.exists():
        if not dest_data.exists():
            shutil.copy2(source_data, dest_data)
            print(f"  ✓ Copied {data_file} to data/")
        else:
            print(f"  → {data_file} already in data/ directory")
    else:
        print(f"  ⚠ {data_file} not found - will generate demo data on startup")
    
    # Create .env if not exists
    print("\n⚙️  Setting up environment...")
    if not Path(".env").exists():
        if Path(".env.example").exists():
            shutil.copy2(".env.example", ".env")
            print("  ✓ Created .env from .env.example")
        else:
            print("  ⚠ .env.example not found, create .env manually")
    else:
        print("  → .env already exists")
    
    print("\n" + "=" * 60)
    print("✅ Setup complete!")
    print("\n🎯 Next steps:")
    print("1. Activate virtual environment:")
    print("   python -m venv venv")
    print("   source venv/bin/activate  # Mac/Linux")
    print("   venv\\Scripts\\activate     # Windows")
    print("\n2. Install dependencies:")
    print("   pip install -r requirements.txt")
    print("\n3. Run the server:")
    print("   uvicorn app.main:app --reload")
    print("\n4. Open browser:")
    print("   http://localhost:8000/docs")
    print("=" * 60)

if __name__ == "__main__":
    setup_project()