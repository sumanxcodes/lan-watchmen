# LAN Watchmen

A containerized home Security Information and Event Management (SIEM) lab built using Wazuh and Pi-hole. This project demonstrates how to set up an enterprise-grade SIEM on a home network, intercept DNS traffic to block malware, and write custom detection rules mapped to the MITRE ATT&CK framework.

![Wazuh Dashboard](docs/screenshots/wazuh_dashboard.png)

## Architecture

The project is split into three main components, all running in Docker containers:

1. **Wazuh (SIEM)**: The core brain. We deploy a single-node Wazuh stack (Manager, Indexer, and Dashboard) using `docker compose`.
2. **Pi-hole (DNS Sinkhole)**: Runs as the local DNS server. It is configured with threat-intel blocklists (like URLhaus) to drop queries to known malware domains. Its logs are mounted directly into the Wazuh manager container.
3. **Device Inventory Script**: A Python script running in a container that continuously sniffs the local network (via ARP) and logs any new, unknown devices joining the network.

Wazuh parses logs from both Pi-hole and the Device Inventory script, running them through custom detection rules to generate alerts mapped to MITRE ATT&CK techniques.

## Blog Series

This project was built iteratively and documented in a conversational blog series:
1. [Part 1: The Pitch](docs/blog-post-1-pitch.md)
2. [Part 2: Planning the Setup](docs/blog-post-2-setting-up-the-environment.md)
3. [Part 3: Deploying Wazuh](docs/blog-post-3-wazuh-setup.md)
4. [Part 4: Pi-hole and Wazuh Integration](docs/blog-post-4-pihole-wazuh.md)
5. [Part 5: Device Inventory](docs/blog-post-5-device-inventory.md)
6. [Part 6: Custom Detection Rules](docs/blog-post-6-detection-rules.md)
7. [Part 7: Wrap-up & MITRE ATT&CK](docs/blog-post-7-wrap-up.md)

## Quick Start Guide

### Prerequisites
- Docker and Docker Compose installed.
- At least 6GB of available RAM.
- Host machine must have `vm.max_map_count` set to at least 262144:
  ```bash
  sudo sysctl -w vm.max_map_count=262144
  ```

### 1. Bring up Wazuh
```bash
cd wazuh-docker/single-node
# First time only: generate certs
docker compose -f generate-indexer-certs.yml run --rm generator
docker compose up -d
```
Log into `https://<host-ip>` using `admin` / `LanWatchmen2026!`.

### 2. Bring up Pi-hole
```bash
cd pihole-docker
docker compose up -d
```
Log into the Pi-hole admin dashboard at `http://<host-ip>/admin` using the password `LanWatchmen2026!`. Update your router or local machine's DNS server to point to this IP.

### 3. Start the Device Inventory Poller
```bash
cd device-inventory
docker compose up -d
```

### 4. Apply Custom Rules
The custom Wazuh rules (`local_rules.xml` and `pihole-rule.xml`) need to be placed in `/var/ossec/etc/rules/` inside the Wazuh manager container, after which you must restart the manager:
```bash
docker compose -f wazuh-docker/single-node/docker-compose.yml restart wazuh.manager
```

## Detection Rules & MITRE ATT&CK Mapping

This stack includes custom rules mapped to specific threat behaviors:

- **Rule 100002 (Level 8)**: Detects unknown devices joining the network.
  - *MITRE ID*: `T1200` (Hardware Additions)
- **Rule 120002 (Level 6)**: Detects a single malicious DNS query blocked by Pi-hole.
  - *MITRE IDs*: `T1189`, `T1568`, `T1566`
- **Rule 120003 (Level 10)**: Detects 5 malicious DNS blocks within 60 seconds from the same source (C2 beaconing).
  - *MITRE IDs*: `T1071.004` (DNS), `T1568` (Dynamic Resolution)

---
*Built with ❤️ for home network defenders.*
