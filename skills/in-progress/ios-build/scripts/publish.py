#!/usr/bin/env python3
"""Publish a development-signed .app as an over-the-air install.

Packages the .app as an .ipa in its own build slot under the served root,
writes its manifest.plist, prunes old builds of the same app and branch,
and rebuilds the landing page that lists every build. Prints the URLs to
check, as JSON, on stdout.

Exit codes: 0 published, 2 bad input, 3 the phone is not in a profile.
"""

import argparse
import datetime
import html
import json
import plistlib
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def fail(code, message):
    print(message, file=sys.stderr)
    sys.exit(code)


def slug(text):
    return re.sub(r"[^A-Za-z0-9._-]+", "-", text).strip("-.") or "detached"


def profiles(app):
    """Every embedded provisioning profile: the app's and each extension's."""
    for path in [app / "embedded.mobileprovision", *sorted(app.glob("PlugIns/*.appex/embedded.mobileprovision")),
                 *sorted(app.glob("Extensions/*.appex/embedded.mobileprovision"))]:
        if path.exists():
            yield path


def check_profiles(app, udid):
    found = False
    now = datetime.datetime.now(datetime.timezone.utc)
    for path in profiles(app):
        found = True
        owner = path.parent.name
        raw = subprocess.run(["security", "cms", "-D", "-i", str(path)], capture_output=True, check=True).stdout
        profile = plistlib.loads(raw)
        expires = profile["ExpirationDate"].replace(tzinfo=datetime.timezone.utc)
        if expires < now:
            fail(3, f"Requirement missing: phone registered in the Apple team. The profile of {owner} expired on {expires:%Y-%m-%d}.")
        if profile.get("ProvisionsAllDevices"):
            continue
        if udid not in profile.get("ProvisionedDevices", []):
            fail(3, f"Requirement missing: phone registered in the Apple team. The profile of {owner} "
                    f"({profile.get('Name', '?')}) does not list this phone, so iOS would refuse the install without saying why.")
    if not found:
        fail(3, "Requirement missing: phone registered in the Apple team. The .app embeds no provisioning profile: it was not signed for a device.")


def package(app, slot):
    with tempfile.TemporaryDirectory(dir=slot) as stage:
        payload = Path(stage) / "Payload"
        payload.mkdir()
        subprocess.run(["ditto", str(app), str(payload / app.name)], check=True)
        subprocess.run(["zip", "-qry", str(slot / "App.ipa"), "Payload"], cwd=stage, check=True)


def write_manifest(slot, url, info, title):
    manifest = {"items": [{
        "assets": [{"kind": "software-package", "url": url}],
        "metadata": {
            "bundle-identifier": info["CFBundleIdentifier"],
            "bundle-version": info.get("CFBundleShortVersionString", "0"),
            "kind": "software",
            "title": title,
        },
    }]}
    with open(slot / "manifest.plist", "wb") as handle:
        plistlib.dump(manifest, handle)


def prune(branch_dir, keep):
    builds = sorted((d for d in branch_dir.iterdir() if (d / "build.json").exists()), reverse=True)
    for old in builds[keep:]:
        shutil.rmtree(old)


def landing(root, base_url):
    builds = [json.loads(p.read_text()) for p in root.glob("*/*/*/build.json")]
    builds.sort(key=lambda b: b["date"], reverse=True)
    rows = []
    for b in builds:
        href = html.escape(f"itms-services://?action=download-manifest&url={b['manifest_url']}")
        rows.append(
            "<tr><td>{app}<br><small>{bundle}</small></td><td>{branch}</td><td><code>{sha}</code></td>"
            "<td>{date}</td><td>{size}</td><td><a href=\"{href}\">Install</a></td></tr>".format(
                app=html.escape(b["app"]), bundle=html.escape(b["bundle_id"]), branch=html.escape(b["branch"]),
                sha=html.escape(b["sha"]), date=html.escape(b["date"].replace("T", " ")[:16] + " UTC"),
                size=f"{b['size'] / 1_000_000:.0f} MB", href=href))
    page = f"""<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Dev builds</title>
<style>body{{font:16px -apple-system,sans-serif;margin:1rem}}table{{border-collapse:collapse;width:100%}}
td,th{{padding:.5rem;border-bottom:1px solid #ddd;text-align:left;vertical-align:top}}a{{font-weight:600}}</style>
</head><body>
<h1>Dev builds</h1>
<p>Open this page in Safari: install links do not work in other browsers.</p>
<table><tr><th>App</th><th>Branch</th><th>Commit</th><th>Built</th><th>Size</th><th></th></tr>
{chr(10).join(rows) or '<tr><td colspan="6">No build yet.</td></tr>'}
</table>
<p><small>Served from {html.escape(base_url)}</small></p>
</body></html>
"""
    (root / "index.html").write_text(page)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--app", required=True, type=Path, help="the built .app")
    parser.add_argument("--root", required=True, type=Path, help="the folder the static server serves")
    parser.add_argument("--base-url", required=True, help="https://<host>:<port> as the phone sees it")
    parser.add_argument("--branch", required=True)
    parser.add_argument("--sha", required=True)
    parser.add_argument("--udid", help="the phone's UDID, checked against every embedded profile")
    parser.add_argument("--keep", type=int, default=3, help="builds kept per app and branch")
    args = parser.parse_args()

    app = args.app.resolve()
    if not (app / "Info.plist").exists():
        fail(2, f"Not an iOS .app bundle: {app}")
    with open(app / "Info.plist", "rb") as handle:
        info = plistlib.load(handle)
    if args.udid:
        check_profiles(app, args.udid)

    base_url = args.base_url.rstrip("/")
    bundle_id = info["CFBundleIdentifier"]
    now = datetime.datetime.now(datetime.timezone.utc)
    branch_dir = args.root / slug(bundle_id) / slug(args.branch)
    slot = branch_dir / f"{now:%Y%m%dT%H%M%SZ}-{slug(args.sha)}"
    slot.mkdir(parents=True)
    prefix = f"{base_url}/{slot.relative_to(args.root).as_posix()}"

    package(app, slot)
    name = info.get("CFBundleDisplayName") or info.get("CFBundleName") or app.stem
    write_manifest(slot, f"{prefix}/App.ipa", info, f"{name} dev {args.sha}")
    build = {
        "app": name, "bundle_id": bundle_id, "branch": args.branch, "sha": args.sha,
        "version": f"{info.get('CFBundleShortVersionString', '?')} ({info.get('CFBundleVersion', '?')})",
        "date": now.isoformat(timespec="seconds"), "size": (slot / "App.ipa").stat().st_size,
        "ipa_url": f"{prefix}/App.ipa", "manifest_url": f"{prefix}/manifest.plist", "landing_url": f"{base_url}/",
    }
    (slot / "build.json").write_text(json.dumps(build, indent=1))
    prune(branch_dir, args.keep)
    landing(args.root, base_url)
    print(json.dumps(build, indent=1))


if __name__ == "__main__":
    main()
