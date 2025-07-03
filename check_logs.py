#!/usr/bin/env python3
"""Simple script to check Google Cloud logs"""

import json
import subprocess
from datetime import datetime


def run_gcloud_command(cmd):
    """Run a gcloud command and return the result"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def check_cloud_run_logs():
    """Check Cloud Run logs"""
    print("📝 Checking Cloud Run logs...")
    print("=" * 50)

    # Check recent logs
    success, output, error = run_gcloud_command(
        'gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=degen-digest-dashboard" --limit=10 --format=json'
    )

    if success and output.strip():
        try:
            logs = json.loads(output)
            if logs:
                print(f"📊 Found {len(logs)} recent log entries:")
                print("-" * 30)
                for log in logs[:5]:  # Show first 5 logs
                    timestamp = log.get("timestamp", "Unknown")
                    severity = log.get("severity", "INFO")
                    text = log.get("textPayload", "No message")

                    # Format timestamp
                    if timestamp != "Unknown":
                        try:
                            dt = datetime.fromisoformat(
                                timestamp.replace("Z", "+00:00")
                            )
                            timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")
                        except Exception:
                            pass

                    print(f"[{timestamp}] {severity}: {text[:100]}...")
            else:
                print("📭 No recent logs found")
        except json.JSONDecodeError:
            print("❌ Error parsing logs")
            print(f"Raw output: {output[:200]}...")
    else:
        print(f"❌ Error getting logs: {error}")
        print("💡 Try running manually:")
        print(
            'gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=degen-digest-dashboard" --limit=10'
        )


def check_service_status():
    """Check service status"""
    print("\n🔍 Checking service status...")
    print("-" * 30)

    success, output, error = run_gcloud_command(
        "gcloud run services describe degen-digest-dashboard --region=us-central1 --format=json"
    )

    if success and output.strip():
        try:
            service = json.loads(output)
            url = service.get("status", {}).get("url", "Unknown")
            print(f"✅ Service URL: {url}")

            # Check conditions
            conditions = service.get("status", {}).get("conditions", [])
            for condition in conditions:
                if condition.get("type") == "Ready":
                    status = condition.get("status", "Unknown")
                    print(f"📊 Ready Status: {status}")
                    if status == "True":
                        print("🎉 Service is ready!")
                    else:
                        print("⚠️ Service is not ready")
                    break
        except json.JSONDecodeError:
            print("❌ Error parsing service info")
    else:
        print(f"❌ Error getting service status: {error}")


def main():
    """Main function"""
    print("🚀 Degen Digest Log Checker")
    print("=" * 50)
    print(f"⏰ Checked at: {datetime.now()}")

    check_cloud_run_logs()
    check_service_status()

    print("\n💡 Manual commands:")
    print(
        'gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=degen-digest-dashboard"'
    )
    print("gcloud run services describe degen-digest-dashboard --region=us-central1")


if __name__ == "__main__":
    main()
