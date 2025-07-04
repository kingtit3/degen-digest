#!/usr/bin/env python3
"""
Web server wrapper for the Solana crawler to run on Google Cloud Run
"""

import os
import subprocess
import sys
import threading
import traceback
from pathlib import Path
from typing import Any

from flask import Flask, jsonify

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

app = Flask(__name__)

# Global variables to track crawler status
crawler_process = None
crawler_running = False
crawler_thread = None


def run_crawler() -> None:
    """Run the continuous crawler in a separate thread"""
    global crawler_process, crawler_running

    try:
        print("🚀 Starting Solana crawler...")
        crawler_running = True

        # Define the crawler command - Use enhanced multi-source crawler
        crawler_command = [
            sys.executable,
            "scripts/enhanced_multi_crawler.py",
            "--username",
            "gorebroai",
            "--password",
            "firefireomg4321",
            "--start-hour",
            "6",
            "--end-hour",
            "0",
            "--interval",
            "30",
        ]

        print(f"🔧 Executing command: {' '.join(crawler_command)}")
        print(f"📁 Working directory: {os.getcwd()}")
        print(f"🐍 Python executable: {sys.executable}")

        # Start the enhanced multi-source crawler
        crawler_process = subprocess.Popen(
            [
                sys.executable,
                "scripts/enhanced_multi_crawler.py",
                "--username",
                "gorebroai",
                "--password",
                "firefireomg4321",
                "--start-hour",
                "6",
                "--end-hour",
                "0",
                "--interval",
                "30",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            env={
                **os.environ,
                "OUTPUT_DIR": "/tmp",  # Force cloud-only operation
                "CLOUD_ONLY": "true",
            },
        )

        print(f"✅ Crawler started with PID: {crawler_process.pid}")

        # Stream stdout and stderr in real time
        def stream_output(pipe, label):
            try:
                for line in iter(pipe.readline, ""):
                    if line:
                        print(f"[{label}] {line.rstrip()}")
            except Exception:
                print(f"❌ Error streaming {label} output:")
                traceback.print_exc()

        stdout_thread = threading.Thread(
            target=stream_output, args=(crawler_process.stdout, "STDOUT")
        )
        stderr_thread = threading.Thread(
            target=stream_output, args=(crawler_process.stderr, "STDERR")
        )
        stdout_thread.start()
        stderr_thread.start()

        # Wait for the process to complete
        crawler_process.wait()
        stdout_thread.join()
        stderr_thread.join()

        if crawler_process.returncode != 0:
            print(f"❌ Crawler exited with code {crawler_process.returncode}")
        else:
            print("✅ Crawler completed successfully")

        # Process the crawler data for digest generation
        print("🔄 Processing crawler data for digest generation...")
        try:
            process_result = subprocess.run(
                [sys.executable, "scripts/process_crawler_data.py"],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if process_result.returncode == 0:
                print("✅ Crawler data processed successfully for digest generation")
            else:
                print(
                    f"⚠️ Data processing completed with warnings: {process_result.stderr}"
                )
        except subprocess.TimeoutExpired:
            print("⚠️ Data processing timed out")
        except Exception as e:
            print(f"❌ Error processing crawler data: {e}")
            traceback.print_exc()

    except Exception as e:
        print(f"❌ Error running crawler: {e}")
        traceback.print_exc()
    finally:
        crawler_running = False
        crawler_process = None


@app.route("/")
def health_check() -> Any:
    """Health check endpoint"""
    return jsonify(
        {
            "status": "healthy",
            "crawler_running": crawler_running,
            "crawler_pid": crawler_process.pid if crawler_process else None,
        }
    )


@app.route("/start", methods=["POST"])
def start_crawler() -> Any:
    """Start the crawler"""
    global crawler_thread, crawler_running

    if crawler_running:
        return jsonify({"status": "running", "message": "Crawler is already running"})

    crawler_thread = threading.Thread(target=run_crawler, daemon=True)
    crawler_thread.start()

    return jsonify({"status": "running", "message": "Crawler started successfully"})


@app.route("/stop", methods=["POST"])
def stop_crawler() -> Any:
    """Stop the crawler"""
    global crawler_process, crawler_running

    if not crawler_running or not crawler_process:
        return jsonify({"status": "stopped", "message": "Crawler is not running"})

    try:
        crawler_process.terminate()
        crawler_process.wait(timeout=10)
        crawler_running = False
        return jsonify({"status": "stopped", "message": "Crawler stopped successfully"})
    except subprocess.TimeoutExpired:
        crawler_process.kill()
        crawler_running = False
        return jsonify({"status": "stopped", "message": "Crawler force stopped"})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error stopping crawler: {e}"})


@app.route("/status")
def get_status() -> Any:
    """Get crawler status"""
    if crawler_running and crawler_process and crawler_process.poll() is None:
        status = "running"
    elif crawler_process and crawler_process.returncode is not None:
        status = "stopped"
    else:
        status = "stopped"

    return jsonify(
        {
            "status": status,
            "crawler_running": crawler_running,
            "crawler_pid": crawler_process.pid if crawler_process else None,
            "crawler_returncode": crawler_process.returncode
            if crawler_process
            else None,
        }
    )


if __name__ == "__main__":
    # Get port from environment variable (Cloud Run sets PORT)
    port = int(os.environ.get("PORT", 8080))

    print(f"🌐 Starting crawler server on port {port}")
    print("📱 Endpoints:")
    print("   GET  /         - Health check")
    print("   POST /start    - Start crawler")
    print("   POST /stop     - Stop crawler")
    print("   GET  /status   - Get status")

    # Start the crawler automatically
    crawler_thread = threading.Thread(target=run_crawler, daemon=True)
    crawler_thread.start()

    # Start the Flask server
    app.run(host="0.0.0.0", port=port, debug=False)
