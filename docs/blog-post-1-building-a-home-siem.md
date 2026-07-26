# I'm building myself a home SIEM (and I don't fully know what I'm doing yet)

I've spent the last few years doing security and data science coursework, building an NDIS invoicing system, and putting together a MITRE ATT&CK recommender system for a uni project. Lots of it has been academic or client-facing. What I haven't done much of is the actual day-to-day work a SOC analyst does: watching logs, tuning alerts, figuring out what's noise and what's a real problem.

So I'm building a home SIEM. Wazuh, Pi-hole, a small Python script to keep an eye on my network, all glued together, running on my own devices. I'm calling it LAN Watchmen, because someone has to watch the LAN, and it might as well be me.

I want to be upfront: I don't know exactly how this is going to go. I've read the docs, I've seen other people's write-ups, but I haven't stood up a Wazuh cluster before. There's a real chance the first week is just me staring at a dashboard that shows nothing, or fighting with certificate generation, or realizing my router doesn't give me the log access I assumed it would. That's fine. That's kind of the point of writing this as I go instead of after I've cleaned it all up.

Here's roughly what I'm trying to build:

![Diagram of a home network security setup. Home network devices connect to two things: Pi-hole, which filters DNS traffic, and a device inventory script, which watches for new devices on the network. Both send data to a Wazuh manager, which applies rules to detect problems. Wazuh then stores the events in an indexer and shows them on a dashboard.](home-siem-architecture.png)

*Here's the rough plan. Home devices go through Pi-hole (for DNS) and a little script I wrote (for spotting new devices), both feed into Wazuh, and Wazuh does the actual detecting.*

- **Wazuh** as the central brain, running single-node in Docker. It'll ingest logs and raise alerts.
- **Pi-hole** sitting in front of my DNS traffic, blocking known-bad domains and logging every query.
- **A small device-inventory script** that watches my network's ARP table and flags anything that shows up that I don't recognize.
- **A handful of custom detection rules** on top of all that, tuned so they tell me something real instead of just being noisy.

Why this and not something flashier? A few reasons. First, it's close to what the job actually looks like. Log aggregation, alert triage, tuning false positives, these are the daily mechanics of SOC work, and I'd rather learn them by doing than by reading about them. Second, it's honest about scope. I'm not trying to build a commercial product here. I'm trying to build something real enough that I understand it end to end, and can talk about it in an interview without hand-waving.

I'm scoping this deliberately small. No full packet inspection, no agents on every device in the house, no custom dashboard UI. Just DNS-level visibility, a device baseline, and a few rules that actually mean something when they fire. If it grows from there, it grows from there.

I'll be writing about each piece as I build it, including the parts that don't work on the first try. Next post is getting Wazuh actually running, which given some of what I've read about indexer memory requirements, might not be entirely painless.

If you've built something like this before and know where I'm about to get stuck, I'd genuinely like to hear about it.

#CyberSecurity #Wazuh #SOCAnalyst #HomeLab #BlueTeam
