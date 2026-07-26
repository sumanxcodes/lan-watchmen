# Setting up the environment (or: the boring stuff that isn't boring)

This is part 2 of my home SIEM build series. [Part 1](blog-post-1-building-a-home-siem.md) was the pitch — here's what I'm building and why. This post is about what I actually did to get ready before touching any security tools.

I know "environment setup" sounds like the skippable chapter in a textbook. But honestly, some of the most useful things I learned in this sprint were things I didn't expect to learn at all.

## The architecture decision I almost overthought

The first thing I had to decide was: am I running this 24/7, or spinning it up when I need it?

I went with **demo-snapshot**. Meaning I bring up the Docker stack when I'm working on it or want to show it to someone, and shut it down when I'm done. I don't want to commit to keeping a home lab running around the clock. This is a learning project and a portfolio piece, not a production SOC.

I almost talked myself into buying a mini PC and leaving it on all the time. Glad I didn't. My laptop has 16GB of RAM and Docker Desktop already installed. That's more than enough for a single-node Wazuh deployment.

## Docker was the easy part

I was expecting at least one Docker headache. There wasn't one. Docker Engine 29.2.1 and Compose v5.1.0 were already on my machine. I ran `docker run --rm alpine echo "hello"` and it worked. That's it. No socket permission errors, no daemon issues. I'm on a Mac with Apple Silicon, and Docker Desktop handles all the Linux VM stuff behind the scenes.

If you're on Linux, this step is probably even simpler. If you're on Windows, I genuinely don't know — I haven't tried.

## The vm.max_map_count thing

This one caught me off guard.

The Wazuh indexer is OpenSearch under the hood, and OpenSearch needs a kernel parameter called `vm.max_map_count` set to at least 262144. On Linux you'd just run `sysctl -w vm.max_map_count=262144` and be done. On macOS, that parameter doesn't exist at the host level. It lives inside Docker Desktop's hidden Linux VM.

The fix is weirdly elegant:

```bash
docker run --rm --privileged alpine sysctl -w vm.max_map_count=262144
```

This spins up a throwaway Alpine container with privileged access to the Docker VM's kernel, sets the value, and exits. I verified it stuck:

```bash
$ docker run --rm alpine sysctl vm.max_map_count
vm.max_map_count = 262144
```

The catch: **this doesn't survive Docker Desktop restarts.** Every time you restart Docker, you need to run that command again. I'll probably script this eventually, but for now I just remember to do it before bringing up the stack. Not ideal, but fine for a demo setup.

This is exactly the kind of thing I wouldn't have known about if I hadn't tried it myself. The Wazuh docs mention `vm.max_map_count` but mostly assume you're on Linux.

## Cloning the Wazuh Docker repo

I cloned the official `wazuh-docker` repo at tag v4.14.6 (the latest stable release as of July 2026):

```bash
git clone https://github.com/wazuh/wazuh-docker.git -b v4.14.6 --depth 1
```

The `--depth 1` keeps it small — I don't need the full commit history, just the config files. The single-node directory has everything I need:

```
wazuh-docker/single-node/
├── config/
├── docker-compose.yml
└── generate-indexer-certs.yml
```

Three containers will come out of this: the Wazuh manager (the brain), the indexer (stores everything), and the dashboard (the thing I'll actually look at). There's also a separate compose file for generating TLS certificates the indexer needs. That's a Sprint 1 problem.

## What I have right now

Nothing running yet. But everything is staged and ready:

| Component | Version |
|---|---|
| Docker Engine | 29.2.1 |
| Docker Compose | v5.1.0 |
| macOS | Darwin 25.5.0 (Apple Silicon) |
| RAM | 16GB |
| Python | 3.14.0 |
| wazuh-docker | v4.14.6 |
| vm.max_map_count | 262144 |

It's a clean starting point. No half-configured services, no leftover containers from previous experiments. Just a cloned repo and a verified Docker install.

## What's next

Sprint 1: actually bringing Wazuh to life. I'll generate the TLS certificates, run `docker compose up`, and try to log into the dashboard for the first time. I'm expecting the certificate step to be the part that trips me up — certificate stuff always is.

If anything goes spectacularly wrong, you'll hear about it. That's the deal with writing in public.

#CyberSecurity #Wazuh #SOCAnalyst #HomeLab #BlueTeam
