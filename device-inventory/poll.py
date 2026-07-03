import subprocess
import re
import json
import time
import os
from datetime import datetime

KNOWN_DEVICES_FILE = "logs/known_devices.json"
INVENTORY_LOG_FILE = "logs/inventory.log"

def load_known_devices():
    if os.path.exists(KNOWN_DEVICES_FILE):
        try:
            with open(KNOWN_DEVICES_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_known_devices(devices):
    with open(KNOWN_DEVICES_FILE, "w") as f:
        json.dump(devices, f, indent=4)

def log_new_device(mac, ip):
    event = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "event_type": "new_device",
        "mac_address": mac,
        "ip_address": ip,
        "message": f"Unknown device joined the network: MAC {mac} at IP {ip}"
    }
    with open(INVENTORY_LOG_FILE, "a") as f:
        f.write(json.dumps(event) + "\n")
    print(f"Logged new device: {mac} ({ip})", flush=True)

def poll_arp():
    print("Running arp -a...", flush=True)
    try:
        output = subprocess.check_output(["arp", "-a"], text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running arp: {e}", flush=True)
        return []

    devices = []
    # Regex handles standard arp -a and Alpine Linux format
    # e.g., ? (172.20.0.2) at a2:a4:32:f4:c8:6f [ether]  on br-dee8d51df2c6
    # e.g., ? (192.168.1.1) at 0:11:22:33:44:55 on en0 ifscope [ethernet]
    for line in output.splitlines():
        match = re.search(r'\(([\d\.]+)\)\s+at\s+([a-fA-F0-9:]+)', line)
        if match:
            ip, mac = match.groups()
            if mac != "<incomplete>":
                devices.append((mac, ip))
    return devices

def main():
    print("Starting device inventory poller...", flush=True)
    os.makedirs("logs", exist_ok=True)
    
    known_devices = load_known_devices()
    print(f"Loaded {len(known_devices)} known devices.", flush=True)

    while True:
        current_devices = poll_arp()
        updated = False
        
        for mac, ip in current_devices:
            if mac not in known_devices:
                log_new_device(mac, ip)
                known_devices[mac] = {
                    "ip": ip,
                    "first_seen": datetime.utcnow().isoformat() + "Z"
                }
                updated = True
            elif known_devices[mac]["ip"] != ip:
                # Update IP if it changed
                known_devices[mac]["ip"] = ip
                updated = True
                
        if updated:
            save_known_devices(known_devices)
            
        time.sleep(30)

if __name__ == "__main__":
    main()
