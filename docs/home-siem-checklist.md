# LAN Watchmen build checklist

Instructions for the agent working this file: check off each task as it's
completed by changing `[ ]` to `[x]`. Don't check off a task until it's been
verified working, not just attempted. If a task is blocked, leave it unchecked
and add a `> blocked:` note directly beneath it explaining why. Work through
sprints in order — don't start a sprint's tasks until the previous sprint's
tasks are all checked off, unless explicitly told otherwise.

---

## Sprint 0 — Planning & environment

- [x] Confirm architecture decision: demo-snapshot deployment, not always-on
- [x] Choose and provision the Docker host (laptop or spare mini PC)
- [x] Install Docker Engine
- [x] Install Docker Compose
- [x] Confirm host has at least 6GB RAM available for the Docker stack
- [x] Set `vm.max_map_count` to 262144 on the host (required for Wazuh indexer)
- [x] Clone the official `wazuh-docker` repo, single-node branch
- [x] Verify `docker` and `docker compose` commands run without errors
- [x] Blog post 1 drafted (the pitch post)

---

## Sprint 1 — Wazuh up and running

- [x] Generate indexer certificates using the repo's cert generator
- [x] Bring up the single-node stack with `docker compose up`
- [x] Confirm all three containers are healthy: manager, indexer, dashboard
- [x] Log into the Wazuh dashboard successfully at `https://<host-ip>`
- [x] Change default dashboard admin password
- [x] Screenshot the empty dashboard (no data flowing in yet) for the blog post
- [x] Note any setup errors/gotchas encountered, for the blog post
- [x] Blog post 2 (actually 3) published (setup + gotchas)

---

## Sprint 2 — Pi-hole + DNS threat intel

- [x] Deploy Pi-hole as a Docker container
- [x] Point Pi-hole at the test network or a VM's DNS resolution
- [x] Confirm Pi-hole is actively resolving and logging DNS queries
- [x] Source a threat-intel blocklist (e.g. URLhaus) and load it into Pi-hole
- [x] Confirm at least one test domain is actually being blocked
- [x] Locate and adapt an existing community Wazuh decoder/rules for Pi-hole logs
- [x] Configure the `localfile` syslog forward from Pi-hole's log into the Wazuh manager
- [x] Trigger a blocked query and confirm it shows up as a Wazuh alert
- [x] Blog post 4 published

---

## Sprint 3 — Device inventory

- [x] Write the ARP/DHCP polling script (Python, scapy or `arp -a` parsing)
- [x] Run the script and confirm it lists currently connected devices
- [x] Establish and save a baseline "known devices" list (MAC + hostname)
- [x] Add logic to detect and flag devices not in the baseline
- [x] Feed new-device events into Wazuh as a custom log source
- [x] Test by connecting an unrecognized device and confirming an event fires
- [x] Blog post 5 published

---

## Sprint 4 — Detection rules + tuning

- [x] Write rule: new/unknown device joins the network
- [x] Write rule: DNS query blocked against threat-intel list
- [x] Write rule: repeated blocked queries from same device in a short window
- [x] Test each rule individually with `wazuh-logtest` before enabling
- [x] Enable all three rules in the live manager config
- [x] Generate test traffic to deliberately trigger each rule
- [x] Confirm each rule fires correctly with no false negatives
- [x] Document Sprint 4 in `sprint-4-notes.md`
- [x] Write a conversational blog post 6 (`blog-post-6-detection-rules.md`)

---

## Sprint 5 — MITRE ATT&CK mapping + wrap-up

- [x] Map "unknown device" alert to a relevant ATT&CK technique ID
- [x] Map "DNS blocked" alert to a relevant ATT&CK technique ID
- [x] Map "repeated blocked queries" alert to a relevant ATT&CK technique ID
- [x] Take final demo screenshots of the dashboard with live alerts
- [x] Write the GitHub repo README (architecture, setup steps, screenshots)
- [x] Link the blog series from the README
- [x] Blog post 6 published (wrap-up / retrospective)

---

## Definition of done (whole project)

- [x] Wazuh dashboard shows real alerts from actual network traffic, not synthetic test data
- [x] All 3 detection rules fire correctly with false positives tuned out
- [x] Every alert type has a documented ATT&CK technique mapping
- [x] Full stack is reproducible from a clean `docker compose up`
- [x] All 6 blog posts published, each in Julia Evans' style (see project overview doc)
- [x] GitHub repo is public with a complete README
