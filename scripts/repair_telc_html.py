#!/usr/bin/env python3
"""One-time, reversible TELC static HTML repair; no learning data or answers changed."""
from pathlib import Path
import gzip
import re
import sys

root = Path(__file__).resolve().parents[1]
paths = sorted(root.rglob("*.html"))
changes = {"gzip_html": 0, "legacy_tracking": 0, "server_only_timer": 0,
           "contact": 0, "files_written": 0, "skipped_non_html": 0}
errors = []
for path in paths:
    if any(folder in path.parts for folder in (".git", "node_modules", ".github")):
        continue
    original = path.read_bytes()
    if original.startswith(b"\x1f\x8b"):
        try:
            decoded = gzip.decompress(original).decode("utf-8")
            if not re.search(r"<html\b|<!doctype\s+html", decoded[:2000], re.I):
                errors.append(str(path.relative_to(root)) + " gzip without HTML")
                continue
            changes["gzip_html"] += 1
        except (OSError, UnicodeError):
            errors.append(str(path.relative_to(root)) + " invalid gzip HTML")
            continue
    else:
        try:
            decoded = original.decode("utf-8")
        except UnicodeError:
            errors.append(str(path.relative_to(root)) + " invalid UTF-8")
            continue
    if not re.search(r"<html\b|<!doctype\s+html", decoded[:2000], re.I):
        changes["skipped_non_html"] += 1
        continue
    before = decoded
    decoded = decoded.replace("905419112503", "905409122503").replace("0541 911 25 03", "0540 912 25 03")
    decoded = decoded.replace("905409102503", "905409122503")
    if decoded != before:
        changes["contact"] += 1
    old = decoded
    decoded = re.sub(r'<script\b[^>]*\bsrc=["\']_vercel/insights/script\.html["\'][^>]*>\s*</script>', '', decoded, flags=re.I)
    decoded = re.sub(r'<script\b[^>]*\bsrc=["\'](?:\.\./)+static\.cloudflareinsights\.com/beacon\.min\.js["\'][^>]*>\s*</script>', '', decoded, flags=re.I)
    decoded = re.sub(r'<!-- Cloudflare Pages Analytics -->', '', decoded, flags=re.I)
    decoded = decoded.replace("../cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css",
                              "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css")
    if old != decoded:
        changes["legacy_tracking"] += 1
    old = decoded
    # Imported mirror pages used /ping and /logout endpoints absent on GitHub Pages.
    # Remove only that obsolete timeout block; preserve quiz/exercise scripts.
    decoded = re.sub(r'<script>\s*let pingTimeout;\s*[\s\S]*?</script>', '', decoded, flags=re.I)
    if decoded != old:
        changes["server_only_timer"] += 1
    if decoded.encode("utf-8") != original:
        path.write_text(decoded, encoding="utf-8")
        changes["files_written"] += 1

print("TELC static maintenance:", changes, flush=True)
if errors:
    print("Unsupported HTML encodings, no publication:", errors[:25], file=sys.stderr)
    sys.exit(2)
if changes["files_written"] < 1:
    print("No further changes required")
