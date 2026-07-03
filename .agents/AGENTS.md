# Writing Style — Julia Evans Mode

Every piece of text an AI agent produces in this repo — code comments, commit
messages, docs, README updates — follows Julia Evans' writing style.

## What that means in practice

- **First-person, active voice.** "I added", "this does", "I'm not sure if".
  Never "the module facilitates" or "it was determined that".
- **Plain words over jargon.** Say "checks if the device is new" not "validates
  device entity novelty". If a technical term is genuinely needed, use it — but
  don't reach for a fancy word when a simple one works.
- **Honest about unknowns.** If something is a workaround, a guess, or
  something you haven't fully tested, say so. "I think this works but I haven't
  tested it on 5GHz clients yet" is better than pretending it's rock-solid.
- **Short sentences.** If a sentence has more than one comma, it probably wants
  to be two sentences.
- **Story/log feel.** Commit messages and docs should read like a journal entry,
  not a changelog robot or a press release.

## Commit messages

Format:
```
<type>: <what I did, in plain words>

<optional body — why I did it, what I learned, what's still rough>
```

Types: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`

Good example:
```
feat: add the device-polling script that runs arp -a every 5 minutes

I went with parsing arp -a output instead of scapy because scapy needs
root and I didn't want to run the whole container as root. this is
probably fine for a home network but I'm not 100% sure it catches
everything — need to test with a device that connects via 5GHz wifi.
```

Bad example:
```
Added device polling functionality

Implemented device polling module with ARP table parsing capabilities
to enable network device discovery and inventory management.
```

## Code comments

Good:
```python
# I'm polling every 300s because that's roughly how often devices
# cycle their ARP cache. honestly I'm not sure if this is too
# aggressive for a Pi — will watch CPU usage in sprint 3.
```

Bad:
```python
# Poll interval configuration for ARP cache refresh cycle
# optimization across network device topology.
```

## Docs and blog posts

Same rules. Write like you're telling a friend what you built over coffee, not
like you're writing a whitepaper. Include what broke, what surprised you, what
you'd do differently.

---

# Git Workflow — Feature Branch Pipeline

Never commit directly to `main`. Every change goes through a feature branch,
gets pushed to the remote, then merges back with `--no-ff`.

## Branch naming

```
sprint-<N>/<feature-slug>
```

Examples:
- `sprint-1/wazuh-docker-compose`
- `sprint-2/pihole-deploy`
- `sprint-3/device-inventory-script`
- `sprint-4/detection-rules`
- `sprint-5/mitre-attack-mapping`

## Workflow for every feature

1. **Start clean from main:**
   ```bash
   git checkout main && git pull origin main
   ```

2. **Create the feature branch:**
   ```bash
   git checkout -b sprint-<N>/<feature-slug>
   ```

3. **Develop and commit.** Each commit should be one logical change. Don't
   bundle unrelated things together.

4. **Push the branch to origin** (so there's a remote record before merging):
   ```bash
   git push -u origin sprint-<N>/<feature-slug>
   ```

5. **Merge to main with `--no-ff`** (this creates a merge commit so the log
   clearly shows where features landed):
   ```bash
   git checkout main
   git merge --no-ff sprint-<N>/<feature-slug>
   ```

6. **Push main:**
   ```bash
   git push origin main
   ```

7. **Delete the feature branch** (keep the tree clean):
   ```bash
   git branch -d sprint-<N>/<feature-slug>
   git push origin --delete sprint-<N>/<feature-slug>
   ```

## Rules

- **Never commit directly to `main`.** Always go through a feature branch.
- **Always push the feature branch before merging.** There should be a remote
  record of every branch that existed.
- **Always use `--no-ff` for merges.** Flat history hides where features start
  and end.
- **Delete branches after merge.** Stale branches are confusing.
- **Run `git status` before merging.** Make sure the working tree is clean.
- **One feature branch per sprint feature.** Don't pile multiple unrelated
  features into one branch.
