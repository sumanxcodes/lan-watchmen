# Sprint 2: Pi-hole + DNS Threat Intel

## Goal
Deploy Pi-hole as a DNS sinkhole, feed it a known threat-intel blocklist (URLhaus), and configure Wazuh to ingest Pi-hole's DNS logs and generate security alerts when devices query malicious domains.

## Steps Completed
1. **Pi-hole Deployment**: 
   - Created `pihole-docker/docker-compose.yml` mapped to ports 53 (TCP/UDP) and 80.
   - Bound `./logs` to `/var/log/pihole` to expose the logs to the host filesystem.
   - Had to set `DNSMASQ_LISTENING: 'all'` in the environment to allow Pi-hole to respond to queries originating from the host Docker NAT (though this may not be strictly necessary if all endpoints query via the host IP later, it helped with local `dig` testing).

2. **Wazuh Log Ingestion**:
   - Modified `wazuh-docker/single-node/docker-compose.yml` to mount the Pi-hole log directory (`../../pihole-docker/logs:/var/log/pihole:ro`) into the `wazuh.manager` container.
   - Updated `wazuh_manager.conf` with a `<localfile>` block pointing at `/var/log/pihole/pihole.log` with `syslog` format.

3. **Wazuh Decoders and Rules**:
   - Pulled community Pi-hole decoders and rules from `Tomo-9925/wazuh-pi-hole-decoder-and-rules`.
   - **Gotcha:** Used a bad raw GitHub URL at first which downloaded `404 Not Found` HTML pages into the XML decoder files. Wazuh manager refused to start and crashed throwing a "Configuration error at 'etc/decoders/pihole-decoder.xml'". Cloned the repo locally, copied the correct files into the container, `chown wazuh:wazuh`, and restarted. Everything loaded correctly.

4. **Threat-Intel Blocklist**:
   - Used the host's native `sqlite3` to inject the URLhaus blocklist directly into the Pi-hole `gravity.db` since the Pi-hole v6 Docker container doesn't ship with sqlite3 in `$PATH` out of the box and the `-a adlist` CLI command didn't work.
   - Ran `docker exec pihole pihole -g` to update gravity.

5. **Validation**:
   - Ran `dig @127.0.0.1 cambodiatouristservice.com` (a domain found via `sqlite3` query in the gravity DB).
   - Confirmed Pi-hole returned `0.0.0.0`.
   - Grepped `/var/ossec/logs/alerts/alerts.log` inside the Wazuh manager container and found:
     ```
     Rule: 120002 (level 6) -> 'Pi-hole blocked malicious DNS requests.'
     Jul  2 23:58:04 dnsmasq[53]: gravity blocked cambodiatouristservice.com is 0.0.0.0
     ```

## Blockers / Next Steps
- Sprint 2 is complete.
- Need to draft blog post 4 covering this sprint in Julia Evans' style.
