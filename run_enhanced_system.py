#!/usr/bin/env python3
"""
Enhanced System Launcher
Easy way to run the enhanced viral prediction system
"""

import os
import sys
import subprocess
from pathlib import Path

def setup_environment():
    """Setup Python path and environment"""
    current_dir = Path(__file__).parent.absolute()
    os.environ['PYTHONPATH'] = f"{current_dir}:{os.environ.get('PYTHONPATH', '')}"
    sys.path.insert(0, str(current_dir))

def run_enhanced_pipeline():
    """Run the enhanced data pipeline"""
    print("🚀 Running Enhanced Data Pipeline...")
    print("=" * 50)
    
    try:
        from scripts.enhanced_data_pipeline import main as run_pipeline
        import asyncio
        
        asyncio.run(run_pipeline())
        print("\n✅ Enhanced pipeline completed successfully!")
        
    except Exception as e:
        print(f"❌ Pipeline failed: {e}")
        return False
    
    return True

def run_dashboard():
    """Launch the Streamlit dashboard"""
    print("\n📊 Launching Enhanced Dashboard...")
    print("=" * 50)
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "dashboard/app.py", "--server.port", "8501"
        ], check=True)
        
    except KeyboardInterrupt:
        print("\n⏹️ Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Dashboard failed: {e}")

def run_tests():
    """Run comprehensive tests"""
    print("🧪 Running Comprehensive Tests...")
    print("=" * 50)
    
    try:
        from test_all_enhancements import main as run_tests
        import asyncio
        
        asyncio.run(run_tests())
        
    except Exception as e:
        print(f"❌ Tests failed: {e}")
        return False
    
    return True

def show_menu():
    """Show the main menu"""
    print("\n🎯 Enhanced Viral Prediction System")
    print("=" * 40)
    print("1. Run Enhanced Data Pipeline")
    print("2. Launch Dashboard")
    print("3. Run Comprehensive Tests")
    print("4. Run Pipeline + Launch Dashboard")
    print("5. Exit")
    print("=" * 40)

def main():
    """Main launcher function"""
    setup_environment()
    
    while True:
        show_menu()
        
        try:
            choice = input("\nSelect an option (1-5): ").strip()
            
            if choice == "1":
                run_enhanced_pipeline()
                
            elif choice == "2":
                run_dashboard()
                
            elif choice == "3":
                run_tests()
                
            elif choice == "4":
                print("\n🔄 Running pipeline first, then launching dashboard...")
                if run_enhanced_pipeline():
                    print("\n📊 Pipeline completed! Launching dashboard...")
                    run_dashboard()
                else:
                    print("❌ Pipeline failed, not launching dashboard")
                    
            elif choice == "5":
                print("👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid choice. Please select 1-5.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 