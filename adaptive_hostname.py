#!/usr/bin/env python3
import os
import random
import json
import re
from datetime import datetime

# --- CONFIG ---
LOG_DIR = "/home/hitanshi/cowrie/var/log/cowrie/"
COWRIE_CFG = "/home/hitanshi/cowrie/etc/cowrie.cfg"
HOSTNAMES = ["web01", "db02", "dev03", "firewall"]

# --- SUSPICIOUS PATTERNS ---
def is_suspicious(entry):
    username = entry.get("username", "")
    suspicious_patterns = [r'root', r'admin\d*', r'test', r'\$', r'\/', r'\.\.']
    return any(re.search(p, username, re.I) for p in suspicious_patterns)

# --- HOSTNAME ROTATION ---
def rotate_hostname():
    new_host = random.choice(HOSTNAMES)
    updated = False

    # update cowrie.cfg hostname under [environment]
    if os.path.exists(COWRIE_CFG):
        with open(COWRIE_CFG, "r") as f:
            lines = f.readlines()

        with open(COWRIE_CFG, "w") as f:
            for line in lines:
                if line.strip().startswith("hostname ="):
                    f.write(f"hostname = {new_host}\n")
                    updated = True
                else:
                    f.write(line)
        # If hostname line didn't exist before, add it
        if not updated:
            with open(COWRIE_CFG, "a") as f:
                f.write(f"\n[environment]\nhostname = {new_host}\n")

    print(f"🔁 Hostname rotated to: {new_host}")
    print("⚠️ Please restart Cowrie for changes to take effect!")

# --- LOG ANALYSIS ---
def check_logs():
    try:
        log_file = os.path.join(LOG_DIR, "cowrie.json")
        with open(log_file) as f:
            for line in f.readlines()[-100:]:
                try:
                    entry = json.loads(line)
                    if entry.get("eventid") in ["cowrie.login.success", "cowrie.login.failed"]:
                        if is_suspicious(entry):
                            return True
                except:
                    continue
    except:
        print("⚠️ Error reading logs. Forcing hostname change.")
        return True
    return False

if __name__ == "__main__":
    if check_logs():
        rotate_hostname()
    else:
        print("✅ No suspicious logins, no hostname change.")

