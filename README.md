# hostfiles

M17 host files built from the [DVRef](https://dvref.com/) API and served
through GitHub Pages.

## What this does

A scheduled GitHub Action runs every 4 hours. It pulls the reflector
listings from the DVRef v2 API, builds `M17Hosts.txt` and `M17Hosts.json`
with [`scripts/build_hostfiles.py`](scripts/build_hostfiles.py), and commits
them when the data has changed. A change to the generation timestamp alone
does not count. GitHub Pages serves the committed files over a Fastly-backed
CDN.

## Sources

| DVRef endpoint | Included | Designator |
| --- | --- | --- |
| `/api/v2/mrefd/reflectors/` | all listed M17 reflectors | `M17-` + designator |
| `/api/v2/urfd/reflectors/` | URFD reflectors with `M17` in `enabled_modes` (port 17000) | `URF` + designator |
| `/api/v2/vex/servers/{slug}/` | Vexillium (VEX) instances with mode `M17` | `VEX` + designator |

A VEX instance with the same IP and port as an MREFD or URFD entry is
skipped as a duplicate. In the `.txt` file each line reads
`DESIGNATOR address port`, using IPv4 when it's available and IPv6
otherwise.

Data © DVRef, licensed [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
Both files carry the attribution "Reflector data provided by DVRef —
https://dvref.com/" and a note that the data has been combined and
reformatted.

Before November 2026 these files mirrored hostfiles.refcheck.radio. That
service shuts down on 2027-01-01.

## Client URLs

Clients fetch from:

```
https://m17-project.github.io/hostfiles/M17Hosts.txt
https://m17-project.github.io/hostfiles/M17Hosts.json
```

## Setup

1. In **Settings → Pages**, set the source to **Deploy from a branch**,
   branch `main`, folder `/ (root)`.
2. In **Settings → Actions → General**, set workflow permissions to
   **Read and write**.
3. In **Settings → Secrets and variables → Actions**, add a repository
   secret named `DVREF_TOKEN` holding a DVRef API token. Generate one at
   https://dvref.com/accounts/token/.
4. Run the **Sync hostfiles** workflow once by hand (Actions tab →
   *Run workflow*).

DVRef identifies this client by the User-Agent
`M17-hostfiles/1.0 (+https://github.com/M17-Project/hostfiles)`. That
string is allowlisted at DVRef's Cloudflare layer, so check with DVRef
before you change it, or requests may be blocked with a challenge page
(HTTP 403).

## Operations

- The workflow runs at `:17` past every 4th hour (UTC).
- Each run makes 3 + (number of VEX servers) API calls. DVRef allows
  60 authenticated requests per hour per account.
- GitHub cron can be delayed or skipped under load.
- To force a refresh, trigger the workflow manually from the Actions tab.
- To test locally: download the API responses into a directory as
  `mrefd.json`, `urfd.json` and `vex_<slug>.json` (see the workflow), then
  run `python3 scripts/build_hostfiles.py <that dir> .`.
