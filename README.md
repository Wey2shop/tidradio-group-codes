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

## How to submit or update a channel

Every submission is a GitHub Issue, opened from a form — you never need to
add labels or edit anything yourself, GitHub applies the right one
automatically based on which form you used:

- **Log a new channel** (labeled `new-channel` behind the scenes) — use the
  "Log a channel" button on the site, or open the
  [new-channel form](https://github.com/Wey2shop/tidradio-group-codes/issues/new?template=new-channel.yml)
  directly.
  Fields: **Group name**, **Join code**, **Category**, **Spots available?**,
  **Notes** (optional), **Your handle** (optional). A duplicate join code is
  rejected automatically, so search the site first.

- **Update a channel** (labeled `channel-update` behind the scenes) — use the
  Upvote / Report inactive / Update spots controls on each channel's tile, or
  open the
  [channel-update form](https://github.com/Wey2shop/tidradio-group-codes/issues/new?template=channel-update.yml)
  directly. Fields: **Join code** of the channel you're updating and **What
  are you reporting?** (Still active / Seems inactive / Now open / Now
  filling up / Now full). Limited to once per person per day, per channel,
  per action.

Either way: it needs a free GitHub account, the issue is public, and the
change shows up on the site within a minute or two once the bot processes it.

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
- **The join code field isn't locked.** The Upvote / Report / Update-spots
  buttons pre-fill the join code, but GitHub Issue Forms have no read-only
  field option, so it can still be edited before submitting. If it's changed
  to a code that doesn't exist, `process_issue.py` just replies that the
  code wasn't found — it can't accidentally update the wrong channel.
