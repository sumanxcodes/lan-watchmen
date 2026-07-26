# Building a Home SIEM, Part 5: Who's on My Wi-Fi?

One of the most important rules of network security is knowing what is actually on your network. If you don't have a baseline of your normal devices, you can't tell when something weird shows up.

For [Sprint 3](sprint-3-notes.md), I wanted Wazuh to alert me the second a new device joined my network.

## The Plan: ARP Polling

I thought about using something heavy like `scapy` to do deep packet inspection, but I didn't want to run my network-monitoring Docker container as root. Honestly, it felt like overkill.

Instead, I wrote a simple Python script that just runs the standard `arp -a` command every 30 seconds.

`arp -a` asks the operating system for its ARP cache, which is essentially a list of every IP address and MAC address the machine has recently talked to on the local network. 

## Writing the Script

I wrote a short script (`poll.py`) that uses Python's `subprocess` to run `arp` and then uses regex to pull out the IP and MAC addresses.

It works like this:
1. Load a `known_devices.json` file.
2. Run `arp -a` and parse it.
3. For every MAC address it sees, check if it's in the JSON file.
4. If it's *not* in the file, it means it's a new device! The script logs a JSON event to a file (`inventory.log`) and then adds the MAC to the JSON file so we don't alert on it again.

## Dockerizing It

I tossed the script into a tiny Alpine Linux Docker container.

Because Docker on a Mac runs inside a virtual machine, the `arp` command inside the container can't actually see my home Wi-Fi network. It only sees the virtual Docker networks. 

At first, I was a little bummed about this, but then I realized: for building a SIEM demo, it's actually perfect! Every time I spin up a new Docker container for testing, it gets a new virtual MAC address, which means I can reliably test my script just by running `docker run alpine`.

## Feeding Wazuh

Wazuh is incredibly flexible. You don't always need complex XML decoders for custom logs. Since my Python script outputs logs as standard JSON strings, I just had to tell Wazuh to treat it as JSON.

I mounted my `inventory.log` directory into the Wazuh manager container, and added this tiny block to Wazuh's `ossec.conf`:

```xml
  <localfile>
    <log_format>json</log_format>
    <location>/var/log/device-inventory/inventory.log</location>
  </localfile>
```

That's it! Wazuh's log collector automatically parses the JSON keys (`mac_address`, `ip_address`, `event_type`) and makes them available for alerting.

## Testing it out

I started the Python script and watched it log the baseline of 6 devices that were already running in Docker.

Then, I opened a new terminal and ran a dummy container:
```bash
docker run --rm -d alpine sleep 60
```

About 20 seconds later, my Python script spit out a new log line:
`"message": "Unknown device joined the network: MAC 52:9c:58:a2:8c:61 at IP 172.19.0.4"`

I jumped into the Wazuh manager container, checked `ossec.log`, and saw that Wazuh had successfully analyzed the file.

The pipeline is working. The data is flowing into the SIEM.

In the next sprint, we're going to write the custom Wazuh rules to take this JSON log and turn it into a screaming red alert on the dashboard.
