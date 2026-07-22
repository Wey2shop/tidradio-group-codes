# Open Channel

A community-run directory of PoC / ODMaster group codes. No server, no database —
GitHub Issues collect submissions, a GitHub Action commits them into `data/channels.json`,
and GitHub Pages serves the static site that reads that file.

## Setup (10 minutes)

1. **Create a new repo** on GitHub (public — Pages needs public on the free tier unless
   you're on a paid plan). Push everything in this folder to it, keeping the folder
   structure exactly as-is (the `.github` folder must be at the repo root).

2. **Set your repo name in the site.** Open `index.html` and change this line near the
   top of the `<script>` block:
   ```js
   const REPO = "YOUR-USERNAME/YOUR-REPO";
   ```
   to your actual `username/repo`.

3. **Update the issue template link.** In
   `.github/ISSUE_TEMPLATE/config.yml`, replace
   `https://YOUR-USERNAME.github.io/YOUR-REPO/` with your real Pages URL (see step 4).

4. **Enable GitHub Pages.** Repo → Settings → Pages → under "Build and deployment",
   set Source to "Deploy from a branch", branch `main`, folder `/ (root)`. Save.
   Your site will be live at `https://YOUR-USERNAME.github.io/YOUR-REPO/` within a
   minute or two.

5. **Check Actions is enabled.** Repo → Settings → Actions → General → make sure
   "Allow all actions and reusable workflows" is selected. It's on by default for
   new repos, but worth a glance.

6. **Test it end to end.** Open your live site, click "Log a channel," fill out the
   form, submit. Within a minute check the repo's Actions tab — you should see a
   run of "Process channel submissions." When it finishes, refresh your site and
   the entry should appear, and the issue you filed should be closed with a
   confirmation comment.

## How it works

- `data/channels.json` is the single source of truth — a plain JSON array.
- `.github/ISSUE_TEMPLATE/new-channel.yml` and `channel-update.yml` are the two forms
  people fill out (GitHub renders these as proper forms, not raw markdown).
- `.github/workflows/process-submissions.yml` fires whenever an issue is opened with
  the `new-channel` or `channel-update` label (Issue Forms apply these automatically).
- `.github/scripts/process_issue.py` parses the issue body, updates the JSON, and
  writes a comment. The workflow commits the change and closes the issue.
- `index.html` just fetches `data/channels.json` and renders it — no build step.

## The upvote system

There's no API into TIDRADIO/ODMaster's backend, so there's no way to see real
member counts. Instead, "Upvote" is a rate-limited confirmation: one person, once
per calendar day (UTC), per channel. GitHub's own login is doing the identity
work for free -- the bot reads `github.event.issue.user.login` from the issue
that was filed, so no separate account system is needed.

That username is never written to `channels.json` in plain text. Before
anything is stored, `process_issue.py` hashes it (`hash_voter()`, using the
`SALT` constant near the top of the file) so the public data file can't be used
to build a list of "who voted for what, when" tied to real identities, while
still blocking the same person from voting twice in a day.

**Change `SALT` to your own string before you go live.** It doesn't need to be
secret from you -- it just needs to not be the literal default in this repo.

The same one-per-person-per-day rule applies to "Report inactive" and the three
"spots" updates too, using the same mechanism -- so no single person can spam
any of these into looking artificially active, quiet, or full.

## Known limitations

- **Not instant.** Every submission or update takes roughly 30–60 seconds (issue →
  Action run → commit → your browser's next poll, which happens every 60s).
- **Public by nature.** Anyone can see the full issue history, including who
  submitted what. Don't put anything sensitive in notes.
- **No real moderation.** Anyone with a free GitHub account can submit. If spam
  becomes a problem, the cheapest fix is changing the workflow's `if:` condition
  to also require a maintainer-applied `approved` label before it processes —
  turns this from fully self-serve into "you review, then it auto-publishes."
- **Duplicate codes are blocked** on new submissions (matched by exact code), but
  typos in a code on an update issue will just fail quietly with a comment saying
  the code wasn't found — nothing breaks, it just won't apply.
