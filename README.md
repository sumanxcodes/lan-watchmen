# LAN Watchmen

I'm building a home SIEM with Wazuh and Pi-hole, mostly to learn what SOC analysts actually do all day. Writing about it as I go, including the parts that don't work yet.

**Status:** early build, in progress. Not much running yet.

## What this is

A small, self-hosted security monitoring setup for a home network. Pi-hole watches DNS traffic and blocks known-bad domains, a script I wrote watches for new devices showing up on the network, and Wazuh ties it all together with detection rules and a dashboard.

## Architecture

![Diagram of a home network security setup. Home network devices connect to two things: Pi-hole, which filters DNS traffic, and a device inventory script, which watches for new devices on the network. Both send data to a Wazuh manager, which applies rules to detect problems. Wazuh then stores the events in an indexer and shows them on a dashboard.](home-siem-architecture.png)

## Why

I've done a fair bit of security coursework and academic project work, but not much of the actual day-to-day of a SOC role: watching logs, tuning alerts, figuring out what's noise. This is me learning that by building it.

## Following along

I'm writing a blog series as I build this, one post per stage. Links go here as they're published:

- [ ] Post 1 — why I'm building this
- [ ] Post 2 — getting Wazuh running
- [ ] Post 3 — wiring up Pi-hole
- [ ] Post 4 — device inventory script
- [ ] Post 5 — writing detection rules
- [ ] Post 6 — MITRE ATT&CK mapping + wrap-up

## Setup

Not documented yet — I'll add real setup steps once the stack is actually working end to end.

## License

TBD
