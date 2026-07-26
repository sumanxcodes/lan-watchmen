# Building a Home SIEM, Part 7: Wrap-up & MITRE ATT&CK Mapping

We made it! After 5 sprints of Docker networking chaos, Python ARP sniffing, parsing JSON logs, and battling the Wazuh default password setup, the LAN Watchmen SIEM is officially complete.

If you look back at where we started, we wanted a home lab that actually *did* something useful, rather than just being a pile of VMs idling on a desk. And I think we pulled it off. 

## Giving our alerts a name (MITRE ATT&CK)

In the final sprint, I wanted to take our custom detection rules and actually make them look like professional SOC alerts. The industry standard way to do this is by mapping rules to the **MITRE ATT&CK** framework. It’s basically a massive dictionary of techniques that bad guys use.

For our `device-inventory` script (which alerts when an unknown MAC address joins the Wi-Fi), I mapped it to `T1200` (Hardware Additions). The idea is that an attacker plugging a rogue device into your physical network is a known "Initial Access" technique.

For our Pi-hole rules, the community decoder already mapped individual blocked DNS queries to things like `T1189` (Drive-by Compromise) and `T1566` (Phishing). But for our custom frequency rule—the one that fires when a device aggressively hits malware domains 5 times in 60 seconds—I added mappings for `T1071.004` (Application Layer Protocol: DNS) and `T1568` (Dynamic Resolution). This perfectly captures the behavior of malware trying to phone home to a Command and Control (C2) server over DNS.

Adding the mappings in Wazuh was as simple as adding a `<mitre>` block to our XML rules:

```xml
<mitre>
    <id>T1071.004</id>
    <id>T1568</id>
</mitre>
```

When those alerts fire in the Wazuh dashboard, they now automatically pull in the tactic names (like "Command and Control") and link directly to the MITRE documentation. It makes a home network feel like an enterprise SOC.

## What went well, and what broke

**The good stuff:**
- Using `docker compose` for everything was a lifesaver. Being able to tear down the entire SIEM and bring it back up cleanly in minutes meant I wasn't scared to experiment and break things.
- Wazuh's out-of-the-box JSON decoding is magic. Pointing Wazuh at my Python script's JSON logs and having it instantly parse `mac_address` and `ip_address` into queryable fields saved me from writing awful regex decoders.
- Pi-hole as a log source is incredible. It’s a DNS sinkhole you actually *want* on your network anyway, and plugging it into a SIEM generates high-fidelity alerts instantly.

**The gotchas:**
- Wazuh's security indexer password change process is deeply unfriendly for containerized setups. You have to jump into a specific container, export Java variables, generate a bcrypt hash manually, and run a bash script to commit it.
- Timing issues! When testing the live alerts, I spent 20 minutes wondering why my new device rule wasn't firing. Turns out, the Python script logged the event *while the Wazuh manager container was restarting*. Since Wazuh log collectors tail from the end of the file when they start, it completely missed the event!

## Wrapping it up

This project was a blast. We built a system that actively monitors the physical network for rogue devices, intercepts malicious DNS traffic using threat intelligence feeds, correlates the logs, and fires alerts mapped to MITRE ATT&CK. 

You can find the complete code, Docker configs, and setup instructions in the [GitHub repo](https://github.com/sumanxcodes/lan-watchmen). 

If you are thinking about building a home lab, don't just stop at installing the software. Write custom rules! Feed it weird data! Breaking things is the only way to figure out how they actually work.
