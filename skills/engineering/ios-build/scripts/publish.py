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


LANDING_STYLE = """
:root{--bg:#f2f2f7;--card:#fff;--text:#1c1c1e;--muted:#6e6e73;--line:rgba(60,60,67,.14);
--accent:#007aff;--accent-text:#fff;--tint:rgba(0,122,255,.1);--chip:rgba(120,120,128,.12);color-scheme:light dark}
@media (prefers-color-scheme:dark){:root{--bg:#000;--card:#1c1c1e;--text:#f2f2f7;--muted:#98989f;
--line:rgba(84,84,88,.55);--accent:#0a84ff;--tint:rgba(10,132,255,.18);--chip:rgba(120,120,128,.24)}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);font:17px/1.4 -apple-system,BlinkMacSystemFont,"SF Pro Text",system-ui,sans-serif;
-webkit-text-size-adjust:100%;padding:max(20px,env(safe-area-inset-top)) max(16px,env(safe-area-inset-right))
max(28px,env(safe-area-inset-bottom)) max(16px,env(safe-area-inset-left))}
main{max-width:560px;margin:0 auto}
header{margin:8px 4px 20px}
h1{font-size:34px;line-height:1.1;font-weight:700;letter-spacing:-.02em;margin:0}
.count{color:var(--muted);font-size:15px;margin:4px 0 12px}
.hint{display:flex;gap:8px;align-items:center;color:var(--muted);font-size:13px;margin:0}
.hint svg{flex:none}
section{margin:0 0 28px}
h2{font-size:22px;font-weight:700;margin:0 4px 2px;letter-spacing:-.01em}
.bundle{color:var(--muted);font-size:13px;margin:0 4px 12px;overflow-wrap:anywhere}
.card{background:var(--card);border-radius:18px;padding:16px;margin:0 0 12px;box-shadow:0 1px 2px rgba(0,0,0,.06)}
.latest{box-shadow:0 0 0 2px var(--accent),0 6px 20px rgba(0,0,0,.08)}
.top{display:flex;gap:8px;align-items:flex-start;justify-content:space-between}
.branch{font-size:19px;font-weight:600;margin:0;overflow-wrap:anywhere;min-width:0}
.badge{flex:none;background:var(--accent);color:var(--accent-text);font-size:12px;font-weight:600;
border-radius:999px;padding:3px 9px;text-transform:uppercase;letter-spacing:.04em}
dl{display:grid;grid-template-columns:auto 1fr;gap:6px 14px;margin:12px 0 16px;font-size:15px}
dt{color:var(--muted)}dd{margin:0;overflow-wrap:anywhere}
code{font:14px ui-monospace,"SF Mono",Menlo,monospace;background:var(--chip);padding:2px 6px;border-radius:6px}
.install{display:flex;align-items:center;justify-content:center;gap:8px;width:100%;min-height:54px;border-radius:14px;
background:var(--accent);color:var(--accent-text);font-size:17px;font-weight:600;text-decoration:none;
-webkit-tap-highlight-color:transparent;transition:transform .1s,opacity .1s}
.install:active{transform:scale(.98);opacity:.85}
.older .install{background:var(--tint);color:var(--accent);min-height:48px}
details{margin:0 0 12px}
summary{list-style:none;cursor:pointer;color:var(--accent);font-size:15px;font-weight:500;padding:12px 4px;min-height:44px}
summary::-webkit-details-marker{display:none}
summary::after{content:"\\203A";display:inline-block;margin-left:6px;transition:transform .2s}
details[open] summary::after{transform:rotate(90deg)}
.empty{background:var(--card);border-radius:18px;padding:32px 16px;text-align:center;color:var(--muted)}
footer{color:var(--muted);font-size:12px;text-align:center;margin-top:8px;overflow-wrap:anywhere}
"""

SAFARI_ICON = ('<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
               'aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="m16 8-2.5 5.5L8 16l2.5-5.5z"/></svg>')

INSTALL_ICON = ('<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" '
                'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 4v11m0 0-4.5-4.5M12 15l4.5-4.5'
                'M5 19h14"/></svg>')

# The page is static, so the phone rewrites each date into its own time zone and language.
LANDING_SCRIPT = """
for (const t of document.querySelectorAll("time[datetime]")) {
  const d = new Date(t.dateTime);
  if (!isNaN(d)) t.textContent = d.toLocaleString(undefined, {weekday: "short", day: "numeric", month: "short",
                                                               hour: "2-digit", minute: "2-digit"});
}
"""


def build_card(b, latest):
    href = html.escape(f"itms-services://?action=download-manifest&url={b['manifest_url']}")
    built = datetime.datetime.fromisoformat(b["date"]).astimezone()
    badge = '<span class="badge">Latest</span>' if latest else ""
    return f"""<article class="card{' latest' if latest else ''}">
<div class="top"><p class="branch">{html.escape(b["branch"])}</p>{badge}</div>
<dl><dt>Commit</dt><dd><code>{html.escape(b["sha"][:8])}</code></dd>
<dt>Built</dt><dd><time datetime="{html.escape(b["date"])}">{html.escape(f"{built:%a %d %b, %H:%M}")}</time></dd>
<dt>Version</dt><dd>{html.escape(b.get("version", "?"))}</dd>
<dt>Size</dt><dd>{b["size"] / 1_000_000:.0f} MB</dd></dl>
<a class="install" href="{href}">{INSTALL_ICON}Install</a>
</article>"""


def landing(root, base_url):
    builds = [json.loads(p.read_text()) for p in root.glob("*/*/*/build.json")]
    builds.sort(key=lambda b: b["date"], reverse=True)
    # Group by app, then by branch, both ordered by their most recent build.
    apps = {}
    for b in builds:
        apps.setdefault(b["bundle_id"], {}).setdefault(b["branch"], []).append(b)
    sections = []
    for bundle_id, branches in apps.items():
        first = next(iter(branches.values()))[0]
        parts = [f'<section><h2>{html.escape(first["app"])}</h2><p class="bundle">{html.escape(bundle_id)}</p>']
        for branch_builds in branches.values():
            parts.append(build_card(branch_builds[0], latest=True))
            older = branch_builds[1:]
            if older:
                label = f"{len(older)} older build{'s' if len(older) > 1 else ''} on {branch_builds[0]['branch']}"
                cards = "".join(build_card(b, latest=False) for b in older)
                parts.append(f'<details><summary>{html.escape(label)}</summary><div class="older">{cards}</div></details>')
        parts.append("</section>")
        sections.append("".join(parts))
    count = f"{len(builds)} build{'s' if len(builds) != 1 else ''} ready to install"
    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="color-scheme" content="light dark">
<title>Dev builds</title>
<style>{LANDING_STYLE}</style>
</head><body><main>
<header><h1>Dev builds</h1><p class="count">{count}</p>
<p class="hint">{SAFARI_ICON}Open in Safari: install links do not work in other browsers.</p></header>
{chr(10).join(sections) or '<p class="empty">No build yet.</p>'}
<footer>Served from {html.escape(base_url)}</footer>
</main><script>{LANDING_SCRIPT}</script></body></html>
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
