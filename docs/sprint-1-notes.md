# Sprint 1 — Wazuh Up and Running

**Sprint goal:** Generate indexer certificates, bring up the single-node Wazuh stack using Docker Compose, log in to the dashboard, and change the default admin password. Document everything for blog post 3.

**Date:** July 2026

---

## 1. Generating Certificates

The Wazuh single-node Docker setup includes a separate compose file just for generating TLS certificates for the indexer and other components. It mounts the config and drops certificates into `config/wazuh_indexer_ssl_certs/`.

```bash
docker compose -f generate-indexer-certs.yml run --rm generator
```

This went smoothly. The script output showed certificates generated for the indexer, Filebeat (used by the manager), and the dashboard. It automatically set the necessary ownerships and permissions for those cert files.

## 2. Bringing up the Stack

Once the certificates were ready, starting the stack was standard Docker Compose:

```bash
docker compose up -d
```

Three containers started:
1. `wazuh.indexer`: The OpenSearch backend (takes the longest to start and warm up).
2. `wazuh.manager`: The core engine, ingesting logs and running rules.
3. `wazuh.dashboard`: The OpenSearch Dashboards frontend we interact with.

I ran `docker compose ps` and `curl -k -I https://localhost` to verify everything was healthy. The indexer was responding on port 9200, and the dashboard served a redirect on port 443. The whole startup took about a minute.

## 3. Changing the Default Password (The Gotcha)

The default dashboard credentials are `admin` / `SecretPassword`. I wanted to change this right away, but it wasn't as straightforward as clicking "Change Password" in the UI.

In a containerized Wazuh setup, you have to update the OpenSearch Security config files and then apply them.

Here is the process I followed to change the `admin` password to `LanWatchmen2026!`:

**A. Generate a bcrypt hash of the new password:**
I used the `hash.sh` script included in the indexer container. The trick is you have to set `OPENSEARCH_JAVA_HOME` first or it fails:

```bash
docker exec -e OPENSEARCH_JAVA_HOME=/usr/share/wazuh-indexer/jdk single-node-wazuh.indexer-1 bash /usr/share/wazuh-indexer/plugins/opensearch-security/tools/hash.sh -p LanWatchmen2026!
```

This gave me the hash: `$2y$12$4JslHK5qIpIomzGg59EUIes1FyIrkc0Ry4mrTUlgQ7mJB5B9S0wte`

**B. Update configuration files:**
1. I updated `wazuh-docker/single-node/config/wazuh_indexer/internal_users.yml`, replacing the old hash for the `admin` user with the newly generated one.
2. I updated `wazuh-docker/single-node/docker-compose.yml`, changing `INDEXER_PASSWORD=SecretPassword` to `INDEXER_PASSWORD=LanWatchmen2026!` so the manager and dashboard containers know the new password.

**C. Apply the security config:**
I had to run `securityadmin.sh` inside the indexer container to actually load the new `internal_users.yml` into OpenSearch's internal `.opendistro_security` index. Again, setting the Java home was necessary:

```bash
docker exec -e OPENSEARCH_JAVA_HOME=/usr/share/wazuh-indexer/jdk single-node-wazuh.indexer-1 bash /usr/share/wazuh-indexer/plugins/opensearch-security/tools/securityadmin.sh -cd /usr/share/wazuh-indexer/config/opensearch-security/ -icl -nhnv -cacert /usr/share/wazuh-indexer/config/certs/root-ca.pem -cert /usr/share/wazuh-indexer/config/certs/admin.pem -key /usr/share/wazuh-indexer/config/certs/admin-key.pem -h localhost -p 9200
```

Once that was done, I verified I could authenticate to the indexer via `curl` with the new password. Then I restarted the stack (`docker compose down && docker compose up -d`) to ensure the dashboard and manager picked up the new environment variables.

## 4. The Empty Dashboard

I navigated to `https://localhost`, got the expected self-signed certificate warning, and logged in with `admin` and my new password. 

The dashboard loaded up, entirely empty. No agents, no security events. Just a blank canvas ready to be configured. This is exactly what I wanted for the end of Sprint 1.

## What's Next (Sprint 2)

Now that the core SIEM is up and running, we need to feed it some data. Next sprint focuses on deploying Pi-hole, configuring a threat-intel blocklist, and forwarding Pi-hole's DNS logs into Wazuh. This will give us our first real visibility into what's happening on the network.
