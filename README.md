# TIDRADIO & ODMaster Group Codes — Open Channel

**Live site: https://Wey2shop.github.io/tidradio-group-codes/**

A free, community-run directory of PoC / ODMaster group join codes. Find a
channel to join, log one you run, upvote channels that are still active, or
flag ones that have gone quiet — all through GitHub, no account on any other
service required.

- 🔎 **Browse** channels by category, spots available, or search by name/code.
- ➕ **Log a channel** in a couple of clicks — opens a pre-filled GitHub Issue.
- 👍 **Upvote** to confirm a channel's still active, or **report** one that's
  gone quiet. Both are rate-limited to once per person per day, per channel.

## How it works

There's no server or database behind this — `data/channels.json` in this repo
is the single source of truth. Submissions and updates come in as GitHub
Issues, a GitHub Action parses them and commits the change, and the site
(GitHub Pages) just fetches and renders that file. Every change is fully
auditable in the git history.

## The upvote system

There's no API into TIDRADIO/ODMaster's backend, so there's no way to see
real member counts. "Upvote" is a proxy for activity, not a headcount — one
person, once per calendar day, confirming a channel is worth joining. GitHub
identities are hashed before anything is written to the public data file, so
votes can't be traced back to a person.

## Known limitations

- **Not instant.** A submission or update takes roughly 30–60 seconds (issue →
  Action run → commit → your browser's next poll, every 60s).
- **Public by nature.** Anyone can see the full issue history, including who
  submitted what. Don't put anything sensitive in notes.
- **No official verification.** Anyone with a free GitHub account can submit
  or update an entry — entries are self-reported, not vetted by TIDRADIO,
  ODMaster, or anyone official.
