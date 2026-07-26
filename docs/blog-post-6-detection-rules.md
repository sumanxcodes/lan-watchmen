# Building a Home SIEM, Part 6: Writing Custom Detection Rules

In the last sprint, we got a Python script constantly sniffing the network for new devices. It logs any unknown MAC addresses to a JSON file. But data sitting in a JSON file doesn't help anyone. We need Wazuh to actually *read* that file and scream "HEY, A NEW DEVICE JUST JOINED!"

And while we're at it, remember our Pi-hole setup? It blocks malware domains just fine, but a single blocked query might just be a random ad banner. If a device hits malware domains *five times in 60 seconds*, that's not a banner ad. That's a compromised machine trying to phone home to a C2 server. 

We need some custom detection rules to catch these specific scenarios.

## Teaching Wazuh to parse JSON

Wazuh is actually pretty smart out of the box. If you feed it a JSON log, it will automatically parse the fields for you.

When our `device-inventory` script sees a new MAC address, it writes a log like this:
```json
{"timestamp": "2026-07-03T05:30:44Z", "event_type": "new_device", "mac_address": "52:9c:58:a2:8c:61", "ip_address": "172.19.0.4", "message": "Unknown device joined the network..."}
```

Since it has an `event_type` field, Wazuh's default Suricata rules (which trigger on JSON with `event_type`) will actually pick it up automatically. But we want a *custom* alert. So I wrote a rule in `local_rules.xml` that specifically looks for `event_type: new_device`:

```xml
<group name="device_inventory,">
  <rule id="100002" level="8">
    <if_sid>86600</if_sid>
    <field name="event_type">new_device</field>
    <description>New unknown device detected on the network: $(mac_address) ($(ip_address))</description>
  </rule>
</group>
```

By hooking into `if_sid` 86600 (the base JSON rule), we can easily trigger a level 8 alert whenever a rogue device shows up. I tested it using the `wazuh-logtest` utility, and it parsed the JSON variables directly into the alert description!

## Catching the C2 Beaconing

For the DNS blocks, we already had Rule `120002`, which triggers every time Pi-hole blocks a malicious domain. I wanted to add a frequency rule. If rule `120002` fires 5 times in 60 seconds, trigger a critical alert.

```xml
<group name="syslog,dnsmasq,">
    <rule id="120003" level="10" frequency="5" timeframe="60">
        <if_matched_sid>120002</if_matched_sid>
        <description>High frequency of malicious DNS requests blocked.</description>
    </rule>
</group>
```

I fed a sample Pi-hole block log into `wazuh-logtest` five times in a row, and boom: Level 10 alert generated.

## The live testing gotchas

The rules worked perfectly in the test lab (`wazuh-logtest`), but generating the live alerts was a bit tricky. When I restarted the Wazuh manager to apply the rules, my `device-inventory` script saw the network interface flap and logged a bunch of "new devices". But the Wazuh log collector was still starting up, so it missed those initial log lines! 

And for the DNS blocks, `dig` commands from inside Docker containers get a little weird with caching and routing, so generating exactly 5 blocks in a row on the live Pi-hole took some fiddling. 

But the detection rules are rock solid. Now, if a new smart fridge joins the network, or a laptop starts desperately trying to contact a malware domain, Wazuh will sound the alarm. 

Next up? Maybe we should actually *do* something when these alerts fire, like kicking the device off the network. Stay tuned.
