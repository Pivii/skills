---
name: ios-build
description: Build the native iOS app of the project you are in and put it on the user's iPhone — installed and launched directly when the phone is on the Mac's network, or as an install link over their private Tailscale network when they are away, on cellular or another Wi-Fi. Use when they ask for a build on their phone ("install this on my phone", "mets la branche sur l'iPhone", "je veux tester sur device"). Native Xcode projects only; for a web dev server on the phone, this is the wrong skill.
---

# iOS build

One sentence from the user — *install this on my phone* — and the app of the checkout you are in ends up on their iPhone, wherever the phone is.

Two routes, and the phone decides which:

- **Direct.** The phone is reachable from the Mac: build for it, install with `devicectl`, launch.
- **Over the air.** It is not: build a development `.ipa`, serve it inside the user's tailnet, and hand them a link they tap in Safari.

The direct route cannot be stretched to reach a phone that is away, and it was measured: replaying the phone's Bonjour record and relaying its ports over Tailscale reaches it, but **iOS closes its developer pairing service when it leaves Wi-Fi** and answers the pairing port with a reset. The over-the-air route needs no pairing at all — an `itms-services://` install is a plain HTTPS download, so cellular is fine. A development-signed build installs this way on every device listed in its provisioning profile.

macOS with Xcode only. A paid Apple developer team only: free accounts sign 7-day profiles, untested here — say it is unsupported.

## 1. Read the project

```bash
ROOT=$(git rev-parse --show-toplevel)
ls "$ROOT"; ls -d "$ROOT"/*.xcworkspace "$ROOT"/*.xcodeproj 2>/dev/null
```

A `pubspec.yaml` at the root is Flutter, which this skill does not build: say so and stop. Otherwise find the project or workspace and the app scheme — from the repo's own `CLAUDE.md` or `AGENTS.md` first, which often also name a derived data path and a package-resolution step a fresh checkout needs; then `xcodebuild -list`. Then read what the build will sign with:

```bash
xcodebuild -showBuildSettings <-project|-workspace> <path> -scheme <scheme> -configuration Debug \
  -destination 'generic/platform=iOS' 2>/dev/null \
  | grep -E '^ +(PRODUCT_BUNDLE_IDENTIFIER|DEVELOPMENT_TEAM|FULL_PRODUCT_NAME) ='
SHA=$(git rev-parse --short HEAD)$(git diff --quiet HEAD -- . || echo -dirty)
BRANCH=$(git branch --show-current); BRANCH=${BRANCH:-$SHA}
```

**Signing is the user's, never the repo's.** An empty `DEVELOPMENT_TEAM`, or a bundle id their team cannot sign, is fixed on the `xcodebuild` command line — `DEVELOPMENT_TEAM=<team> PRODUCT_BUNDLE_IDENTIFIER=<id>` — with values the user gives you. Never by editing `project.pbxproj`, an `.xcconfig` or an entitlements file.

Build into `DD` — the repo's documented derived data path, otherwise one per checkout outside it: `DD="${TMPDIR:-/tmp}/ios-build/$(printf %s "$ROOT" | shasum | cut -c1-8)"`. The app lands in `$DD/Build/Products/Debug-iphoneos/<FULL_PRODUCT_NAME>`.

**Done when you can state the project, scheme, bundle id, team, branch and sha.**

## 2. Pick the route

```bash
xcrun devicectl list devices --json-output "$DD/devices.json"
```

The phone is the entry whose `hardwareProperties` say `reality: physical` and `deviceType: iPhone`; its `hardwareProperties.udid` is the UDID. Several, take the one the user named, otherwise ask. None at all means this Mac has never paired with it — that is the *phone registered* requirement below.

`connectionProperties.tunnelState` reads `disconnected` on a phone that is perfectly reachable: the tunnel comes up on demand. So probe instead of reading the list:

```bash
xcrun devicectl device info details --device <udid>
```

It succeeds within seconds and shows `Device State: connected` → **direct**. It fails or the phone is listed `unavailable` → **over the air**. Prefer direct whenever it works: it is faster, launches the app, and asks nothing of the user.

## 3. Direct

```bash
xcodebuild build <-project|-workspace> <path> -scheme <scheme> -configuration Debug \
  -destination "id=<udid>" -derivedDataPath "$DD" \
  -allowProvisioningUpdates -allowProvisioningDeviceRegistration [DEVELOPMENT_TEAM=… PRODUCT_BUNDLE_IDENTIFIER=…]
xcrun devicectl device install app --device <udid> "$APP"
xcrun devicectl device process launch --device <udid> <bundle-id>
```

`-allowProvisioningDeviceRegistration` registers a phone the team does not know yet, and that is the cheapest moment to do it: a phone registered now is a phone the over-the-air route will accept later.

A launch refused with `BSErrorCodeDescription = Locked` is not a failed install — the app is on the phone, and it opens once they unlock it.

**Done when** the install succeeded and you have reported `<app> <branch> @ <sha> installed on <phone name>`, followed by `launched` or `not launched: phone locked`.

## 4. Over the air

### Check the requirements first

Check each row of [the requirements](#requirements) before building. A missing one is reported **by its name, with its fix** — never as a vague "it does not work", and never discovered by the user on their phone ten minutes later.

### Build for any device

```bash
xcodebuild build <-project|-workspace> <path> -scheme <scheme> -configuration Debug \
  -destination 'generic/platform=iOS' -derivedDataPath "$DD" -allowProvisioningUpdates [overrides]
```

`generic/platform=iOS` needs no phone at build time. `-allowProvisioningUpdates` renews the team profile without the user. A plain `build` is enough: development builds need no `archive` or `-exportArchive`.

### Serve the build root

One root and one static server for every app and every checkout on this machine:

```bash
WWW="$HOME/Library/Caches/ios-build/www"; mkdir -p "$WWW"
```

Bind it to `127.0.0.1` and let Tailscale Serve proxy it. The Mac App Store build of Tailscale cannot serve a folder itself — `Path serving is not supported on macOS due to sandbox restrictions`.

- **With Portly** (`command -v portly`): take the server of project `ios-build` from `portly status --json` and `portly start ios-build/static` if it is stopped. Absent, declare it once on a free fixed port (`portly port <port>` says whether it is free; 8780 is the default):

  ```bash
  portly add-project --name ios-build --path "$WWW"
  portly add-server --project ios-build --name static --port <port> \
    --command "python3 -m http.server <port> --bind 127.0.0.1" --start
  ```

- **Without Portly**: reuse the server whose PID is in `$WWW/../server.pid` if `kill -0` says it is alive; otherwise start one and record it:

  ```bash
  nohup python3 -m http.server <port> --bind 127.0.0.1 --directory "$WWW" > "$WWW/../server.log" 2>&1 &
  echo $! > "$WWW/../server.pid"
  ```

  Tell the user the PID and that `kill <pid>` stops it.

### Publish the build

```bash
TS=$(command -v tailscale || echo /Applications/Tailscale.app/Contents/MacOS/Tailscale)
HOST=$("$TS" status --json | python3 -c "import json,sys;print(json.load(sys.stdin)['Self']['DNSName'].rstrip('.'))")
python3 -I <this skill's folder>/scripts/publish.py --app "$APP" --root "$WWW" \
  --base-url "https://$HOST:8443" --branch "$BRANCH" --sha "$SHA" --udid <udid>
```

The script checks the phone's UDID against **every** embedded profile — the app's and each extension's — because a phone missing from one installs nothing and the phone says nothing about why. It exits 3 naming the target, which is the *phone registered* requirement. Then it packages the `.ipa` into its own slot, `<bundle-id>/<branch>/<time>-<sha>/`, writes the manifest with the sha in its title, keeps the 3 most recent builds of this app and branch, and rewrites the landing page at the root that lists them all. Two apps, or two checkouts of one app, never overwrite each other, and no manifest URL is ever reused, so the phone never installs a cached one.

### Expose it on 8443

The OTA route owns its own HTTPS port. Port 443 and its `/` belong to whatever else this machine serves on the tailnet — a web dev server for the phone, typically. Leave them as they are, and leave `serve reset` unrun: it erases every config, not just this one.

```bash
"$TS" serve status --json
"$TS" serve --bg --https=8443 http://127.0.0.1:<port>
```

Already proxying 8443 to `<port>`, skip the second command. Proxying 8443 to anything else, it is not yours: stop and tell the user rather than repoint it.

### Prove the link before handing it over

```bash
curl -sI "https://$HOST:8443/<slot>/App.ipa"        # 200, content-length = the size publish.py printed
curl -sI "https://$HOST:8443/<slot>/manifest.plist" # 200
curl -sI "https://$HOST:8443/"                      # 200
```

A TLS error here is the *HTTPS certificates* requirement. A connection refused is the static server.

### Hand over

```
Open https://<host>:8443/ in Safari on the phone, Tailscale on → Install next to <app> <branch> <sha>.
```

Safari only: `itms-services` links do nothing in other browsers. Say that the Mac must stay awake until they have installed. Then leave the server and the serve running — stopping them breaks the link before the user has tapped it.

**Done when** all three `curl` lines returned what they should and the user has the URL, the build to tap, and the Safari and awake caveats.

## Requirements

| Requirement | How to check | If missing |
|---|---|---|
| **Tailscale on the Mac** | `"$TS" status` runs and lists this machine online. On macOS the App Store build keeps its CLI inside the app bundle, so `command -v tailscale` alone proves nothing. | Install Tailscale and sign in. |
| **Tailscale on the phone, same tailnet** | `"$TS" status` lists an iOS peer, online. | Install Tailscale on the phone with the same account, and switch it on. |
| **MagicDNS and HTTPS certificates** | `serve --https=8443` succeeds, and `curl -sI https://$HOST:8443/` has no TLS error. Serve prints an enable link when HTTPS is off. | Enable MagicDNS and HTTPS in the Tailscale admin console, DNS page. A self-signed certificate is no substitute: iOS refuses the install. |
| **Phone registered in the Apple team, Developer Mode on** | The UDID is in every embedded profile (`publish.py` exits 3 otherwise); `devicectl device info details` shows `developerModeStatus: enabled`. | Connect the phone once to this Mac by cable or same Wi-Fi and run the direct route, which registers it. Then Settings → Privacy & Security → Developer Mode, and reboot. |
| **Mac awake while the user is away** | `pmset -g` shows `sleep 0`, or the Mac is on power with sleep disabled. | Change the energy settings, or `caffeinate -s` for the session. Say it either way: a sleeping Mac looks exactly like a broken link. |
| **Static file server** | `python3` runs. | Any static server bound to `127.0.0.1` that answers `HEAD` will do. |

## App data

Whether an over-the-air install keeps the data of the build it replaces has **not been measured yet**. Until it is, say so before handing over the link when the app already sits on the phone with data the user cares about, and let them choose.

## Leave the repo as you found it

Before reporting, on either route:

```bash
git status --porcelain -- '*.pbxproj' '*.xcconfig' '*.entitlements'
```

Empty, or the run is not finished: anything here is a signing change the build or you introduced, and it goes back. Other noise a build regenerates follows the repo's own rule for it.

## Stopping

When the user asks, and not before:

```bash
"$TS" serve --https=8443 off
portly stop ios-build/static   # or: kill $(cat "$HOME/Library/Caches/ios-build/server.pid")
```
