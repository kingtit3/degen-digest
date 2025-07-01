#!/usr/bin/env python3
"""Setup script for Google Cloud AI (Vertex AI) integration"""

import os
from dotenv import load_dotenv

load_dotenv()

def setup_google_ai():
    """Setup instructions for Google Cloud AI"""
    print("🚀 Google Cloud AI (Vertex AI) Setup")
    print("=" * 50)
    
    print("\n📋 Prerequisites:")
    print("1. Google Cloud Project with billing enabled")
    print("2. Vertex AI API enabled")
    print("3. Service account with Vertex AI permissions")
    
    print("\n🔧 Setup Steps:")
    print("1. Install Google Cloud SDK:")
    print("   pip install google-cloud-aiplatform")
    
    print("\n2. Authenticate with Google Cloud:")
    print("   gcloud auth application-default login")
    
    print("\n3. Set your project ID:")
    print("   gcloud config set project YOUR_PROJECT_ID")
    
    print("\n4. Enable Vertex AI API:")
    print("   gcloud services enable aiplatform.googleapis.com")
    
    print("\n5. Update your .env file:")
    print("   GOOGLE_CLOUD_PROJECT=your-project-id")
    print("   GOOGLE_CLOUD_LOCATION=us-central1")
    
    print("\n6. Create a service account (optional, for production):")
    print("   gcloud iam service-accounts create degen-digest-ai \\")
    print("       --display-name='Degen Digest AI Service Account'")
    print("   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \\")
    print("       --member='serviceAccount:degen-digest-ai@YOUR_PROJECT_ID.iam.gserviceaccount.com' \\")
    print("       --role='roles/aiplatform.user'")
    
    print("\n💰 Pricing:")
    print("- Gemini Pro: $0.0005 / 1K input tokens")
    print("- Gemini Flash: $0.000075 / 1K input tokens")
    print("- Much cheaper than OpenAI for high volume!")

if __name__ == "__main__":
    setup_google_ai() 