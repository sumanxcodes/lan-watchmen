# Sprint 0 — Planning & environment setup

**Sprint goal:** get the environment ready so I can actually start building
things in Sprint 1. Architecture confirmed, Docker host provisioned, Wazuh
repo cloned, everything verified.

**Date:** July 2026

---

## Architecture decision

I'm going with a **demo-snapshot deployment**, not an always-on setup. This
means I spin up the Docker stack when I want to work on it or demo it, and shut
it down when I'm done. I don't want to commit to running a home-lab 24/7 — this
is a learning project and a portfolio piece, not a production security
deployment.

The stack runs on my laptop (macOS, Apple Silicon, 16GB RAM). That's plenty for
a single-node Wazuh deployment. If I wanted to leave it running all the time,
I'd move it to a spare mini PC or a Pi, but for now, laptop is fine.

## Docker host

**Machine:** MacBook, Apple Silicon (arm64), macOS 15 (Darwin 25.5.0)
**RAM:** 16GB (Wazuh docs recommend at least 6GB for the indexer alone)
**Docker:** Docker Desktop for Mac, Docker Engine 29.2.1, Compose v5.1.0

Docker was already installed. I didn't need to do anything special here.

## vm.max_map_count

This one tripped me up for a second. The Wazuh indexer (which is basically
OpenSearch under the hood) needs `vm.max_map_count` set to at least 262144.
On Linux, you'd just do `sysctl -w vm.max_map_count=262144`. On macOS, that
kernel parameter doesn't exist at the host level — it lives inside Docker
Desktop's hidden Linux VM.

The fix is:

```bash
docker run --rm --privileged alpine sysctl -w vm.max_map_count=262144
```

This runs a throwaway alpine container with privileged access to the Docker
VM's kernel and sets the value. I verified it works:

```bash
$ docker run --rm alpine sysctl vm.max_map_count
vm.max_map_count = 262144
```

**Heads up:** this doesn't survive Docker Desktop restarts. Every time you
restart Docker Desktop, you need to run that command again. I might add a
script for this later, but for now, I'll just remember to do it before bringing
up the Wazuh stack.

## Cloning the wazuh-docker repo

I cloned the official repo at tag `v4.14.6` (latest stable as of July 2026):

```bash
git clone https://github.com/wazuh/wazuh-docker.git -b v4.14.6 --depth 1
```

I used `--depth 1` because I don't need the full git history — I just want the
config files. The single-node directory has what I need:

```
wazuh-docker/single-node/
├── README.md
├── config/
├── docker-compose.yml
└── generate-indexer-certs.yml
```

The `docker-compose.yml` brings up three containers: wazuh-manager,
wazuh-indexer, and wazuh-dashboard. The `generate-indexer-certs.yml` is a
separate compose file that generates the TLS certs the indexer needs — that's
a Sprint 1 task.

I added `wazuh-docker/` to `.gitignore` because it's an upstream clone, not my
code. No point pushing someone else's repo into mine.

## Verifying docker commands

Everything runs clean:

```
$ docker --version
Docker version 29.2.1, build a5c7197

$ docker compose version
Docker Compose version v5.1.0

$ docker run --rm alpine echo "hello from docker"
hello from docker
```

No errors, no permission issues, no socket problems. Docker Desktop on macOS
handles all of this pretty smoothly these days.

## Blog post 1

The pitch post is drafted — it explains why I'm building this, what the
architecture looks like, and what I'm hoping to learn. It's written in Julia
Evans' style: first-person, honest about what I don't know, not pretending this
is a polished tutorial.

See: `docs/blog-post-1-building-a-home-siem.md`

## What's next (Sprint 1)

Sprint 1 is where the real work starts: generating the indexer certificates,
bringing up the Wazuh stack with `docker compose up`, and logging into the
dashboard for the first time. I'm expecting the cert generation step to be the
trickiest part — certificate stuff always is.

---

## Environment snapshot

For the record, here's exactly what I'm working with:

| Component | Version / spec |
|---|---|
| macOS | Darwin 25.5.0, arm64 |
| RAM | 16GB |
| Docker Engine | 29.2.1 |
| Docker Compose | v5.1.0 |
| Python | 3.14.0 |
| wazuh-docker | v4.14.6 (single-node) |
| vm.max_map_count | 262144 (set in Docker VM) |
