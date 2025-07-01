#!/usr/bin/env python3
"""Generate and rename digest with comprehensive error handling"""

import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Add the project root to Python path
root_path = Path(__file__).resolve().parent
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

load_dotenv()

def check_environment():
    """Check if all required environment variables are set"""
    required_vars = ["OPENROUTER_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file")
        return False
    
    return True

def main():
    """Generate digest with automatic renaming"""
    print("🚀 Degen Digest Generation & Auto-Rename")
    print("=" * 50)
    
    # Check environment
    if not check_environment():
        return
    
    print(f"✅ Environment check passed")
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Import and run main digest generation
        from main import main as run_digest
        print("🔄 Generating digest...")
        run_digest()
        print("✅ Digest generation completed!")
        
        # Verify the digest was created and renamed
        output_dir = Path("output")
        digest_files = list(output_dir.glob("digest*.md"))
        
        if digest_files:
            print(f"📄 Found {len(digest_files)} digest files:")
            for file in sorted(digest_files, key=lambda x: x.stat().st_mtime, reverse=True):
                size = file.stat().st_size
                mtime = datetime.fromtimestamp(file.stat().st_mtime)
                print(f"   - {file.name} ({size:,} bytes, {mtime.strftime('%Y-%m-%d %H:%M')})")
            
            # Show the most recent digest preview
            latest_digest = max(digest_files, key=lambda x: x.stat().st_mtime)
            print(f"\n📝 Latest digest preview ({latest_digest.name}):")
            with open(latest_digest, 'r', encoding='utf-8') as f:
                lines = f.readlines()[:8]  # Show first 8 lines
                for line in lines:
                    print(f"   {line.rstrip()}")
            print("   ...")
            
        else:
            print("⚠️ No digest files found - check logs for errors")
            
    except Exception as e:
        print(f"❌ Error during digest generation: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print(f"\n🎉 Digest generation and renaming completed successfully!")
    print(f"🕐 Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 