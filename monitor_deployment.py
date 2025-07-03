#!/usr/bin/env python3
"""Monitor deployment and service status"""

import json
import subprocess
from datetime import datetime


def run_command(cmd):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def check_service_status():
    """Check the Cloud Run service status"""
    print("🔍 Checking Cloud Run service status...")

    # Get service info
    success, output, error = run_command(
        "gcloud run services describe degen-digest-dashboard --region=us-central1 --format=json"
    )

    if not success:
        print(f"❌ Error getting service info: {error}")
        return

    try:
        service_info = json.loads(output)
        url = service_info.get("status", {}).get("url", "Unknown")
        ready = service_info.get("status", {}).get("conditions", [])

        print(f"✅ Service URL: {url}")

        # Check if service is ready
        for condition in ready:
            if condition.get("type") == "Ready":
                status = condition.get("status", "Unknown")
                print(f"📊 Service Status: {status}")
                if status == "True":
                    print("🎉 Service is ready and running!")
                else:
                    print("⚠️ Service is not ready yet")
                break

    except json.JSONDecodeError:
        print("❌ Error parsing service info")


def check_logs():
    """Check recent logs"""
    print("\n📝 Checking recent logs...")

    success, output, error = run_command(
        'gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=degen-digest-dashboard" --limit=5 --format="table(timestamp,severity,textPayload)"'
    )

    if success:
        print(output)
    else:
        print(f"❌ Error getting logs: {error}")


def main():
    """Main monitoring function"""
    print("🚀 Degen Digest Deployment Monitor")
    print("=" * 50)
    print(f"⏰ Started at: {datetime.now()}")

    # Check service status
    check_service_status()

    # Check logs
    check_logs()

    print("\n💡 To monitor logs in real-time, run:")
    print(
        'gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=degen-digest-dashboard"'
    )


if __name__ == "__main__":
    main()
