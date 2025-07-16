#!/usr/bin/env python3
import os
import json
import shutil
import hashlib
import time
import sys
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --- CONFIGURATION (VERIFY THESE PATHS) ---
HONEYFS_BASE = "/home/hitanshi/cowrie/honeyfs/"
LOG_DIR = "/home/hitanshi/cowrie/var/log/cowrie/"
BAIT_DIR = os.path.join(HONEYFS_BASE, "home")

# --- BAIT FILE TEMPLATES ---
BAIT_PROFILES = {
    "scanner": {
        "scan_results.txt": "PORTS SCANNED:\n22: OpenSSH\n80: Apache",
        "targets.txt": "10.0.0.1\n192.168.1.1"
    },
    "exploiter": {
        ".ssh/id_rsa": "-----BEGIN FAKE RSA KEY-----\n...",
        "db_backup.sql": "INSERT INTO users VALUES ('admin','P@ssw0rd')"
    },
    "default": {
        "notes.txt": "System maintenance scheduled",
        "todo.txt": "- Change passwords\n- Update firewall"
    }
}

# --- CORE FUNCTIONALITY ---
def force_generate_files(username, attacker_type="scanner"):
    """GUARANTEED file generation (manual override)"""
    user_dir = os.path.join(BAIT_DIR, username)
    # 1. Wipe and recreate directory
    shutil.rmtree(user_dir, ignore_errors=True)
    os.makedirs(user_dir, mode=0o777, exist_ok=True)

    # 2. Generate bait files
    for path, content in BAIT_PROFILES[attacker_type].items():
        full_path = os.path.join(user_dir, path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w") as f:
            f.write(content)

    # 3. Create forensic marker
    marker = {
        "username": username,
        "type": attacker_type,
        "timestamp": datetime.now().isoformat(),
        "generated_by": "force_generate_files"
    }
    with open(os.path.join(user_dir, ".forensic"), "w") as f:
        json.dump(marker, f, indent=2)

    print(f"🔥 FORCED GENERATION for {username} ({attacker_type})")
    print(f"Created files: {list(BAIT_PROFILES[attacker_type].keys())}")

def detect_attacker_type(commands):
    """Determine profile from command attempts"""
    cmd_str = " ".join(commands).lower()
    if any(c in cmd_str for c in ["curl", "wget", "nmap"]):
        return "scanner"
    elif any(c in cmd_str for c in ["passwd", "chmod", "ssh"]):
        return "exploiter"
    return "default"

class CowrieWatcher(FileSystemEventHandler):
    def on_modified(self, event):
        if "cowrie.json" in event.src_path:
            with open(event.src_path) as f:
                for line in f.readlines()[-20:]:
                    try:
                        entry = json.loads(line)
                        if entry.get("eventid") == "cowrie.login.success":
                            username = entry.get("username", "attacker")
                            print(f"🚨 Detected login: {username}")
                            force_generate_files(username)  # Use forced generation
                    except:
                        continue

def start_monitoring():
    """Watch logs for new attacks"""
    observer = Observer()
    observer.schedule(CowrieWatcher(), path=LOG_DIR)
    observer.start()
    print(f"🔍 Monitoring {LOG_DIR} for attacks...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    # Manual mode (for testing)
    if len(sys.argv) > 1:
        force_generate_files(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "scanner")
    else:
        # Auto mode
        os.makedirs(BAIT_DIR, exist_ok=True)
        start_monitoring()
