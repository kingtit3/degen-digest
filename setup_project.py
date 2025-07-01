#!/usr/bin/env python3
"""Setup script to fix project issues and get Degen Digest running."""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 12):
        print(f"❌ Python 3.12+ required, found {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - compatible")
    return True

def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = [
        "streamlit", "pandas", "sqlmodel", "httpx", "python-dotenv"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} - installed")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - missing")
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        return run_command(f"pip install {' '.join(missing_packages)}", "Installing dependencies")
    
    return True

def setup_database():
    """Set up the database with correct schema."""
    print("\n🗄️  Setting up database...")
    
    # Check if database exists and has issues
    db_path = Path("output/degen_digest.db")
    if db_path.exists():
        print("⚠️  Database exists - checking for schema issues...")
        try:
            from storage.db import stats
            stats()
            print("✅ Database schema appears correct")
            return True
        except Exception as e:
            print(f"❌ Database schema issues detected: {e}")
            print("🔄 Recreating database...")
    
    # Recreate database
    return run_command("python recreate_db.py", "Recreating database")

def test_scrapers():
    """Test if scrapers can run without errors."""
    print("\n🔍 Testing scrapers...")
    
    scrapers = [
        ("scrapers/newsapi_headlines.py", "News API Headlines"),
        ("scrapers/coingecko_gainers.py", "CoinGecko Gainers"),
    ]
    
    for scraper_path, name in scrapers:
        if Path(scraper_path).exists():
            print(f"🔄 Testing {name}...")
            try:
                result = subprocess.run(
                    f"python {scraper_path}", 
                    shell=True, 
                    capture_output=True, 
                    text=True,
                    timeout=30
                )
                if result.returncode == 0:
                    print(f"✅ {name} - working")
                else:
                    print(f"⚠️  {name} - has issues (non-critical)")
            except subprocess.TimeoutExpired:
                print(f"⚠️  {name} - timed out (non-critical)")
            except Exception as e:
                print(f"⚠️  {name} - error: {e} (non-critical)")

def check_environment():
    """Check environment variables."""
    print("\n🔧 Checking environment variables...")
    
    required_vars = [
        "APIFY_API_TOKEN",
        "OPENROUTER_API_KEY", 
        "NEWSAPI_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if os.getenv(var):
            print(f"✅ {var} - set")
        else:
            missing_vars.append(var)
            print(f"❌ {var} - missing")
    
    if missing_vars:
        print(f"\n⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these in your .env file")
        return False
    
    return True

def setup_pre_commit():
    """Set up pre-commit hooks."""
    print("\n🔧 Setting up pre-commit hooks...")
    
    if not Path(".pre-commit-config.yaml").exists():
        print("⚠️  Pre-commit config not found, skipping...")
        return True
    
    return run_command("pre-commit install", "Installing pre-commit hooks")

def main():
    """Main setup function."""
    print("🚀 Degen Digest Project Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Check environment variables
    if not check_environment():
        print("⚠️  Environment variables missing - some features may not work")
    
    # Setup database
    if not setup_database():
        print("❌ Failed to setup database")
        sys.exit(1)
    
    # Test scrapers
    test_scrapers()
    
    # Setup pre-commit
    setup_pre_commit()
    
    print("\n🎉 Setup completed!")
    print("\n📋 Next steps:")
    print("1. Start the dashboard: cd dashboard && streamlit run app.py")
    print("2. Generate a digest: python main.py")
    print("3. Run tests: make test")
    print("4. Check health: python -c \"from utils.health_monitor import health_monitor; print(health_monitor.get_health_summary())\"")
    
    print("\n📚 Useful commands:")
    print("- make help          # Show all available commands")
    print("- make dashboard     # Start dashboard")
    print("- make digest        # Generate digest")
    print("- make test          # Run tests")
    print("- make format        # Format code")
    print("- make clean         # Clean cache files")

if __name__ == "__main__":
    main() 