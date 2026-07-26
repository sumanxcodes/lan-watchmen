# LAN Watchmen

A self-hosted, demo-able security monitoring stack built to practice real SOC analyst
skills — log aggregation, alert triage, and detection tuning — using open-source
tools on a home network.

**Project name:** LAN Watchmen
**Suggested repo slug:** `lan-watchmen`

## Why this project

Most of my work so far has been academic or client-facing: an NDIS invoicing
system, a MITRE ATT&CK-based recommender system, various API and data science
coursework. What's missing is hands-on experience with the daily mechanics of a
SOC role — watching logs, deciding what's noise and what's not, tuning alerts so
they mean something. This project is built to close that gap and produce a
concrete, demo-able artifact for job applications.

## Goals

- Learn Wazuh (a real SIEM/XDR platform used in actual SOCs), not a toy tool
- Get hands-on with log aggregation, detection rule writing, and alert tuning
- Produce a working, screenshot-able demo for interviews and a GitHub portfolio piece
- Tie detections back to MITRE ATT&CK technique IDs, connecting this project to
  the recommender system work
- Document the build as a public blog series, including the parts that don't
  work on the first try

## Non-goals (explicitly out of scope for v1)

- Full packet inspection / deep traffic analysis
- Multi-agent Wazuh deployment across every device in the house
- A custom-built dashboard UI (Wazuh's built-in dashboard is enough)
- Mobile device agents
- Automated response or active blocking beyond Pi-hole's default behavior
- An always-on production deployment — this is a demo-able snapshot, not a
  home-lab infrastructure commitment

## Architecture

![Diagram of a home network security setup. Home network devices connect to two things: Pi-hole, which filters DNS traffic, and a device inventory script, which watches for new devices on the network. Both send data to a Wazuh manager, which applies rules to detect problems. Wazuh then stores the events in an indexer and shows them on a dashboard.](home-siem-architecture.png)

Home network devices are watched two ways: Pi-hole handles DNS-level visibility
(logging queries and blocking known-bad domains against a threat-intel list), and
a small custom script polls the ARP/DHCP table to flag new or unknown devices.
Both feed into Wazuh, which decodes the logs, applies detection rules, stores
everything in its indexer, and surfaces alerts on its dashboard.

## Feature set (MVP)

**1. Device inventory**
- Poll ARP table / DHCP leases on a short interval
- Maintain a baseline of known devices (MAC + hostname)
- Flag new/unknown devices as they appear
- Simple table: device, first seen, last seen, status

**2. DNS-level threat detection**
- Pi-hole as the DNS resolver
- A public threat-intel blocklist (e.g. URLhaus) loaded into Pi-hole
- Every blocked query logged with source device + domain

**3. Log aggregation**
- Wazuh manager, single-node Docker deployment (no multi-node cluster needed)
- Pi-hole logs shipped into Wazuh via an adapted community decoder/rule set,
  rather than building log parsing from scratch
- One central log-collection point instead of full agents on every device

**4. Alerting — a small, curated ruleset (3-5 rules max)**
- New/unknown device joins the network
- DNS query blocked against the threat-intel list
- Repeated blocked queries from the same device in a short window (possible
  beaconing)
- Deliberately capped here to avoid scope creep — more rules later only if the
  first few prove useful

**5. Dashboard**
- Wazuh's built-in dashboard (OpenSearch Dashboards-based)
- No custom UI for v1

**6. MITRE ATT&CK mapping**
- Each alert type mapped to a relevant technique ID
- Ties this project back to the recommender system work

## Requirements

**Hardware / infra**
- One machine to run Docker — a laptop is fine for demo purposes, or a spare
  Pi/mini PC for something semi-persistent
- No dedicated router hardware (e.g. pfSense/OPNsense) needed for v1 — DNS-level
  visibility via Pi-hole is enough
- Recommend allocating at least 6GB RAM to the Docker host, since the Wazuh
  indexer is the most resource-intensive component
- `vm.max_map_count` needs increasing on the host for the indexer to run
  stably

**Software**
- Docker + Docker Compose
- Wazuh (official single-node Docker Compose stack)
- Pi-hole (Docker container)
- Python (scapy or `arp -a` parsing) for the device-polling script
- A free threat-intel blocklist source (e.g. URLhaus)

## Build order / sprint plan

| Sprint | Focus | Deliverable |
|---|---|---|
| 0 | Planning, environment setup, Wazuh repo cloned, host provisioned | Blog post 1 — the pitch |
| 1 | Wazuh stack up via Docker Compose, first dashboard login | Blog post 2 — setup + gotchas |
| 2 | Pi-hole deployed, threat-intel blocklist loaded, logs flowing into Wazuh | Blog post 3 |
| 3 | Device-inventory script built, baseline established, new-device events feeding into Wazuh | Blog post 4 |
| 4 | Custom detection rules written and tested with `wazuh-logtest`, false positives tuned out | Blog post 5 (strongest post — the tuning story) |
| 5 | MITRE ATT&CK mapping, demo screenshots, GitHub write-up | Blog post 6 — wrap-up |

## Blog series

Publishing sprint-by-sprint rather than all at once, in the style of writing in
public — posting while things are still unresolved, not after they've been
cleaned up. Each post ties to a sprint deliverable above.

Hashtags in use: `#CyberSecurity #Wazuh #SOCAnalyst #HomeLab #BlueTeam`
(swap `#BlueTeam` for `#MITREATTACK` on the sprint 5 wrap-up post).

**Writing style:** every post is written strictly in Julia Evans' style —
first-person, plain conversational sentences, no systems-jargon where plain
words work, honest about what I don't know yet, signs my own work explicitly
("I wrote", "I built") instead of passive voice, and reads like a story or log
rather than a polished tutorial.

## Success criteria

- Wazuh dashboard shows real alerts generated by actual traffic on my network,
  not synthetic test data
- All 3-5 detection rules fire correctly and don't spam false positives once
  tuned
- Each alert type has a documented MITRE ATT&CK technique mapping
- Full build is reproducible from a clean Docker Compose bring-up, documented
  in a GitHub README
- Six-post blog series published, each tied to a working increment

## Possible future work (not committed)

- Always-on deployment on dedicated hardware
- Additional detection rules once the initial three prove out
- Slack/Discord alert forwarding via `wazuh-integratord`
- Expanding device fingerprinting beyond MAC vendor lookup
