# Sprint 3: Device Inventory

## Goal
Write a custom script to poll the network using `arp -a`, establish a baseline of known MAC addresses, and forward new device detections to Wazuh.

## Steps Completed
1. **Python Polling Script (`poll.py`)**:
   - Used `subprocess.check_output` to run `arp -a`.
   - Used regex `\(([\d\.]+)\)\s+at\s+([a-fA-F0-9:]+)` to extract IPs and MAC addresses.
   - Script loads `logs/known_devices.json` as a baseline.
   - If an unknown MAC is found, it appends a JSON event to `logs/inventory.log` and updates the baseline.
   - Runs in a continuous loop, sleeping for 30 seconds between polls.

2. **Dockerization**:
   - Created a simple `Dockerfile` based on `python:3.11-alpine`.
   - Created `docker-compose.yml` using `network_mode: "host"` so the `arp` command could see the host's networking (which for Docker on Mac is the Docker VM's bridge networks).

3. **Wazuh Log Ingestion**:
   - Added a volume mount to `wazuh-docker/single-node/docker-compose.yml` to mount `../../device-inventory/logs:/var/log/device-inventory:ro`.
   - Updated `wazuh_manager.conf` to tail the new log file using Wazuh's native JSON decoder:
     ```xml
     <localfile>
       <log_format>json</log_format>
       <location>/var/log/device-inventory/inventory.log</location>
     </localfile>
     ```

4. **Validation**:
   - Started the `device-inventory` container and watched it build the initial baseline (it found 6 devices on the Docker internal network).
   - Started a temporary Alpine container (`docker run --rm -d alpine sleep 60`) to generate a new MAC address.
   - The script successfully detected the new MAC and logged it: `{"timestamp": "...", "event_type": "new_device", "mac_address": "52:9c:58:a2:8c:61", "ip_address": "172.19.0.4", "message": "Unknown device joined the network..."}`
   - Confirmed in Wazuh's `ossec.log` that the `wazuh-logcollector` daemon is actively analyzing `/var/log/device-inventory/inventory.log`.

## Blockers / Next Steps
- Sprint 3 is functionally complete.
- We will draft Blog Post 5 using Julia Evans' style.
- Next sprint (Sprint 4) we need to write the actual Wazuh detection rule that parses this JSON event and triggers a high-level alert on the dashboard.
