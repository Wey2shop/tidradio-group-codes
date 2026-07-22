import hashlib
import json
import os
import re
from datetime import datetime, timedelta, timezone

ISSUE_BODY = os.environ.get("ISSUE_BODY", "")
ISSUE_AUTHOR = os.environ.get("ISSUE_AUTHOR", "unknown")
IS_NEW = os.environ.get("IS_NEW_CHANNEL", "false") == "true"
IS_UPDATE = os.environ.get("IS_UPDATE", "false") == "true"
DATA_PATH = "data/channels.json"

# Change this before going live. It keeps hashed voter IDs from being guessable
# via a common rainbow table -- it doesn't need to stay secret from you, only
# from someone trying to reverse a hash back to a GitHub username.
SALT = "tidradio-group-codes-98l6unhsqi1zxdkr5pfa027mvwetcogy"

ACTION_KEYS = {
    "Still active (confirm)": "confirm",
    "Seems inactive (report)": "report",
    "Now open": "open",
    "Now filling up": "filling",
    "Now full": "full",
}


def parse_fields(body):
    parts = re.split(r"\n### ", "\n" + body)
    fields = {}
    for part in parts:
        if "\n" not in part:
            continue
        label, _, rest = part.partition("\n")
        fields[label.strip()] = "" if rest.strip() == "_No response_" else rest.strip()
    return fields


def load_data():
    try:
        with open(DATA_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_data(data):
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def today_str():
    return datetime.now(timezone.utc).date().isoformat()


def hash_voter(login):
    return hashlib.sha256((SALT + login).encode()).hexdigest()[:16]


def write_outputs(changed, should_close, comment):
    with open("comment.txt", "w") as f:
        f.write(comment)
    gh_out = os.environ.get("GITHUB_OUTPUT")
    if gh_out:
        with open(gh_out, "a") as f:
            f.write(f"changed={'true' if changed else 'false'}\n")
            f.write(f"should_close={'true' if should_close else 'false'}\n")


def already_did(entry, action_key, voter_hash, today):
    log = entry.get("actionLog", [])
    return any(x["h"] == voter_hash and x["a"] == action_key and x["d"] == today for x in log)


def record_action(entry, action_key, voter_hash, today):
    log = entry.setdefault("actionLog", [])
    log.append({"h": voter_hash, "a": action_key, "d": today})
    entry["actionLog"] = log[-500:]  # keep the file from growing forever


def confirm_stats(entry, today):
    log = entry.get("actionLog", [])
    today_count = sum(1 for x in log if x["a"] == "confirm" and x["d"] == today)
    week_ago = (datetime.now(timezone.utc).date() - timedelta(days=6)).isoformat()
    week_count = sum(1 for x in log if x["a"] == "confirm" and x["d"] >= week_ago)
    return today_count, week_count


def handle_new_channel(fields, data):
    name = fields.get("Group name", "").strip()
    code = fields.get("Join code", "").strip()
    models = fields.get("Radio / app compatibility", "").strip()
    category = fields.get("Category", "Other").strip() or "Other"
    spots = fields.get("Spots available?", "Open").strip() or "Open"
    notes = fields.get("Notes", "").strip()
    handle = fields.get("Your handle (optional)", "").strip() or "Anonymous"

    if not name or not code:
        write_outputs(False, True,
            "Missing a group name or join code -- please open a new submission with both filled in.")
        return

    existing = next((e for e in data if e["code"] == code), None)
    if existing:
        write_outputs(False, True,
            f"A channel with code **{code}** already exists: **{existing['name']}**. "
            f"If you meant to update it, please open a **Channel update** issue instead.")
        return

    entry = {
        "id": f"e{int(datetime.now().timestamp())}",
        "name": name,
        "code": code,
        "models": models,
        "category": category,
        "spots": spots,
        "notes": notes,
        "addedBy": handle,
        "addedAt": now_iso(),
        "upvotes": 0,
        "upvotesToday": 0,
        "upvotes7d": 0,
        "reports": 0,
        "lastConfirmed": None,
        "lastUpdated": now_iso(),
        "actionLog": [],
    }
    data.append(entry)
    save_data(data)
    write_outputs(True, True,
        f"Logged **{name}** (`{code}`). It'll appear on the site within a minute or two.")


def handle_update(fields, data):
    code = fields.get("Join code of the channel you're updating", "").strip()
    action = fields.get("What are you reporting?", "").strip()
    entry = next((e for e in data if e["code"] == code), None)

    if not entry:
        write_outputs(False, True,
            f"Couldn't find a channel with code **{code}**. Check the directory for the exact code and try again.")
        return

    key = ACTION_KEYS.get(action)
    if key is None:
        write_outputs(False, True, f"Didn't recognize the action \"{action}\".")
        return

    voter_hash = hash_voter(ISSUE_AUTHOR)
    today = today_str()

    if already_did(entry, key, voter_hash, today):
        write_outputs(False, True,
            f"You've already logged that for **{entry['name']}** (`{code}`) today -- thanks for checking in "
            f"though. Come back tomorrow to vote again.")
        return

    record_action(entry, key, voter_hash, today)

    if key == "confirm":
        entry["upvotes"] = entry.get("upvotes", 0) + 1
        entry["lastConfirmed"] = now_iso()
        today_count, week_count = confirm_stats(entry, today)
        entry["upvotesToday"] = today_count
        entry["upvotes7d"] = week_count
        msg = f"Logged your upvote for **{entry['name']}** (`{code}`) -- {entry['upvotes']} total, {today_count} today."
    elif key == "report":
        entry["reports"] = entry.get("reports", 0) + 1
        msg = f"Logged a quiet report for **{entry['name']}** (`{code}`)."
    elif key == "open":
        entry["spots"] = "Open"
        msg = f"**{entry['name']}** (`{code}`) marked as Open."
    elif key == "filling":
        entry["spots"] = "Filling up"
        msg = f"**{entry['name']}** (`{code}`) marked as Filling up."
    elif key == "full":
        entry["spots"] = "Full"
        msg = f"**{entry['name']}** (`{code}`) marked as Full."

    entry["lastUpdated"] = now_iso()
    save_data(data)
    write_outputs(True, True, msg)


def main():
    fields = parse_fields(ISSUE_BODY)
    data = load_data()

    if IS_NEW:
        handle_new_channel(fields, data)
    elif IS_UPDATE:
        handle_update(fields, data)
    else:
        write_outputs(False, False, "")


if __name__ == "__main__":
    main()
