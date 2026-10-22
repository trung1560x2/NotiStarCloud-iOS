import json
import urllib.request

WEBAPP_URL = "https://script.google.com/macros/s/AKfycbzjPZ5K00RzxkpNRp_AMkq3FUrznjefkW-pq6cqlBzjeVuQ_Hp6YWeTiC9UvFqSy-r93w/exec"

print("[1] Downloading current backup from Google Drive...")
raw = urllib.request.urlopen(f"{WEBAPP_URL}?action=pull", timeout=30).read().decode("utf-8")
data = json.loads(raw)
items = data.get("notifications", [])
print(f"    Loaded {len(items)} items ({len(raw)/1e6:.2f} MB)")

# Clean false-positive isRevoked & strip redundant smallIconB64 to speed up Google Drive sync
cleaned_for_drive = []
for item in items:
    c = dict(item)
    # Remove redundant smallIconB64 (saves ~3.6 MB)
    c.pop("smallIconB64", None)
    # Fix false-positive isRevoked on normal Telegram/chat messages
    if c.get("isRevoked") and c.get("key") != "demo_zalo_2":
        c["isRevoked"] = False
    cleaned_for_drive.append(c)

# Push in batches of 500 to overwrite map[packageName|time|title] on Google Drive
print("[2] Updating Google Drive backup to clear false isRevoked flags and shrink size...")
batch_size = 600
for i in range(0, len(cleaned_for_drive), batch_size):
    batch = cleaned_for_drive[i:i + batch_size]
    payload = json.dumps({
        "action": "sync",
        "device": data.get("device", "samsung SM-S928B"),
        "notifications": batch
    }).encode("utf-8")
    req = urllib.request.Request(
        WEBAPP_URL,
        data=payload,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST"
    )
    resp = urllib.request.urlopen(req, timeout=45).read().decode("utf-8")
    print(f"    Batch {i//batch_size + 1}: {resp}")

# Build a deduplicated, clean snapshot with real photos for instant iOS startup
seen_content = set()
dedup_items = []
# Sort newest first, but prefer items that have pictureB64 when deduplicating!
items_sorted = sorted(
    cleaned_for_drive,
    key=lambda x: (1 if x.get("pictureB64") else 0, x.get("time", 0)),
    reverse=True
)
for item in items_sorted:
    pkg = item.get("packageName", "")
    title = item.get("title", "")
    body = item.get("bigText") or item.get("contentText") or ""
    # Skip NotiStar Cloud's own false revoke alert spam
    if pkg == "com.notistar.cloud" and ("vừa thu hồi" in title or "Nội dung gốc:" in body):
        continue
    sig = (pkg, title.strip(), body.strip())
    if sig in seen_content:
        continue
    seen_content.add(sig)
    dedup_items.append(item)

dedup_items.sort(key=lambda x: x.get("time", 0), reverse=True)
pics_count = sum(1 for x in dedup_items if x.get("pictureB64"))
print(f"[3] Deduplicated clean items: {len(dedup_items)} (with pictureB64: {pics_count})")

snapshot_obj = {
    "updatedAt": data.get("updatedAt"),
    "device": data.get("device", "samsung SM-S928B"),
    "total": len(dedup_items),
    "notifications": dedup_items[:350]
}
for out_path in [
    r"e:\MOD\NotiStarCloud_iOS\cloud_snapshot.json",
    r"e:\MOD\NotiStarCloud_iOS\WebApp_PWA\cloud_snapshot.json",
]:
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(snapshot_obj, f, ensure_ascii=False)
print("[4] Saved cloud_snapshot.json successfully!")
