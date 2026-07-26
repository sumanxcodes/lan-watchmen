# Setting up Wazuh in Docker (and changing that default password)

In [my last post](blog-post-2-setting-up-the-environment.md), I got everything staged and ready for Wazuh—the Docker environment, the `vm.max_map_count` fix, and the compose files. I ended that post expecting the TLS certificate generation to be the thing that tripped me up.

Turns out, the certificates were the easy part. It was changing the default admin password that ended up being the real gotcha.

Here's how I actually brought the Wazuh stack to life and secured it.

## The Architecture

Wazuh in a single-node Docker setup is really three separate containers working together:

1. **wazuh-manager**: This is the brain. It receives the logs from agents (which we'll set up later), decodes them, and runs them against a massive set of security rules.
2. **wazuh-indexer**: This is basically OpenSearch under the hood. It stores all the alerts and logs so you can search them quickly.
3. **wazuh-dashboard**: This is the web UI (built on OpenSearch Dashboards) where you actually look at the data.

## Getting it running

Before bringing up the stack, I had to fix one system setting for the indexer. OpenSearch needs a lot of memory-mapped areas to function well, so you have to increase `vm.max_map_count` on the host machine. Since I'm using Docker Desktop on a Mac, I had to run this inside the Docker Linux VM:

```bash
docker run --rm --privileged alpine sysctl -w vm.max_map_count=262144
```

*Note: This setting resets every time Docker Desktop restarts. I might need to automate this later if it gets annoying.*

Next, I generated the TLS certificates so the containers can talk to each other securely. Wazuh provides a separate compose file just for this:

```bash
cd wazuh-docker/single-node
docker compose -f generate-indexer-certs.yml run --rm generator
```

Once the certificates were built, I fired up the main stack:

```bash
docker compose up -d
```

It took about a minute for everything to initialize (the indexer takes its time warming up), but running `docker compose ps` showed all three containers healthy.

## The Gotcha: Changing the default password

This is where things got a bit tricky. The default admin password for the dashboard is `SecretPassword`. I obviously wanted to change this, but in a containerized Wazuh setup, there's no simple "Change Password" button in the UI. You have to update the OpenSearch Security configuration files and push them into the running indexer.

Here's the process I ended up using:

First, I needed to generate a bcrypt hash of my new password. I used a script included inside the indexer container to do this, but I had to explicitly tell it where Java was installed:

```bash
docker exec -e OPENSEARCH_JAVA_HOME=/usr/share/wazuh-indexer/jdk single-node-wazuh.indexer-1 bash /usr/share/wazuh-indexer/plugins/opensearch-security/tools/hash.sh -p MyNewSecurePassword!
```

This gave me a hash (something like `$2y$12$...`). 

Next, I opened `config/wazuh_indexer/internal_users.yml` in my code editor, found the `admin` user, and replaced the old hash with the new one. I also updated the `docker-compose.yml` file, changing `INDEXER_PASSWORD=SecretPassword` to match my new password so the manager and dashboard could still authenticate.

Finally, I had to apply the changes to the running indexer. This meant running a tool called `securityadmin.sh` inside the container and pointing it at all the admin certificates:

```bash
docker exec -e OPENSEARCH_JAVA_HOME=/usr/share/wazuh-indexer/jdk single-node-wazuh.indexer-1 bash /usr/share/wazuh-indexer/plugins/opensearch-security/tools/securityadmin.sh -cd /usr/share/wazuh-indexer/config/opensearch-security/ -icl -nhnv -cacert /usr/share/wazuh-indexer/config/certs/root-ca.pem -cert /usr/share/wazuh-indexer/config/certs/admin.pem -key /usr/share/wazuh-indexer/config/certs/admin-key.pem -h localhost -p 9200
```

It printed a bunch of success messages, which was a relief. I restarted the docker containers (`docker compose down && docker compose up -d`) just to be sure everything picked up the changes.

## The Empty Dashboard

I went to `https://localhost` in my browser, ignored the self-signed certificate warning, and logged in with my new password. 

The dashboard loaded perfectly. It's completely empty right now because there's no data flowing into it, but seeing it running locally feels like a huge win. 

Next up: setting up Pi-hole to block ads and malware, and feeding its DNS logs into Wazuh so I can start seeing what my devices are actually doing on the network.
