# Building a Home SIEM, Part 4: Trapping Malware DNS with Pi-hole and Wazuh

In [Part 3](blog-post-3-wazuh-setup.md), I got the Wazuh SIEM stack up and running, changed the default password (which was a whole adventure with Docker containers), and got a nice clean dashboard. But a SIEM isn't very useful without data.

For my first real data source, I wanted to tackle DNS. If a device on my network gets infected with malware, one of the first things it usually does is try to call home to a command and control (C2) server. If I can block that DNS query and log it, I've got a fantastic high-fidelity alert.

To do this, I set up Pi-hole, loaded it with a threat-intel blocklist, and wired its logs into Wazuh. Here's how I built it.

## Spinning up Pi-hole in Docker

I decided to run Pi-hole as a Docker container right next to Wazuh. It's lightweight, and keeping everything containerized makes it easier to manage.

I created a simple `docker-compose.yml` for it. The most important part was mapping `./logs:/var/log/pihole` so that the Pi-hole log file would be visible on my host machine. This is critical because Wazuh needs to read those logs.

I also had to set the `DNSMASQ_LISTENING: 'all'` environment variable. By default, Pi-hole drops queries from non-local networks. Because of how Docker Desktop on Mac handles networking, my host queries were coming in from a Docker NAT IP that Pi-hole didn't recognize, so it ignored them! 

## Feeding Pi-hole logs to Wazuh

Next, I needed to tell Wazuh to watch the Pi-hole log file.

Since I mapped the Pi-hole logs to my host, I went into my Wazuh `docker-compose.yml` and added a volume mount to the `wazuh.manager` container: `../../pihole-docker/logs:/var/log/pihole:ro`. The `:ro` makes it read-only, so Wazuh can't accidentally mess up Pi-hole's logs.

Then, I opened Wazuh's `ossec.conf` file (which controls the manager's settings) and added a `<localfile>` block:

```xml
  <localfile>
    <log_format>syslog</log_format>
    <location>/var/log/pihole/pihole.log</location>
  </localfile>
```

This tells Wazuh: "Hey, tail this file and treat the lines like syslog."

## The Decoders Gotcha (Oops)

Wazuh reads the raw text logs, but it needs to know how to parse them to understand what's a domain, what's an IP, and what's a block action. This is what decoders and rules do.

I found a great community repo (`Tomo-9925/wazuh-pi-hole-decoder-and-rules`) on GitHub that had exactly what I needed.

My first attempt at installing them was... bad. I ran a quick `curl` command to download the XML files directly into the Wazuh container. Unfortunately, I got the GitHub URLs wrong. Instead of downloading XML, `curl` downloaded GitHub's `404 Not Found` HTML pages and saved them as `.xml` files. 

When I restarted Wazuh, it immediately crashed. I checked `ossec.log` and saw:
`CRITICAL: (1202): Configuration error at 'etc/decoders/pihole-decoder.xml'.`

Wazuh is very strict about its XML! Once I realized what I did, I cloned the repo properly, used `docker cp` to copy the actual XML files over, fixed the file ownership with `chown wazuh:wazuh`, and restarted the manager. This time, it booted up perfectly.

## Adding Threat Intel

A DNS sinkhole needs a list of bad domains to block. I decided to use URLhaus, which tracks malware distribution sites.

Interestingly, the Pi-hole v6 Docker container doesn't have `sqlite3` in its path, so the usual command-line way of adding an adlist didn't work for me. Since Pi-hole's `gravity.db` was mapped to my host, I just used my Mac's native `sqlite3` to inject it directly:

```bash
sqlite3 pihole-docker/etc-pihole/gravity.db "INSERT INTO adlist (address, enabled, comment) VALUES ('https://malware-filter.gitlab.io/malware-filter/urlhaus-filter-domains.txt', 1, 'URLhaus');"
```

Then I ran `docker exec pihole pihole -g` to pull down the list and build the gravity database. 

## Testing the trap

To see if it all worked, I needed to trigger an alert. I used `sqlite3` to grab a known malware domain from the gravity database (it gave me `cambodiatouristservice.com`) and queried it locally:

```bash
dig @127.0.0.1 cambodiatouristservice.com
```

Pi-hole blocked it and returned `0.0.0.0`. That's step one. But did Wazuh catch it?

I jumped into the Wazuh container and grepped the `alerts.log` file, and there it was:

```
** Alert 1783054686.703771: - syslog,dnsmasq
2026 Jul 03 04:58:06 wazuh->/var/log/pihole/pihole.log
Rule: 120002 (level 6) -> 'Pi-hole blocked malicious DNS requests.'
Jul  2 23:58:04 dnsmasq[53]: gravity blocked cambodiatouristservice.com is 0.0.0.0
```

Success! My SIEM is officially digesting network data and alerting on known threats. 

In the next sprint, I'm going to tackle device inventory so I know exactly *what* is connected to my network.
