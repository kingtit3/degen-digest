#!/usr/bin/env python3
"""Trigger script to run digest generation with new OpenRouter key"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the project root to Python path
root_path = Path(__file__).resolve().parent
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

load_dotenv()

def main():
    """Main function to trigger digest generation"""
    print("🚀 Triggering Degen Digest Generation...")
    print("=" * 50)
    
    # Check OpenRouter API key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ No OpenRouter API key found in .env file")
        return
    
    print(f"✅ OpenRouter API key found: {api_key[:10]}...")
    
    # Import and run main
    try:
        from main import main as run_digest
        print("🔄 Starting digest generation...")
        run_digest()
        print("✅ Digest generation completed!")
        
        # Check if new digest was created
        digest_path = Path("output/digest.md")
        if digest_path.exists():
            print(f"📄 New digest created: {digest_path}")
            # Show first few lines
            with open(digest_path, 'r') as f:
                lines = f.readlines()[:5]
                print("📝 Preview:")
                for line in lines:
                    print(f"   {line.strip()}")
        else:
            print("⚠️ No digest file found - check logs for errors")
            
    except Exception as e:
        print(f"❌ Error running digest generation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 